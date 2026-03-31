# Nemoclaw Guard — Runtime / Execution Contract

This document defines the intended contract between the Nemoclaw runtime
and execution providers.

The purpose of this contract is to separate:

- approval and policy handling
- runtime orchestration
- real system execution

This allows the runtime to remain generic while execution providers
perform family-specific work.


--------------------------------------------------

High Level Model

Runtime
↓
Execution Router
↓
Execution Provider
↓
Execution Receipt


--------------------------------------------------

1. Runtime Responsibilities

Before calling an execution provider, the runtime is responsible for:

- validating that execution is allowed
- ensuring approval requirements are already satisfied
- normalizing the action into a structured object
- attaching execution context
- preventing duplicate execution where possible

The runtime decides whether execution should happen.

The provider only performs the execution.


--------------------------------------------------

2. Provider Responsibilities

An execution provider is responsible for:

- validating provider-specific input
- performing the real side effect
- returning a structured execution result
- exposing enough metadata for audit and replay safety

A provider must not decide whether an action is approved.
That decision belongs to the runtime.


--------------------------------------------------

3. Runtime Input to Provider

Recommended input contract:

{
  "action_id": "act_123",
  "family": "file.delete",
  "target": "/tmp/test.txt",
  "parameters": {},
  "approval_context": {
    "approval_id": "apr_123",
    "status": "approved"
  },
  "execution_context": {
    "requested_by": {
      "agent": "openclaw",
      "session_key": "agent:main:main"
    },
    "requested_at": "2026-03-31T00:00:00Z"
  }
}


--------------------------------------------------

4. Provider Output to Runtime

Recommended output contract:

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

5. Failure Cases

Providers should return structured failure information when execution fails.

Recommended shape:

{
  "execution_id": "exec_124",
  "action_id": "act_123",
  "status": "failed",
  "provider": "file_provider",
  "executed_at": "2026-03-31T00:00:10Z",
  "result_summary": "delete failed",
  "details": {
    "reason": "target_not_found"
  }
}


--------------------------------------------------

6. Why This Contract Matters

A stable runtime / execution contract allows Nemoclaw Guard to:

- support multiple execution families
- swap providers without changing approval logic
- improve replay protection
- improve audit logging
- keep adapters thin
- keep runtime orchestration generic


--------------------------------------------------

7. Current Transitional State

The current repository still includes execution flows that are partly shaped by:

- wrapper-specific shell entrypoints
- family-specific runtime helpers
- current OpenClaw integration assumptions

The contract described here is the intended target direction.


--------------------------------------------------

8. Long-Term Direction

The long-term direction is:

- runtime normalizes actions once
- runtime dispatches by family
- providers perform execution only
- providers return structured receipts
- runtime records final execution state

This keeps execution logic modular and makes Nemoclaw Guard easier to extend.
