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
  local resource="${5:-}"
  local service="${6:-}"
  local entity_id="${7:-}"

  printf "{"
  printf "\"status\":\"%s\"," "$status"
  printf "\"decision\":\"%s\"," "$decision"
  printf "\"reason\":\"%s\"," "$reason"
  printf "\"message\":%s" "$(printf "%s" "$message" | json_escape)"

  if [ -n "$resource" ]; then
    printf ",\"resource\":%s" "$(printf "%s" "$resource" | json_escape)"
  fi
  if [ -n "$service" ]; then
    printf ",\"service\":%s" "$(printf "%s" "$service" | json_escape)"
  fi
  if [ -n "$entity_id" ]; then
    printf ",\"entity_id\":%s" "$(printf "%s" "$entity_id" | json_escape)"
  fi

  printf "}\n"
}

usage() {
  cat >&2 <<USAGE
usage: guarded_ha_call.sh <requester_id> <requester_role> <service> <entity_id> [json_payload]
USAGE
}

if [ "$#" -lt 4 ]; then
  usage
  emit_json "error" "DENY" "invalid_arguments" "missing required arguments"
  exit 1
fi

REQUESTER_ID="$1"
REQUESTER_ROLE="$2"
SERVICE="$3"
ENTITY_ID="$4"
JSON_PAYLOAD="${5:-}"

if [ -z "$REQUESTER_ID" ] || [ -z "$REQUESTER_ROLE" ] || [ -z "$SERVICE" ] || [ -z "$ENTITY_ID" ]; then
  emit_json "error" "DENY" "invalid_arguments" "one or more required arguments are empty" "" "$SERVICE" "$ENTITY_ID"
  exit 1
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

case "$DECISION" in
  ALLOW)
    ;;
  DENY)
    emit_json "denied" "DENY" "policy_denied" "$DECISION_JSON" "$RESOURCE" "$SERVICE" "$ENTITY_ID"
    exit 2
    ;;
  REQUIRE_OWNER_CONFIRMATION)
    emit_json "requires_confirmation" "REQUIRE_OWNER_CONFIRMATION" "policy_requires_owner_confirmation" "$DECISION_JSON" "$RESOURCE" "$SERVICE" "$ENTITY_ID"
    exit 3
    ;;
  REQUIRE_OWNER_APPROVAL)
    emit_json "requires_approval" "REQUIRE_OWNER_APPROVAL" "policy_requires_owner_approval" "$DECISION_JSON" "$RESOURCE" "$SERVICE" "$ENTITY_ID"
    exit 4
    ;;
  *)
    emit_json "error" "DENY" "unknown_policy_decision" "$DECISION_JSON" "$RESOURCE" "$SERVICE" "$ENTITY_ID"
    exit 5
    ;;
esac

if [ -n "$JSON_PAYLOAD" ]; then
  if ! BODY="$(python3 - "$ENTITY_ID" "$JSON_PAYLOAD" <<'PY'
import json, sys
entity_id = sys.argv[1]
payload = json.loads(sys.argv[2])
payload["entity_id"] = entity_id
print(json.dumps(payload))
PY
)"; then
    emit_json "error" "ALLOW" "invalid_json_payload" "json_payload is not valid JSON" "$RESOURCE" "$SERVICE" "$ENTITY_ID"
    exit 6
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
  emit_json "error" "ALLOW" "ha_call_failed" "home assistant service call failed" "$RESOURCE" "$SERVICE" "$ENTITY_ID"
  exit 7
fi

printf "{"
printf "\"status\":\"executed\","
printf "\"decision\":\"ALLOW\","
printf "\"reason\":\"ha_call_executed\","
printf "\"message\":\"home assistant service call executed successfully\","
printf "\"resource\":%s," "$(printf "%s" "$RESOURCE" | json_escape)"
printf "\"service\":%s," "$(printf "%s" "$SERVICE" | json_escape)"
printf "\"entity_id\":%s," "$(printf "%s" "$ENTITY_ID" | json_escape)"
printf "\"response\":%s" "$(printf "%s" "$RESPONSE" | json_escape)"
printf "}\n"
