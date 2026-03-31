#!/usr/bin/env python3
import os
from pathlib import Path


def _env_path(name: str, default: str) -> str:
    value = os.environ.get(name, "").strip()
    return value or default


NEMOCLAW_GUARD_ROOT = _env_path("NEMOCLAW_GUARD_ROOT", "/opt/nemoclaw-guard")
NEMOCLAW_OPENCLAW_ENV_PATH = _env_path("NEMOCLAW_OPENCLAW_ENV_PATH", "/opt/openclaw/openclaw.env")

RUNTIME_STATE_DIR = str(Path(NEMOCLAW_GUARD_ROOT) / "runtime" / "state")
RESOLVER_DIR = str(Path(NEMOCLAW_GUARD_ROOT) / "resolver")

APPROVAL_SESSION_STORE_PATH = str(Path(RUNTIME_STATE_DIR) / "approval_session_store.py")
APPROVAL_APPLY_BRIDGE_PATH = str(Path(RUNTIME_STATE_DIR) / "approval_apply_bridge.py")
APPROVAL_RESOLVE_BRIDGE_PATH = str(Path(RUNTIME_STATE_DIR) / "approval_resolve_bridge.py")
APPROVAL_SESSION_CREATE_PATH = str(Path(RUNTIME_STATE_DIR) / "approval_session_create.py")
APPROVAL_PREPARE_FILE_DELETE_PATH = str(Path(RUNTIME_STATE_DIR) / "approval_prepare_file_delete.py")
APPROVAL_EXECUTE_FILE_DELETE_PATH = str(Path(RUNTIME_STATE_DIR) / "approval_execute_file_delete.py")
APPROVAL_APPLY_RUNTIME_OUTCOME_PATH = str(Path(RUNTIME_STATE_DIR) / "approval_apply_runtime_outcome.py")

APPROVAL_RESOLVER_V1_PATH = str(Path(RESOLVER_DIR) / "approval_resolver_v1.py")
APPROVAL_RESOLVER_V2_PATH = str(Path(RESOLVER_DIR) / "approval_resolver_v2.py")
