# Status and Roadmap

This document summarizes the current validated behavior of Nemoclaw Guard
and the main remaining work areas.

It reflects the state of the repository and the currently validated
OpenClaw-integrated slice.

---

# Current validated slice

The following behavior has been validated end-to-end in the OpenClaw-connected runtime.

### Inbound message correlation

- WhatsApp inbound messages are correlated to the active OpenClaw agent session
- conversation ↔ session binding works
- plugin state persists inbound/session/run metadata

### Dangerous action interception

- dangerous `exec` calls are detected in the OpenClaw plugin `before_tool_call`
- interception occurs **before execution**
- dangerous operations are blocked before they run

### Approval session creation

When a dangerous action is detected:

- an approval session is created
- the approval request is linked to the active session
- the action receives an `action_id`
- the user is prompted for approval

### Approval reply resolution

User replies are processed through the resolver pipeline:

- natural language approval messages are supported
- approval replies are classified into structured intents
- the resolver determines the approval scope and target

Supported intent types:

- approve_single
- deny_single
- approve_session
- deny_session
- ambiguous
- no_match

### Approval application

Resolver output is applied to the stored approval session:

- pending → approved
- pending → denied

Session status is recomputed accordingly.

### Approved action execution

For the validated vertical slice (`file.delete`):

- approved actions execute successfully
- execution metadata is recorded
- execution is idempotent

### Repeated requests

A new dangerous request after a previously completed request:

- creates a new approval session
- does not incorrectly reuse the previous execution state

### Runtime refactors completed

Recent refactors improved maintainability of the runtime flow:

- approval reply handling moved into smaller helper functions
- dangerous exec interception logic extracted into helpers
- runtime path defaults and path-config helpers added
- wrapper path configuration hardened

---

# Current limitations and design debt

The system works end-to-end for the validated slice but still contains
areas that require architectural cleanup.

### Approval store semantics

The structure currently called `pendingApprovals` now acts as a
general approval store including:

- pending
- denied
- executed

The naming does not reflect the current behavior.

### Approval lifecycle cleanup

Approval sessions are not yet pruned or archived automatically.

Future work should introduce lifecycle management for:

- completed approvals
- expired approvals
- stale sessions

### State update race safety

The runtime currently uses a read → mutate → write pattern
for state updates.

Hardening for concurrent updates may be required in future.

### Duplicate execution suppression

Duplicate execution protection currently relies on:

- command matching
- resource matching
- family-specific logic

The long-term target is an ID-based execution receipt model.

### Plugin responsibilities

The OpenClaw plugin still performs more orchestration than intended.

The long-term direction is:

plugin → thin adapter
runtime → approval lifecycle and execution orchestration

---

# Next priorities

## P1 — approval UX completion

- improve resolver behavior for natural approval replies
- support clearer target selection and multi-action approvals
- polish approval confirmation messaging

## P2 — runtime lifecycle improvements

- add approval lifecycle cleanup
- strengthen replay / resume behavior
- improve runtime state transitions

## P3 — operational tooling

- create a dedicated Nemoclaw Guard CLI
- implement lifecycle commands:

nemoclaw-guard install
nemoclaw-guard uninstall
nemoclaw-guard enable
nemoclaw-guard disable
nemoclaw-guard status

## P4 — open source readiness

- documentation alignment
- packaging and installation story
- example policies and configs
- CI and test coverage
- final license selection

