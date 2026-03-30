#!/opt/nemoclaw/.venv/bin/python3
import sys
import json
from pathlib import Path
from fnmatch import fnmatch
import yaml

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from path_config import PERMISSIONS_YML_PATH, USERS_YML_PATH

PERMISSIONS_PATH = Path(PERMISSIONS_YML_PATH)
USERS_PATH = Path(USERS_YML_PATH)


VALID_EFFECTS = {
    "ALLOW",
    "DENY",
    "REQUIRE_OWNER_CONFIRMATION",
    "REQUIRE_OWNER_APPROVAL",
    "NO_MATCH",
}


ACTION_CLASSES = {
    "file.read": "read",
    "file.stat": "read_meta",
    "file.list": "read_meta",
    "file.delete": "delete",
    "file.write": "write",
    "file.move": "write",
    "file.copy": "write",
}


def load_yaml(path: Path, default: dict):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else default


def load_policy():
    permissions = load_yaml(PERMISSIONS_PATH, {"roles": [], "rules": [], "defaults": {}})
    users_doc = load_yaml(USERS_PATH, {"users": []})

    return {
        "users": users_doc.get("users", []),
        "rules": permissions.get("rules", []),
        "defaults": permissions.get("defaults", {}),
    }


def normalize_user(policy, requester_id, requester_role):
    rid = (requester_id or "").strip().lower()
    rrole = (requester_role or "").strip().lower()

    for user in policy["users"]:
        uid = str(user.get("id", "")).lower()
        aliases = [str(x).lower() for x in user.get("aliases", [])]
        role = str(user.get("role", rrole)).lower()

        if rid == uid or rid in aliases:
            return uid, role

    return rid, rrole


def classify_resource(resource, resource_meta):

    meta = resource_meta if isinstance(resource_meta, dict) else {}

    kind = meta.get("kind", "file")
    extension = meta.get("extension") or Path(resource).suffix
    sensitivity = meta.get("sensitivity", "normal")
    location_scope = meta.get("location_scope", "single")

    prefixes = []
    if resource:
        parts = Path(resource).parts
        current = ""
        for part in parts:
            if part == "/":
                current = "/"
            elif current in ("", "/"):
                current = "/" + part
            else:
                current = current + "/" + part
            prefixes.append(current)

    return {
        "kind": kind,
        "extension": extension,
        "sensitivity": sensitivity,
        "location_scope": location_scope,
        "path_prefixes": prefixes,
    }


def match_subject(subject, requester_id, requester_role):

    if subject == "*":
        return True

    subject = subject.lower()

    if subject.startswith("role:"):
        return requester_role == subject.split(":", 1)[1]

    return requester_id == subject


def match_rule(rule, requester_id, requester_role, action, resource, attrs):

    if not match_subject(rule.get("subject", "*"), requester_id, requester_role):
        return False

    if not fnmatch(action, rule.get("action", "*")):
        return False

    rule_op = rule.get("operation_class")
    if rule_op and rule_op != ACTION_CLASSES.get(action):
        return False

    if rule.get("path_prefix"):
        if rule["path_prefix"] not in attrs["path_prefixes"]:
            return False

    if rule.get("extension"):
        if rule["extension"] != attrs["extension"]:
            return False

    if rule.get("resource_kind"):
        if rule["resource_kind"] != attrs["kind"]:
            return False

    if rule.get("sensitivity"):
        if rule["sensitivity"] != attrs["sensitivity"]:
            return False

    if rule.get("location_scope"):
        if rule["location_scope"] != attrs["location_scope"]:
            return False

    return True


def main():

    try:
        req = json.loads(sys.stdin.read())
    except Exception:
        print("DENY")
        return

    requester_id = req.get("requester_id", "")
    requester_role = req.get("requester_role", "")
    action = req.get("action", "")
    resource = req.get("resource", "")
    resource_meta = req.get("resource_meta", {})

    policy = load_policy()

    requester_id, requester_role = normalize_user(policy, requester_id, requester_role)

    attrs = classify_resource(resource, resource_meta)

    for rule in policy["rules"]:

        if match_rule(rule, requester_id, requester_role, action, resource, attrs):

            effect = rule.get("effect", "DENY").upper()

            if effect not in VALID_EFFECTS:
                effect = "DENY"

            print(effect)
            return

    defaults = policy.get("defaults", {})

    if requester_role == "owner":
        print(defaults.get("owner_risky", "REQUIRE_OWNER_CONFIRMATION"))
        return

    print(defaults.get("non_owner_risky", "REQUIRE_OWNER_APPROVAL"))


if __name__ == "__main__":
    main()
