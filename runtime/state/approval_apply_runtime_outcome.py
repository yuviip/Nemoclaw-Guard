#!/usr/bin/env python3
import json
import sys

def apply_runtime_outcome(payload: dict) -> dict:
    state = payload["state"]
    session_key = payload["session_key"]
    runtime_approval = payload["runtime_approval"]
    session_status = payload.get("session_status")
    execution_status = payload.get("execution_status")

    # update pending approvals
    for approval in state.get("pendingApprovals", {}).values():
        if approval.get("runtimeRequestSessionId") == runtime_approval.get("requestSessionId"):
            if execution_status == "executed":
                approval["status"] = "executed"
            elif session_status == "approved":
                approval["status"] = "approved"
            elif session_status == "denied":
                approval["status"] = "denied"

    # record completed runtime action
    if execution_status == "executed":
        state.setdefault("completedRuntimeActionBySession", {})
        state["completedRuntimeActionBySession"][session_key] = {
            "family": runtime_approval.get("family"),
            "target": runtime_approval.get("target"),
            "requestSessionId": runtime_approval.get("requestSessionId")
        }

    # finalize lifecycle
    if execution_status == "executed" or (
        session_status and session_status not in ("pending", "partial")
    ):
        if "runtimeApprovalBySession" in state:
            state["runtimeApprovalBySession"].pop(session_key, None)

        if "guardActionsBySession" in state:
            state["guardActionsBySession"].pop(session_key, None)

    return state


def main():
    payload = json.load(sys.stdin)
    updated = apply_runtime_outcome(payload)
    print(json.dumps({"ok": True, "state": updated}))


if __name__ == "__main__":
    main()
