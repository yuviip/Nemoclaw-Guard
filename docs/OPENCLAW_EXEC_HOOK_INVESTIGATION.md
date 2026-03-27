# OpenClaw exec hook investigation

## Goal

Verify whether OpenClaw managed hooks with `before_tool_call` can reliably intercept and block `exec` tool calls in the live runtime.

## Environment

- OpenClaw runtime inside CT110
- managed hooks path: `/opt/openclaw/state/hooks`
- investigated hooks:
  - `nemoclaw-exec-guard`
  - `test-hook`

## What was verified

### Hook registration and readiness

The following commands succeeded:

- `openclaw hooks list`
- `openclaw hooks check`
- `openclaw hooks info nemoclaw-exec-guard`
- `openclaw hooks info test-hook`

Both managed hooks appeared as ready.

### Hook execution test

A test hook was created and later modified to:

- log received context
- explicitly block `exec` with:
  - `block: true`
  - `blockReason: "test-hook blocked exec intentionally"`

OpenClaw was restarted after changes.

### Live behavior observed

Despite hooks being reported as ready, live agent requests still executed raw `exec` commands successfully.

Confirmed examples from session logs:

- `whoami`
- `pwd`
- `rm -f /tmp/test123`

These commands reached execution and returned successful tool results.

### Missing evidence of hook firing

No runtime evidence was observed for actual hook invocation:

- no `[test-hook]` log lines
- no `[nemoclaw-exec-guard]` log lines
- no visible `before_tool_call` activity in container logs
- no blocking behavior even when a hook intentionally blocked all `exec`

## Conclusion

Current finding:

**In the tested OpenClaw runtime path, managed hooks may load and report ready, but they are not effectively enforcing `before_tool_call` interception for the agent `exec` tool path used in practice.**

This means OpenClaw hooks should not currently be treated as the primary security boundary for shell execution control.

## Security implication

Raw `exec` remains reachable in the live agent path even when guard hooks are present and marked ready.

That makes hook-based enforcement insufficient as the main protection layer for dangerous shell actions.

## Recommended architecture

Use a durable integration layer outside the OpenClaw hook path:

- canonical wrappers under `/opt/nemoclaw-guard/runtime/bin`
- shim entrypoints under `/opt/openclaw/bin`
- guarded action routing through wrapper-specific policy enforcement

This should be the main enforcement model for:

- git push
- file delete
- Home Assistant control
- systemctl control
- docker restart

## Recommended next step

Move from hook investigation to durable integration:

1. treat hooks as optional future enhancement only
2. keep policy enforcement in Nemoclaw Guard canonical runtime wrappers
3. ensure OpenClaw instructions/tools route sensitive actions only through guarded wrapper entrypoints
4. continue end-to-end validation through OpenClaw itself using those guarded entrypoints

