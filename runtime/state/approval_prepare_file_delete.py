#!/usr/bin/env python3
import json
import sys
import importlib.util
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from path_config import APPROVAL_SESSION_CREATE_PATH

CREATE_MOD_PATH = APPROVAL_SESSION_CREATE_PATH


def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


approval_session_create = load_module("approval_session_create", CREATE_MOD_PATH)


def build_resource(target_path: str) -> dict:
    name = Path(target_path).name or target_path
    return {
        "kind": "file",
        "primary": target_path,
        "display": name,
        "aliases": [name, target_path]
    }


def main():
    payload = json.load(sys.stdin)

    chat_id = payload.get("chat_id")
    target_path = payload.get("target_path")

    if not chat_id or not isinstance(chat_id, str):
        print(json.dumps({
            "ok": False,
            "error": "missing_chat_id"
        }))
        raise SystemExit(1)

    if not target_path or not isinstance(target_path, str):
        print(json.dumps({
            "ok": False,
            "error": "missing_target_path"
        }))
        raise SystemExit(1)

    session_payload = {
        "chat_id": chat_id,
        "family": "file.delete",
        "resource": build_resource(target_path)
    }

    created = approval_session_create.build_session(session_payload)
    approval_session_create.store.put_session(created["request_session_id"], created)

    print(json.dumps({
        "ok": True,
        "request_session_id": created["request_session_id"],
        "action_id": created["actions"][0]["action_id"],
        "session": created,
        "family": "file.delete",
        "target_path": target_path
    }))


if __name__ == "__main__":
    main()
