"""Data audit for the Little Joys creator-selection task.

Read-only pass over the four source files in data/. Loads each file, checks
schema against the README column guide, checks ads.csv integrity, describes
exposure, summarises creator posts, and reports audience coverage. Writes all
findings to outputs/audit/ and a factual summary to outputs/audit/audit_summary.md.

This script computes and presents only. It does not interpret, rank, or choose.
Every rate it prints carries its denominator n. No figure is typed by hand: the
summary is generated from the loaded data.
"""

from __future__ import annotations

import random
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

# Candidate spend floors only. The user chooses the real floor later.
SPEND_FLOORS = [0, 1000, 5000, 10000, 25000, 50000, 100000]

# Exact column sets listed in the README column guide, per file. Used to
# compute columns that are missing (in guide, absent from CSV) or extra
# (in CSV, not in guide).
README_COLUMNS = {
    "ads.csv": [
        "ad_id", "meta_ad_library_id", "video_url", "launch_date",
        "stopped_date", "days_live", "duration_s", "language", "ad_copy",
        "transcript", "hook_line", "on_screen_text", "claims_made",
        "hook_type", "hook_driver", "hook_delivered_by", "hook_text_on_screen",
        "ad_format", "story_structure", "main_benefit", "performance_style",
        "humour", "creator_type", "creator_gender", "creator_age",
        "people_on_screen", "child_on_screen", "child_age", "child_role",
        "child_in_first_3s", "brand_first_said", "brand_said_aloud",
        "product_form", "product_shown_as", "demo_shown", "proof_used",
        "persuasion", "production", "audio", "music", "captions",
        "language_mixing", "first_frame", "setting", "cta_type", "offer",
        "narratives", "ad_categories", "spend_inr", "impressions",
        "video_3s_views", "thruplays", "link_clicks", "add_to_carts",
        "purchases", "revenue_inr",
    ],
    "creators.csv": [
        "handle", "bio", "followers", "following", "total_posts", "verified",
        "persona", "feed_story", "voice", "language_use", "catchphrases",
        "themes", "format_habits", "what_feels_native",
        "what_would_feel_foreign", "audience_read",
    ],
    "creator_posts.csv": [
        "post_url", "posted_on", "type", "duration_s", "caption", "plays",
        "likes", "comments", "reshares", "content_type", "content_form",
        "topic", "hook_style", "creator_on_camera", "children_on_camera",
        "child_ages", "presenter_age", "presenter_gender", "language",
        "setting", "tone", "product_shown", "is_sponsored", "brands_visible",
        "production_quality_1to5", "audience_signal", "on_screen_text",
        "what_stands_out", "transcript",
    ],
    "creator_audience.csv": [
        "as_of", "women_pct", "men_pct", "age_split", "top_cities",
        "top_countries", "brands_in_past_year",
    ],
}

# Collected lines for the human-readable summary.
_summary: list[str] = []


def line(text: str = "") -> None:
    _summary.append(text)


def pct(num: int, den: int) -> str:
    """Format a rate with its denominator n, guarding against n == 0."""
    if den == 0:
        return f"0/0 (n=0)"
    return f"{num}/{den} = {num / den:.1%} (n={den})"


def write_csv(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT_DIR / name, index=False)


# ---------------------------------------------------------------------------
# 1. Schema
# ---------------------------------------------------------------------------

def audit_schema(frames: dict[str, pd.DataFrame]) -> None:
    line("## 1. Schema")
    line()
    for fname, df in frames.items():
        guide = README_COLUMNS[fname]
        n = len(df)
        rows = []
        for col in df.columns:
            nn = int(df[col].isna().sum())
            rows.append({
                "column": col,
                "dtype": str(df[col].dtype),
                "n_null": nn,
                "pct_null": round(nn / n, 4) if n else 0.0,
                "n_rows": n,
                "in_readme_guide": col in guide,
            })
        schema_df = pd.DataFrame(rows)
        stem = fname.replace(".csv", "")
        write_csv(schema_df, f"schema_{stem}.csv")

        missing = [c for c in guide if c not in df.columns]
        extra = [c for c in df.columns if c not in guide]
        cols_with_nulls = schema_df.loc[schema_df["n_null"] > 0, "column"].tolist()

        line(f"**{fname}** — {n} rows, {df.shape[1]} columns.")
        line(f"- Columns in README guide present: "
             f"{len([c for c in guide if c in df.columns])}/{len(guide)}.")
        line(f"- Missing (in guide, absent from file): "
             f"{', '.join(missing) if missing else 'none'}.")
        line(f"- Extra (in file, not in guide): "
             f"{', '.join(extra) if extra else 'none'}.")
        line(f"- Columns with any nulls: "
             f"{', '.join(cols_with_nulls) if cols_with_nulls else 'none'} "
             f"(per-column counts in schema_{stem}.csv).")
        line()


