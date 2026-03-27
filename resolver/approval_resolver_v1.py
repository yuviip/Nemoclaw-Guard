#!/usr/bin/env python3
import json
import re
import sys


def normalize(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def detect_polarity(text: str):
    positive_words = {"approve", "yes", "confirm", "ok", "do it"}
    negative_words = {"deny", "cancel", "stop", "no", "dont", "do not"}

    for w in negative_words:
        if w in text:
            return "negative"

    for w in positive_words:
        if w in text:
            return "positive"

    return "unknown"


def detect_session_scope(text: str):
    if "all" in text:
        return "session"
    return "single"


def match_resource(text: str, actions):
    matches = []

    for act in actions:
        resource = act.get("resource", {})
        aliases = resource.get("aliases", [])
        display = resource.get("display")

        candidates = set(aliases)
        if display:
            candidates.add(display)

        for c in candidates:
            if c and c.lower() in text:
                matches.append(act["action_id"])
                break

    return matches


def resolve(text, session):
    text_n = normalize(text)
    actions = session.get("actions", [])

    polarity = detect_polarity(text_n)
    scope = detect_session_scope(text_n)
    matches = match_resource(text_n, actions)

    if polarity == "unknown":
        return {"intent": "no_match"}

    if scope == "session":
        if polarity == "positive":
            return {"intent": "approve_session"}
        else:
            return {"intent": "deny_session"}

    if len(matches) == 1:
        if polarity == "positive":
            return {"intent": "approve_single", "action_id": matches[0]}
        else:
            return {"intent": "deny_single", "action_id": matches[0]}

    if len(matches) > 1:
        return {"intent": "ambiguous"}

    return {"intent": "no_match"}


def main():
    payload = json.load(sys.stdin)

    text = payload["text"]
    session = payload["request_session"]

    result = resolve(text, session)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
