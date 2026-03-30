#!/usr/bin/env bash
set -euo pipefail

source /opt/nemoclaw-guard/wrappers/lib/path_config.sh
source "$NEMOCLAW_OPENCLAW_POLICY_SDK_PATH"
source "$NEMOCLAW_GUARDED_COMMON_PATH"

usage() {
  cat >&2 <<USAGE
usage: guarded_file_delete.sh <requester_id> <requester_role> <target_path>
USAGE
}

if [ "$#" -lt 3 ]; then
  usage
  guard_emit_json "error" "DENY" "invalid_arguments" "missing required arguments"
  exit "$GUARD_RC_INVALID_ARGS"
fi

REQUESTER_ID="$1"
REQUESTER_ROLE="$2"
TARGET_PATH="$3"

if [ -z "$REQUESTER_ID" ] || [ -z "$REQUESTER_ROLE" ] || [ -z "$TARGET_PATH" ]; then
  guard_emit_json "error" "DENY" "invalid_arguments" "one or more required arguments are empty" \
    "target_path" "$TARGET_PATH"
  exit "$GUARD_RC_INVALID_ARGS"
fi

if [ ! -e "$TARGET_PATH" ]; then
  guard_emit_json "denied" "DENY" "target_not_found" "target path does not exist" \
    "target_path" "$TARGET_PATH"
  exit "$GUARD_RC_INVALID_ARGS"
fi

DECISION_JSON="$(policy_decide \
  "$REQUESTER_ID" \
  "$REQUESTER_ROLE" \
  "delete_files" \
  "$TARGET_PATH" \
  "high"
)"
DECISION="$(policy_extract_decision "$DECISION_JSON")"

if ! guard_handle_decision "$DECISION" "$DECISION_JSON" \
  "target_path" "$TARGET_PATH"; then
  exit "$?"
fi

if ! rm -f -- "$TARGET_PATH"; then
  guard_emit_json "error" "ALLOW" "delete_failed" "file deletion command failed" \
    "target_path" "$TARGET_PATH"
  exit "$GUARD_RC_EXEC_FAILURE"
fi

guard_emit_json "executed" "ALLOW" "delete_executed" "file deleted successfully" \
  "target_path" "$TARGET_PATH"
