"""Independent recomputation of the headline figures in the report.

This script does not import any other module in src/. It reads data/ and
outputs/ directly, recomputes each figure with its own code, and compares it
with the value the pipeline wrote. A mismatch prints FAIL and exits non-zero.

Run:  python src/verify_independent.py
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ads = pd.read_csv(ROOT / "data" / "ads.csv")
cre = pd.read_csv(ROOT / "data" / "creators.csv")
posts = pd.read_csv(ROOT / "data" / "creator_posts.csv", parse_dates=["posted_on"])
find = pd.read_csv(ROOT / "outputs" / "ads" / "findings.csv")
find = find[find["is_primary_floor"]].set_index("hypothesis_id")
scores = pd.read_csv(ROOT / "outputs" / "creators" / "creator_scores.csv").set_index("creator_id")

FLOOR, SEED, DRAWS = 10_000, 42, 2000
results = []

def check(name, got, want, tol=1e-6):
    ok = abs(float(got) - float(want)) <= tol
    results.append(ok)
    print(f"{'ok  ' if ok else 'FAIL'} {name}: recomputed {got:.4f} vs pipeline {float(want):.4f}")

def roas(d): return d["revenue_inr"].sum() / d["spend_inr"].sum()
def cvr(d): return d["purchases"].sum() / d["link_clicks"].sum()

floor = ads[ads["spend_inr"] >= FLOOR]
print(f"ads {len(ads)}, floor set {len(floor)}")
check("floor-set share of spend", floor["spend_inr"].sum() / ads["spend_inr"].sum(), 0.985, 0.0005)
check("floor-set pooled ROAS", roas(floor), 1.4981, 0.0001)

masks = {
    "H1": floor["child_role"].fillna("").str.split("; ").apply(lambda x: "reacts_to_taste" in x),
    "H3": floor["brand_first_said"] == "under_3s",
    "H6": floor["creator_type"] == "parent_or_caregiver",
}
rng = np.random.default_rng(SEED)
for h, m in masks.items():
    i, o = floor[m], floor[~m]
    check(f"{h} ROAS in-group", roas(i), find.loc[h, "pooled_roas_in"])
    check(f"{h} ROAS out-group", roas(o), find.loc[h, "pooled_roas_out"])
    check(f"{h} purchase rate in-group", cvr(i), find.loc[h, "cvr_in"])
    diffs = []
    for _ in range(DRAWS):
        a = i.iloc[rng.integers(0, len(i), len(i))]
        b = o.iloc[rng.integers(0, len(o), len(o))]
        diffs.append(roas(a) - roas(b))
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    check(f"{h} CI low (own bootstrap, tolerance 0.1)", lo, find.loc[h, "boot_ci_low"], 0.1)
    check(f"{h} CI high (own bootstrap, tolerance 0.1)", hi, find.loc[h, "boot_ci_high"], 0.1)
    check(f"{h} CI excludes zero agrees", float(lo > 0 or hi < 0), float(find.loc[h, "ci_excludes_zero"]))
check("H1 and H6 overlap (ads)", (masks["H1"] & masks["H6"]).sum(), 22)

end = pd.Timestamp("2026-10-27")
win = posts[(posts["posted_on"] > end - pd.DateOffset(years=1)) & (posts["posted_on"] <= end)]
check("posts in 12-month window", len(win), 374)
check("posts with no play count", posts["plays"].isna().sum(), 39)
check("creators in file", len(cre), 20)

five = ["CR-13", "CR-03", "CR-11", "CR-01", "CR-19"]
check("followers of the five, total", cre.set_index("creator_id").loc[five, "followers"].sum(), 814_499)
check("CR-12 composite rank", scores.loc["CR-12", "composite_rank"], 1)

bad = results.count(False)
print(f"\n{len(results) - bad} of {len(results)} checks match")
sys.exit(1 if bad else 0)
