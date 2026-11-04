"""Score the 20 creators against the rules fixed in config/weights.yaml.

Resolves the 12-month window from the data, computes the three weighted
components per creator, converts each to a percentile rank among the creators
with sufficient data for that component, combines them into a composite, and
runs the weight-jitter stability check. It ranks by composite but does not
choose or recommend any five, and uses no causal language.

Every parameter comes from config/weights.yaml: the weights, the window length,
the min-data floors, the seed, the draw count and the jitter bounds (the floors
and jitter bounds are parsed out of the rule strings, since the config is not
edited here). Nothing is typed by hand except column names. Every rate is
reported with its n.

Outputs (outputs/creators/): creator_scores.csv, stability.csv, scores_summary.md.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"
OUT_DIR = ROOT / "outputs" / "creators"

WEIGHTS = yaml.safe_load((CONFIG_DIR / "weights.yaml").read_text(encoding="utf-8"))

# --- config-driven constants (nothing hardcoded) ---------------------------
COMP = WEIGHTS["components"]
COMPONENTS = ["evidence_fit", "audience_response", "sponsored_fit"]
W = {c: float(COMP[c]["weight"]) for c in COMPONENTS}

LENGTH_MONTHS = int(WEIGHTS["window"]["length_months"])
SEED = int(WEIGHTS["stability"]["seed"])
DRAWS = int(WEIGHTS["stability"]["draws"])


def _first_int(text: str) -> int:
    """First integer in a rule string, e.g. 'requires >= 10 posts' -> 10."""
    return int(re.search(r"\d+", str(text)).group())


def _two_floats(text: str) -> tuple[float, float]:
    """The two floats in a jitter string, e.g. 'uniform(0.7, 1.3)' -> (0.7, 1.3)."""
    a, b = re.findall(r"\d+\.\d+", str(text))[:2]
    return float(a), float(b)


AUD_MIN_POSTS = _first_int(COMP["audience_response"]["min_data"]["rule"])
SPON_MIN_POSTS = _first_int(COMP["sponsored_fit"]["min_data"]["rule"])
JITTER_LO, JITTER_HI = _two_floats(WEIGHTS["stability"]["weight_jitter"])

FLAGS = WEIGHTS["flags"]
HIDDEN_LIKES = set(FLAGS["hidden_likes"]["creator_ids"])
NO_AUDIENCE = set(FLAGS["no_audience_data"]["creator_ids"])
LEGAL_REVIEW = set(FLAGS["legal_review_flag"]["creator_ids"])

NEUTRAL = 0.5

_summary: list[str] = []


def line(text: str = "") -> None:
    _summary.append(text)


# ---------------------------------------------------------------------------
# Per-post engagement and per-creator components
# ---------------------------------------------------------------------------

def engagement(df: pd.DataFrame) -> pd.Series:
    """(comments + reshares) / plays over posts with plays; likes never used."""
    pp = df[df["plays"].notna() & (df["plays"] > 0)]
    return (pp["comments"] + pp["reshares"]) / pp["plays"]


def creator_components(posts: pd.DataFrame) -> dict:
    """Raw component values and sufficiency status for one creator's window posts."""
    n_window = int(len(posts))
    with_plays = posts[posts["plays"].notna() & (posts["plays"] > 0)]
    n_with_plays = int(len(with_plays))
    spon = posts[posts["is_sponsored"] == "yes"]
    nonspon = posts[posts["is_sponsored"] == "no"]
    n_spon, n_nonspon = int(len(spon)), int(len(nonspon))

    # evidence_fit: share of window posts with child on camera AND product shown.
    if n_window > 0:
        hits = ((posts["children_on_camera"] == "yes")
                & (posts["product_shown"] == "yes")).sum()
        ev_raw, ev_status = float(hits) / n_window, "ok"
    else:
        ev_raw, ev_status = np.nan, "insufficient"

    # audience_response: median per-post engagement; needs >= AUD_MIN_POSTS with plays.
    if n_with_plays >= AUD_MIN_POSTS:
        ar_raw, ar_status = float(engagement(posts).median()), "ok"
    else:
        ar_raw, ar_status = np.nan, "insufficient"

    # sponsored_fit: median sponsored engagement / median non-sponsored engagement.
    sp_med = engagement(spon).median() if n_spon else np.nan
    ns_med = engagement(nonspon).median() if n_nonspon else np.nan
    if (n_spon >= SPON_MIN_POSTS and pd.notna(sp_med) and pd.notna(ns_med)
            and ns_med != 0):
        sf_raw, sf_status = float(sp_med / ns_med), "ok"
    else:
        sf_raw, sf_status = np.nan, "insufficient"

    return {
        "n_posts_window": n_window,
        "n_posts_with_plays": n_with_plays,
        "n_sponsored": n_spon,
        "n_nonsponsored": n_nonspon,
        "evidence_fit_raw": ev_raw, "evidence_fit_status": ev_status,
        "audience_response_raw": ar_raw, "audience_response_status": ar_status,
        "sponsored_fit_raw": sf_raw, "sponsored_fit_status": sf_status,
    }


