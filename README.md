# Nemoclaw Guard

Nemoclaw Guard is a guardrail and approval framework for risky agent actions.

It currently includes:
- an OpenClaw plugin integration layer
- approval intent resolvers
- approval-session runtime bridges
- guarded wrappers and runtime entrypoints
- imported architecture and policy documentation

The project started from a live OpenClaw-integrated implementation and is now being reorganized into a clean open-source repository.

## Current repository scope

This repository now contains four major layers:

### 1. OpenClaw integration layer
Tracked under:

- `plugin/`

This layer observes agent/session/tool events inside OpenClaw and is responsible for intercepting risky tool usage in the current integrated flow.

### 2. Resolver layer
Tracked under:

- `resolver/`

This layer is responsible for classifying approval replies into structured intents such as:

- approve single
- deny single
- approve session
- deny session
- ambiguous
- no match

The intent classification is designed to live in Nemoclaw Guard rather than be hard-coded in OpenClaw-specific logic.

### 3. Runtime layer
Tracked under:

- `runtime/`

This layer contains:
- approval session creation
- approval session storage
- resolver bridge
- apply bridge
- execution bridge
- runtime guarded shell entrypoints
- shim installation helpers

### 4. Wrapper layer
Tracked under:

- `wrappers/`

This layer contains:
- reference wrappers
- refactored wrappers
- shared wrapper helper logic

## Current validated slice

The currently validated OpenClaw-connected slice is:

- inbound WhatsApp message correlation to the active main agent session
- conversation/session binding
- dangerous `exec` detection in the plugin `before_tool_call`
- approval creation on the real dangerous `exec`
- blocking of dangerous `exec` before execution
- state persistence for inbound/session/run/approval tracking

In parallel, the repository also contains a broader Nemoclaw Guard runtime for:
- approval session creation
- reply resolution
- approval application
- approved file-delete execution
- reusable guarded wrappers

## Current live runtime paths

Live plugin path inside the OpenClaw container:

- `/home/node/.openclaw/workspace/.openclaw/extensions/nemoclaw-guard/index.js`

Live plugin state path inside the OpenClaw container:

- `/home/node/.openclaw/workspace/.openclaw/nemoclaw-guard/state.json`

Live Nemoclaw Guard runtime path in CT110:

- `/opt/nemoclaw-guard`

OpenClaw shim wrapper path currently used in integration:

- `/opt/openclaw/bin/guarded_file_delete.sh`

## Repository structure

- `plugin/` — OpenClaw plugin integration layer
- `resolver/` — approval reply intent resolvers, tests, and fixtures
- `runtime/` — approval session runtime, execution bridges, and install helpers
- `wrappers/` — reference and refactored guarded wrappers
- `docs/` — architecture, approval-flow, testing, policy, and investigation docs
- `state/` — example state payloads and future state-related assets
- `cli/` — future dedicated Nemoclaw Guard CLI
- `scripts/` — future maintenance and ops helpers
- `tools/patch/` — future patch/import helpers
- `docs/history/` — archived historical/imported materials

## What is still in progress

Important items still not finished:

- connect the OpenClaw plugin layer cleanly to the runtime resolver/apply/execute flow
- remove or replace legacy approval interception logic in `plugin/index.js`
- finish approval-resolution UX for natural approve/deny/approve-all/target-specific replies
- implement replay/resume behavior cleanly after approval
- create a polished dedicated CLI
- create install/uninstall/enable/disable/status/test lifecycle commands
- improve open-source packaging and release readiness
- finalize licensing

## Project direction

The direction is to keep a clear separation between:

- **OpenClaw integration**
- **Nemoclaw Guard core runtime**
- **guarded wrappers**
- **approval intent resolution**

OpenClaw-specific behavior should stay in the plugin/integration boundary.

Approval interpretation, state transitions, and guarded execution should live in Nemoclaw Guard itself.

## Documentation

Start here:

- `docs/README.md`

Important docs:

- `docs/ARCHITECTURE.md`
- `docs/POLICY_MODEL.md`
- `docs/TESTING.md`
- `docs/approval_sessions_runtime_flow.md`
- `docs/approval_resolution_contract.md`

## Planned CLI

The intended CLI surface includes commands such as:

- `nemoclaw-guard install`
- `nemoclaw-guard uninstall`
- `nemoclaw-guard enable`
- `nemoclaw-guard disable`
- `nemoclaw-guard status`
- `nemoclaw-guard paths`
- `nemoclaw-guard test`
