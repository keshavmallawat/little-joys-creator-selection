"""Post-hoc sensitivity of the creator ranking.

POST-HOC, not pre-registered: the frozen result in outputs/creators/creator_scores.csv
remains the primary ranking. This pass is prompted by a thin input — CR-09's
sponsored_fit ratio rests on only 3 non-sponsored posts — and asks how far the
ranking moves when the sponsored_fit component is weakened (Part 1) and under
post-sampling noise (Part 2). It reports and ranks only: it selects no five and
uses no causal language.

All scoring logic and every parameter are reused from src/score_creators.py
(imported, never edited): the component definitions, the percentile method, the
weights, the min-data floors, the seed and the draw count. The 12-month window
is rebuilt the same way, from the imported window length.

Outputs (outputs/creators/): sensitivity.csv, bootstrap_top5.csv,
sensitivity_summary.md.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import score_creators as sc

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "outputs" / "creators"

COMPONENTS = sc.COMPONENTS                 # [evidence_fit, audience_response, sponsored_fit]
W = sc.W
SEED = sc.SEED
DRAWS = sc.DRAWS
SPON_MIN_POSTS = sc.SPON_MIN_POSTS
NEUTRAL = sc.NEUTRAL

LABEL = ("post-hoc sensitivity, not pre-registered; the frozen result in "
         "creator_scores.csv remains the primary ranking")
MOTIVATION = "CR-09's sponsored_fit ratio rests on 3 non-sponsored posts"

_summary: list[str] = []


def line(text: str = "") -> None:
    _summary.append(text)


def rank_desc(comp: pd.Series) -> pd.Series:
    """Rank by composite descending, ties broken by creator_id ascending."""
    order = (comp.rename_axis("creator_id").rename("comp").reset_index()
             .sort_values(["comp", "creator_id"], ascending=[False, True])
             .reset_index(drop=True))
    order["rank"] = np.arange(1, len(order) + 1)
    return order.set_index("creator_id")["rank"]


def load_window_posts() -> tuple[pd.DataFrame, pd.Timestamp, pd.Timestamp]:
    posts = pd.read_csv(DATA_DIR / "creator_posts.csv")
    posts["posted_on"] = pd.to_datetime(posts["posted_on"])
    anchor = posts["posted_on"].max()
    start = anchor - pd.DateOffset(months=sc.LENGTH_MONTHS)
    win = posts[(posts["posted_on"] >= start) & (posts["posted_on"] <= anchor)]
    return win, start, anchor


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frozen = pd.read_csv(OUT_DIR / "creator_scores.csv").set_index("creator_id")
    win, start, anchor = load_window_posts()
    ids = sorted(frozen.index.tolist())

    ev = frozen["evidence_fit_score"]
    ar = frozen["audience_response_score"]
    sf = frozen["sponsored_fit_score"]

    # ---- Part 1: alternate composites from stored component scores ---------
    w_ev, w_ar, w_sf = W["evidence_fit"], W["audience_response"], W["sponsored_fit"]

    comp_frozen = w_ev * ev + w_ar * ar + w_sf * sf

    # A: drop sponsored_fit, renormalise the other two weights.
    tot = w_ev + w_ar
    comp_A = (w_ev / tot) * ev + (w_ar / tot) * ar

    # B: sponsored_fit neutral 0.5 for everyone.
    comp_B = w_ev * ev + w_ar * ar + w_sf * NEUTRAL

    # C: sponsored_fit also needs >= SPON_MIN_POSTS non-sponsored posts with plays.
    nonspon_with_plays = {}
    for cr in frozen.index:
        cp = win[win["creator_id"] == cr]
        ns = cp[(cp["is_sponsored"] == "no") & cp["plays"].notna() & (cp["plays"] > 0)]
        nonspon_with_plays[cr] = int(len(ns))
    n_ns_plays = pd.Series(nonspon_with_plays)
    status_C = pd.Series(
        np.where((frozen["sponsored_fit_status"] == "ok")
                 & (n_ns_plays >= SPON_MIN_POSTS), "ok", "insufficient"),
        index=frozen.index,
    )
    sf_C = sc.percentile_scores(frozen["sponsored_fit_raw"], status_C)
    comp_C = w_ev * ev + w_ar * ar + w_sf * sf_C

    scenarios = {"frozen": comp_frozen, "A": comp_A, "B": comp_B, "C": comp_C}
    ranks = {name: rank_desc(c) for name, c in scenarios.items()}
    top5 = {name: (ranks[name] <= 5) for name in scenarios}

    def classify(cr: str) -> str:
        hits = [bool(top5[name][cr]) for name in scenarios]
        if all(hits):
            return "all"
        return "some" if any(hits) else "none"

    sens_rows = []
    for cr in frozen.index:
        sens_rows.append({
            "creator_id": cr, "handle": frozen.loc[cr, "handle"],
            "composite_frozen": round(float(comp_frozen[cr]), 6),
            "rank_frozen": int(ranks["frozen"][cr]),
            "composite_A": round(float(comp_A[cr]), 6), "rank_A": int(ranks["A"][cr]),
            "composite_B": round(float(comp_B[cr]), 6), "rank_B": int(ranks["B"][cr]),
            "composite_C": round(float(comp_C[cr]), 6), "rank_C": int(ranks["C"][cr]),
            "n_nonsponsored_with_plays": int(n_ns_plays[cr]),
            "sponsored_fit_status_C": status_C[cr],
            "sponsored_fit_score_C": round(float(sf_C[cr]), 6),
            "top5_frozen": bool(top5["frozen"][cr]),
            "top5_A": bool(top5["A"][cr]), "top5_B": bool(top5["B"][cr]),
            "top5_C": bool(top5["C"][cr]),
            "top5_class": classify(cr),
        })
    sens = pd.DataFrame(sens_rows).sort_values("rank_frozen").reset_index(drop=True)
    sens.to_csv(OUT_DIR / "sensitivity.csv", index=False)

    # ---- Part 2: post-sampling uncertainty (bootstrap) ---------------------
    posts_by_creator = {cr: win[win["creator_id"] == cr].reset_index(drop=True)
                        for cr in ids}
    rng = np.random.default_rng(SEED)
    top5_counts = {cr: 0 for cr in ids}
    best_rank = {cr: len(ids) for cr in ids}
    worst_rank = {cr: 1 for cr in ids}

    for _ in range(DRAWS):
        raw = {c: {} for c in COMPONENTS}
        status = {c: {} for c in COMPONENTS}
        for cr in ids:                      # fixed order -> reproducible draws
            cp = posts_by_creator[cr]
            n = len(cp)
            sample = cp.iloc[rng.integers(0, n, size=n)]
            comp = sc.creator_components(sample)
            for c in COMPONENTS:
                raw[c][cr] = comp[f"{c}_raw"]
                status[c][cr] = comp[f"{c}_status"]
        scores = {}
        for c in COMPONENTS:
            scores[c] = sc.percentile_scores(
                pd.Series(raw[c]), pd.Series(status[c])
            )
        comp_b = sum(W[c] * scores[c] for c in COMPONENTS)
        r = rank_desc(comp_b)
        for cr in ids:
            best_rank[cr] = min(best_rank[cr], int(r[cr]))
            worst_rank[cr] = max(worst_rank[cr], int(r[cr]))
            if r[cr] <= 5:
                top5_counts[cr] += 1

    boot = pd.DataFrame({
        "creator_id": ids,
        "handle": [frozen.loc[cr, "handle"] for cr in ids],
        "top5_share": [round(top5_counts[cr] / DRAWS, 4) for cr in ids],
        "best_rank": [best_rank[cr] for cr in ids],
        "worst_rank": [worst_rank[cr] for cr in ids],
    }).sort_values("top5_share", ascending=False).reset_index(drop=True)
    boot.to_csv(OUT_DIR / "bootstrap_top5.csv", index=False)

    write_summary(sens, boot, start, anchor, len(win))

    print("Wrote to", OUT_DIR)
    for p in ["sensitivity.csv", "bootstrap_top5.csv", "sensitivity_summary.md"]:
        print(" -", p)


def write_summary(sens, boot, start, anchor, n_window_posts) -> None:
    n_cre = len(sens)
    part1 = len(["frozen", "A", "B", "C"]) * n_cre
    part2 = DRAWS * n_cre

    line(f"# Creator ranking — {LABEL}")
    line()
    line(f"Motivation: {MOTIVATION}. The frozen ranking in creator_scores.csv is "
         f"unchanged; this file only probes its sensitivity. Ranks only — no five "
         f"are selected, no causal language.")
    line()
    line(f"Window: {start.date()} to {anchor.date()} inclusive "
         f"({sc.LENGTH_MONTHS} months). Posts in window: n={n_window_posts}. "
         f"Creators: n={n_cre}. All weights, floors, seed and draw count reused "
         f"from config/weights.yaml via score_creators.")
    line()
    line("## Comparisons run")
    line()
    line(f"Total: **{part1 + part2}** = Part 1: 4 scenarios x {n_cre} creators "
         f"({part1} composites) + Part 2: {DRAWS} resamples x {n_cre} creators "
         f"({part2} composite recomputations, seed {SEED}).")
    line()

    line("## Part 1 — alternate composites (ranks of all 20)")
    line()
    line("Scenarios: frozen (0.40/0.35/0.25); A drop sponsored_fit, other two "
         "weights renormalised; B sponsored_fit neutral 0.5 for all; C "
         f"sponsored_fit also needs >={SPON_MIN_POSTS} non-sponsored posts with "
         "plays, else neutral 0.5 (re-ranked among the reduced pool).")
    line()
    for r in sens.itertuples():
        line(f"- **{r.creator_id}** ({r.handle}): ranks frozen={r.rank_frozen}, "
             f"A={r.rank_A}, B={r.rank_B}, C={r.rank_C}; top5={r.top5_class} "
             f"(C sponsored_fit: {r.sponsored_fit_status_C}, "
             f"n_nonsponsored_with_plays={r.n_nonsponsored_with_plays})")
    line()
    for cls in ("all", "some", "none"):
        members = sens[sens["top5_class"] == cls]["creator_id"].tolist()
        line(f"- top5 under {cls} four: {len(members)} creator(s)"
             + (f" — {', '.join(members)}" if members else ""))
    line()

    line(f"## Part 2 — post-sampling uncertainty ({DRAWS} resamples, seed {SEED})")
    line()
    line("Window posts resampled with replacement within each creator (same n), "
         "all three components, percentile ranks and the frozen-weight composite "
         "recomputed each draw. Share of resamples in the top 5, and rank range.")
    for r in boot.itertuples():
        line(f"- {r.creator_id} ({r.handle}): top5 in {r.top5_share:.1%} of "
             f"{DRAWS} resamples; rank range {r.best_rank}-{r.worst_rank}")
    line()
    line("Full detail: sensitivity.csv, bootstrap_top5.csv.")

    (OUT_DIR / "sensitivity_summary.md").write_text(
        "\n".join(_summary) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
