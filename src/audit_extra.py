"""Supplementary data audit for the Little Joys creator-selection task.

Read-only drill-down into five questions the first audit (src/audit.py) left
open: the systematic days_live off-by-one, per-ad exposure (purchases and
link_clicks), possible hidden likes per creator, label group sizes, and
transcript coverage/placeholders. Writes all findings to outputs/audit/ and a
factual summary to outputs/audit/audit_extra_summary.md.

This script computes and presents only. It does not interpret, rank, or choose,
and it computes no performance metric broken down by label. Every rate it prints
carries its denominator n. No figure is typed by hand: the summary is generated
from the loaded data.
"""

from __future__ import annotations

import random
import re
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

random.seed(42)  # project convention; this audit has no randomness

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "outputs" / "audit"

# A blank stopped_date means the ad was still live on this date (per README).
# days_live is "days run up to 26 Oct 2026".
LIVE_AS_OF = pd.Timestamp("2026-10-26")

# Posts with likes <= this are treated as possible hidden like counts
# (README: hidden likes show as 0 or a very low number).
HIDDEN_LIKES_MAX = 5

# Task 4 fixes this spend floor for the per-value exposure count.
SPEND_FLOOR = 5000

# A value (label or literal cell) backed by fewer than this many ads is thin.
LOW_N = 10

# A transcript shorter than this many characters is flagged as possibly a
# placeholder rather than a real spoken transcript.
SHORT_TRANSCRIPT_CHARS = 100

# Within one transcript, a normalised sentence this long or longer that recurs
# at least this many times is flagged as repeated text.
REPEAT_SEGMENT_MIN_CHARS = 15
REPEAT_SEGMENT_MIN_COUNT = 3

# ads.csv columns to tabulate in section 4.
LABEL_COLUMNS = [
    "child_on_screen", "child_in_first_3s", "child_role", "brand_said_aloud",
    "brand_first_said", "hook_type", "creator_type", "language_mixing",
    "ad_format", "proof_used", "cta_type", "offer", "product_form",
    "demo_shown",
]

MISSING = "(missing)"

# Collected lines for the human-readable summary.
_summary: list[str] = []


def line(text: str = "") -> None:
    _summary.append(text)


def pct(num: int, den: int) -> str:
    """Format a rate with its denominator n, guarding against n == 0."""
    if den == 0:
        return "0/0 (n=0)"
    return f"{num}/{den} = {num / den:.1%} (n={den})"


def write_csv(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT_DIR / name, index=False)


# ---------------------------------------------------------------------------
# 1. days_live mismatch cross-tabs
# ---------------------------------------------------------------------------

def audit_days_live(ads: pd.DataFrame) -> None:
    line("## 1. days_live mismatch cross-tabs")
    line()

    launch = pd.to_datetime(ads["launch_date"], errors="coerce")
    stopped = pd.to_datetime(ads["stopped_date"], errors="coerce")
    expected = (stopped.fillna(LIVE_AS_OF) - launch).dt.days
    diff = (ads["days_live"] - expected).astype("Int64")
    ad_id = ads["ad_id"].astype(str)

    diffs = sorted(int(d) for d in diff.dropna().unique())
    line(f"diff = days_live - expected, where expected = "
         f"(stopped_date or {LIVE_AS_OF.date()}) - launch_date.")
    overall = "; ".join(
        f"diff={d:+d}: {int((diff == d).sum())}" for d in diffs
    )
    line(f"Overall diff distribution (n={int(diff.notna().sum())}): {overall}.")
    line()

    # Dimension definitions: (name, bucket_series, ordered_buckets_or_None).
    stopped_ge_live = stopped >= LIVE_AS_OF
    dims = [
        ("stopped_date_ge_2026-10-26",
         stopped_ge_live.map({True: "True", False: "False"}),
         ["False", "True"]),
        ("stopped_date",
         stopped.dt.date.astype("string"),
         None),
        ("launch_month",
         launch.dt.to_period("M").astype("string"),
         None),
    ]

    rows = []
    for dim_name, bucket_series, ordered in dims:
        buckets = ordered if ordered is not None else sorted(
            bucket_series.dropna().unique(), key=str
        )
        for bucket in buckets:
            bmask = bucket_series == bucket
            for d in diffs:
                m = bmask & (diff == d)
                ids = ad_id[m].tolist()
                rows.append({
                    "dimension": dim_name,
                    "bucket": str(bucket),
                    "diff": d,
                    "n_ads": int(m.sum()),
                    "ad_ids": "; ".join(ids),
                })

    crosstab = pd.DataFrame(
        rows, columns=["dimension", "bucket", "diff", "n_ads", "ad_ids"]
    )
    write_csv(crosstab, "audit_extra_days_live_crosstab.csv")

    for dim_name, _, _ in dims:
        sub = crosstab[crosstab["dimension"] == dim_name]
        line(f"- By {dim_name}:")
        for bucket, g in sub.groupby("bucket", sort=True):
            parts = "; ".join(
                f"diff={int(r.diff):+d}: n={int(r.n_ads)}"
                for r in g.itertuples()
            )
            total = int(g["n_ads"].sum())
            line(f"  - {bucket} (n={total}): {parts}")
        line("  - ad_ids per cell in audit_extra_days_live_crosstab.csv.")
    line()


