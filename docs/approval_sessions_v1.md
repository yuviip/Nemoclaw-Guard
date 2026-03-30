# Approval Sessions V1

## Goal
Generic approval flow for guarded actions, with minimal token usage and staged rollout.

## Scope of V1
This stage defines only the data model.
No runtime logic changes yet.

## Core ideas
- approvals should be state-based, not hard-coded to one language
- one request may open multiple pending guarded actions
- user can approve:
  - one action
  - a whole request session
- later we will add family-specific adapters

## Proposed session shape

Example JSON shape:

{
  "request_session_id": "reqsess_xxx",
  "chat_id": "whatsapp:+972500000000",
  "status": "pending",
  "actions": [
    {
      "action_id": "act_001",
      "family": "file.delete",
      "resource": {
        "kind": "file",
        "primary": "/tmp/test123",
        "display": "test123",
        "aliases": ["/tmp/test123", "test123"]
      },
      "approval_state": "pending"
    }
  ]
}

## Approval scopes
- single_action
- whole_session

## Future stages
- V2: generic resolver
- V3: file.delete adapter
- V4: other guarded families
