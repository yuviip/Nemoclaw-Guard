# Nemoclaw Guard — Execution Provider Model

This document defines the intended execution-provider model for Nemoclaw Guard.

The purpose of this model is to separate:

- approval and policy logic
- runtime orchestration
- real system execution

This allows Nemoclaw Guard to support multiple action families without duplicating execution logic.


--------------------------------------------------

High Level Model

Agent
↓
Adapter
↓
Nemoclaw Runtime
↓
Execution Provider
↓
Protected System


--------------------------------------------------

1. What an Execution Provider Is

An execution provider is the component responsible for performing a real system action.

Examples:

- file provider
- systemctl provider
- docker provider
- git provider
- home assistant provider

A provider receives a normalized action from the runtime and performs the real execution.


--------------------------------------------------

2. What Providers Should Do

Execution providers should:

- validate provider-specific execution input
- perform the action safely
- return a structured execution result
- avoid duplicate side effects when possible
- expose execution details for audit purposes


--------------------------------------------------

3. What Providers Must Not Do

Providers must NOT:

- evaluate policy
- interpret approval replies
- manage approval lifecycle
- decide whether approval is needed
- perform adapter-specific logic

These responsibilities belong to the runtime and policy layers.


--------------------------------------------------

4. Execution Provider Input

Providers should receive normalized execution input.

Recommended structure:

{
  "action_id": "act_123",
  "family": "file.delete",
  "target": "/tmp/test.txt",
  "parameters": {},
  "approval_context": {
    "approval_id": "apr_123"
  }
}


--------------------------------------------------

5. Execution Provider Output

Providers should return structured execution receipts.

Recommended structure:

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

6. Example Provider Families

### file.delete

Responsible for deleting files only after approval and runtime authorization.

### systemctl.control

Responsible for actions such as restart / stop / status on system services.

### docker.control

Responsible for actions such as restart / stop / inspect on containers.

### git.push

Responsible for pushing repository changes through a guarded execution path.

### ha.call

Responsible for guarded Home Assistant service calls.


--------------------------------------------------

7. Why This Matters

Execution providers make it possible to:

- support multiple action families
- keep plugin logic thin
- keep runtime orchestration generic
- support future provider plugins
- improve auditability and replay protection


--------------------------------------------------

8. Current Transitional State

The current repository still includes execution paths that are partially tied to:

- wrapper-specific shell entrypoints
- family-specific runtime helpers
- current OpenClaw integration assumptions

The provider model described here is the intended target direction.


--------------------------------------------------

9. Target Direction

The long-term direction is:

- runtime dispatches by action family
- providers execute real system work
- providers return structured receipts
- wrappers become compatibility entrypoints or thin shims where needed

This allows Nemoclaw Guard to evolve into a generic guardrails framework instead of a single integration-specific implementation.