# ---------------------------------------------------------------------------
# 2. Exposure — purchases and link_clicks
# ---------------------------------------------------------------------------

def audit_exposure(ads: pd.DataFrame) -> None:
    line("## 2. Exposure — purchases and link_clicks per ad")
    line()
    n = len(ads)
    cols = ["purchases", "link_clicks"]
    quantiles = [0.0, 0.10, 0.25, 0.50, 0.75, 0.90, 1.0]

    dist_rows = []
    for c in cols:
        s = ads[c]
        row = {"metric": c, "n": int(s.notna().sum()),
               "mean": round(float(s.mean()), 2)}
        for q in quantiles:
            label = {0.0: "min", 1.0: "max"}.get(q, f"p{int(q * 100)}")
            row[label] = round(float(s.quantile(q)), 2)
        dist_rows.append(row)
    dist_df = pd.DataFrame(dist_rows)
    write_csv(dist_df, "audit_extra_exposure_distributions.csv")
    line("- Per-ad distributions (audit_extra_exposure_distributions.csv):")
    for r in dist_rows:
        line(f"  - {r['metric']}: min={r['min']}, p25={r['p25']}, "
             f"p50={r['p50']}, p75={r['p75']}, p90={r['p90']}, "
             f"max={r['max']}, mean={r['mean']} (n={r['n']}).")

    thresholds = {
        "purchases": [5, 10, 20, 50],
        "link_clicks": [100, 500, 1000],
    }
    thr_rows = []
    line("- Ads meeting exposure thresholds:")
    for col, cuts in thresholds.items():
        for cut in cuts:
            k = int((ads[col] >= cut).sum())
            thr_rows.append({
                "metric": col, "threshold": cut, "n_at_or_above": k,
                "share_at_or_above": round(k / n, 4) if n else 0.0,
                "n_total": n,
            })
            line(f"  - {col} >= {cut}: {pct(k, n)}.")
    write_csv(pd.DataFrame(thr_rows), "audit_extra_exposure_thresholds.csv")
    line()


# ---------------------------------------------------------------------------
# 3. Hidden likes (per creator)
# ---------------------------------------------------------------------------

