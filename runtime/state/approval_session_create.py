#!/usr/bin/env python3
import json
import sys
import uuid
import importlib.util
from path_config import APPROVAL_SESSION_STORE_PATH

STORE_MOD_PATH = APPROVAL_SESSION_STORE_PATH


def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


store = load_module("approval_session_store", STORE_MOD_PATH)


def build_session(payload: dict) -> dict:
    session_id = payload.get("request_session_id") or f"reqsess_{uuid.uuid4().hex[:12]}"
    action_id = payload.get("action_id") or f"act_{uuid.uuid4().hex[:8]}"

    session = {
        "request_session_id": session_id,
        "chat_id": payload["chat_id"],
        "status": "pending",
        "actions": [
            {
                "action_id": action_id,
                "family": payload["family"],
                "resource": payload["resource"],
                "approval_state": "pending"
            }
        ]
    }
    return session


def main():
    payload = json.load(sys.stdin)
    session = build_session(payload)
    store.put_session(session["request_session_id"], session)
    print(json.dumps({
        "ok": True,
        "request_session_id": session["request_session_id"],
        "action_id": session["actions"][0]["action_id"],
        "session": session
    }))


if __name__ == "__main__":
    main()
