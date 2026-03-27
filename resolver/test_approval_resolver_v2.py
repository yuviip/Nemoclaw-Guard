#!/usr/bin/env python3
import json
from pathlib import Path
import importlib.util
import sys

resolver_path = "/opt/nemoclaw-guard/resolver/approval_resolver_v2.py"
spec = importlib.util.spec_from_file_location("approval_resolver_v2", resolver_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

cases = json.loads(
    Path("/opt/nemoclaw-guard/resolver/fixtures/approval_resolver_v2_cases.json").read_text()
)

failed = 0

for case in cases:
    got = mod.resolve(case["input"])
    expected = case["expected"]

    ok = True
    for k, v in expected.items():
        if got.get(k) != v:
            ok = False
            break

    case_name = case["name"]

    if ok:
        print(f"PASS: {case_name}")
    else:
        failed += 1
        print(f"FAIL: {case_name}")
        print("  expected:", expected)
        print("  got     :", got)

if failed:
    print(f"FAILED: {failed} case(s)")
    sys.exit(1)

print("ALL PASS")