def audit_hidden_likes(posts: pd.DataFrame) -> None:
    line("## 3. Hidden likes (per creator)")
    line()

    likes = posts["likes"]
    plays = posts["plays"]
    ratio_valid = plays.notna() & (plays > 0) & likes.notna()
    ratio = (likes / plays).where(ratio_valid)

    rows = []
    for cid, grp in posts.groupby("creator_id", sort=True):
        idx = grp.index
        g_likes = likes.loc[idx]
        g_ratio = ratio.loc[idx].dropna()
        n_posts = len(grp)
        n_le5 = int((g_likes <= HIDDEN_LIKES_MAX).sum())
        row = {
            "creator_id": cid,
            "handle": grp["handle"].iloc[0] if "handle" in grp else "",
            "n_posts": n_posts,
            "likes_min": int(g_likes.min()),
            "likes_median": float(g_likes.median()),
            "n_likes_le5": n_le5,
            "share_likes_le5": round(n_le5 / n_posts, 4) if n_posts else 0.0,
            "n_ratio_valid": int(len(g_ratio)),
        }
        for q, label in [(0.0, "min"), (0.25, "p25"), (0.50, "p50"),
                         (0.75, "p75"), (1.0, "max")]:
            row[f"likes_per_play_{label}"] = (
                round(float(g_ratio.quantile(q)), 6) if len(g_ratio) else ""
            )
        rows.append(row)

    by_creator = pd.DataFrame(rows).sort_values("creator_id").reset_index(drop=True)
    write_csv(by_creator, "audit_extra_hidden_likes_by_creator.csv")

    total_posts = len(posts)
    overall_le5 = int((likes <= HIDDEN_LIKES_MAX).sum())
    n_ratio = int(ratio.notna().sum())
    line(f"- Posts with likes <= {HIDDEN_LIKES_MAX}: "
         f"{pct(overall_le5, total_posts)}.")
    line(f"- likes/plays computed only where plays > 0: n={n_ratio} of "
         f"{total_posts} posts ({total_posts - n_ratio} excluded for "
         f"missing or zero plays).")
    line("- Per creator (audit_extra_hidden_likes_by_creator.csv):")
    for r in by_creator.itertuples():
        line(f"  - {r.creator_id} (n_posts={r.n_posts}): likes min="
             f"{r.likes_min}, median={r.likes_median:g}; likes<=5: "
             f"{pct(r.n_likes_le5, r.n_posts)}; likes/play p50="
             f"{r.likes_per_play_p50} (n={r.n_ratio_valid}).")
    line()


# ---------------------------------------------------------------------------
# 4. Label group sizes (ads.csv)
# ---------------------------------------------------------------------------

def _literal_values(series: pd.Series) -> pd.Series:
    return series.where(series.notna(), MISSING).astype(str)


def _atomic_labels(cell) -> list[str]:
    if pd.isna(cell):
        return [MISSING]
    parts = [p.strip() for p in str(cell).split(";")]
    parts = [p for p in parts if p != ""]
    # de-duplicate within a cell so one ad counts once per distinct label
    return sorted(set(parts)) if parts else [MISSING]


