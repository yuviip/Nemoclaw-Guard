#!/usr/bin/env bash
set -euo pipefail

source /opt/openclaw-policy-sdk/lib/policy_sdk.sh
source /opt/nemoclaw-guard/wrappers/lib/guarded_common.sh

usage() {
  cat >&2 <<USAGE
usage: guarded_ha_call.sh <requester_id> <requester_role> <service> <entity_id> [json_payload]
USAGE
}

if [ "$#" -lt 4 ]; then
  usage
  guard_emit_json "error" "DENY" "invalid_arguments" "missing required arguments"
  exit "$GUARD_RC_INVALID_ARGS"
fi

REQUESTER_ID="$1"
REQUESTER_ROLE="$2"
SERVICE="$3"
ENTITY_ID="$4"
JSON_PAYLOAD="${5:-}"

if [ -z "$REQUESTER_ID" ] || [ -z "$REQUESTER_ROLE" ] || [ -z "$SERVICE" ] || [ -z "$ENTITY_ID" ]; then
  guard_emit_json "error" "DENY" "invalid_arguments" "one or more required arguments are empty" \
    "service" "$SERVICE" \
    "entity_id" "$ENTITY_ID"
  exit "$GUARD_RC_INVALID_ARGS"
fi

if [ -f /opt/openclaw/openclaw.env ]; then
  set -a
  . /opt/openclaw/openclaw.env
  set +a
fi

: "${HA_TOKEN:?HA_TOKEN is required}"
: "${HA_BASE:?HA_BASE is required}"

RESOURCE="$(policy_build_ha_resource "$SERVICE" "$ENTITY_ID")"

DECISION_JSON="$(policy_decide \
  "$REQUESTER_ID" \
  "$REQUESTER_ROLE" \
  "ha_control" \
  "$RESOURCE" \
  "high"
)"
DECISION="$(policy_extract_decision "$DECISION_JSON")"

if ! guard_handle_decision "$DECISION" "$DECISION_JSON" \
  "resource" "$RESOURCE" \
  "service" "$SERVICE" \
  "entity_id" "$ENTITY_ID"; then
  exit "$?"
fi

if [ -n "$JSON_PAYLOAD" ]; then
  if ! BODY="$(python3 - "$ENTITY_ID" "$JSON_PAYLOAD" <<'PY'
import json, sys
entity_id = sys.argv[1]
payload = json.loads(sys.argv[2])
payload["entity_id"] = entity_id
print(json.dumps(payload))
PY
)"; then
    guard_emit_json "error" "ALLOW" "invalid_json_payload" "json_payload is not valid JSON" \
      "resource" "$RESOURCE" \
      "service" "$SERVICE" \
      "entity_id" "$ENTITY_ID"
    exit "$GUARD_RC_EXEC_FAILURE"
  fi
else
  BODY="$(python3 - "$ENTITY_ID" <<'PY'
import json, sys
print(json.dumps({"entity_id": sys.argv[1]}))
PY
)"
fi

if ! RESPONSE="$(curl -sS -X POST \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$BODY" \
  "$HA_BASE/api/services/${SERVICE%.*}/${SERVICE#*.}")"; then
  guard_emit_json "error" "ALLOW" "ha_call_failed" "home assistant service call failed" \
    "resource" "$RESOURCE" \
    "service" "$SERVICE" \
    "entity_id" "$ENTITY_ID"
  exit "$GUARD_RC_EXEC_FAILURE"
fi

guard_emit_json "executed" "ALLOW" "ha_call_executed" "home assistant service call executed successfully" \
  "resource" "$RESOURCE" \
  "service" "$SERVICE" \
  "entity_id" "$ENTITY_ID" \
  "response" "$RESPONSE"
