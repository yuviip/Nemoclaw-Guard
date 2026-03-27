#!/usr/bin/env bash
set -euo pipefail

source /opt/openclaw-policy-sdk/lib/policy_sdk.sh

json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'
}

emit_json() {
  local status="$1"
  local decision="$2"
  local reason="$3"
  local message="$4"
  local target_path="${5:-}"

  printf "{"
  printf "\"status\":\"%s\"," "$status"
  printf "\"decision\":\"%s\"," "$decision"
  printf "\"reason\":\"%s\"," "$reason"
  printf "\"message\":%s" "$(printf "%s" "$message" | json_escape)"

  if [ -n "$target_path" ]; then
    printf ",\"target_path\":%s" "$(printf "%s" "$target_path" | json_escape)"
  fi

  printf "}\n"
}

usage() {
  cat >&2 <<'USAGE'
usage: guarded_file_delete.sh <requester_id> <requester_role> <target_path>
USAGE
}

if [ "$#" -lt 3 ]; then
  usage
  emit_json "error" "DENY" "invalid_arguments" "missing required arguments"
  exit 1
fi

REQUESTER_ID="$1"
REQUESTER_ROLE="$2"
TARGET_PATH="$3"

if [ -z "$REQUESTER_ID" ] || [ -z "$REQUESTER_ROLE" ] || [ -z "$TARGET_PATH" ]; then
  emit_json "error" "DENY" "invalid_arguments" "one or more required arguments are empty" "$TARGET_PATH"
  exit 1
fi

if [ ! -e "$TARGET_PATH" ]; then
  emit_json "denied" "DENY" "target_not_found" "target path does not exist" "$TARGET_PATH"
  exit 1
fi

DECISION_JSON="$(policy_decide \
  "$REQUESTER_ID" \
  "$REQUESTER_ROLE" \
  "delete_files" \
  "$TARGET_PATH" \
  "high"
)"

DECISION="$(policy_extract_decision "$DECISION_JSON")"

case "$DECISION" in
  ALLOW)
    ;;
  DENY)
    emit_json "denied" "DENY" "policy_denied" "$DECISION_JSON" "$TARGET_PATH"
    exit 2
    ;;
  REQUIRE_OWNER_CONFIRMATION)
    emit_json "requires_confirmation" "REQUIRE_OWNER_CONFIRMATION" "policy_requires_owner_confirmation" "$DECISION_JSON" "$TARGET_PATH"
    exit 3
    ;;
  REQUIRE_OWNER_APPROVAL)
    emit_json "requires_approval" "REQUIRE_OWNER_APPROVAL" "policy_requires_owner_approval" "$DECISION_JSON" "$TARGET_PATH"
    exit 4
    ;;
  *)
    emit_json "error" "DENY" "unknown_policy_decision" "$DECISION_JSON" "$TARGET_PATH"
    exit 5
    ;;
esac

if ! rm -f -- "$TARGET_PATH"; then
  emit_json "error" "ALLOW" "delete_failed" "file deletion command failed" "$TARGET_PATH"
  exit 6
fi

emit_json "executed" "ALLOW" "delete_executed" "file deleted successfully" "$TARGET_PATH"
