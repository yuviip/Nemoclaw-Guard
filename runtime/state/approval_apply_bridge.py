#!/usr/bin/env python3
import json
import sys
import os
import importlib.util
import urllib.request
import urllib.error

STORE_MOD_PATH = "/opt/nemoclaw-guard/runtime/state/approval_session_store.py"
RESOLVER_MOD_PATH = "/opt/nemoclaw-guard/resolver/approval_resolver_v2.py"
OPENCLAW_ENV_PATH = "/opt/openclaw/openclaw.env"


def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_openclaw_env(path: str) -> None:
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


store = load_module("approval_session_store", STORE_MOD_PATH)
resolver = load_module("approval_resolver_v2", RESOLVER_MOD_PATH)


def resolve_via_policy_api(text: str, session: dict):
    load_openclaw_env(OPENCLAW_ENV_PATH)

    base = os.environ.get("POLICY_API_BASE", "").strip()
    if not base:
        return None

    url = base.rstrip("/") + "/approval/resolve"
    payload = {
        "text": text,
        "request_session": session
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        # 404/501/etc -> endpoint not ready yet, fallback locally
        return None
    except Exception:
        return None

    try:
        parsed = json.loads(body)
    except Exception:
        return None

    if isinstance(parsed, dict) and isinstance(parsed.get("resolver_result"), dict):
        return parsed["resolver_result"]

    if isinstance(parsed, dict) and isinstance(parsed.get("result"), dict):
        return parsed["result"]

    if isinstance(parsed, dict) and parsed.get("intent"):
        return parsed

    return None


def apply_result(session: dict, resolver_result: dict) -> dict:
    intent = resolver_result.get("intent")

    if intent == "approve_single":
        target_id = resolver_result.get("action_id")
        for action in session.get("actions", []):
            if action.get("action_id") == target_id:
                action["approval_state"] = "approved"

    elif intent == "deny_single":
        target_id = resolver_result.get("action_id")
        for action in session.get("actions", []):
            if action.get("action_id") == target_id:
                action["approval_state"] = "denied"

    elif intent == "approve_session":
        for action in session.get("actions", []):
            if action.get("approval_state", "pending") == "pending":
                action["approval_state"] = "approved"

    elif intent == "deny_session":
        for action in session.get("actions", []):
            if action.get("approval_state", "pending") == "pending":
                action["approval_state"] = "denied"

    return session


def recompute_session_status(session: dict) -> None:
    actions = session.get("actions", [])
    states = [a.get("approval_state", "pending") for a in actions]

    if actions and all(s == "approved" for s in states):
        session["status"] = "approved"
    elif actions and all(s == "denied" for s in states):
        session["status"] = "denied"
    elif any(s in ("approved", "denied") for s in states):
        session["status"] = "partial"
    else:
        session["status"] = "pending"


def main():
    payload = json.load(sys.stdin)
    session_id = payload["request_session_id"]
    text = payload["text"]

    session = store.get_session(session_id)
    if not session:
        print(json.dumps({
            "ok": False,
            "reason": "session_not_found"
        }))
        return

    resolver_result = resolve_via_policy_api(text, session)

    if not resolver_result:
        resolver_result = resolver.resolve({
            "text": text,
            "request_session": session
        })

    updated_session = apply_result(session, resolver_result)
    recompute_session_status(updated_session)
    store.put_session(session_id, updated_session)

    print(json.dumps({
        "ok": True,
        "request_session_id": session_id,
        "resolver_result": resolver_result,
        "updated_session": updated_session
    }))


if __name__ == "__main__":
    main()