# ---------------------------------------------------------------------------
# 2. ads.csv integrity
# ---------------------------------------------------------------------------

def audit_ads_integrity(ads: pd.DataFrame) -> None:
    line("## 2. ads.csv integrity")
    line()
    n = len(ads)

    # --- duplicate ad_id ---
    dup_mask = ads["ad_id"].duplicated(keep=False)
    dups = ads.loc[dup_mask, ["ad_id"]].copy()
    write_csv(dups, "ads_duplicate_ad_id.csv")
    line(f"- Duplicate ad_id rows: {int(dup_mask.sum())} "
         f"(distinct ad_id values: {ads['ad_id'].nunique()} of {n}). "
         f"See ads_duplicate_ad_id.csv.")

    # --- dates ---
    launch = pd.to_datetime(ads["launch_date"], errors="coerce")
    stopped = pd.to_datetime(ads["stopped_date"], errors="coerce")
    blank_stopped = int(stopped.isna().sum())
    unparsed_launch = int(launch.isna().sum() - ads["launch_date"].isna().sum())
    unparsed_stopped = int(
        stopped.isna().sum() - ads["stopped_date"].isna().sum()
    )

    date_issues = []

    # stopped before launch (only where both dates present)
    both = launch.notna() & stopped.notna()
    before = both & (stopped < launch)
    for i in ads.index[before]:
        date_issues.append({
            "ad_id": ads.at[i, "ad_id"],
            "issue": "stopped_before_launch",
            "launch_date": ads.at[i, "launch_date"],
            "stopped_date": ads.at[i, "stopped_date"],
            "days_live": ads.at[i, "days_live"],
            "expected_days_live": "",
            "diff": "",
        })

    # days_live mismatch: expected = (stopped or LIVE_AS_OF) - launch
    effective_stop = stopped.fillna(LIVE_AS_OF)
    expected = (effective_stop - launch).dt.days
    valid = launch.notna()
    mismatch = valid & (ads["days_live"] != expected)
    for i in ads.index[mismatch]:
        date_issues.append({
            "ad_id": ads.at[i, "ad_id"],
            "issue": "days_live_mismatch",
            "launch_date": ads.at[i, "launch_date"],
            "stopped_date": ads.at[i, "stopped_date"],
            "days_live": ads.at[i, "days_live"],
            "expected_days_live": int(expected[i]) if pd.notna(expected[i]) else "",
            "diff": int(ads.at[i, "days_live"] - expected[i])
            if pd.notna(expected[i]) else "",
        })

    date_df = pd.DataFrame(date_issues, columns=[
        "ad_id", "issue", "launch_date", "stopped_date", "days_live",
        "expected_days_live", "diff",
    ])
    write_csv(date_df, "ads_date_issues.csv")
    n_before = int(before.sum())
    n_mismatch = int(mismatch.sum())
    line(f"- Blank stopped_date (treated as live on {LIVE_AS_OF.date()}): "
         f"{blank_stopped} of {n}.")
    if unparsed_launch or unparsed_stopped:
        line(f"- Unparseable dates — launch_date: {unparsed_launch}, "
             f"stopped_date: {unparsed_stopped}.")
    line(f"- stopped_date before launch_date: {n_before}.")
    line(f"- days_live inconsistent with dates: {n_mismatch} "
         f"(expected = (stopped_date or {LIVE_AS_OF.date()}) - launch_date). "
         f"See ads_date_issues.csv.")
    if n_mismatch:
        diffs = (ads["days_live"] - expected)[mismatch]
        diff_counts = diffs.value_counts().sort_index()
        parts = "; ".join(
            f"diff={int(d):+d}: {int(c)}" for d, c in diff_counts.items()
        )
        line(f"  - Mismatch diff distribution (recorded minus expected): "
             f"{parts}.")

    # --- funnel ordering ---
    funnel_rows = []

    def check(mask: pd.Series, name: str, a: str, b: str) -> None:
        for i in ads.index[mask]:
            funnel_rows.append({
                "ad_id": ads.at[i, "ad_id"],
                "violation": name,
                "left_col": a,
                "left_value": ads.at[i, a],
                "right_col": b,
                "right_value": ads.at[i, b],
            })

    check(ads["impressions"] < ads["video_3s_views"],
          "impressions >= video_3s_views", "impressions", "video_3s_views")
    check(ads["video_3s_views"] < ads["thruplays"],
          "video_3s_views >= thruplays", "video_3s_views", "thruplays")
    check(ads["impressions"] < ads["link_clicks"],
          "impressions >= link_clicks", "impressions", "link_clicks")
    check(ads["purchases"] > ads["add_to_carts"],
          "purchases <= add_to_carts", "purchases", "add_to_carts")

    funnel_df = pd.DataFrame(funnel_rows, columns=[
        "ad_id", "violation", "left_col", "left_value",
        "right_col", "right_value",
    ])
    write_csv(funnel_df, "ads_funnel_violations.csv")
    if funnel_rows:
        counts = funnel_df["violation"].value_counts()
        parts = "; ".join(f"{k}: {v}" for k, v in counts.items())
        line(f"- Funnel ordering violations: {len(funnel_rows)} ({parts}). "
             f"See ads_funnel_violations.csv.")
    else:
        line("- Funnel ordering violations: 0.")

    # --- revenue > 0 with 0 purchases ---
    rev_no_purch = ads[(ads["revenue_inr"] > 0) & (ads["purchases"] == 0)]
    write_csv(rev_no_purch[["ad_id", "revenue_inr", "purchases"]],
              "ads_revenue_no_purchase.csv")
    line(f"- revenue_inr > 0 with 0 purchases: {len(rev_no_purch)}. "
         f"See ads_revenue_no_purchase.csv.")

    # --- spend == 0 ---
    zero_spend = ads[ads["spend_inr"] == 0]
    write_csv(zero_spend[["ad_id", "spend_inr", "impressions"]],
              "ads_zero_spend.csv")
    line(f"- spend_inr = 0: {len(zero_spend)}. See ads_zero_spend.csv.")
    line()


