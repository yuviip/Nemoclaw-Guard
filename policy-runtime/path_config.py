#!/usr/bin/env python3
import os
from pathlib import Path


def _env_path(name: str, default: str) -> str:
    value = os.environ.get(name, "").strip()
    return value or default


NEMOCLAW_POLICY_ROOT = _env_path("NEMOCLAW_POLICY_ROOT", "/opt/nemoclaw")
NEMOCLAW_POLICY_BIN_DIR = _env_path("NEMOCLAW_POLICY_BIN_DIR", str(Path(NEMOCLAW_POLICY_ROOT) / "bin"))
NEMOCLAW_POLICY_CONFIG_DIR = _env_path("NEMOCLAW_POLICY_CONFIG_DIR", str(Path(NEMOCLAW_POLICY_ROOT) / "policy"))

POLICY_DECIDE_PATH = str(Path(NEMOCLAW_POLICY_BIN_DIR) / "policy_decide.sh")
APPROVAL_RESOLVE_PATH = str(Path(NEMOCLAW_POLICY_BIN_DIR) / "approval_resolve.py")
PERMISSIONS_CHECK_PATH = str(Path(NEMOCLAW_POLICY_BIN_DIR) / "permissions_check.py")

PERMISSIONS_YML_PATH = str(Path(NEMOCLAW_POLICY_CONFIG_DIR) / "permissions.yml")
USERS_YML_PATH = str(Path(NEMOCLAW_POLICY_CONFIG_DIR) / "users.yml")
