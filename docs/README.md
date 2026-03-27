# Nemoclaw Guard Docs Index

This directory contains the working documentation for the Nemoclaw Guard project.

## Main architecture layers

The project currently consists of four main layers:

- `plugin/` — OpenClaw integration and hook interception layer
- `resolver/` — approval reply intent resolution
- `runtime/` — approval session state, bridges, execution helpers, and shim install flow
- `wrappers/` — guarded wrapper implementations and shared wrapper helpers

## Core docs

- `ARCHITECTURE.md`  
  High-level system structure, major layers, boundaries, and intended runtime model.

- `POLICY_MODEL.md`  
  Policy concepts, approval model, and guard decision boundaries.

- `QUICKSTART.md`  
  Quick bootstrap notes for getting the project running in a basic environment.

- `REFERENCE_WRAPPERS.md`  
  Reference wrapper patterns and guarded wrapper behavior.

- `SKILL_FORMAT.md`  
  Skill structure and formatting conventions for guarded capabilities.

- `TESTING.md`  
  Testing approach, validation flow, and expected behavior checks.

- `OPENCLAW_EXEC_HOOK_INVESTIGATION.md`  
  Investigation notes around OpenClaw exec hooks and interception behavior.

## Approval-flow docs

- `approval_resolution_contract.md`  
  Approval resolution contract and expected approval/deny semantics.

- `approval_sessions_runtime_flow.md`  
  Runtime approval flow and current session-linked behavior.

- `approval_sessions_v1.md`  
  Early approval-session design notes.

- `approval_sessions_v2_resolver.md`  
  Resolver-oriented approval flow evolution.

- `approval_sessions_v3_file_delete.md`  
  File-delete approval vertical slice notes.

- `approval_sessions_v4_resolver_io.md`  
  Resolver I/O refinement notes for approval handling.

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
