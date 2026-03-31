# Nemoclaw Guard Docs Index

This directory contains the working documentation for the Nemoclaw Guard project.

It includes:

- current source-of-truth documents
- current runtime and approval-flow documents
- target architecture documents
- historical approval-design evolution notes


## Read these first

For most readers, the recommended reading order is:

1. `SOURCE_OF_TRUTH.md`
   Defines what is authoritative in the repository right now.

2. `STATUS_AND_ROADMAP.md`
   Summarizes the validated behavior and the main remaining work areas.

3. `CURRENT_APPROVAL_FLOW.md`
   Describes the current end-to-end approval flow.

4. `ACTION_AND_APPROVAL_MODEL.md`
   Defines the target structured model for actions, approvals, and execution receipts.

5. `ARCHITECTURE.md`
   Describes the current architecture and integration boundaries.

6. `ARCHITECTURE_V2_TARGET.md`
   Describes the intended long-term target architecture.


## Main architecture layers

The project currently consists of four main layers:

- `plugin/` — OpenClaw integration and hook interception layer
- `resolver/` — approval reply intent resolution
- `runtime/` — approval session state, bridges, execution helpers, and shim install flow
- `wrappers/` — guarded wrapper implementations and shared wrapper helpers


## Current source-of-truth and runtime docs

- `SOURCE_OF_TRUTH.md`
  Defines what is authoritative today and what is still transitional.

- `STATUS_AND_ROADMAP.md`
  Current validated slice, limitations, and roadmap.

- `CURRENT_APPROVAL_FLOW.md`
  Current end-to-end approval flow across plugin, runtime, resolver, and execution.

- `ACTION_AND_APPROVAL_MODEL.md`
  Target contract model for structured guarded actions and approvals.

- `ARCHITECTURE.md`
  Current architectural structure, boundaries, and intended model.

- `POLICY_MODEL.md`
  Policy concepts, approval model, and guard decision boundaries.

- `QUICKSTART.md`
  Quick bootstrap notes for getting the project running in a basic environment.

- `REFERENCE_WRAPPERS.md`
  Reference wrapper patterns and guarded wrapper behavior.

- `TESTING.md`
  Testing approach, validation flow, and expected behavior checks.

- `OPENCLAW_EXEC_HOOK_INVESTIGATION.md`
  Investigation notes around OpenClaw exec hooks and interception behavior.


## Target architecture docs

- `ARCHITECTURE_V2_TARGET.md`
  Long-term target architecture for Nemoclaw Guard as a generic guardrails framework.

- `PLUGIN_RUNTIME_BOUNDARY.md`
  Intended boundary between agent adapters and the Nemoclaw runtime.

- `EXECUTION_PROVIDER_MODEL.md`
  Intended execution-provider model for provider-based guarded execution.


## Approval-flow and contract docs

- `approval_resolution_contract.md`
  Approval resolution contract and expected approval/deny semantics.

- `approval_sessions_runtime_flow.md`
  Runtime approval flow notes for the current approval-session implementation.


## Historical approval evolution docs

These documents are useful historical design notes, but they are not the primary source of truth for the current implementation:

- `approval_sessions_v1.md`
- `approval_sessions_v2_resolver.md`
- `approval_sessions_v3_file_delete.md`
- `approval_sessions_v4_resolver_io.md`


## Repository source-of-truth notes

At the current stage:

- `../plugin/index.js` is the source of truth for the current OpenClaw plugin integration logic
- `../resolver/` is the source of truth for approval reply classification logic
- `../runtime/` is the source of truth for approval session runtime/apply/execute flows
- `../wrappers/` is the source of truth for wrapper implementations
- `../README.md` is the source of truth for repository-level overview


## History

Historical or imported materials that are useful for context but are not the primary source of truth are kept under:

- `history/`
