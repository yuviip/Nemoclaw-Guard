# Status and Roadmap

## Current validated slice

Validated today:

- WhatsApp inbound -> active session correlation works
- dangerous `exec` detection works
- direct approval creation on dangerous `exec` works
- dangerous `exec` is blocked before execution
- plugin state records pending approvals and guard actions

## Current limitation

After blocking the dangerous `exec`, the surrounding agent flow may still produce follow-up reactions or messages unless the runtime flow is tightened further.

This means the approval interception is working on the real risky action, but the surrounding UX still needs refinement.

## Next priorities

### P1
- finish approval-flow UX and resolver behavior
- ensure approve/deny replies are resolved correctly from user text
- support specific target approval, negative approval, and broader approval scopes where intended

### P2
- add safe replay/resume flow after approval
- prevent confusing post-block follow-up behavior
- polish runtime state transitions

### P3
- create install/uninstall/enable/disable lifecycle tooling
- create dedicated Nemoclaw Guard CLI
- make plugin lifecycle easy and reliable

### P4
- public open-source polish
- packaging cleanup
- docs cleanup and source-of-truth alignment
- examples and validation scripts
- final license selection
