# Nemoclaw Guard Source of Truth

This document defines what is authoritative in the repository right now.

Its goal is to reduce ambiguity between:
- live imported runtime pieces
- current validated integration behavior
- experimental or transitional areas
- future design direction

This document should be read together with:
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/STATUS_AND_ROADMAP.md`

---

## Repository authority model

Nemoclaw Guard currently contains both:
1. repository-tracked source-of-truth components
2. integration-specific deployed runtime entrypoints outside the repository
3. historical or transitional materials kept for context

The intent is that the repository becomes the long-term source of truth for the project.

---

## What is authoritative in this repository now

The following repository areas should be treated as the source of truth for their respective domains.

### 1. Repository-level overview

Authoritative file:

- `README.md`

This is the source of truth for:
- project scope
- high-level project positioning
- current repository structure
- current validated slice summary
- top-level direction

---

### 2. Architecture and boundaries

Authoritative file:

- `docs/ARCHITECTURE.md`

This is the source of truth for:
- architectural layering
- integration boundary expectations
- separation between plugin, runtime, resolver, and wrappers
- current architectural gaps
- intended long-term target model

If a lower-level implementation detail conflicts with the architecture document, the architecture document defines the intended direction, while code defines current behavior.

---

### 3. OpenClaw integration behavior

Authoritative path:

- `plugin/`

Primary file today:

- `plugin/index.js`

This is the source of truth for the current OpenClaw integration behavior, including:
- event hook handling
- session and conversation correlation
- current dangerous tool interception behavior
- current OpenClaw-specific approval linkage behavior
- current plugin-side state structure

Important note:
`plugin/` is authoritative for the current integration behavior, but it is not intended to remain the long-term home of core approval/runtime logic.

---

### 4. Approval reply classification logic

Authoritative paths:

- `resolver/`
- `policy-runtime/approval_resolve.py`

Current rule:
- `resolver/` is the source of truth for repository-native resolver implementations and tests
- `policy-runtime/approval_resolve.py` is the source of truth for the current live policy-runtime approval resolve entrypoint imported from CT115

This means the repository currently contains both:
- generic resolver logic under `resolver/`
- live policy-runtime resolve logic under `policy-runtime/`

That split is transitional but intentional for now.

---

### 5. Approval session runtime and execution flow

Authoritative path:

- `runtime/`

This is the source of truth for:
- approval session creation
- approval session persistence
- approval apply flow
- approval execution flow
- runtime shim installation helpers
- runtime-side guarded execution support

For current file-delete approval flow behavior, the repository runtime files are authoritative unless explicitly documented otherwise.

---

### 6. Policy runtime entrypoints

Authoritative path:

- `policy-runtime/`

This is the source of truth for the imported live policy runtime entrypoints currently brought in from CT115, including:
- `policy_api.py`
- `policy_decide.sh`
- `approval_resolve.py`
- `permissions_check.py`

These files represent the currently relevant policy-runtime implementation that the repository now tracks explicitly.

---

### 7. Guarded wrapper implementations

Authoritative paths:

- `runtime/bin/`
- `wrappers/`

Interpretation:
- `runtime/bin/` is authoritative for runtime entrypoint wrappers tracked in the repository
- `wrappers/` is authoritative for reusable wrapper implementations, reference wrappers, and refactored wrapper variants

Deployed copies in OpenClaw or other host paths are integration artifacts, not the long-term source of truth.

---

### 8. Documentation set

Authoritative path:

- `docs/`

Interpretation:
- documentation is authoritative for design intent, structure, and usage guidance
- documentation is not authoritative for live runtime behavior when it conflicts with current tracked code

In conflicts:
- tracked runtime code defines current behavior
- architecture docs define intended direction
- roadmap docs define planned work

---

## What is validated today

The currently validated live slice is still narrower than the full repository scope.

Validated today:

- inbound WhatsApp message correlation to the active session
- conversation/session binding in the OpenClaw-integrated flow
- dangerous `exec` detection in the OpenClaw plugin
- approval creation on the real dangerous `exec`
- blocking of dangerous execution before it runs
- plugin state persistence for inbound/session/run/approval tracking

Additionally, the repository contains broader runtime and policy components for:
- approval session creation
- approval reply resolution
- approval application
- approved file-delete execution
- policy-based wrapper decisions

These components are present and tracked, but not all repository paths should be assumed to have the same level of end-to-end validation in the integrated live OpenClaw flow.

---

## What is transitional or experimental

The following areas should currently be treated as transitional or partially aligned:

### 1. Plugin-to-runtime boundary
The OpenClaw plugin still contains more responsibility than the intended final architecture.

Examples:
- direct runtime invocation from the plugin
- plugin-side approval flow coordination
- duplicate-exec suppression tied to current integration behavior

The intended direction is for the plugin to become thinner and act more like an adapter.

---

### 2. Replay / duplicate-execution handling
The repository contains current replay/duplicate suppression behavior, but the long-term target is a stronger ID-based receipt model rather than command/target matching.

Current code is authoritative for present behavior.
It is not yet the final intended model.

---

### 3. Policy runtime import status
`policy-runtime/` contains imported live runtime pieces from CT115.

These are authoritative for the current tracked implementation, but this area should still be considered recently imported and subject to cleanup, packaging, and interface normalization.

---

### 4. CLI surface
The repository contains `cli/`, but the dedicated Nemoclaw Guard CLI is not yet implemented as a finished control surface.

So:
- the intended CLI shape is documented
- the actual CLI product is still in progress

---

## What is not authoritative

The following should not be treated as source of truth.

### 1. Backup files
Any files such as:
- `*.bak*`
- `*.backup*`
- ad hoc copied runtime backups
- temporary recovery files

These are not authoritative.

---

### 2. Deployed host/container copies outside tracked repository paths
Examples include deployed integration paths such as:
- OpenClaw-installed extension copies
- host-installed shim copies
- ad hoc deployed runtime files

These may reflect what is currently running, but the repository is intended to become the durable source of truth.

If such copies diverge from the repository, that divergence should be treated as a synchronization issue to resolve.

---

### 3. Historical/imported context documents
Historical materials kept under:
- `docs/history/`

are useful context but are not the primary source of truth for current implementation direction.

---

### 4. Markdown as runtime authority
Markdown documents do not override runtime code.

Documentation explains:
- intent
- architecture
- usage
- boundaries
- roadmap

But runtime code remains the source of truth for actual current behavior.

---

## Current boundary rule

The intended boundary remains:

### OpenClaw integration layer owns
- hooks
- OpenClaw-specific event handling
- session and conversation linkage
- passing approval-related context into Nemoclaw Guard runtime

### Nemoclaw Guard core owns
- approval reply interpretation
- approval lifecycle state transitions
- policy-aware guarded execution
- action-family runtime behavior
- reusable runtime and wrapper logic

Current implementation only partially satisfies this boundary.
The repository tracks both the current behavior and the intended direction.

---

## Current live paths of interest

These paths are operationally important, but the repository should be treated as the durable project source of truth.

Examples:

- OpenClaw live plugin inside container:
  - `/home/node/.openclaw/workspace/.openclaw/extensions/nemoclaw-guard/index.js`
- OpenClaw live plugin state inside container:
  - `/home/node/.openclaw/workspace/.openclaw/nemoclaw-guard/state.json`
- Nemoclaw Guard runtime path in CT110:
  - `/opt/nemoclaw-guard`
- Policy runtime path in CT115:
  - `/opt/nemoclaw/bin/`

These paths are runtime deployment locations, not repository structure guidance.

### Runtime path resolution note

Python runtime modules now support centralized path resolution through:

- `runtime/state/path_config.py`
- `policy-runtime/path_config.py`

This means the repository still documents `/opt/...` paths as current deployment defaults, but Python runtime code is no longer limited to hard-coded filesystem constants only.

Current default environment-backed path controls include values such as:

- `NEMOCLAW_GUARD_ROOT`
- `NEMOCLAW_OPENCLAW_ENV_PATH`
- `NEMOCLAW_POLICY_ROOT`
- `NEMOCLAW_POLICY_BIN_DIR`
- `NEMOCLAW_POLICY_CONFIG_DIR`

So `/opt/...` remains the current operational default, but not the only supported path layout for Python runtime modules.

---

## Practical interpretation for contributors

When deciding what to trust:

1. Use `README.md` for repository scope and current positioning.
2. Use `docs/ARCHITECTURE.md` for layering and intended boundaries.
3. Use tracked code under `plugin/`, `runtime/`, `resolver/`, `policy-runtime/`, and `wrappers/` for current implementation behavior.
4. Treat deployed copies outside the repository as operational artifacts that may need synchronization.
5. Treat backup files and historical notes as non-authoritative.

---

## Near-term cleanup goals

The most important follow-up tasks after this document are:

1. add example policy files to the repository
2. make quickstart runnable end-to-end
3. add a minimal real CLI
4. thin the OpenClaw plugin boundary
5. replace replay/duplicate behavior with an ID-based model
6. improve packaging and release readiness

---

## Summary

The repository is now the primary long-term source of truth for Nemoclaw Guard.

However, the current implementation still includes:
- imported live runtime pieces
- a plugin that remains thicker than intended
- partially transitional boundaries between integration logic and core runtime

This is acceptable at the current stage, as long as contributors treat:
- tracked code as authoritative for current behavior
- architecture docs as authoritative for intended direction
- roadmap docs as authoritative for what still needs to be hardened
