# Approval Sessions V4 - Resolver I/O

## Goal
Define a tiny generic resolver contract for approval-session handling.

This stage still does NOT change runtime logic.

## Resolver input

Example:

{
  "text": "approve delete test123",
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
          "aliases": ["/tmp/test123", "test123"]
        },
        "approval_state": "pending"
      }
    ]
  }
}

## Resolver output

Example:

{
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

## Scope meanings

- single_action
- whole_session
- none

## Minimal matching pipeline

1. detect approval polarity
2. detect session-wide intent vs resource-specific intent
3. detect resource match
4. resolve ambiguity
5. emit compact result

## Important design rules

- resolver must stay generic
- resolver must not hard-code one language
- resolver must not execute actions
- resolver must only classify intent
- resolver should be cheap in tokens and logic

## Confidence levels

- high
- medium
- low

## Example outcomes

### approve single
Input:
- positive intent
- matched one resource

Example text:
"approve delete test123"

Output:
- approve_single

### deny single
Input:
- negative intent
- matched one resource

Example text:
"do not delete test123"

Output:
- deny_single

### approve session
Input:
- positive session-wide intent
- no conflicting resource-specific target

Example text:
"approve all"

Output:
- approve_session

### ambiguous
Input:
- one basename matches multiple pending actions

Output:
- ambiguous

### no match
Input:
- no clear polarity
- or no matched pending target

Output:
- no_match

## Next stage

V5: implement a tiny pure resolver function with fixtures/tests only
