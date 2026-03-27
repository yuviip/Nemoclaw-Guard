# Nemoclaw Guard Testing

This document describes the current test approach for the in-repo refactored wrappers.

## Goals

The current test harness is designed to validate:

- wrapper argument validation
- policy decision branching
- structured JSON output
- execution-path behavior without real side effects

## Test layout

Current files:

- tests/run_tests.sh
- tests/test_guarded_systemctl.sh
- tests/test_guarded_docker_restart.sh
- tests/stubs/policy_sdk.sh
- tests/stubs/systemctl
- tests/stubs/docker

## Current approach

The test runner injects stub implementations through environment-variable overrides.

This allows the wrappers to run in a controlled environment without depending on:

- the live policy runtime
- real systemctl execution
- real docker execution

## Supported test override variables

### NEMOCLAW_POLICY_SDK_PATH

Overrides which policy SDK file is sourced by refactored wrappers.

Default refactored behavior:

/opt/nemoclaw-guard/sdk/lib/policy_sdk.sh

Test override used by the harness:

tests/stubs/policy_sdk.sh

### NEMOCLAW_SYSTEMCTL_BIN

Overrides the executable used by guarded_systemctl.sh.

Default behavior:

systemctl

Test override used by the harness:

tests/stubs/systemctl

### NEMOCLAW_DOCKER_BIN

Overrides the executable used by guarded_docker_restart.sh.

Default behavior:

docker

Test override used by the harness:

tests/stubs/docker

## Running tests

Run:

/opt/nemoclaw-guard/tests/run_tests.sh

## Current expected behaviors

### systemctl wrapper

- invalid arguments -> local validation error
- guest restart -> requires owner approval
- owner status -> executed successfully through stub executor

### docker restart wrapper

- invalid arguments -> local validation error
- guest restart -> requires owner approval
- owner restart -> executed successfully through stub executor

## Important scope note

These tests validate the in-repo refactored wrappers, not the live OpenClaw runtime wrappers.

They are intended for:

- wrapper pattern development
- regression checking of common logic
- safe iteration on new wrapper types

## Recommended next step

After refactored wrapper tests pass, perform end-to-end validation through OpenClaw itself to confirm that:

- requests are routed through the intended guard layer
- policy decisions are surfaced correctly
- blocked actions do not execute
- the integration remains durable across future OpenClaw updates
