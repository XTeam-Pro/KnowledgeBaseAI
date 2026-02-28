#!/usr/bin/env python3
import json
data = json.load(open("/tmp/audit2.json"))
ok = sum(1 for t in data if t["status"] == "OK")
few = sum(1 for t in data if t["status"] == "FEW_METHODS")
irr = sum(1 for t in data if t["status"] == "IRRELEVANT_METHODS")
crit = sum(1 for t in data if t["status"] == "CRITICAL")
print(f"OK: {ok}, FEW: {few}, IRREL: {irr}, CRIT: {crit}, TOTAL: {len(data)}")
print()
problems = [t for t in data if t["status"] != "OK"]
for t in sorted(problems, key=lambda x: x["status"]):
    irr_m = ", ".join([m["method_title"] for m in t.get("irrelevant_methods", [])])
    print(f"{t['status']:20s} | methods={t['method_count']:2d} | {t['uid']} | {t['title']}")
    if irr_m:
        print(f"{'':20s} |   IRREL: {irr_m}")