# ---------------------------------------------------------------------------
# 3. Exposure
# ---------------------------------------------------------------------------

def audit_exposure(ads: pd.DataFrame) -> None:
    line("## 3. Exposure")
    line()
    n = len(ads)
    cols = ["spend_inr", "impressions", "days_live"]
    quantiles = [0.0, 0.10, 0.25, 0.50, 0.75, 0.90, 1.0]
    rows = []
    for c in cols:
        s = ads[c]
        row = {"metric": c, "n": int(s.notna().sum()),
               "mean": round(float(s.mean()), 2)}
        for q in quantiles:
            label = {0.0: "min", 1.0: "max"}.get(q, f"p{int(q * 100)}")
            row[label] = round(float(s.quantile(q)), 2)
        rows.append(row)
    dist_df = pd.DataFrame(rows)
    write_csv(dist_df, "exposure_distributions.csv")
    line("- Distributions of spend_inr, impressions, days_live written to "
         "exposure_distributions.csv. Key values:")
    for row in rows:
        line(f"  - {row['metric']}: min={row['min']}, p50={row['p50']}, "
             f"p90={row['p90']}, max={row['max']}, mean={row['mean']} "
             f"(n={row['n']}).")

    # spend floor counts
    floor_rows = []
    for floor in SPEND_FLOORS:
        at_or_above = int((ads["spend_inr"] >= floor).sum())
        below = n - at_or_above
        floor_rows.append({
            "spend_floor": floor,
            "n_at_or_above": at_or_above,
            "share_at_or_above": round(at_or_above / n, 4) if n else 0.0,
            "n_below": below,
            "share_below": round(below / n, 4) if n else 0.0,
            "n_total": n,
        })
    floor_df = pd.DataFrame(floor_rows)
    write_csv(floor_df, "exposure_spend_floor_counts.csv")
    line("- Ads meeting candidate spend floors (n=%d total):" % n)
    for r in floor_rows:
        line(f"  - spend_inr >= {r['spend_floor']}: "
             f"{pct(r['n_at_or_above'], n)}.")
    line()


# ---------------------------------------------------------------------------
# 4. Creators (posts)
# ---------------------------------------------------------------------------

