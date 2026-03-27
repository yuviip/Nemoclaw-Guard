# Nemoclaw Guard Reference Wrappers

This document records the first canonical guarded wrapper pattern validated in the live runtime and the in-repo refactoring structure prepared for future wrappers.

## Goal

A guarded wrapper must:

1. validate input
2. build the policy resource
3. call the local policy SDK
4. branch explicitly on the returned decision
5. execute the real action only on ALLOW
6. return structured machine-readable JSON

## Canonical decision handling

Supported decision branches:

- ALLOW
- DENY
- REQUIRE_OWNER_CONFIRMATION
- REQUIRE_OWNER_APPROVAL

Recommended exit codes used in the current reference wrappers:

- 1 invalid arguments or local precheck failure
- 2 denied by policy
- 3 requires owner confirmation
- 4 requires owner approval
- 5 unknown policy decision
- 6+ execution failure after allow

## Runtime-validated wrappers

The currently active runtime wrappers live under:

- /opt/openclaw/bin/guarded_git_push.sh
- /opt/openclaw/bin/guarded_file_delete.sh
- /opt/openclaw/bin/guarded_ha_call.sh

These wrappers were validated end-to-end against the active policy API and current system integration.

## In-repo wrapper structure

The repository now contains three layers.

### 1. Runtime snapshot layer

Location:

- wrappers/reference/

Purpose:

- preserves a repo-local copy of the currently validated runtime wrappers
- acts as a documentation snapshot of the live implementation pattern

Files:

- wrappers/reference/guarded_git_push.sh
- wrappers/reference/guarded_file_delete.sh
- wrappers/reference/guarded_ha_call.sh

### 2. Shared helper layer

Location:

- wrappers/lib/guarded_common.sh

Purpose:

- centralize JSON emission
- centralize decision branching
- centralize exit-code conventions

Current shared helpers:

- guard_json_escape
- guard_emit_json
- guard_handle_decision

Current shared constants:

- GUARD_RC_INVALID_ARGS
- GUARD_RC_DENY
- GUARD_RC_REQUIRE_CONFIRMATION
- GUARD_RC_REQUIRE_APPROVAL
- GUARD_RC_UNKNOWN_DECISION
- GUARD_RC_EXEC_FAILURE

### 3. Refactored wrapper layer

Location:

- wrappers/refactored/

Purpose:

- provide the cleaner target structure for future wrapper development
- reduce duplicated shell logic
- serve as the preferred implementation template for new wrappers

Files:

- wrappers/refactored/guarded_git_push.sh
- wrappers/refactored/guarded_file_delete.sh
- wrappers/refactored/guarded_ha_call.sh
- wrappers/refactored/guarded_systemctl.sh
- wrappers/refactored/guarded_docker_restart.sh

### SDK sourcing convention

There are currently two SDK contexts in the project:

- runtime and live wrappers under /opt/openclaw/bin use the runtime SDK at /opt/openclaw-policy-sdk/lib/policy_sdk.sh
- in-repo refactored wrappers should prefer the repo SDK at /opt/nemoclaw-guard/sdk/lib/policy_sdk.sh

Reason:

- the runtime SDK reflects the currently deployed live environment
- the repo SDK is the place where new resource builders and wrapper-development helpers should evolve first

Current example:

- wrappers/refactored/guarded_systemctl.sh sources /opt/nemoclaw-guard/sdk/lib/policy_sdk.sh

## Current validated wrapper flows

### guarded_git_push.sh

Flow:

- validate repo path
- verify git repository
- build resource as repo_name:remote:branch
- evaluate policy for action git_push
- execute git push only on ALLOW

### guarded_file_delete.sh

Flow:

- validate target path
- evaluate policy for action delete_files
- delete only on ALLOW

### guarded_ha_call.sh

Flow:

- validate service and entity_id
- build resource as service:entity_id
- evaluate policy for action ha_control
- execute Home Assistant service call only on ALLOW

### guarded_systemctl.sh

Flow:

- validate operation and unit_name
- build resource as operation:unit_name
- treat status as low risk
- evaluate policy for action systemctl_control
- execute systemctl only on ALLOW


### guarded_docker_restart.sh

Flow:

- validate container_name
- build resource as container_name
- evaluate policy for action docker_restart
- execute docker restart only on ALLOW

## Active policy source of truth

The active policy engine currently loads policy from:

- /opt/nemoclaw/policy/permissions.yml
- /opt/nemoclaw/policy/users.yml

The example files inside the repository are documentation and examples, not the active runtime source of truth.

## Current validated policy behavior

### git_push

- family -> DENY
- owner -> ALLOW
- non-owner risky fallback may require approval when no explicit deny exists

### delete_files

- family -> DENY by explicit rule, except allowed exception on /tmp/nemoclaw-test/**
- guest -> DENY by explicit rule
- owner -> REQUIRE_OWNER_CONFIRMATION through risky owner default

### ha_control

- family light, camera, cover, and switch patterns can be allowed by rule
- family switch.turn_on:switch.boiler is explicitly denied
- guest camera access is explicitly denied

### systemctl_control

Current refactored pattern was validated with these outcomes:

- invalid operation -> local validation failure
- guest restart -> REQUIRE_OWNER_APPROVAL
- owner restart -> REQUIRE_OWNER_CONFIRMATION
- family status -> ALLOW and successful execution


### docker_restart

Current refactored pattern was validated with these outcomes:

- invalid arguments -> local validation failure
- guest restart -> REQUIRE_OWNER_APPROVAL
- owner restart -> REQUIRE_OWNER_CONFIRMATION
- family restart -> REQUIRE_OWNER_APPROVAL

## Design lesson

Because the current policy matcher uses first-match-wins ordering, rule order is security-critical.

This means:

- specific denies must appear before broader allows
- exceptions must appear before broader denies if they should remain reachable

## Recommended structure for future wrappers

A new guarded wrapper should follow this pattern:

1. source the local policy SDK
2. source wrappers/lib/guarded_common.sh
3. validate required arguments
4. validate local execution preconditions
5. build the policy resource
6. request a policy decision
7. call guard_handle_decision
8. perform the real action only if decision handling returned allow
9. emit structured success or execution-failure JSON

## Next recommended step

Create the next wrapper from the refactored common-based pattern, most likely:

- guarded_docker_restart.sh

A good follow-up after that is adding tests that validate wrapper decision branching and structured output without requiring live side effects.