def audit_labels(ads: pd.DataFrame) -> None:
    line("## 4. Label group sizes (ads.csv)")
    line()
    n = len(ads)
    high_spend = ads["spend_inr"] >= SPEND_FLOOR

    literal_rows = []
    atomic_rows = []

    for col in LABEL_COLUMNS:
        # --- literal whole-cell counts ---
        lit = _literal_values(ads[col])
        for value, cnt in lit.value_counts(dropna=False).items():
            n_ads = int(cnt)
            n_hi = int((high_spend & (lit == value)).sum())
            literal_rows.append({
                "column": col, "value": value, "n_ads": n_ads,
                f"n_ads_spend_ge_{SPEND_FLOOR}": n_hi,
                "low_n": n_ads < LOW_N,
            })

        # --- atomic split counts (an ad may contribute to several labels) ---
        exploded = ads[col].map(_atomic_labels)
        labels = sorted({lab for labs in exploded for lab in labs}, key=str)
        for lab in labels:
            contains = exploded.map(lambda labs, _l=lab: _l in labs)
            n_ads = int(contains.sum())
            n_hi = int((high_spend & contains).sum())
            atomic_rows.append({
                "column": col, "value": lab, "n_ads": n_ads,
                f"n_ads_spend_ge_{SPEND_FLOOR}": n_hi,
                "low_n": n_ads < LOW_N,
            })

    lit_df = pd.DataFrame(literal_rows)
    atom_df = pd.DataFrame(atomic_rows)
    write_csv(lit_df, "audit_extra_label_counts_literal.csv")
    write_csv(atom_df, "audit_extra_label_counts_atomic.csv")

    line(f"n = {n} ads. Each value row shows n_ads and, in brackets, the count "
         f"with spend_inr >= {SPEND_FLOOR}. Values with n_ads < {LOW_N} are "
         f"flagged [low n].")
    line("Literal = whole-cell string. Atomic = cells split on ';' into single "
         "labels (an ad can contribute to several, so atomic n_ads may sum past "
         f"{n}). Full tables in audit_extra_label_counts_literal.csv and "
         "audit_extra_label_counts_atomic.csv.")
    line()

    hi_col = f"n_ads_spend_ge_{SPEND_FLOOR}"
    for col in LABEL_COLUMNS:
        lit_sub = lit_df[lit_df["column"] == col].sort_values(
            "n_ads", ascending=False
        )
        atom_sub = atom_df[atom_df["column"] == col].sort_values(
            "n_ads", ascending=False
        )
        is_compound = (atom_sub["value"].tolist() != lit_sub["value"].tolist())
        line(f"- **{col}** — {len(lit_sub)} literal value(s), "
             f"{len(atom_sub)} atomic label(s).")

        # Literal: list values at or above LOW_N inline; summarise the thin tail.
        strong = lit_sub[lit_sub["n_ads"] >= LOW_N]
        thin = lit_sub[lit_sub["n_ads"] < LOW_N]
        line("  - literal:")
        for r in strong.itertuples():
            line(f"    - {r.value}: n_ads={r.n_ads} "
                 f"(spend>={SPEND_FLOOR}: {getattr(r, hi_col)})")
        if len(thin):
            thin_ads = int(thin["n_ads"].sum())
            line(f"    - + {len(thin)} value(s) each with n_ads < {LOW_N} "
                 f"[low n], covering {thin_ads} ads (see CSV)")

        # Atomic: list in full only when the column is actually compound;
        # otherwise it equals the literal table and is not repeated.
        if is_compound:
            line("  - atomic:")
            for r in atom_sub.itertuples():
                flag = " [low n]" if r.n_ads < LOW_N else ""
                line(f"    - {r.value}: n_ads={r.n_ads} "
                     f"(spend>={SPEND_FLOOR}: {getattr(r, hi_col)}){flag}")
        else:
            line("  - atomic: identical to literal (no ';'-compound cells).")
    line()


# ---------------------------------------------------------------------------
# 5. Transcripts (per creator)
# ---------------------------------------------------------------------------

def _max_segment_repeat(text: str) -> tuple[int, str]:
    """Return (max repeat count, segment) for the most-repeated long sentence."""
    segments = [s.strip() for s in re.split(r"[.!?।\n]+", text)]
    segments = [s for s in segments if len(s) >= REPEAT_SEGMENT_MIN_CHARS]
    if not segments:
        return 0, ""
    counts = pd.Series(segments).value_counts()
    return int(counts.iloc[0]), str(counts.index[0])


