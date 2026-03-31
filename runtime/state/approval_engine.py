#!/usr/bin/env python3
import json
import sys
import importlib.util
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from path_config import (
    APPROVAL_PREPARE_FILE_DELETE_PATH,
    APPROVAL_EXECUTE_FILE_DELETE_PATH,
    APPROVAL_APPLY_RUNTIME_OUTCOME_PATH,
    APPROVAL_CHECK_DUPLICATE_EXEC_PATH,
)

def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

prepare_file_delete_mod = load_module(
    "approval_prepare_file_delete",
    APPROVAL_PREPARE_FILE_DELETE_PATH,
)
execute_file_delete_mod = load_module(
    "approval_execute_file_delete",
    APPROVAL_EXECUTE_FILE_DELETE_PATH,
)
apply_runtime_outcome_mod = load_module(
    "approval_apply_runtime_outcome",
    APPROVAL_APPLY_RUNTIME_OUTCOME_PATH,
)
check_duplicate_exec_mod = load_module(
    "approval_check_duplicate_exec",
    APPROVAL_CHECK_DUPLICATE_EXEC_PATH,
)

def action_prepare_file_delete(payload: dict) -> dict:
    chat_id = payload.get("chat_id")
    target_path = payload.get("target_path")

    if not chat_id or not isinstance(chat_id, str):
        return {
            "ok": False,
            "error": "missing_chat_id",
        }

    if not target_path or not isinstance(target_path, str):
        return {
            "ok": False,
            "error": "missing_target_path",
        }

    session_payload = {
        "chat_id": chat_id,
        "target_path": target_path,
    }

    # approval_prepare_file_delete.py currently exposes main() only,
    # so we reproduce its public behavior here by using its helper functions if present.
    if hasattr(prepare_file_delete_mod, "build_resource") and hasattr(prepare_file_delete_mod, "approval_session_create"):
        created = prepare_file_delete_mod.approval_session_create.build_session({
            "chat_id": chat_id,
            "family": "file.delete",
            "resource": prepare_file_delete_mod.build_resource(target_path),
        })
        prepare_file_delete_mod.approval_session_create.store.put_session(
            created["request_session_id"], created
        )
        return {
            "ok": True,
            "request_session_id": created["request_session_id"],
            "action_id": created["actions"][0]["action_id"],
            "session": created,
            "family": "file.delete",
            "target_path": target_path,
        }

    return {
        "ok": False,
        "error": "prepare_file_delete_runtime_not_supported",
    }

def action_execute_file_delete(payload: dict) -> dict:
    import io
    import contextlib

    old_stdin = sys.stdin
    sys.stdin = io.StringIO(json.dumps(payload))
    try:
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            execute_file_delete_mod.main()
        return json.loads(captured.getvalue().strip())
    finally:
        sys.stdin = old_stdin

def action_apply_runtime_outcome(payload: dict) -> dict:
    if hasattr(apply_runtime_outcome_mod, "apply_runtime_outcome"):
        updated = apply_runtime_outcome_mod.apply_runtime_outcome(payload)
        return {
            "ok": True,
            "state": updated,
        }

    return {
        "ok": False,
        "error": "apply_runtime_outcome_runtime_not_supported",
    }

def action_check_duplicate_exec(payload: dict) -> dict:
    if hasattr(check_duplicate_exec_mod, "is_duplicate_exec"):
        return check_duplicate_exec_mod.is_duplicate_exec(payload)

    return {
        "ok": False,
        "error": "check_duplicate_exec_runtime_not_supported",
    }

ACTIONS = {
    "prepare_file_delete": action_prepare_file_delete,
    "execute_file_delete": action_execute_file_delete,
    "apply_runtime_outcome": action_apply_runtime_outcome,
    "check_duplicate_exec": action_check_duplicate_exec,
}

def main():
    req = json.load(sys.stdin)

    action = req.get("action")
    payload = req.get("payload") or {}

    if not action or not isinstance(action, str):
        print(json.dumps({
            "ok": False,
            "error": "missing_action",
        }))
        raise SystemExit(1)

    if action not in ACTIONS:
        print(json.dumps({
            "ok": False,
            "error": f"unknown_action:{action}",
        }))
        raise SystemExit(1)

    result = ACTIONS[action](payload)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
