#!/opt/nemoclaw/.venv/bin/python3
import json
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

    prompt = """
You are an approval intent resolver for Nemoclaw Guard.

Given:
1. a user message
2. a request session with one or more pending approval actions

Return ONLY valid JSON with exactly one intent:
- approve_single
- deny_single
- approve_session
- deny_session
- ambiguous
- no_match

Critical rules:
1. Only classify approve/deny when the message is clearly an approval reply to a pending request.
2. If the message is a fresh operational request, a restatement of the original request, or an instruction to perform the action itself, return {"intent":"no_match"}.
3. Mentioning the file/resource/action is not enough by itself to count as approval.
4. Imperative requests like "delete the file", "remove it", "do it", "please execute" are fresh requests, not approvals.
5. If there is exactly one pending action and the message is clearly approving, you may return approve_single for that action_id.
6. If there is exactly one pending action and the message is clearly denying, you may return deny_single for that action_id.
7. Do not invent action_ids.
8. No markdown. No explanation. JSON only.

User text:
__USER_TEXT__

Pending actions:
__ACTIONS__

Examples:
{"intent":"approve_session"}
{"intent":"deny_session"}
{"intent":"approve_single","action_id":"act_123"}
{"intent":"deny_single","action_id":"act_123"}
{"intent":"ambiguous"}
{"intent":"no_match"}
""".strip()

    prompt = prompt.replace("__USER_TEXT__", text)
    prompt = prompt.replace("__ACTIONS__", "\n".join(action_lines) if action_lines else "- none")

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

    return {"ok": True, **parsed, "resolver": "llm"}


def resolve(text: str, session: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return call_nemo_llm(text, session)
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