def audit_transcripts(creators: pd.DataFrame, posts: pd.DataFrame) -> None:
    line("## 5. Transcripts (per creator)")
    line()

    tr = posts["transcript"].astype("string").str.strip()
    has_tr = tr.notna() & (tr != "")

    rows = []
    for cid, grp in posts.groupby("creator_id", sort=True):
        idx = grp.index
        n_posts = len(grp)
        n_tr = int(has_tr.loc[idx].sum())
        rows.append({
            "creator_id": cid,
            "handle": grp["handle"].iloc[0] if "handle" in grp else "",
            "n_posts": n_posts,
            "n_with_transcript": n_tr,
            "share_with_transcript": round(n_tr / n_posts, 4) if n_posts else 0.0,
        })
    by_creator = pd.DataFrame(rows).sort_values("creator_id").reset_index(drop=True)
    write_csv(by_creator, "audit_extra_transcripts_by_creator.csv")

    total_posts = len(posts)
    total_tr = int(has_tr.sum())
    line(f"- Posts with a transcript: {pct(total_tr, total_posts)}.")
    line("- Per creator in audit_extra_transcripts_by_creator.csv.")

    # --- placeholder flags over posts that have a transcript ---
    present = posts.loc[has_tr].copy()
    present["txt"] = tr.loc[present.index]
    present["txt_len"] = present["txt"].str.len().astype(int)

    # cross-post duplicates: identical trimmed text on more than one post
    dup_counts = present["txt"].value_counts()
    dup_texts = set(dup_counts[dup_counts > 1].index)

    flag_rows = []
    for r in present.itertuples():
        post_url = getattr(r, "post_url", "")
        text = r.txt
        if r.txt_len < SHORT_TRANSCRIPT_CHARS:
            flag_rows.append({
                "creator_id": r.creator_id, "post_url": post_url,
                "flag": "very_short",
                "detail": f"length={r.txt_len} (< {SHORT_TRANSCRIPT_CHARS})",
            })
        if text in dup_texts:
            flag_rows.append({
                "creator_id": r.creator_id, "post_url": post_url,
                "flag": "repeated_across_posts",
                "detail": f"text appears on {int(dup_counts[text])} posts",
            })
        rep_n, seg = _max_segment_repeat(text)
        if rep_n >= REPEAT_SEGMENT_MIN_COUNT:
            flag_rows.append({
                "creator_id": r.creator_id, "post_url": post_url,
                "flag": "repeated_within_post",
                "detail": f"a sentence recurs {rep_n}x: {seg[:60]!r}",
            })

    flags_df = pd.DataFrame(
        flag_rows, columns=["creator_id", "post_url", "flag", "detail"]
    )
    write_csv(flags_df, "audit_extra_transcript_flags.csv")

    def count_flag(name: str) -> int:
        return int((flags_df["flag"] == name).sum()) if len(flags_df) else 0

    line(f"- Placeholder-looking transcripts (of {total_tr} with text), "
         f"audit_extra_transcript_flags.csv:")
    line(f"  - very short (< {SHORT_TRANSCRIPT_CHARS} chars): "
         f"{count_flag('very_short')}.")
    line(f"  - repeated across posts (identical text on >1 post): "
         f"{count_flag('repeated_across_posts')}.")
    line(f"  - repeated within a post (a sentence >= "
         f"{REPEAT_SEGMENT_MIN_CHARS} chars recurring "
         f">= {REPEAT_SEGMENT_MIN_COUNT}x): "
         f"{count_flag('repeated_within_post')}.")
    line()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ads = pd.read_csv(DATA_DIR / "ads.csv")
    creators = pd.read_csv(DATA_DIR / "creators.csv")
    posts = pd.read_csv(DATA_DIR / "creator_posts.csv")

    line("# Supplementary data audit — Little Joys")
    line()
    line(f"Source: data/ (read-only). Reference live date: {LIVE_AS_OF.date()}. "
         f"Facts only; no interpretation, ranking, or selection. No performance "
         f"metric is computed broken down by label.")
    line()
    line(f"Rows loaded: ads={len(ads)}, creators={len(creators)}, "
         f"creator_posts={len(posts)}.")
    line()
    line("Comparisons run (5 sections): (1) one two-level days_live diff "
         "cross-tabbed on 3 dimensions; (2) 2 distributions + 7 threshold "
         "counts; (3) per-creator likes stats + 1 likes/plays ratio "
         f"distribution; (4) {len(LABEL_COLUMNS)} columns x 2 tables "
         "(literal + atomic); (5) per-creator transcript coverage + 3 "
         "placeholder checks.")
    line()

    audit_days_live(ads)
    audit_exposure(ads)
    audit_hidden_likes(posts)
    audit_labels(ads)
    audit_transcripts(creators, posts)

    (OUT_DIR / "audit_extra_summary.md").write_text(
        "\n".join(_summary) + "\n", encoding="utf-8"
    )

    print("Wrote to", OUT_DIR)
    for p in sorted(OUT_DIR.glob("audit_extra_*")):
        print(" -", p.name)


if __name__ == "__main__":
    main()
