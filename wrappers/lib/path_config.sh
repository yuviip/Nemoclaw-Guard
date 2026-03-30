#!/usr/bin/env bash

: "${NEMOCLAW_GUARD_ROOT:=/opt/nemoclaw-guard}"

: "${NEMOCLAW_WRAPPERS_LIB_DIR:=${NEMOCLAW_GUARD_ROOT}/wrappers/lib}"
: "${NEMOCLAW_GUARDED_COMMON_PATH:=${NEMOCLAW_WRAPPERS_LIB_DIR}/guarded_common.sh}"

: "${NEMOCLAW_POLICY_SDK_PATH:=${NEMOCLAW_GUARD_ROOT}/sdk/lib/policy_sdk.sh}"
: "${NEMOCLAW_OPENCLAW_POLICY_SDK_PATH:=/opt/openclaw-policy-sdk/lib/policy_sdk.sh}"

: "${NEMOCLAW_RUNTIME_STATE_DIR:=${NEMOCLAW_GUARD_ROOT}/runtime/state}"
: "${NEMOCLAW_APPROVAL_SESSION_CREATE_PATH:=${NEMOCLAW_RUNTIME_STATE_DIR}/approval_session_create.py}"
