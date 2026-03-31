#!/usr/bin/env python3
import json
import sys

def is_duplicate_exec(payload: dict) -> dict:
    state = payload.get("state") or {}
    session_key = payload.get("session_key")
    command = payload.get("command")
    tool_name = payload.get("tool_name")

    completed = (
        (state.get("completedRuntimeActionBySession") or {}).get(session_key)
        if session_key else None
    )

    is_duplicate = bool(
        completed
        and completed.get("family") == "file.delete"
        and isinstance(command, str)
        and "guarded_file_delete.sh" in command
        and completed.get("target")
        and completed["target"] in command
    )

    return {
        "ok": True,
        "is_duplicate": is_duplicate,
        "completed_runtime_action": completed,
        "tool_name": tool_name,
        "command": command,
    }

def main():
    payload = json.load(sys.stdin)
    print(json.dumps(is_duplicate_exec(payload)))

if __name__ == "__main__":
    main()
