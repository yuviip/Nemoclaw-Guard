#!/usr/bin/env bash
set -euo pipefail

source /opt/openclaw-policy-sdk/lib/policy_sdk.sh

json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'
}

emit_json() {
  local status="$1"
  local decision="$2"
  local reason="$3"
  local message="$4"
  local resource="${5:-}"
  local repo_path="${6:-}"
  local remote="${7:-}"
  local branch="${8:-}"

  printf "{"
  printf "\"status\":\"%s\"," "$status"
  printf "\"decision\":\"%s\"," "$decision"
  printf "\"reason\":\"%s\"," "$reason"
  printf "\"message\":%s" "$(printf "%s" "$message" | json_escape)"

  if [ -n "$resource" ]; then
    printf ",\"resource\":%s" "$(printf "%s" "$resource" | json_escape)"
  fi
  if [ -n "$repo_path" ]; then
    printf ",\"repo_path\":%s" "$(printf "%s" "$repo_path" | json_escape)"
  fi
  if [ -n "$remote" ]; then
    printf ",\"remote\":%s" "$(printf "%s" "$remote" | json_escape)"
  fi
  if [ -n "$branch" ]; then
    printf ",\"branch\":%s" "$(printf "%s" "$branch" | json_escape)"
  fi

  printf "}\n"
}

usage() {
  cat >&2 <<'USAGE'
usage: guarded_git_push.sh <requester_id> <requester_role> <repo_path> <remote> <branch> [extra_git_args...]
USAGE
}

if [ "$#" -lt 5 ]; then
  usage
  emit_json "error" "DENY" "invalid_arguments" "missing required arguments"
  exit 1
fi

REQUESTER_ID="$1"
REQUESTER_ROLE="$2"
REPO_PATH="$3"
REMOTE="$4"
BRANCH="$5"
shift 5
EXTRA_ARGS=("$@")

if [ -z "$REQUESTER_ID" ] || [ -z "$REQUESTER_ROLE" ] || [ -z "$REPO_PATH" ] || [ -z "$REMOTE" ] || [ -z "$BRANCH" ]; then
  emit_json "error" "DENY" "invalid_arguments" "one or more required arguments are empty" "" "$REPO_PATH" "$REMOTE" "$BRANCH"
  exit 1
fi

if [ ! -d "$REPO_PATH" ]; then
  emit_json "denied" "DENY" "repo_not_found" "repository path does not exist" "" "$REPO_PATH" "$REMOTE" "$BRANCH"
  exit 1
fi

if [ ! -d "$REPO_PATH/.git" ]; then
  emit_json "denied" "DENY" "not_a_git_repo" "target path is not a git repository" "" "$REPO_PATH" "$REMOTE" "$BRANCH"
  exit 1
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

case "$DECISION" in
  ALLOW)
    ;;
  DENY)
    emit_json "denied" "DENY" "policy_denied" "$DECISION_JSON" "$RESOURCE" "$REPO_PATH" "$REMOTE" "$BRANCH"
    exit 2
    ;;
  REQUIRE_OWNER_CONFIRMATION)
    emit_json "requires_confirmation" "REQUIRE_OWNER_CONFIRMATION" "policy_requires_owner_confirmation" "$DECISION_JSON" "$RESOURCE" "$REPO_PATH" "$REMOTE" "$BRANCH"
    exit 3
    ;;
  REQUIRE_OWNER_APPROVAL)
    emit_json "requires_approval" "REQUIRE_OWNER_APPROVAL" "policy_requires_owner_approval" "$DECISION_JSON" "$RESOURCE" "$REPO_PATH" "$REMOTE" "$BRANCH"
    exit 4
    ;;
  *)
    emit_json "error" "DENY" "unknown_policy_decision" "$DECISION_JSON" "$RESOURCE" "$REPO_PATH" "$REMOTE" "$BRANCH"
    exit 5
    ;;
esac

cd "$REPO_PATH"

if ! git push "$REMOTE" "$BRANCH" "${EXTRA_ARGS[@]}"; then
  emit_json "error" "ALLOW" "git_push_failed" "git push command failed" "$RESOURCE" "$REPO_PATH" "$REMOTE" "$BRANCH"
  exit 6
fi

emit_json "executed" "ALLOW" "git_push_executed" "git push executed successfully" "$RESOURCE" "$REPO_PATH" "$REMOTE" "$BRANCH"