def percentile_scores(raw: pd.Series, status: pd.Series) -> pd.Series:
    """Average-rank percentile among sufficient creators, scaled (rank-1)/(m-1).

    Insufficient creators get the neutral 0.5. A lone sufficient creator (m==1)
    also gets 0.5 (the scaling is undefined).
    """
    out = pd.Series(NEUTRAL, index=raw.index, dtype=float)
    ok = status == "ok"
    m = int(ok.sum())
    if m >= 2:
        ranks = raw[ok].rank(method="average", ascending=True)
        out[ok] = (ranks - 1.0) / (m - 1.0)
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    creators = pd.read_csv(DATA_DIR / "creators.csv")
    posts = pd.read_csv(DATA_DIR / "creator_posts.csv")
    posts["posted_on"] = pd.to_datetime(posts["posted_on"])

    # Window: 12 months inclusive, anchored at the latest post date.
    anchor = posts["posted_on"].max()
    start = anchor - pd.DateOffset(months=LENGTH_MONTHS)
    in_window = posts[(posts["posted_on"] >= start) & (posts["posted_on"] <= anchor)]

    # Per-creator component values, keeping all 20 creators (no silent drop).
    rows = []
    for cr in creators["creator_id"]:
        cp = in_window[in_window["creator_id"] == cr]
        comp = creator_components(cp)
        meta = creators[creators["creator_id"] == cr].iloc[0]
        rows.append({
            "creator_id": cr, "handle": meta["handle"],
            "persona": meta["persona"], "followers": int(meta["followers"]),
            **comp,
        })
    df = pd.DataFrame(rows)

    # Percentile score per component, then weighted composite.
    for c in COMPONENTS:
        df[f"{c}_score"] = percentile_scores(df[f"{c}_raw"], df[f"{c}_status"])
    df["composite"] = sum(W[c] * df[f"{c}_score"] for c in COMPONENTS)

    # Composite rank: descending composite, ties broken by creator_id ascending.
    df = df.sort_values(["composite", "creator_id"],
                        ascending=[False, True]).reset_index(drop=True)
    df["composite_rank"] = np.arange(1, len(df) + 1)

    # Flags from the yaml lists (do not affect any score).
    df["flag_hidden_likes"] = df["creator_id"].isin(HIDDEN_LIKES)
    df["flag_no_audience_data"] = df["creator_id"].isin(NO_AUDIENCE)
    df["flag_legal_review"] = df["creator_id"].isin(LEGAL_REVIEW)

    col_order = [
        "creator_id", "handle", "persona", "followers",
        "n_posts_window", "n_posts_with_plays", "n_sponsored", "n_nonsponsored",
        "evidence_fit_raw", "audience_response_raw", "sponsored_fit_raw",
        "evidence_fit_status", "audience_response_status", "sponsored_fit_status",
        "evidence_fit_score", "audience_response_score", "sponsored_fit_score",
        "composite", "composite_rank",
        "flag_hidden_likes", "flag_no_audience_data", "flag_legal_review",
    ]
    df[col_order].to_csv(OUT_DIR / "creator_scores.csv", index=False)

    # --- Stability: jitter the weights, re-rank, track top-5 membership ------
    scores = df.set_index("creator_id")[[f"{c}_score" for c in COMPONENTS]]
    base_w = np.array([W[c] for c in COMPONENTS], dtype=float)
    ids = scores.index.to_numpy()
    score_mat = scores.to_numpy()                      # (20, 3)
    rng = np.random.default_rng(SEED)

    top5_counts = {cr: 0 for cr in ids}
    best_rank = {cr: len(ids) for cr in ids}
    worst_rank = {cr: 1 for cr in ids}
    for _ in range(DRAWS):
        jit = base_w * rng.uniform(JITTER_LO, JITTER_HI, size=len(base_w))
        jit = jit / jit.sum()
        comp = score_mat @ jit
        # Rank descending, ties broken by creator_id ascending (ids are sorted).
        order = pd.DataFrame({"creator_id": ids, "comp": comp}).sort_values(
            ["comp", "creator_id"], ascending=[False, True]
        ).reset_index(drop=True)
        for rank, cr in enumerate(order["creator_id"], start=1):
            best_rank[cr] = min(best_rank[cr], rank)
            worst_rank[cr] = max(worst_rank[cr], rank)
        for cr in order["creator_id"].iloc[:5]:
            top5_counts[cr] += 1

    stab = pd.DataFrame({
        "creator_id": ids,
        "handle": df.set_index("creator_id").loc[ids, "handle"].to_numpy(),
        "top5_share": [round(top5_counts[cr] / DRAWS, 4) for cr in ids],
        "best_rank": [best_rank[cr] for cr in ids],
        "worst_rank": [worst_rank[cr] for cr in ids],
    }).sort_values("top5_share", ascending=False).reset_index(drop=True)
    stab.to_csv(OUT_DIR / "stability.csv", index=False)

    write_summary(df, stab, start, anchor, len(in_window))

    print("Wrote to", OUT_DIR)
    for p in sorted(OUT_DIR.glob("*")):
        print(" -", p.name)


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def write_summary(df, stab, start, anchor, n_window_posts) -> None:
    n_cre = len(df)
    n_component_scores = n_cre * len(COMPONENTS)
    total = n_component_scores + n_cre + DRAWS

    line("# Creator scores — Little Joys creator selection")
    line()
    line("Source: data/creators.csv and data/creator_posts.csv (read-only); all "
         "weights, floors, window length, seed, draw count and jitter bounds from "
         "config/weights.yaml. Ranked by composite. This pass presents and ranks; "
         "it does not choose or recommend any five. No causal language; every rate "
         "carries its n.")
    line()
    line(f"Window: {start.date()} to {anchor.date()} inclusive "
         f"({LENGTH_MONTHS} months, anchored at the latest post date). "
         f"Posts in window: n={n_window_posts}. Creators: n={n_cre}.")
    line()
    line(f"Weights (from config): "
         + ", ".join(f"{c}={W[c]:.2f}" for c in COMPONENTS)
         + f" (sum={sum(W.values()):.2f}). Floors: audience_response needs "
         f">={AUD_MIN_POSTS} posts with plays; sponsored_fit needs "
         f">={SPON_MIN_POSTS} sponsored posts.")
    line()
    line("## Comparisons run")
    line()
    line(f"Total: **{total}** = {n_cre} creators x {len(COMPONENTS)} components "
         f"({n_component_scores} component scores) + {n_cre} composite scores + "
         f"{DRAWS} weight-jitter stability re-rankings (seed {SEED}).")
    line()

    line("## Ranked by composite (no five are selected)")
    line()
    for r in df.itertuples():
        def rate(val, status, n, nlabel):
            if status != "ok":
                return f"insufficient (n={n} {nlabel})"
            return f"{val:.4f} (n={n} {nlabel})"
        ev = rate(r.evidence_fit_raw, r.evidence_fit_status,
                  r.n_posts_window, "window posts")
        ar = rate(r.audience_response_raw, r.audience_response_status,
                  r.n_posts_with_plays, "posts w/ plays")
        sf = rate(r.sponsored_fit_raw, r.sponsored_fit_status,
                  r.n_sponsored, "sponsored")
        line(f"- **{r.composite_rank}. {r.creator_id}** ({r.handle}) — "
             f"composite={r.composite:.4f}; followers={r.followers:,} (context "
             f"only). evidence_fit={ev} [score {r.evidence_fit_score:.3f}]; "
             f"audience_response={ar} [score {r.audience_response_score:.3f}]; "
             f"sponsored_fit={sf} [score {r.sponsored_fit_score:.3f}]. flags: "
             + ", ".join(f for f, on in [
                 ("hidden_likes", r.flag_hidden_likes),
                 ("no_audience_data", r.flag_no_audience_data),
                 ("legal_review", r.flag_legal_review)] if on) or "none")
    line()

    line("## Insufficient components")
    line()
    any_insuff = False
    for c in COMPONENTS:
        bad = df[df[f"{c}_status"] != "ok"]["creator_id"].tolist()
        if bad:
            any_insuff = True
            line(f"- {c}: {len(bad)} creator(s) scored neutral 0.5 — "
                 + ", ".join(bad))
    if not any_insuff:
        line("- none; every creator had sufficient data for all three components.")
    line()

    line(f"## Stability ({DRAWS} draws, seed {SEED})")
    line()
    line(f"Share of draws each creator lands in the top 5 (weights jittered by "
         f"uniform({JITTER_LO}, {JITTER_HI}) then renormalised); best and worst "
         f"rank across draws.")
    for r in stab.itertuples():
        line(f"- {r.creator_id} ({r.handle}): top5 in {r.top5_share:.1%} of "
             f"{DRAWS} draws; rank range {r.best_rank}-{r.worst_rank}")
    line()
    line("Full detail: creator_scores.csv, stability.csv.")

    (OUT_DIR / "scores_summary.md").write_text(
        "\n".join(_summary) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
