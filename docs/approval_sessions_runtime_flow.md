# Approval Sessions Runtime Flow

## Current implemented pieces

### 1. Session creator
- runtime/state/approval_session_create.py

Creates a pending approval session with:
- request_session_id
- chat_id
- actions[]
- approval_state=pending

### 2. Resolver
- resolver/approval_resolver_v2.py

Classifies reply intent into:
- approve_single
- deny_single
- approve_session
- deny_session
- ambiguous
- no_match

### 3. Resolve bridge
- runtime/state/approval_resolve_bridge.py

Loads stored session and runs resolver against:
- user text
- request_session context

### 4. Apply bridge
- runtime/state/approval_apply_bridge.py

Applies resolver result into stored session state:
- pending -> approved
- pending -> denied

Recomputes session status:
- pending
- partial
- approved
- denied


### 5. File-delete executor
- runtime/state/approval_execute_file_delete.py

Runs the approval apply step, then executes approved file.delete actions,
and persists execution metadata such as:
- execution_state
- execution_reason
- executed_at

Repeated execution is idempotent:
- if an action is already marked as executed, it is not executed again


### 6. Guarded file-delete entrypoint
- runtime/bin/guarded_file_delete.sh

When policy returns requires_confirmation, it now creates an approval session
and returns:
- request_session_id
- action_id
- target_path

## Important note

Current flow is no longer dry-run only.
Approval-state handling is live, and file.delete execution after approval is already working.

Approval session state is stored in writable OpenClaw state:
- /home/node/.openclaw/nemoclaw/approval_sessions.json
