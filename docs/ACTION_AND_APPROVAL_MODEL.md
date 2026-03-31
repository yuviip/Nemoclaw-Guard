# Nemoclaw Guard — Action and Approval Model

This document defines the intended core data model for guarded actions,
approvals, and execution receipts in Nemoclaw Guard.

Its goal is to make the runtime behavior easier to reason about and to
provide a stable contract for future integrations.


--------------------------------------------------

Why this model exists

Nemoclaw Guard should reason about structured actions, not raw command strings.

Instead of relying only on commands such as:

rm /tmp/test.txt

the system should normalize requests into action objects such as:

family: file.delete
target: /tmp/test.txt

This makes policy evaluation, approval handling, execution routing,
and replay protection more reliable.


--------------------------------------------------

1. Action Model

A guarded action represents a requested operation before execution.

Recommended fields:

- action_id
- family
- target
- parameters
- requested_by
- risk_level
- created_at
- status

Example:

{
  "action_id": "act_123",
  "family": "file.delete",
  "target": "/tmp/test.txt",
  "parameters": {},
  "requested_by": {
    "agent": "openclaw",
    "session_key": "agent:main:main"
  },
  "risk_level": "high",
  "created_at": "2026-03-31T00:00:00Z",
  "status": "pending_approval"
}


--------------------------------------------------

2. Approval Model

An approval represents the human decision layer for a guarded action.

Recommended fields:

- approval_id
- action_id
- status
- created_at
- decided_at
- decided_by
- decision_reason

Suggested approval states:

- pending
- approved
- denied
- expired
- executed
- failed

Example:

{
  "approval_id": "apr_123",
  "action_id": "act_123",
  "status": "pending",
  "created_at": "2026-03-31T00:00:00Z",
  "decided_at": null,
  "decided_by": null,
  "decision_reason": null
}


--------------------------------------------------

3. Execution Receipt Model

An execution receipt records what actually happened after approval.

Recommended fields:

- execution_id
- action_id
- status
- provider
- executed_at
- result_summary
- details

Example:

{
  "execution_id": "exec_123",
  "action_id": "act_123",
  "status": "executed",
  "provider": "file_provider",
  "executed_at": "2026-03-31T00:00:10Z",
  "result_summary": "deleted",
  "details": {
    "target": "/tmp/test.txt"
  }
}


--------------------------------------------------

4. Current Runtime Reality

The current Nemoclaw Guard implementation is still transitional.

Today the system still contains:

- plugin-side approval orchestration
- session-based runtime state
- command/resource matching for some replay protection
- approval records stored in structures currently named `pendingApprovals`

This means the model in this document is the target contract direction,
not yet the full live implementation.


--------------------------------------------------

5. Why this matters

A structured action and approval model allows Nemoclaw Guard to support:

- multiple agent adapters
- multiple communication channels
- stronger replay protection
- provider-based execution routing
- better audit logging
- future packaging as a generic guardrails framework


--------------------------------------------------

6. Direction

The intended long-term direction is:

- actions become first-class structured objects
- approvals become first-class tracked records
- execution results become explicit receipts
- replay protection becomes ID-based
- raw command matching becomes a fallback, not the primary model

