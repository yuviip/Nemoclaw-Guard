#!/usr/bin/env bash
set -euo pipefail

source /opt/openclaw-policy-sdk/lib/policy_sdk.sh
source /opt/nemoclaw-guard/wrappers/lib/guarded_common.sh

usage() {
  cat >&2 <<USAGE
usage: guarded_git_push.sh <requester_id> <requester_role> <repo_path> <remote> <branch> [extra_git_args...]
USAGE
}

if [ "$#" -lt 5 ]; then
  usage
  guard_emit_json "error" "DENY" "invalid_arguments" "missing required arguments"
  exit "$GUARD_RC_INVALID_ARGS"
fi

REQUESTER_ID="$1"
REQUESTER_ROLE="$2"
REPO_PATH="$3"
REMOTE="$4"
BRANCH="$5"
shift 5
EXTRA_ARGS=("$@")

if [ -z "$REQUESTER_ID" ] || [ -z "$REQUESTER_ROLE" ] || [ -z "$REPO_PATH" ] || [ -z "$REMOTE" ] || [ -z "$BRANCH" ]; then
  guard_emit_json "error" "DENY" "invalid_arguments" "one or more required arguments are empty" \
    "repo_path" "$REPO_PATH" \
    "remote" "$REMOTE" \
    "branch" "$BRANCH"
  exit "$GUARD_RC_INVALID_ARGS"
fi

if [ ! -d "$REPO_PATH" ]; then
  guard_emit_json "denied" "DENY" "repo_not_found" "repository path does not exist" \
    "repo_path" "$REPO_PATH" \
    "remote" "$REMOTE" \
    "branch" "$BRANCH"
  exit "$GUARD_RC_INVALID_ARGS"
fi

if [ ! -d "$REPO_PATH/.git" ]; then
  guard_emit_json "denied" "DENY" "not_a_git_repo" "target path is not a git repository" \
    "repo_path" "$REPO_PATH" \
    "remote" "$REMOTE" \
    "branch" "$BRANCH"
  exit "$GUARD_RC_INVALID_ARGS"
fi

REPO_NAME="$(basename "$REPO_PATH")"
RESOURCE="$(policy_build_git_push_resource "$REPO_NAME" "$REMOTE" "$BRANCH")"

DECISION_JSON="$(policy_decide \
  "$REQUESTER_ID" \
  "$REQUESTER_ROLE" \
  "git_push" \
  "$RESOURCE" \
  "high"
)"
DECISION="$(policy_extract_decision "$DECISION_JSON")"

if ! guard_handle_decision "$DECISION" "$DECISION_JSON" \
  "resource" "$RESOURCE" \
  "repo_path" "$REPO_PATH" \
  "remote" "$REMOTE" \
  "branch" "$BRANCH"; then
  exit "$?"
fi

cd "$REPO_PATH"

if ! git push "$REMOTE" "$BRANCH" "${EXTRA_ARGS[@]}"; then
  guard_emit_json "error" "ALLOW" "git_push_failed" "git push command failed" \
    "resource" "$RESOURCE" \
    "repo_path" "$REPO_PATH" \
    "remote" "$REMOTE" \
    "branch" "$BRANCH"
  exit "$GUARD_RC_EXEC_FAILURE"
fi

guard_emit_json "executed" "ALLOW" "git_push_executed" "git push executed successfully" \
  "resource" "$RESOURCE" \
  "repo_path" "$REPO_PATH" \
  "remote" "$REMOTE" \
  "branch" "$BRANCH"
