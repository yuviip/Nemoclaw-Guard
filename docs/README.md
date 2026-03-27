# Nemoclaw Guard Docs Index

This directory contains the working documentation for the Nemoclaw Guard project.

## Core docs

- `ARCHITECTURE.md`  
  High-level system structure, major components, and intended runtime model.

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

## History

Historical or imported materials that are useful for context but are not the primary source of truth should be kept under:

- `history/`

## Current source of truth

At this stage, the main source of truth for the live plugin logic is:

- `../plugin/index.js`

The main source of truth for the repository overview is:

- `../README.md`
