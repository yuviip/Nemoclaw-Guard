# Approval Resolution Contract

## Goal
Move approval-reply interpretation into NemoClaw Guard.

OpenClaw should stay generic:
- it collects raw user reply
- it sends normalized pending-action context
- NemoClaw Guard resolves the reply into a structured decision

## Resolver input

Example:

{
  "text": "approve test123",
  "request_session": {
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
          "aliases": ["test123", "/tmp/test123"]
        },
        "approval_state": "pending"
      }
    ]
  }
}

## Resolver output

Example:

{
  "ok": true,
  "intent": "approve_single",
  "scope": "single_action",
  "action_id": "act_001",
  "confidence": "high",
  "reason": "positive + resource_match"
}

## Allowed intents
- no_match
- ambiguous
- approve_single
- deny_single
- approve_session
- deny_session

## Allowed scopes
- none
- single_action
- whole_session

## Notes
- wording/parsing logic should live in NemoClaw Guard
- OpenClaw should not hard-code one language
- resource aliases should be family-aware
- resolver only classifies intent, never executes actions
