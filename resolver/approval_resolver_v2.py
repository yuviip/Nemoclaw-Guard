#!/usr/bin/env python3
import json
import sys


def norm(s):
    return (s or "").strip().lower()


POS = {"approve", "yes", "ok", "confirm"}
NEG = {"deny", "no", "cancel", "stop"}
SESSION_ALL = {"all", "everything", "whole session", "entire session"}


def detect_polarity(text):
    t = norm(text)
    has_pos = any(w in t for w in POS)
    has_neg = any(w in t for w in NEG)

    if has_pos and not has_neg:
        return "approve"
    if has_neg and not has_pos:
        return "deny"
    return None


def is_session_wide(text):
    t = norm(text)
    return any(w in t for w in SESSION_ALL)


def extract_aliases(action):
    r = action.get("resource", {})
    vals = []

    for x in [r.get("display"), r.get("primary")] + r.get("aliases", []):
        if isinstance(x, str) and x.strip():
            vals.append(norm(x))

    return list(set(vals))


def match_actions(text, actions):
    t = norm(text)
    matches = []

    for a in actions:
        aliases = extract_aliases(a)
        if any(alias and alias in t for alias in aliases):
            matches.append(a)

    return matches


def resolve(payload):
    text = payload.get("text", "")
    session = payload.get("request_session", {})
    actions = session.get("actions", [])

    pol = detect_polarity(text)
    if not pol:
        return {"ok": True, "intent": "no_match"}

    if is_session_wide(text):
        return {
            "ok": True,
            "intent": "approve_session" if pol == "approve" else "deny_session",
            "scope": "whole_session"
        }

    matches = match_actions(text, actions)

    if not matches:
        return {"ok": True, "intent": "no_match"}

    if len(matches) > 1:
        return {"ok": True, "intent": "ambiguous"}

    action_id = matches[0].get("action_id")

    return {
        "ok": True,
        "intent": "approve_single" if pol == "approve" else "deny_single",
        "scope": "single_action",
        "action_id": action_id
    }


if __name__ == "__main__":
    data = json.load(sys.stdin)
    print(json.dumps(resolve(data)))