def audit_creators(creators: pd.DataFrame, posts: pd.DataFrame) -> None:
    line("## 4. Creators (posts)")
    line()

    posted = pd.to_datetime(posts["posted_on"], errors="coerce")
    unparsed_posted = int(posted.isna().sum() - posts["posted_on"].isna().sum())
    posts = posts.assign(_posted=posted)

    has_transcript = posts["transcript"].notna() & (
        posts["transcript"].astype(str).str.strip() != ""
    )
    sponsored = posts["is_sponsored"].astype(str).str.strip().str.lower()

    rows = []
    for cid, grp in posts.groupby("creator_id"):
        handle = grp["handle"].iloc[0] if "handle" in grp else ""
        n_posts = len(grp)
        g_sp = sponsored.loc[grp.index]
        n_yes = int((g_sp == "yes").sum())
        n_no = int((g_sp == "no").sum())
        n_unclear = int((g_sp == "unclear").sum())
        rows.append({
            "creator_id": cid,
            "handle": handle,
            "n_posts": n_posts,
            "posted_on_min": grp["_posted"].min().date()
            if grp["_posted"].notna().any() else "",
            "posted_on_max": grp["_posted"].max().date()
            if grp["_posted"].notna().any() else "",
            "n_with_transcript": int(has_transcript.loc[grp.index].sum()),
            "n_sponsored_yes": n_yes,
            "n_sponsored_no": n_no,
            "n_sponsored_unclear": n_unclear,
            "share_sponsored_yes": round(n_yes / n_posts, 4) if n_posts else 0.0,
            "n_likes_le5": int((grp["likes"] <= HIDDEN_LIKES_MAX).sum()),
        })
    summary_df = pd.DataFrame(rows).sort_values("creator_id").reset_index(drop=True)
    write_csv(summary_df, "creators_posts_summary.csv")

    total_posts = len(posts)
    overall_yes = int((sponsored == "yes").sum())
    overall_tr = int(has_transcript.sum())
    overall_hidden = int((posts["likes"] <= HIDDEN_LIKES_MAX).sum())
    creators_with_posts = posts["creator_id"].nunique()

    line(f"- Creators with at least one post: {creators_with_posts} of "
         f"{len(creators)}.")
    line(f"- Posts total: {total_posts}. Per-creator detail in "
         f"creators_posts_summary.csv.")
    if posts["_posted"].notna().any():
        line(f"- Post date range overall: "
             f"{posts['_posted'].min().date()} to "
             f"{posts['_posted'].max().date()}.")
    if unparsed_posted:
        line(f"- Unparseable posted_on values: {unparsed_posted}.")
    line(f"- Posts with a transcript: {pct(overall_tr, total_posts)}.")
    line(f"- Sponsored posts (is_sponsored = 'yes'): "
         f"{pct(overall_yes, total_posts)}. "
         f"Values yes/no/unclear: {int((sponsored == 'yes').sum())}/"
         f"{int((sponsored == 'no').sum())}/"
         f"{int((sponsored == 'unclear').sum())}.")
    line(f"- Posts with likes <= {HIDDEN_LIKES_MAX} (possible hidden likes): "
         f"{pct(overall_hidden, total_posts)}.")
    line()


# ---------------------------------------------------------------------------
# 5. creator_audience coverage
# ---------------------------------------------------------------------------

def audit_audience(creators: pd.DataFrame, audience: pd.DataFrame) -> None:
    line("## 5. creator_audience coverage")
    line()
    have = audience["creator_id"].tolist()
    all_ids = creators["creator_id"].tolist() if "creator_id" in creators else []
    missing = [c for c in all_ids if c not in have]

    cov_rows = []
    for _, r in creators.iterrows():
        cid = r.get("creator_id", "")
        cov_rows.append({
            "creator_id": cid,
            "handle": r.get("handle", ""),
            "has_audience_data": cid in have,
        })
    cov_df = pd.DataFrame(cov_rows)
    write_csv(cov_df, "creator_audience_coverage.csv")

    line(f"- Creators with audience data: {pct(len(have), len(all_ids))}.")
    line(f"- With data: {', '.join(have) if have else 'none'}.")
    line(f"- Without data: {', '.join(missing) if missing else 'none'}.")
    line("- See creator_audience_coverage.csv.")
    line()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ads = pd.read_csv(DATA_DIR / "ads.csv")
    creators = pd.read_csv(DATA_DIR / "creators.csv")
    posts = pd.read_csv(DATA_DIR / "creator_posts.csv")
    audience = pd.read_csv(DATA_DIR / "creator_audience.csv")

    frames = {
        "ads.csv": ads,
        "creators.csv": creators,
        "creator_posts.csv": posts,
        "creator_audience.csv": audience,
    }

    line("# Data audit — Little Joys")
    line()
    line(f"Source: data/ (read-only). Reference live date: {LIVE_AS_OF.date()}. "
         f"Facts only; no interpretation or recommendations.")
    line()
    line(f"Rows loaded: ads={len(ads)}, creators={len(creators)}, "
         f"creator_posts={len(posts)}, creator_audience={len(audience)}.")
    line()

    audit_schema(frames)
    audit_ads_integrity(ads)
    audit_exposure(ads)
    audit_creators(creators, posts)
    audit_audience(creators, audience)

    (OUT_DIR / "audit_summary.md").write_text(
        "\n".join(_summary) + "\n", encoding="utf-8"
    )

    # Manifest: one line per output file.
    print("Wrote to", OUT_DIR)
    for p in sorted(OUT_DIR.iterdir()):
        print(" -", p.name)


if __name__ == "__main__":
    main()
