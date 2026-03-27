#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime, timezone
import importlib.util


STORE_MOD_PATH = "/opt/nemoclaw-guard/runtime/state/approval_session_store.py"
APPLY_BRIDGE_PATH = "/opt/nemoclaw-guard/runtime/state/approval_apply_bridge.py"


def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


store = load_module("approval_session_store", STORE_MOD_PATH)
apply_bridge = load_module("approval_apply_bridge", APPLY_BRIDGE_PATH)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def run_apply(request_session_id: str, text: str) -> dict:
    import io
    import contextlib

    payload = {
        "request_session_id": request_session_id,
        "text": text,
    }

    old_stdin = sys.stdin
    sys.stdin = io.StringIO(json.dumps(payload))
    try:
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            apply_bridge.main()
        return json.loads(captured.getvalue().strip())
    finally:
        sys.stdin = old_stdin


def execute_file_delete_actions(session: dict) -> list:
    executed = []

    for action in session.get("actions", []):
        if action.get("family") != "file.delete":
            continue

        if action.get("approval_state") != "approved":
            continue

        if action.get("execution_state") == "executed":
            continue

        target = action.get("resource", {}).get("primary")
        if not target:
            action["execution_state"] = "failed"
            action["execution_reason"] = "missing_primary_resource"
            action["executed_at"] = now_iso()
            continue

        try:
            if os.path.exists(target):
                os.remove(target)
                action["execution_state"] = "executed"
                action["execution_reason"] = "file_deleted"
            else:
                action["execution_state"] = "skipped"
                action["execution_reason"] = "target_not_found"
        except Exception as e:
            action["execution_state"] = "failed"
            action["execution_reason"] = f"delete_failed:{type(e).__name__}"

        action["executed_at"] = now_iso()
        executed.append({
            "action_id": action.get("action_id"),
            "target_path": target,
            "execution_state": action.get("execution_state"),
            "execution_reason": action.get("execution_reason"),
        })

    return executed


def recompute_execution_status(session: dict):
    actions = session.get("actions", [])
    exec_states = [a.get("execution_state") for a in actions if a.get("family") == "file.delete"]

    if exec_states and all(s == "executed" for s in exec_states):
        session["execution_status"] = "executed"
    elif exec_states and any(s == "executed" for s in exec_states):
        session["execution_status"] = "partial"
    elif exec_states and all(s in ("skipped", "failed") for s in exec_states):
        session["execution_status"] = "not_executed"
    else:
        session["execution_status"] = "pending"


def main():
    payload = json.load(sys.stdin)
    request_session_id = payload["request_session_id"]
    text = payload["text"]

    apply_result = run_apply(request_session_id, text)
    session = store.get_session(request_session_id)

    if not session:
        print(json.dumps({
            "ok": False,
            "reason": "session_not_found_after_apply"
        }))
        return

    executed = execute_file_delete_actions(session)
    recompute_execution_status(session)
    store.put_session(request_session_id, session)

    print(json.dumps({
        "ok": True,
        "request_session_id": request_session_id,
        "apply_result": apply_result,
        "executed": executed,
        "updated_session": session
    }))


if __name__ == "__main__":
    main()
