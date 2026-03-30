#!/opt/nemoclaw/.venv/bin/python3
import json
import re
import sys
from typing import Any, Dict, List


VALID_INTENTS = {
    "approve_single",
    "deny_single",
    "approve_session",
    "deny_session",
    "ambiguous",
    "no_match",
}


def norm(s: str) -> str:
    return (s or "").strip().lower()


def extract_aliases(action: Dict[str, Any]) -> List[str]:
    r = action.get("resource", {}) or {}
    vals: List[str] = []
    for x in [r.get("display"), r.get("primary")] + list(r.get("aliases") or []):
        if isinstance(x, str) and x.strip():
            vals.append(norm(x))
    # unique, stable
    out = []
    seen = set()
    for v in vals:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def deterministic_resolve(text: str, session: Dict[str, Any]) -> Dict[str, Any]:
    t = norm(text)
    actions = session.get("actions", []) or []

    if not t:
        return {"ok": True, "intent": "no_match", "resolver": "deterministic"}

    pos_words = ["approve", "confirm", "yes", "ok"]
    neg_words = ["deny", "reject", "cancel", "no", "stop"]

    has_pos = any(w in t for w in pos_words)
    has_neg = any(w in t for w in neg_words)

    if has_pos and not has_neg:
        polarity = "approve"
    elif has_neg and not has_pos:
        polarity = "deny"
    else:
        return {"ok": True, "intent": "no_match", "resolver": "deterministic"}

    session_wide_markers = [
        "all",
        "everything",
        "entire session",
        "whole session",
    ]
    if any(m in t for m in session_wide_markers):
        return {
            "ok": True,
            "intent": "approve_session" if polarity == "approve" else "deny_session",
            "scope": "whole_session",
            "resolver": "deterministic",
        }

    matches = []
    for action in actions:
        aliases = extract_aliases(action)
        if any(alias and alias in t for alias in aliases):
            matches.append(action)

    if len(matches) == 1:
        return {
            "ok": True,
            "intent": "approve_single" if polarity == "approve" else "deny_single",
            "scope": "single_action",
            "action_id": matches[0].get("action_id"),
            "resolver": "deterministic",
        }

    if len(matches) > 1:
        return {"ok": True, "intent": "ambiguous", "resolver": "deterministic"}

    if len(actions) == 1:
        only_action_id = actions[0].get("action_id")
        return {
            "ok": True,
            "intent": "approve_single" if polarity == "approve" else "deny_single",
            "scope": "single_action",
            "action_id": only_action_id,
            "resolver": "deterministic_single_action_fallback",
        }

    return {"ok": True, "intent": "no_match", "resolver": "deterministic"}


def call_nemo_llm(text: str, session: Dict[str, Any]) -> Dict[str, Any]:
    # additive helper only; if anything goes wrong we fallback safely
    import os
    import subprocess

    nemo_url = os.environ.get("NEMO_URL", "http://127.0.0.1:8000/v1/chat/completions")
    nemo_model = os.environ.get("NEMO_MODEL", "gpt-4o-mini")
    config_id = os.environ.get("CONFIG_ID", "openclaw")

    actions = session.get("actions", []) or []
    action_lines = []
    for a in actions:
        rid = a.get("action_id")
        aliases = extract_aliases(a)
        action_lines.append(
            f"- action_id={rid}; aliases={aliases}; approval_state={a.get('approval_state', 'pending')}"
        )

    prompt = f"""
You are an approval intent resolver for Nemoclaw Guard.

Your task:
Given a user's natural-language reply and a request session with one or more pending actions,
return ONLY a JSON object with one of these intents:

- approve_single
- deny_single
- approve_session
- deny_session
- ambiguous
- no_match

Rules:
1. If the user clearly approves all pending actions -> approve_session
2. If the user clearly denies all pending actions -> deny_session
3. If the user clearly approves one specific action -> approve_single with action_id
4. If the user clearly denies one specific action -> deny_single with action_id
5. If the user intent is unclear -> ambiguous or no_match
6. Return valid JSON only. No markdown. No explanation.
7. Do not invent action_ids.
8. Prefer exact action match when aliases or file names match the text.
9. If there is exactly one action in the session and the user's reply is clearly positive/negative,
   you may map it to approve_single/deny_single for that action.

User text:
{text}

Pending actions:
{chr(10).join(action_lines) if action_lines else "- none"}

Return format examples:
{{"intent":"approve_session"}}
{{"intent":"deny_session"}}
{{"intent":"approve_single","action_id":"act_123"}}
{{"intent":"deny_single","action_id":"act_123"}}
{{"intent":"ambiguous"}}
{{"intent":"no_match"}}
""".strip()

    payload = {
        "model": nemo_model,
        "messages": [{"role": "user", "content": prompt}],
        "guardrails": {"config_id": config_id},
    }

    proc = subprocess.run(
        ["curl", "-sS", nemo_url, "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
        text=True,
        capture_output=True,
        check=False,
        timeout=25,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"curl_failed rc={proc.returncode}: {proc.stderr.strip()}")

    raw = proc.stdout.strip()
    data = json.loads(raw)
    content = data["choices"][0]["message"]["content"].strip()

    parsed = json.loads(content)
    if not isinstance(parsed, dict):
        raise ValueError("llm_result_not_object")

    intent = parsed.get("intent")
    if intent not in VALID_INTENTS:
        raise ValueError("invalid_intent")

    out = {"ok": True, **parsed, "resolver": "llm"}
    return out


def resolve(text: str, session: Dict[str, Any]) -> Dict[str, Any]:
    try:
        llm_result = call_nemo_llm(text, session)
        return llm_result
    except Exception:
        return deterministic_resolve(text, session)


def main():
    payload = json.load(sys.stdin)
    text = payload.get("text", "")
    session = payload.get("request_session", {}) or {}
    result = resolve(text, session)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
