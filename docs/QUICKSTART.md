# Quickstart

This quickstart validates the runnable core of Nemoclaw Guard.

Validated components:
- example policy files
- policy decision engine
- policy API
- approval reply resolver

This quickstart does NOT require OpenClaw.

Repository path used in this guide:
/opt/nemoclaw-guard

The paths used below are the current default runtime layout.

For Python runtime modules, Nemoclaw Guard now also supports environment-driven path resolution through:

- `runtime/state/path_config.py`
- `policy-runtime/path_config.py`

So the quickstart uses `/opt/...` as the default deployment example, not as the only possible filesystem layout.

----

Step 1: create policy files
sudo mkdir -p /opt/nemoclaw/policy
sudo cp policy/permissions.example.yml /opt/nemoclaw/policy/permissions.yml
sudo cp policy/users.example.yml /opt/nemoclaw/policy/users.yml

Step 2: install runtime scripts
sudo mkdir -p /opt/nemoclaw/bin
sudo cp policy-runtime/* /opt/nemoclaw/bin/
sudo chmod +x /opt/nemoclaw/bin/policy_decide.sh

Step 3: test policy decision
echo '{"requester_role":"agent","action":"file.delete","resource":"/tmp/test","risk_level":"high"}' | /opt/nemoclaw/bin/policy_decide.sh

Step 4: start policy API
python3 /opt/nemoclaw/bin/policy_api.py

Step 5: test health endpoint
curl http://127.0.0.1:8001/health

Step 6: test approval resolver
curl http://127.0.0.1:8001/approval/resolve -H 'Content-Type: application/json' -d '{"text":"approve test","request_session":{"request_session_id":"req_demo","chat_id":"whatsapp:+972500000000","status":"pending","actions":[{"action_id":"act1","approval_state":"pending"}]}}'
