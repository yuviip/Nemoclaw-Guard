# Nemoclaw Guard Architecture

Nemoclaw Guard is a guardrail and approval framework for risky agent actions.

The repository currently contains both:

1. an **OpenClaw integration layer**
2. a broader **Nemoclaw Guard core runtime**

These must be treated as separate architectural layers.

---

## High-level model

Current target model:

User / Operator
↓
Agent runtime (for example OpenClaw)
↓
OpenClaw integration layer (`plugin/`)
↓
Nemoclaw Guard runtime (`resolver/` + `runtime/` + `wrappers/`)
↓
Guarded system action

---

## Main architectural layers

## 1. OpenClaw integration layer

Location:

- `plugin/index.js`

Purpose:

- observe inbound messages
- correlate inbound conversation context to active agent sessions
- observe tool calls
- intercept dangerous tool usage in the current OpenClaw-connected flow
- maintain plugin-side state for session linkage and pending approvals

This layer is integration-specific.

It should contain only the logic required to:
- bind OpenClaw runtime events
- route relevant approval-related activity into Nemoclaw Guard core
- preserve auditability and visibility in the OpenClaw environment

It should **not** be the long-term home of approval-language parsing or family-specific execution logic.

---

## 2. Resolver layer

Location:

- `resolver/`

Purpose:

- classify approval replies into structured intents
- avoid hard-coding one language or one exact phrasing in the OpenClaw plugin
- support both action-specific and session-wide approval/deny decisions

Examples of outputs:

- `approve_single`
- `deny_single`
- `approve_session`
- `deny_session`
- `ambiguous`
- `no_match`

This layer should stay:
- generic
- cheap
- deterministic-first
- integration-agnostic

---

## 3. Runtime layer

Location:

- `runtime/`

Purpose:

- create approval sessions
- persist approval sessions
- resolve replies against stored session context
- apply approval decisions to session actions
- execute approved actions where relevant
- install or manage integration shims

Current runtime state/action components include:

- approval session store
- session create bridge
- resolve bridge
- apply bridge
- execution bridge
- runtime guarded wrapper entrypoints
- OpenClaw shim installer

This is the core orchestration layer for approval lifecycle behavior.

---

## 4. Wrapper layer

Location:

- `wrappers/`

Purpose:

- provide reusable guarded wrappers
- separate reference implementations from more refactored/commonized versions
- encapsulate policy checks and execution boundaries

Sub-areas:

- `wrappers/reference/`
- `wrappers/refactored/`
- `wrappers/lib/`

The wrapper layer is where risky actions are turned into:
- policy decisions
- approval requests
- controlled execution

---

## Current validated implementation slice

The currently validated live slice is focused on dangerous file deletion through OpenClaw.

Validated behavior includes:

- inbound WhatsApp message capture
- fallback/session correlation into the active main agent session
- dangerous `exec` detection in `plugin/index.js`
- approval creation on the real dangerous `exec`
- blocking of dangerous execution before it runs
- persistence of approval/session state in plugin state

In parallel, the runtime layer also already contains approval-session machinery and file-delete execution helpers, but the OpenClaw integration path is not yet fully aligned to that runtime.

---

## Current architectural gap

There is currently a gap between:

### A. plugin-side interception
and
### B. runtime-side approval resolution/apply/execute flow

The repository already contains runtime components for:
- approval session creation
- reply resolution
- approval application
- approved file-delete execution

But the current OpenClaw plugin layer still contains direct interception logic that has not yet been fully refactored to delegate cleanly into the runtime flow.

This is one of the most important next integration tasks.

---

## Boundary rule

The intended boundary is:

### OpenClaw integration layer should own:
- hooks
- session/event correlation
- OpenClaw-specific state linkage
- passing context into Nemoclaw Guard runtime

### Nemoclaw Guard core should own:
- approval reply interpretation
- approval session lifecycle
- policy-aware guarded execution
- action-family runtime behavior
- reusable wrapper and bridge logic

This boundary is important so the project remains:
- portable
- testable
- reusable beyond OpenClaw
- easier to package as open source

---

## State model

There are currently two important state domains:

### Plugin state
Current live path:

- `/home/node/.openclaw/workspace/.openclaw/nemoclaw-guard/state.json`

Used for:
- inbound events
- conversation/session linkage
- active runs
- plugin-side pending approvals
- guard actions

### Runtime approval session state
Current runtime path in CT110:

- `/home/node/.openclaw/nemoclaw/approval_sessions.json`

Used for:
- request sessions
- actions
- approval states
- execution states

These two state models are related but not yet fully unified.

---

## OpenClaw shim boundary

There is also an integration shim layer currently installed in OpenClaw paths, such as:

- `/opt/openclaw/bin/guarded_file_delete.sh`

These shims should be treated as deployed integration entrypoints, not as the long-term source of truth.

The source of truth should live in this repository under:

- `runtime/bin/`
- `wrappers/`
- `plugin/`

---

## Near-term priorities

1. align repository docs with the actual layered structure
2. preserve imported runtime/resolver/wrapper assets as source of truth
3. connect plugin approval handling to runtime resolver/apply/execute flow
4. remove or retire legacy plugin-side approval logic once the runtime path is fully integrated
5. build a proper install/uninstall/enable/disable/status/test CLI around the repository

---

## Long-term direction

Nemoclaw Guard should mature into:

- a reusable guardrail runtime
- a clean integration target for OpenClaw
- a portable approval framework for risky automation actions
- a project with clear packaging, lifecycle tooling, and operator-grade auditability
