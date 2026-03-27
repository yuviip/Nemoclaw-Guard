#!/usr/bin/env bash
set -euo pipefail

source "${NEMOCLAW_POLICY_SDK_PATH:-/opt/nemoclaw-guard/sdk/lib/policy_sdk.sh}"
source /opt/nemoclaw-guard/wrappers/lib/guarded_common.sh

usage() {
  cat >&2 <<USAGE
usage: guarded_docker_restart.sh <requester_id> <requester_role> <container_name>
USAGE
}

if [ "$#" -lt 3 ]; then
  usage
  guard_emit_json "error" "DENY" "invalid_arguments" "missing required arguments"
  exit "$GUARD_RC_INVALID_ARGS"
fi

REQUESTER_ID="$1"
REQUESTER_ROLE="$2"
CONTAINER_NAME="$3"

if [ -z "$REQUESTER_ID" ] || [ -z "$REQUESTER_ROLE" ] || [ -z "$CONTAINER_NAME" ]; then
  guard_emit_json "error" "DENY" "invalid_arguments" "one or more required arguments are empty" \
    "container_name" "$CONTAINER_NAME"
  exit "$GUARD_RC_INVALID_ARGS"
fi

RESOURCE="$(policy_build_docker_restart_resource "$CONTAINER_NAME")"

DECISION_JSON="$(policy_decide \
  "$REQUESTER_ID" \
  "$REQUESTER_ROLE" \
  "docker_restart" \
  "$RESOURCE" \
  "high"
)"
DECISION="$(policy_extract_decision "$DECISION_JSON")"

if ! guard_handle_decision "$DECISION" "$DECISION_JSON" \
  "resource" "$RESOURCE" \
  "container_name" "$CONTAINER_NAME"; then
  exit "$?"
fi

DOCKER_BIN="${NEMOCLAW_DOCKER_BIN:-docker}"

if ! command -v "$DOCKER_BIN" >/dev/null 2>&1; then
  guard_emit_json "error" "ALLOW" "docker_not_found" "docker is not available on this host" \
    "resource" "$RESOURCE" \
    "container_name" "$CONTAINER_NAME"
  exit "$GUARD_RC_EXEC_FAILURE"
fi

if ! OUTPUT="$("$DOCKER_BIN" restart "$CONTAINER_NAME" 2>&1)"; then
  guard_emit_json "error" "ALLOW" "docker_restart_failed" "$OUTPUT" \
    "resource" "$RESOURCE" \
    "container_name" "$CONTAINER_NAME"
  exit "$GUARD_RC_EXEC_FAILURE"
fi

guard_emit_json "executed" "ALLOW" "docker_restart_executed" "docker restart executed successfully" \
  "resource" "$RESOURCE" \
  "container_name" "$CONTAINER_NAME" \
  "output" "$OUTPUT"
