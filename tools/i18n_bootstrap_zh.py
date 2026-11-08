#!/usr/bin/env python3
"""One-off: import the existing hand-made /zh/ pages into i18n/zh-hans.json by aligning their
segments with the English originals they were generated from (git commit 7b7c6dc).
Only pairs whose structure matches (same placeholders) are imported."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
import i18n

BASE = "7b7c6dc"
tm = i18n.load_tm("zh-hans")
pages = ["index.html", "guides/index.html"] + ["guides/%s/index.html" % s for s in [
    "aging-in-place-powered-exoskeleton", "exoskeleton-for-elderly-parent-caregiver-guide",
    "exoskeleton-vs-walking-frame-cane-wheelchair", "hip-torque-16nm-explained", "exoskeleton-battery-life-explained",
    "ip54-rating-tropical-climate", "powered-hip-assist-for-stairs", "exoskeleton-daily-commute-singapore",
    "trekking-poles-vs-powered-exoskeleton"]]
added = conflicts = 0
for rel in pages:
    en = subprocess.run(["git", "show", "%s:%s" % (BASE, rel)], cwd=i18n.ROOT, capture_output=True, text=True).stdout
    zh = subprocess.run(["git", "show", "%s:zh/%s" % (BASE, rel)], cwd=i18n.ROOT, capture_output=True, text=True).stdout
    _, se = i18n.segments(i18n.normalise_en(en))
    _, sz = i18n.segments(i18n.normalise_en(zh))
    for kind in ("run", "attr", "ld"):
        a = [s for s in se if s.kind == kind]
        b = [s for s in sz if s.kind == kind]
        if len(a) != len(b):
            print("count mismatch", rel, kind, len(a), len(b))
            continue
        for x, y in zip(a, b):
            if not x.id:
                continue
            if not i18n.check_ph(x.text, y.text):
                print("ph mismatch", rel, x.text[:50], "|", y.text[:50]); continue
            if x.id in tm and tm[x.id] != y.text:
                conflicts += 1
                continue
            if x.id not in tm:
                tm[x.id] = y.text; added += 1
i18n.save_tm("zh-hans", tm)
print("added", added, "conflicts kept first", conflicts, "total", len(tm))
