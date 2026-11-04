"""Run the whole pipeline in order, from the raw CSVs in data/ to outputs/final/claims.csv.

Usage (from the repo root):
    python src/run_all.py            run everything
    python src/run_all.py --dry-run  print the order and stop

Notes
- data/ is not in the repo. Put Galvor's four CSVs there first (ads.csv, creators.csv,
  creator_posts.csv, creator_audience.csv).
- src/label_sample.py is NOT run here. It writes the blank label spot-check sheet, and
  running it again would overwrite a filled-in sheet. The spot-check itself is a human
  step; src/label_error.py scores it. If outputs/audit/label_check.csv is not present
  (it is not committed), label_error.py is skipped and the committed
  outputs/audit/label_agreement.csv is used as is.
- outputs/final/manual_checks.csv is hand-entered (post-level checks) and is read, never
  written, by this pipeline.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

REQUIRED_DATA = ["ads.csv", "creators.csv", "creator_posts.csv", "creator_audience.csv"]

# (script, what it does). Order matters: later steps read earlier outputs.
STEPS = [
    ("audit.py", "data audit"),
    ("audit_extra.py", "supplementary audit"),
    ("audit_cross.py", "hypothesis-group structure"),
    ("label_error.py", "score the filled label spot-check (skipped if the sheet is absent)"),
    ("analyze_ads.py", "ad analysis, robustness, tiers"),
    ("posthoc_h1_h6.py", "post-hoc H1 x H6 table"),
    ("score_creators.py", "creator scoring (frozen weights)"),
    ("sensitivity_creators.py", "post-hoc creator sensitivity"),
    ("reading_pack.py", "reading pack"),
    ("reading_pack_extra.py", "extra reading pack, child-presenter share"),
    ("validity_checks.py", "link-request and proxy checks"),
    ("content_scan.py", "food-term and brand scan"),
    ("claims.py", "claims table (outputs/final/claims.csv)"),
]


def main() -> int:
    dry = "--dry-run" in sys.argv
    missing = [f for f in REQUIRED_DATA if not (ROOT / "data" / f).exists()]
    if missing and not dry:
        print("Missing from data/:", ", ".join(missing))
        print("Put Galvor's four CSVs in data/ and run again.")
        return 2
    label_sheet = ROOT / "outputs" / "audit" / "label_check.csv"
    t_all = time.time()
    for i, (script, what) in enumerate(STEPS, 1):
        tag = f"[{i}/{len(STEPS)}] {script}: {what}"
        if script == "label_error.py" and not label_sheet.exists():
            print(tag, "-> SKIPPED (no label_check.csv; using committed label_agreement.csv)")
            continue
        print(tag, "-> dry run" if dry else "")
        if dry:
            continue
        t0 = time.time()
        r = subprocess.run([sys.executable, str(SRC / script)], cwd=ROOT,
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if r.returncode != 0:
            print(r.stderr[-2000:])
            print(f"FAILED at {script} (exit {r.returncode}). Stopping.")
            return r.returncode
        print(f"    ok ({time.time() - t0:.1f}s)")
    print(f"Done in {time.time() - t_all:.0f}s. Final table: outputs/final/claims.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
