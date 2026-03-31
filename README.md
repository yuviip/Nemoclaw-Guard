# Nemoclaw Guard

Nemoclaw Guard is a guardrail and approval framework for risky agent actions.

It is evolving toward a policy and approval enforcement layer for AI agents and automation systems.

It currently includes:

- an OpenClaw plugin integration layer
- approval intent resolvers
- approval-session runtime bridges
- guarded wrappers and runtime entrypoints
- policy-runtime entrypoints
- architecture and runtime documentation

The project started from a live OpenClaw-integrated implementation and is now being reorganized into a cleaner open-source repository.


## Current repository scope

This repository currently contains four major layers.

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

The currently validated OpenClaw-connected slice includes:

- inbound WhatsApp message correlation to the active main agent session
- conversation/session binding
- dangerous `exec` detection in the plugin `before_tool_call`
- approval creation on the real dangerous `exec`
- blocking of dangerous `exec` before execution
- plugin state persistence for inbound/session/run/approval tracking
- deny flow validation for dangerous file deletion
- natural-language approval flow validation
- approved file-delete execution
- repeated new dangerous request after a previously completed request
- duplicate-execution suppression improvements for the validated file-delete slice

In parallel, the repository also contains broader Nemoclaw Guard runtime components for:

- approval session creation
- reply resolution
- approval application
- approved file-delete execution
- policy-based wrapper decisions
- reusable guarded wrappers

Not every repository path should yet be assumed to have the same end-to-end validation coverage as the current OpenClaw-connected file-delete slice.


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
- `policy-runtime/` — tracked policy runtime entrypoints
- `docs/` — architecture, approval-flow, testing, policy, and investigation docs
- `state/` — example state payloads and future state-related assets
- `cli/` — future dedicated Nemoclaw Guard CLI
- `scripts/` — future maintenance and ops helpers
- `tools/patch/` — future patch/import helpers
- `docs/history/` — archived historical/imported materials


## What is still in progress

Important items still not finished:

- further thin the OpenClaw plugin boundary
- continue moving approval lifecycle responsibility toward runtime contracts
- improve approval-resolution UX for natural approve/deny/approve-all/target-specific replies
- implement stronger replay/resume behavior after approval
- move duplicate suppression toward a stronger ID-based execution receipt model
- introduce more structured action / approval / execution contracts
- create a polished dedicated CLI
- create install/uninstall/enable/disable/status/test lifecycle commands
- improve open-source packaging and release readiness
- finalize licensing


## Project direction

The direction is to keep a clear separation between:

- **OpenClaw integration**
- **Nemoclaw Guard core runtime**
- **policy and approval resolution**
- **guarded wrappers / execution providers**

OpenClaw-specific behavior should stay in the plugin/integration boundary.

Approval interpretation, state transitions, execution orchestration, and replay protection should increasingly live inside Nemoclaw Guard itself.


## Documentation

Start here:

- `docs/README.md`

Recommended first reading:

- `docs/SOURCE_OF_TRUTH.md`
- `docs/STATUS_AND_ROADMAP.md`
- `docs/CURRENT_APPROVAL_FLOW.md`
- `docs/ACTION_AND_APPROVAL_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/ARCHITECTURE_V2_TARGET.md`

Other important docs:

- `docs/POLICY_MODEL.md`
- `docs/REFERENCE_WRAPPERS.md`
- `docs/QUICKSTART.md`
- `docs/TESTING.md`
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
