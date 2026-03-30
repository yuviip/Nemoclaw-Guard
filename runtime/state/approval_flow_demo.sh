#!/usr/bin/env bash
set -euo pipefail

CREATE_OUT="$(cat <<JSON | python3 /opt/nemoclaw-guard/runtime/state/approval_session_create.py
{
  "chat_id": "whatsapp:+972500000000",
  "family": "file.delete",
  "resource": {
    "kind": "file",
    "primary": "/tmp/demo_file_123",
    "display": "demo_file_123",
    "aliases": ["demo_file_123", "/tmp/demo_file_123"]
  }
}
JSON
)"

echo "=== create ==="
echo "$CREATE_OUT"

SESSION_ID="$(printf "%s" "$CREATE_OUT" | python3 -c 'import sys,json; print(json.load(sys.stdin)["request_session_id"])')"

echo
echo "=== apply reply ==="
cat <<JSON | python3 /opt/nemoclaw-guard/runtime/state/approval_apply_bridge.py
{
  "request_session_id": "$SESSION_ID",
  "text": "approve demo_file_123"
}
JSON

echo
echo "=== final stored session ==="
python3 - <<PY
from importlib.util import spec_from_file_location, module_from_spec
p = "/opt/nemoclaw-guard/runtime/state/approval_session_store.py"
spec = spec_from_file_location("approval_session_store", p)
mod = module_from_spec(spec)
spec.loader.exec_module(mod)
print(mod.get_session("$SESSION_ID"))
PY
