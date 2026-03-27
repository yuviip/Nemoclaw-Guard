#!/usr/bin/env bash
set -euo pipefail

GUARD_RC_INVALID_ARGS=1
GUARD_RC_DENY=2
GUARD_RC_REQUIRE_CONFIRMATION=3
GUARD_RC_REQUIRE_APPROVAL=4
GUARD_RC_UNKNOWN_DECISION=5
GUARD_RC_EXEC_FAILURE=6

guard_json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'
}

guard_emit_json() {
  local status="$1"
  local decision="$2"
  local reason="$3"
  local message="$4"
  shift 4 || true

  printf "{"
  printf "\"status\":\"%s\"," "$status"
  printf "\"decision\":\"%s\"," "$decision"
  printf "\"reason\":\"%s\"," "$reason"
  printf "\"message\":%s" "$(printf "%s" "$message" | guard_json_escape)"

  while [ "$#" -gt 1 ]; do
    local key="$1"
    local value="$2"
    shift 2 || true

    if [ -n "${value:-}" ]; then
      printf ",\"%s\":%s" "$key" "$(printf "%s" "$value" | guard_json_escape)"
    fi
  done

  printf "}\n"
}

guard_handle_decision() {
  local decision="$1"
  local decision_json="$2"
  shift 2 || true

  case "$decision" in
    ALLOW)
      return 0
      ;;
    DENY)
      guard_emit_json "denied" "DENY" "policy_denied" "$decision_json" "$@"
      return "$GUARD_RC_DENY"
      ;;
    REQUIRE_OWNER_CONFIRMATION)
      guard_emit_json "requires_confirmation" "REQUIRE_OWNER_CONFIRMATION" "policy_requires_owner_confirmation" "$decision_json" "$@"
      return "$GUARD_RC_REQUIRE_CONFIRMATION"
      ;;
    REQUIRE_OWNER_APPROVAL)
      guard_emit_json "requires_approval" "REQUIRE_OWNER_APPROVAL" "policy_requires_owner_approval" "$decision_json" "$@"
      return "$GUARD_RC_REQUIRE_APPROVAL"
      ;;
    *)
      guard_emit_json "error" "DENY" "unknown_policy_decision" "$decision_json" "$@"
      return "$GUARD_RC_UNKNOWN_DECISION"
      ;;
  esac
}
