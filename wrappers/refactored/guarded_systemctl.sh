#!/usr/bin/env bash
set -euo pipefail

source "${NEMOCLAW_POLICY_SDK_PATH:-/opt/nemoclaw-guard/sdk/lib/policy_sdk.sh}"
source /opt/nemoclaw-guard/wrappers/lib/guarded_common.sh

usage() {
  cat >&2 <<USAGE
usage: guarded_systemctl.sh <requester_id> <requester_role> <operation> <unit_name>
USAGE
}

if [ "$#" -lt 4 ]; then
  usage
  guard_emit_json "error" "DENY" "invalid_arguments" "missing required arguments"
  exit "$GUARD_RC_INVALID_ARGS"
fi

REQUESTER_ID="$1"
REQUESTER_ROLE="$2"
OPERATION="$3"
UNIT_NAME="$4"

if [ -z "$REQUESTER_ID" ] || [ -z "$REQUESTER_ROLE" ] || [ -z "$OPERATION" ] || [ -z "$UNIT_NAME" ]; then
  guard_emit_json "error" "DENY" "invalid_arguments" "one or more required arguments are empty" \
    "operation" "$OPERATION" \
    "unit_name" "$UNIT_NAME"
  exit "$GUARD_RC_INVALID_ARGS"
fi

case "$OPERATION" in
  start|stop|restart|reload|status)
    ;;
  *)
    guard_emit_json "error" "DENY" "invalid_operation" "operation must be one of: start, stop, restart, reload, status" \
      "operation" "$OPERATION" \
      "unit_name" "$UNIT_NAME"
    exit "$GUARD_RC_INVALID_ARGS"
    ;;
esac

RESOURCE="$(policy_build_systemctl_resource "$OPERATION" "$UNIT_NAME")"

RISK_LEVEL="high"
if [ "$OPERATION" = "status" ]; then
  RISK_LEVEL="low"
fi

DECISION_JSON="$(policy_decide \
  "$REQUESTER_ID" \
  "$REQUESTER_ROLE" \
  "systemctl_control" \
  "$RESOURCE" \
  "$RISK_LEVEL"
)"
DECISION="$(policy_extract_decision "$DECISION_JSON")"

if ! guard_handle_decision "$DECISION" "$DECISION_JSON" \
  "resource" "$RESOURCE" \
  "operation" "$OPERATION" \
  "unit_name" "$UNIT_NAME"; then
  exit "$?"
fi

SYSTEMCTL_BIN="${NEMOCLAW_SYSTEMCTL_BIN:-systemctl}"

if ! command -v "$SYSTEMCTL_BIN" >/dev/null 2>&1; then
  guard_emit_json "error" "ALLOW" "systemctl_not_found" "systemctl is not available on this host" \
    "resource" "$RESOURCE" \
    "operation" "$OPERATION" \
    "unit_name" "$UNIT_NAME"
  exit "$GUARD_RC_EXEC_FAILURE"
fi

if ! OUTPUT="$("$SYSTEMCTL_BIN" "$OPERATION" "$UNIT_NAME" 2>&1)"; then
  guard_emit_json "error" "ALLOW" "systemctl_command_failed" "$OUTPUT" \
    "resource" "$RESOURCE" \
    "operation" "$OPERATION" \
    "unit_name" "$UNIT_NAME"
  exit "$GUARD_RC_EXEC_FAILURE"
fi

guard_emit_json "executed" "ALLOW" "systemctl_executed" "systemctl command executed successfully" \
  "resource" "$RESOURCE" \
  "operation" "$OPERATION" \
  "unit_name" "$UNIT_NAME" \
  "output" "$OUTPUT"
