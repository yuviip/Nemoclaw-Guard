# Nemoclaw Guard

Nemoclaw Guard is an OpenClaw guardrail plugin focused on intercepting risky actions, creating approval checkpoints, and preserving safe operator control over destructive flows.

## Current status

The repository currently contains the working plugin source captured from the live environment and the documentation imported from the container-side project directory.

The currently implemented vertical slice focuses on dangerous `exec`-based file deletion flows triggered through OpenClaw.

## What works now

Current validated behavior includes:

- inbound WhatsApp message correlation to the active main agent session
- stable conversation/session binding using conversation-key-based linkage
- state persistence for inbound/session/run/approval tracking
- dangerous `exec` detection inside `before_tool_call`
- approval creation on the real dangerous `exec` action
- blocking of dangerous `exec` before execution
- preservation of pending approval records in plugin state

## Current live runtime paths

Live plugin path inside the OpenClaw container:

- `/home/node/.openclaw/workspace/.openclaw/extensions/nemoclaw-guard/index.js`

Live plugin state path inside the OpenClaw container:

- `/home/node/.openclaw/workspace/.openclaw/nemoclaw-guard/state.json`

Repository source path:

- `plugin/index.js`

Repository state example:

- `state/state.example.json`

## Repository structure

- `plugin/` — live plugin source tracked in this repository
- `state/` — example state payloads and future state-related utilities
- `docs/` — architecture, approval-flow, policy, testing, and investigation docs
- `docs/history/` — archived/imported historical materials kept for reference

## Main implemented runtime model

Today the plugin is centered around:

1. receiving inbound user messages
2. binding inbound conversation context to the active agent session
3. observing tool calls in `before_tool_call`
4. marking dangerous `exec` actions
5. creating approval records for destructive execution attempts
6. blocking execution until explicit approval resolution is implemented

## What is not finished yet

The repository is not yet at its final open-source packaging level.

Important items still in progress:

- approval resolution UX for natural replies such as approve / deny / approve all / specific target
- replay/resume execution after approval
- polished install / uninstall / enable / disable flow
- dedicated Nemoclaw Guard CLI
- packaging and lifecycle management for clean deployment
- repository polish for public open-source release
- test assets and repeatable validation scripts
- final license selection

## Project goals

Nemoclaw Guard is intended to become a high-quality guardrail layer for risky agent actions, with emphasis on:

- robust approval interception for risky actions
- natural-language approval and denial handling
- safe replay/execution after approval
- clean open-source packaging
- easy installation and removal
- strong operator visibility and auditability
- dedicated CLI for managing the plugin lifecycle

## Planned CLI

The intended CLI surface includes commands such as:

- `nemoclaw-guard install`
- `nemoclaw-guard uninstall`
- `nemoclaw-guard enable`
- `nemoclaw-guard disable`
- `nemoclaw-guard status`
- `nemoclaw-guard paths`
- `nemoclaw-guard test`

## Documentation

Start here:

- `docs/README.md`

Important docs:

- `docs/ARCHITECTURE.md`
- `docs/POLICY_MODEL.md`
- `docs/TESTING.md`
- `docs/approval_sessions_runtime_flow.md`
- `docs/approval_resolution_contract.md`

## Open-source direction

This repository is being reorganized into a clean, public-quality project layout.

The current priority is to preserve the working plugin logic, document the real runtime behavior accurately, and then build a polished install/control surface around it without losing the validated guard behavior already achieved.
