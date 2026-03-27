#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Any, Dict, Optional

STORE_PATH = Path("/home/node/.openclaw/nemoclaw/approval_sessions.json")


def _ensure_store() -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not STORE_PATH.exists():
        STORE_PATH.write_text("{}", encoding="utf-8")


def load_store() -> Dict[str, Any]:
    _ensure_store()
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save_store(data: Dict[str, Any]) -> None:
    _ensure_store()
    STORE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    data = load_store()
    return data.get(session_id)


def put_session(session_id: str, session_payload: Dict[str, Any]) -> None:
    data = load_store()
    data[session_id] = session_payload
    save_store(data)
