#!/usr/bin/env python3
import json
import sys
import importlib.util

STORE_MOD_PATH = "/opt/nemoclaw-guard/runtime/state/approval_session_store.py"
RESOLVER_MOD_PATH = "/opt/nemoclaw-guard/resolver/approval_resolver_v2.py"


def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


store = load_module("approval_session_store", STORE_MOD_PATH)
resolver = load_module("approval_resolver_v2", RESOLVER_MOD_PATH)


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
