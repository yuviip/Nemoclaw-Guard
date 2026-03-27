#!/usr/bin/env python3
import json
from pathlib import Path
import importlib.util
import sys

resolver_path = "/opt/nemoclaw-guard/resolver/approval_resolver_v1.py"
spec = importlib.util.spec_from_file_location("approval_resolver_v1", resolver_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

cases = json.loads(
    Path("/opt/nemoclaw-guard/resolver/fixtures/approval_resolver_v1_cases.json").read_text()
)

failed = 0

for case in cases:
    got = mod.resolve(case["input"]["text"], case["input"]["request_session"])
    expected = case["expected"]

    ok = True
    for k, v in expected.items():
        if got.get(k) != v:
            ok = False
            break

    if ok:
        print("PASS:", case["name"])
    else:
        failed += 1
        print("FAIL:", case["name"])
        print("  expected:", expected)
        print("  got     :", got)

if failed:
    sys.exit(1)

print("ALL PASS")
