#!/usr/bin/env python3
import json
import sys
import importlib.util
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from path_config import (
    APPROVAL_SESSION_STORE_PATH,
    APPROVAL_RESOLVER_V2_PATH,
)

STORE_MOD_PATH = APPROVAL_SESSION_STORE_PATH
RESOLVER_MOD_PATH = APPROVAL_RESOLVER_V2_PATH


def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


store = load_module("approval_session_store", STORE_MOD_PATH)
resolver = load_module("approval_resolver_v2", RESOLVER_MOD_PATH)


def main():
    payload = json.load(sys.stdin)
    session_id = payload["request_session_id"]
    text = payload["text"]

    session = store.get_session(session_id)
    if not session:
        print(json.dumps({
            "ok": False,
            "intent": "no_match",
            "reason": "session_not_found"
        }))
        return

    result = resolver.resolve({
        "text": text,
        "request_session": session
    })

    print(json.dumps({
        "ok": True,
        "request_session_id": session_id,
        "resolver_result": result
    }))


if __name__ == "__main__":
    main()
