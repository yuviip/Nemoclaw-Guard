#!/usr/bin/env bash
set -euo pipefail

NEMO_URL="${NEMO_URL:-http://127.0.0.1:8000/v1/chat/completions}"
NEMO_MODEL="${NEMO_MODEL:-gpt-4o-mini}"
CONFIG_ID="${CONFIG_ID:-openclaw}"

REQ_JSON="$(cat)"

if [[ -z "${REQ_JSON}" ]]; then
python3 <<'PY'
import json
print(json.dumps({
"decision":"DENY",
"source":"policy_decide",
"reason":"empty_request",
"summary":"Empty request",
"message_for_owner":"A policy request was empty and denied."
}))
PY
exit 0
fi

RULE_DECISION="$(
printf "%s" "$REQ_JSON" | /opt/nemoclaw/bin/permissions_check.py
)"

REQUESTER_ID="$(printf "%s" "$REQ_JSON" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("requester_id",""))')"
REQUESTER_ROLE="$(printf "%s" "$REQ_JSON" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("requester_role",""))')"
ACTION="$(printf "%s" "$REQ_JSON" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("action",""))')"
RESOURCE="$(printf "%s" "$REQ_JSON" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("resource",""))')"
RISK_LEVEL="$(printf "%s" "$REQ_JSON" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("risk_level",""))')"

emit_json () {

python3 <<PY
import json

decision = "$1"
source = "$2"
reason = "$3"

requester_id = "$REQUESTER_ID"
requester_role = "$REQUESTER_ROLE"
action = "$ACTION"
resource = "$RESOURCE"
risk_level = "$RISK_LEVEL"

if decision == "ALLOW":
    summary = f"{requester_id} allowed to perform {action}"
    message = f"Allowed: requester={requester_id}, action={action}, resource={resource}, risk={risk_level}"

elif decision == "REQUIRE_OWNER_CONFIRMATION":
    summary = "Owner confirmation required"
    message = f"You requested {action} on {resource} (risk {risk_level})"

elif decision == "REQUIRE_OWNER_APPROVAL":
    summary = f"{requester_id} requires owner approval"
    message = f"{requester_id} requested {action} on {resource} (risk {risk_level})"

else:
    summary = "Action denied"
    message = f"Denied: requester={requester_id}, action={action}, resource={resource}, risk={risk_level}"

print(json.dumps({
"decision":decision,
"source":source,
"reason":reason,
"summary":summary,
"message_for_owner":message,
"requester_id":requester_id,
"requester_role":requester_role,
"action":action,
"resource":resource,
"risk_level":risk_level
}))
PY

}

case "$RULE_DECISION" in
ALLOW|REQUIRE_OWNER_CONFIRMATION|REQUIRE_OWNER_APPROVAL|DENY)
emit_json "$RULE_DECISION" "rules" "matched_rules_or_defaults"
exit 0
;;
NO_MATCH)
;;
*)
emit_json "DENY" "policy_decide" "invalid_rule_decision"
exit 0
;;
esac

PROMPT="requester_id=${REQUESTER_ID}
requester_role=${REQUESTER_ROLE}
action=${ACTION}
resource=${RESOURCE}
risk_level=${RISK_LEVEL}"

PAYLOAD=$(python3 <<PY
import json
print(json.dumps({
"model":"$NEMO_MODEL",
"messages":[{"role":"user","content":"""$PROMPT"""}],
"guardrails":{"config_id":"$CONFIG_ID"}
}))
PY
)

RESP=$(curl -s "$NEMO_URL" -H "Content-Type: application/json" -d "$PAYLOAD")

DECISION=$(printf "%s" "$RESP" | python3 -c '
import sys,json
try:
d=json.load(sys.stdin)
print(d["choices"][0]["message"]["content"].strip())
except:
print("DENY")
')

case "$DECISION" in
ALLOW|REQUIRE_OWNER_CONFIRMATION|REQUIRE_OWNER_APPROVAL|DENY)
emit_json "$DECISION" "nemoclaw" "llm_policy_fallback"
;;
*)
emit_json "DENY" "nemoclaw" "invalid_nemoclaw_decision"
;;
esac
