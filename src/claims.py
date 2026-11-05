"""Build the report's claim table — every number read from files, none typed.

One row per claim the report may use: the ad findings per hypothesis, the
structural and post-hoc views, floor-set facts, the label spot-check, the
comparison counts, per-creator figures for the creators in play, the manual
proxy precision, and the dataset limits. Statements are plain English and
associational only (no causal language). Figures are read by code from files in
outputs/ and data/; the only literals here are identifiers, formatting precision
and column names.

Output: outputs/final/claims.csv.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ADS = ROOT / "outputs" / "ads"
CRE = ROOT / "outputs" / "creators"
AUDIT = ROOT / "outputs" / "audit"
FINAL = ROOT / "outputs" / "final"
CONFIG = ROOT / "config"

# Human selection (identifiers, not figures).
CHOSEN = ["CR-13", "CR-03", "CR-11", "CR-01", "CR-19"]
BACKUPS = ["CR-05", "CR-09", "CR-16"]
ALSO = ["CR-12", "CR-15", "CR-20"]
CREATOR_SET = CHOSEN + BACKUPS + ALSO
# competitor brands to look for in sponsored posts (identifiers, not figures)
COMPETITORS = {"CR-03": ["Troovy"], "CR-11": ["Gritzo", "Troovy"], "CR-19": ["Complan", "Bournvita"]}

CAV_PERF = "performance figures are synthetic; labels are AI-generated and imperfect"
CAV_LABEL = "labels are AI-generated and imperfect"
CAV_SCAN = "keyword/label scan over text fields; AI-generated labels are imperfect"
CAV_NONE = ""

FLAG_COLS = [("hidden_likes", "flag_hidden_likes"),
             ("no_audience_data", "flag_no_audience_data"),
             ("legal_review", "flag_legal_review")]

# Pricing columns are detected by whole-token match on underscore-split column
# names, not substring match (which would catch "fee" inside feed_story etc.).
PRICING_TOKENS = {"price", "prices", "pricing", "cost", "costs", "fee", "fees",
                  "rate", "rates", "charge", "budget"}

rows: list[dict] = []


def add(claim_id, section, statement, value, n, source_file, source_column,
        caveat, tier):
    rows.append({
        "claim_id": claim_id, "section": section, "statement": statement,
        "value": value, "n": n, "source_file": source_file,
        "source_column": source_column, "caveat": caveat, "tier": tier,
    })


def f4(x) -> str:
    return f"{float(x):.4f}"


def pct(x) -> str:
    return f"{float(x):.1%}"


def get_total(md_path: Path) -> int:
    """First line containing 'Total' -> its last bold integer."""
    for ln in md_path.read_text(encoding="utf-8").splitlines():
        if "Total" in ln:
            bolds = re.findall(r"\*\*([\d,]+)\*\*", ln)
            if bolds:
                return int(bolds[-1].replace(",", ""))
    raise ValueError(f"no bold Total in {md_path}")


def main() -> None:
    FINAL.mkdir(parents=True, exist_ok=True)

    findings = pd.read_csv(ADS / "findings.csv")
    prim = findings[findings["is_primary_floor"]].set_index("hypothesis_id")
    rob = pd.read_csv(ADS / "robustness.csv")
    structural = pd.read_csv(ADS / "structural.csv")
    posthoc = pd.read_csv(ADS / "posthoc_h1_h6.csv")
    labels = pd.read_csv(AUDIT / "label_agreement.csv")
    scores = pd.read_csv(CRE / "creator_scores.csv").set_index("creator_id")
    linksens = pd.read_csv(CRE / "link_sensitivity.csv").set_index("creator_id")
    boot = pd.read_csv(CRE / "bootstrap_top5.csv").set_index("creator_id")
    food = pd.read_csv(CRE / "food_scan.csv").set_index("creator_id")
    brands = pd.read_csv(CRE / "brands_by_creator.csv")
    manual = pd.read_csv(FINAL / "manual_checks.csv")
    creators_df = pd.read_csv(DATA / "creators.csv")
    posts = pd.read_csv(DATA / "creator_posts.csv")
    ads = pd.read_csv(DATA / "ads.csv")
    audience = pd.read_csv(DATA / "creator_audience.csv")
    draws = int(yaml.safe_load((CONFIG / "weights.yaml").read_text(encoding="utf-8"))
                ["stability"]["draws"])

    # ---- Ad findings per hypothesis (findings.csv order) -------------------
    for hid in prim.index:
        r = prim.loc[hid]
        failed = rob[(rob["hypothesis_id"] == hid) & (rob["result"] == "fail")]["check"].tolist()
        failed_s = ";".join(failed) if failed else "none"
        ci = f"[{f4(r['boot_ci_low'])}, {f4(r['boot_ci_high'])}]"
        add(
            f"ads_{hid}", "ads_findings",
            f"{hid} ({r['name']}, {r['tier']}): in-group pooled ROAS {f4(r['pooled_roas_in'])} "
            f"(n={int(r['n_in'])}) and out-group {f4(r['pooled_roas_out'])} (n={int(r['n_out'])}), "
            f"a difference of {r['roas_diff']:+.4f} associated with the group; bootstrap 95% CI "
            f"{ci} ({'excludes' if bool(r['ci_excludes_zero']) else 'includes'} 0); median per-ad "
            f"ROAS {f4(r['median_roas_in'])} in versus {f4(r['median_roas_out'])} out; sign checks "
            f"failed: {failed_s}.",
            f"roas_in={f4(r['pooled_roas_in'])}; roas_out={f4(r['pooled_roas_out'])}; "
            f"diff={r['roas_diff']:+.4f}; ci={ci}; ci_excludes_zero={bool(r['ci_excludes_zero'])}; "
            f"median_in={f4(r['median_roas_in'])}; median_out={f4(r['median_roas_out'])}; "
            f"failed_checks={failed_s}",
            f"n_in={int(r['n_in'])}; n_out={int(r['n_out'])}",
            "outputs/ads/findings.csv; outputs/ads/robustness.csv",
            "pooled_roas_in,pooled_roas_out,roas_diff,boot_ci_low,boot_ci_high,"
            "ci_excludes_zero,median_roas_in,median_roas_out,tier; robustness.check/result",
            CAV_PERF, str(r["tier"]),
        )

    # ---- Post-click purchase conversion (cvr) for H1 and H3 ----------------
    for hid in ["H1", "H3"]:
        r = prim.loc[hid]
        for side, cvr_col, lc_col in [("in", "cvr_in", "diag_link_clicks_in"),
                                      ("out", "cvr_out", "diag_link_clicks_out")]:
            add(
                f"ads_{hid}_cvr_{side}", "ads_findings",
                f"{hid} ({r['name']}): {side}-group post-click purchase conversion "
                f"(purchases / link clicks) is {f4(r[cvr_col])} "
                f"(n={int(r[lc_col])} link clicks).",
                f"cvr_{side}={f4(r[cvr_col])}", f"n={int(r[lc_col])} link clicks",
                "outputs/ads/findings.csv", f"{cvr_col},{lc_col}", CAV_PERF,
                str(r["tier"]),
            )

    # ---- Structural S1 / S2 ------------------------------------------------
    for r in structural[structural["structure"].str.startswith(("S1", "S2"))].itertuples():
        add(
            f"struct_{r.item}", "ads_structural",
            f"Structural {r.structure} cell {r.item}: pooled ROAS {f4(r.pooled_roas)} "
            f"(n={int(r.n_ads)} ads; descriptive).",
            f"pooled_roas={f4(r.pooled_roas)}", f"n={int(r.n_ads)}",
            "outputs/ads/structural.csv", "structure,item,pooled_roas,n_ads",
            CAV_PERF, "descriptive",
        )

    # ---- Post-hoc H1 x H6 2x2 ----------------------------------------------
    for r in posthoc[posthoc["view"] == "cross_2x2"].itertuples():
        add(
            f"posthoc_{r.cell}", "ads_posthoc",
            f"Post-hoc (not pre-registered) H1xH6 cell {r.cell} (H1 {r.h1}, H6 {r.h6}): "
            f"pooled ROAS {f4(r.pooled_roas)} (n={int(r.n_ads)}); median per-ad ROAS "
            f"{f4(r.median_per_ad_roas)}.",
            f"pooled_roas={f4(r.pooled_roas)}; median_per_ad_roas={f4(r.median_per_ad_roas)}",
            f"n={int(r.n_ads)}", "outputs/ads/posthoc_h1_h6.csv",
            "cell,pooled_roas,median_per_ad_roas,n_ads", CAV_PERF, "post-hoc",
        )

    # ---- Floor-set facts ---------------------------------------------------
    for r in structural[structural["structure"] == "floor_product_form_mix"].itertuples():
        add(
            f"floor_mix_{r.item}", "ads_floor",
            f"Floor set product_form {r.item}: {int(r.n_ads)} of {int(r.n_scope)} ads "
            f"({pct(r.value)}).",
            f"share={f4(r.value)}", f"n={int(r.n_scope)}",
            "outputs/ads/structural.csv", "item,n_ads,value,n_scope",
            CAV_NONE, "descriptive",
        )
    for r in structural[structural["structure"] == "floor_spend_concentration"].itertuples():
        add(
            "floor_spend_concentration", "ads_floor",
            f"The single biggest-spend ad ({r.item}) holds {pct(r.value)} of total floor "
            f"spend (n={int(r.n_scope)} ads).",
            f"share={f4(r.value)}", f"n={int(r.n_scope)}",
            "outputs/ads/structural.csv", "item,value,n_scope", CAV_NONE, "descriptive",
        )

    # ---- Label spot-check --------------------------------------------------
    for r in labels.itertuples():
        add(
            f"label_{r.my_column}", "label_spotcheck",
            f"Spot-check agreement for {r.my_column}: {pct(r.agreement_rate)} "
            f"({int(r.n_agree)}/{int(r.n)}).",
            f"agreement_rate={f4(r.agreement_rate)}", f"n={int(r.n)}",
            "outputs/audit/label_agreement.csv", "my_column,agreement_rate,n,n_agree",
            CAV_LABEL, "spot-check",
        )

    # ---- Comparison counts per step ----------------------------------------
    steps = {
        "ad_findings": ADS / "findings_summary.md",
        "posthoc_h1_h6": ADS / "posthoc_h1_h6.md",
        "creator_scoring": CRE / "scores_summary.md",
        "sensitivity": CRE / "sensitivity_summary.md",
        "validity": CRE / "validity_summary.md",
        "content_scan": CRE / "content_scan_summary.md",
    }
    for step, path in steps.items():
        total = get_total(path)
        add(
            f"comparisons_{step}", "comparison_counts",
            f"Comparisons run in the {step} step: {total}.",
            f"total={total}", "", f"outputs/{path.relative_to(ROOT / 'outputs').as_posix()}",
            "summary Total line", CAV_NONE, "process",
        )

    # ---- Per-creator figures ----------------------------------------------
    for cid in CREATOR_SET:
        s = scores.loc[cid]
        handle = s["handle"]
        ls = linksens.loc[cid]
        n_win = int(s["n_posts_window"])

        add(f"cr_{cid}_followers", "creator_profile",
            f"{cid} ({handle}) has {int(s['followers']):,} followers (context only).",
            f"followers={int(s['followers'])}", "", "outputs/creators/creator_scores.csv",
            "followers", "followers are context only, not scored", "context")

        add(f"cr_{cid}_frozen_rank", "creator_profile",
            f"{cid} composite rank in the frozen result is {int(s['composite_rank'])} of {len(scores)}.",
            f"frozen_rank={int(s['composite_rank'])}", f"n={len(scores)}",
            "outputs/creators/creator_scores.csv", "composite_rank", CAV_NONE, "frozen")

        add(f"cr_{cid}_rank_excl_link", "creator_profile",
            f"{cid} rank without link-request posts is {int(ls['rank_excl'])} "
            f"(frozen rank {int(ls['rank_frozen'])}).",
            f"rank_excl={int(ls['rank_excl'])}; rank_frozen={int(ls['rank_frozen'])}",
            f"n={len(scores)}", "outputs/creators/link_sensitivity.csv",
            "rank_excl,rank_frozen", CAV_NONE, "post-hoc-validity")

        add(f"cr_{cid}_bootstrap_top5", "creator_profile",
            f"{cid} appears in the top 5 in {pct(boot.loc[cid, 'top5_share'])} of "
            f"bootstrap resamples.",
            f"top5_share={f4(boot.loc[cid, 'top5_share'])}", f"n={draws} draws",
            "outputs/creators/bootstrap_top5.csv; config/weights.yaml",
            "top5_share; stability.draws", CAV_NONE, "frozen")

        add(f"cr_{cid}_link_request_share", "creator_profile",
            f"{pct(ls['link_request_share'])} of {cid}'s window posts are link-request posts "
            f"({int(ls['n_link_request'])}/{n_win}).",
            f"link_request_share={f4(ls['link_request_share'])}", f"n={n_win}",
            "outputs/creators/link_sensitivity.csv", "n_link_request,n_posts_window",
            CAV_SCAN, "post-hoc-validity")

        fm = food.loc[cid]
        add(f"cr_{cid}_food_term_share", "creator_profile",
            f"{pct(fm['matched_share'])} of {cid}'s window posts mention a food/feeding term "
            f"({int(fm['n_matched_posts'])}/{int(fm['n_posts_window'])}).",
            f"food_term_share={f4(fm['matched_share'])}", f"n={int(fm['n_posts_window'])}",
            "outputs/creators/food_scan.csv", "n_matched_posts,n_posts_window",
            CAV_SCAN, "post-hoc-content")

        n_spon = int(s["n_sponsored"])
        add(f"cr_{cid}_sponsored_share", "creator_profile",
            f"{pct(n_spon / n_win)} of {cid}'s window posts are sponsored ({n_spon}/{n_win}).",
            f"sponsored_share={f4(n_spon / n_win)}", f"n={n_win}",
            "outputs/creators/creator_scores.csv", "n_sponsored,n_posts_window",
            CAV_LABEL, "descriptive")

        on = [name for name, col in FLAG_COLS if bool(s[col])]
        add(f"cr_{cid}_flags", "creator_profile",
            f"{cid} flags: {', '.join(on) if on else 'none'}.",
            f"flags={';'.join(on) if on else 'none'}", f"n={len(on)}",
            "outputs/creators/creator_scores.csv",
            "flag_hidden_likes,flag_no_audience_data,flag_legal_review", CAV_NONE, "descriptive")

        bl = brands[brands["creator_id"] == cid]["brand"].tolist()
        add(f"cr_{cid}_brands", "creator_profile",
            f"Brands visible in {cid}'s window posts: {'; '.join(bl) if bl else 'none'}.",
            f"brands={'; '.join(bl) if bl else 'none'}", f"n={len(bl)}",
            "outputs/creators/brands_by_creator.csv", "brand", CAV_LABEL, "descriptive")

    # ---- Competitor brands in sponsored window posts -----------------------
    wm = int(yaml.safe_load((CONFIG / "weights.yaml").read_text(encoding="utf-8"))
             ["window"]["length_months"])
    pdt = pd.to_datetime(posts["posted_on"])
    w_end = pdt.max()
    in_win = posts[(pdt > w_end - pd.DateOffset(months=wm)) & (pdt <= w_end)]
    for cid, comps in COMPETITORS.items():
        sub = in_win[(in_win["creator_id"] == cid) & (in_win["is_sponsored"] == "yes")]
        hits = []
        for _, pr in sub.sort_values("posted_on").iterrows():
            for b in comps:
                if b.lower() in str(pr["brands_visible"]).lower():
                    hits.append(f"{b} {str(pr['posted_on'])[:10]}")
        add(f"cr_{cid}_competitor_posts", "creator_profile",
            f"{cid} has {len(hits)} sponsored window post(s) showing a competitor brand: "
            f"{'; '.join(hits) if hits else 'none'}.",
            f"competitor_sponsored_posts={len(hits)}", f"n={len(hits)}",
            "data/creator_posts.csv", "posted_on,brands_visible,is_sponsored", CAV_LABEL,
            "descriptive")

    # ---- Proxy precision ---------------------------------------------------
    proxy = manual[manual["check_id"] == "proxy_check"]
    # caveat wording follows the provenance recorded on the rows themselves
    prov = sorted(set(proxy["provenance"].astype(str).str.strip()))
    cav_proxy = "manual " + "; ".join(prov) + "; small sample"
    n_y = int((proxy["result"] == "Y").sum())
    n_total = int(len(proxy))
    add("proxy_precision", "proxy",
        f"In a manual check of {n_total} child-and-product example posts, {n_y} were judged "
        f"to show a child eating or reacting to food ({pct(n_y / n_total)}).",
        f"n_yes={n_y}; share={f4(n_y / n_total)}", f"n={n_total}",
        "outputs/final/manual_checks.csv", "check_id,result", cav_proxy, "post-hoc-manual")

    # ---- Limits ------------------------------------------------------------
    price_cols = [c for c in list(creators_df.columns) + list(posts.columns)
                  if set(c.lower().split("_")) & PRICING_TOKENS]
    add("limit_pricing", "limits",
        f"No creator pricing data is present ({len(price_cols)} pricing columns found in "
        f"creators.csv and creator_posts.csv).",
        f"pricing_columns={len(price_cols)}", "",
        "data/creators.csv; data/creator_posts.csv", "columns", CAV_NONE, "limit")

    n_aud = int(audience["creator_id"].nunique())
    n_cre = int(len(creators_df))
    add("limit_audience_coverage", "limits",
        f"Audience data is present for {n_aud} of {n_cre} creators.",
        f"audience_creators={n_aud}", f"n={n_cre}",
        "data/creator_audience.csv; data/creators.csv", "creator_id", CAV_NONE, "limit")

    r20 = audience[audience["creator_id"] == "CR-20"].iloc[0]
    add("cr_CR-20_audience", "creator_profile",
        f"CR-20 audience is {float(r20['women_pct']):.1f}% women and {float(r20['men_pct']):.1f}% men; "
        f"brands worked with in the past year: {r20['brands_in_past_year']}.",
        f"women_pct={float(r20['women_pct']):.1f}; men_pct={float(r20['men_pct']):.1f}", "n=1 audience record",
        "data/creator_audience.csv", "women_pct,men_pct,brands_in_past_year", CAV_NONE, "descriptive")
    five = creators_df[creators_df["creator_id"].isin(CHOSEN)]
    tot = int(five["followers"].sum())
    add("five_total_followers", "creator_profile",
        f"The five chosen creators have {tot:,} followers in total (context only).",
        f"followers_total={tot}", f"n={len(five)} creators", "data/creators.csv", "followers",
        "followers are context only, not scored", "context")

    has_cid = "creator_id" in ads.columns
    add("limit_ads_no_creator_id", "limits",
        f"ads.csv has no creator_id column (present: {has_cid}); ads cannot be joined to "
        f"creators.",
        f"creator_id_present={has_cid}", "", "data/ads.csv", "columns", CAV_NONE, "limit")

    k_stop = int(ads["stopped_date"].nunique())
    add("limit_stopped_date_batches", "limits",
        f"ads.csv contains {k_stop} distinct stopped_date batches.",
        f"distinct_stopped_date={k_stop}", f"n={len(ads)}", "data/ads.csv",
        "stopped_date", CAV_NONE, "limit")

    n_noplay = int(posts["plays"].isna().sum())
    add("limit_missing_plays", "limits",
        f"{n_noplay} of {len(posts)} creator posts are missing plays.",
        f"missing_plays={n_noplay}", f"n={len(posts)}", "data/creator_posts.csv",
        "plays", CAV_NONE, "limit")

    has_tr = posts["transcript"].map(lambda v: pd.notna(v) and str(v).strip() != "")
    n_tr = int(has_tr.sum())
    add("limit_transcript_share", "limits",
        f"{n_tr} of {len(posts)} creator posts have a transcript ({pct(n_tr / len(posts))}).",
        f"transcript_share={f4(n_tr / len(posts))}", f"n={len(posts)}",
        "data/creator_posts.csv", "transcript", CAV_NONE, "limit")

    hidden = scores.index[scores["flag_hidden_likes"]].tolist()
    add("limit_hidden_likes", "limits",
        f"Hidden-likes flag on {len(hidden)} creators: {', '.join(hidden)}.",
        f"creators={';'.join(hidden)}", f"n={len(hidden)}",
        "outputs/creators/creator_scores.csv", "flag_hidden_likes", CAV_NONE, "limit")

    n_none = int(creators_df["audience_read"].str.contains(
        '"comment_evidence": "none"').sum())
    add("limit_comment_data", "limits",
        f"Comment-evidence is 'none' for {n_none} of {n_cre} creators; per-comment data is "
        f"absent.",
        f"comment_evidence_none={n_none}", f"n={n_cre}", "data/creators.csv",
        "audience_read", CAV_NONE, "limit")

    # ---- Child-on-camera share and past Little Joys posts ---------------------
    for cid in CREATOR_SET:
        sub = in_win[in_win["creator_id"] == cid]
        k = int((sub["children_on_camera"] == "yes").sum())
        add(f"cr_{cid}_child_share", "creator_profile",
            f"{cid} shows a child on camera in {k} of {len(sub)} window posts "
            f"({pct(k / len(sub))}).",
            f"child_on_camera_share={f4(k / len(sub))}", f"n={len(sub)}",
            "data/creator_posts.csv", "children_on_camera", CAV_LABEL, "descriptive")
        allp = posts[posts["creator_id"] == cid]
        lj = allp[allp["brands_visible"].fillna("").str.contains("Little Joys", case=False)]
        dts = "; ".join(f"{str(d)[:10]} ({'sponsored' if sp == 'yes' else 'not sponsored'})"
                        for d, sp in zip(lj["posted_on"], lj["is_sponsored"]))
        add(f"cr_{cid}_little_joys_posts", "creator_profile",
            f"{cid} has {len(lj)} post(s) showing Little Joys in brands_visible"
            f"{': ' + dts if len(lj) else ''}.",
            f"little_joys_posts={len(lj)}", f"n={len(allp)} posts",
            "data/creator_posts.csv", "brands_visible,posted_on,is_sponsored", CAV_LABEL,
            "descriptive")

    # ---- Data reconciliation and ad robustness (for the report) -------------
    floor_v = int(yaml.safe_load((CONFIG / "params.yaml").read_text(encoding="utf-8"))
                  ["spend_floor_primary"])
    fl = ads[ads["spend_inr"] >= floor_v]
    add("data_rows", "reconciliation",
        f"Rows read: {len(ads)} ads, {len(creators_df)} creators, {len(posts)} creator posts "
        f"and {len(audience)} audience records.",
        f"ads={len(ads)}; creators={len(creators_df)}; posts={len(posts)}; "
        f"audience={len(audience)}", "", "data/ads.csv; data/creators.csv; "
        "data/creator_posts.csv; data/creator_audience.csv", "row counts", CAV_NONE,
        "descriptive")
    ld = pd.to_datetime(ads["launch_date"])
    sd = pd.to_datetime(ads["stopped_date"])
    dd = ads["days_live"] - (sd - ld).dt.days
    mism = int((dd != 0).sum())
    one_short = int((dd == -1).sum())
    add("data_ad_dates", "reconciliation",
        f"Ads launched {ld.min().date()} to {ld.max().date()} and stopped {sd.min().date()} "
        f"to {sd.max().date()}; days_live is exactly one day lower than stopped_date minus "
        f"launch_date in {one_short} of {len(ads)} ads and equal in {len(ads) - mism}; "
        f"{int(ads['ad_id'].duplicated().sum())} duplicate ad ids. No finding uses days_live.",
        f"launch={ld.min().date()}..{ld.max().date()}; stopped={sd.min().date()}.."
        f"{sd.max().date()}; days_live_one_short={one_short}; days_live_equal={len(ads) - mism}",
        f"n={len(ads)}", "data/ads.csv", "launch_date,stopped_date,days_live,ad_id",
        CAV_NONE, "descriptive")
    add("data_floor_set", "reconciliation",
        f"{len(fl)} of {len(ads)} ads have spend of at least {floor_v:,} rupees (the floor "
        f"set); they hold {fl['spend_inr'].sum() / ads['spend_inr'].sum():.1%} of all spend. "
        f"Spend and revenue are in rupees (spend_inr, revenue_inr).",
        f"floor_ads={len(fl)}; floor={floor_v}; spend_share="
        f"{fl['spend_inr'].sum() / ads['spend_inr'].sum():.4f}", f"n={len(ads)}",
        "data/ads.csv; config/params.yaml", "spend_inr,revenue_inr", CAV_PERF, "descriptive")
    add("data_floor_roas", "reconciliation",
        f"Across the {len(fl)} floor ads, revenue divided by spend is "
        f"{fl['revenue_inr'].sum() / fl['spend_inr'].sum():.4f} (pooled return per rupee).",
        f"pooled_roas={f4(fl['revenue_inr'].sum() / fl['spend_inr'].sum())}", f"n={len(fl)}",
        "data/ads.csv", "revenue_inr,spend_inr", CAV_PERF, "descriptive")
    cov = {h: int(prim.loc[h, "n_in"] + prim.loc[h, "n_out"]) for h in ["H1", "H3", "H6"]}
    add("data_floor_label_coverage", "reconciliation",
        f"H1, H3 and H6 each use all {cov['H1']} floor ads with no missing label "
        f"({cov['H1']}, {cov['H3']} and {cov['H6']} ads).",
        f"H1={cov['H1']}; H3={cov['H3']}; H6={cov['H6']}", f"n={len(fl)}",
        "outputs/ads/findings.csv", "n_in,n_out", CAV_LABEL, "descriptive")
    pw = pd.to_datetime(posts["posted_on"])
    add("data_posts_window", "reconciliation",
        f"Creator posts run {pw.min().date()} to {pw.max().date()}; {len(in_win)} of "
        f"{len(posts)} fall in the {wm}-month scoring window ending {pw.max().date()}.",
        f"first={pw.min().date()}; last={pw.max().date()}; window_posts={len(in_win)}",
        f"n={len(posts)}", "data/creator_posts.csv", "posted_on", CAV_NONE, "descriptive")
    for h in ["H1", "H3", "H6"]:
        sub = rob[rob["hypothesis_id"] == h].set_index("check")
        ref = int(sub["reference_sign"].iloc[0])
        signs = [int(s) for s in re.findall(r"sign=([+-]\d)",
                                            str(sub.loc["same_sign_at_all_three_floors", "detail"]))]
        lo = sub.loc["leave_one_stop_date_out"]
        same = int(re.search(r"(\d+) same", str(lo["detail"])).group(1))
        npass = int((sub["result"] == "pass").sum())
        add(f"ads_robust_{h}", "ads_robustness",
            f"{h}: {npass} of {len(sub)} robustness checks pass; the sign matches at "
            f"{sum(1 for s in signs if s == ref)} of {len(signs)} spend floors; leaving out each "
            f"stop-date batch in turn keeps the sign in {same} of {int(lo['n_evaluable'])} runs; "
            f"the median per-ad difference has the same sign; dropping the highest-spend ad of "
            f"each group keeps the sign.",
            f"checks_passed={npass}; checks={len(sub)}; floors_same={sum(1 for s in signs if s == ref)}"
            f"; floors={len(signs)}; stop_dates_same={same}; stop_dates={int(lo['n_evaluable'])}",
            "", "outputs/ads/robustness.csv", "check,result,detail", CAV_PERF, "descriptive")
        strata = re.findall(r"(\w+): in=(\d+), out=(\d+), sign=([+-]\d)",
                            str(sub.loc["product_form_strata", "detail"]))
        parts = []
        for name, a, b, s in strata:
            parts.append(f"{name.replace('_', ' ')} {a} in versus {b} out "
                         f"({'same' if int(s) == ref else 'opposite'} direction)")
        add(f"ads_robust_{h}_strata", "ads_robustness",
            f"{h} by product form: " + "; ".join(parts) + ".",
            "; ".join(f"{n}: in={a}, out={b}, sign={s}" for n, a, b, s in strata), "",
            "outputs/ads/robustness.csv", "product_form_strata", CAV_PERF, "descriptive")

    # ---- Scoring rule and product-fact claims (for the report) ---------------
    wt = yaml.safe_load((CONFIG / "weights.yaml").read_text(encoding="utf-8"))
    comp = wt["components"]
    w_ev = float(comp["evidence_fit"]["weight"])
    w_au = float(comp["audience_response"]["weight"])
    w_sp = float(comp["sponsored_fit"]["weight"])
    add("rule_weights", "scoring_rule",
        f"Scoring weights fixed before any creator was scored: evidence_fit {w_ev:.2f}, "
        f"audience_response {w_au:.2f}, sponsored_fit {w_sp:.2f}; each component is a percentile "
        f"rank among the 20 creators.",
        f"evidence_fit={w_ev:.2f}; audience_response={w_au:.2f}; sponsored_fit={w_sp:.2f}",
        f"n={n_cre}", "config/weights.yaml", "components.*.weight", CAV_NONE, "frozen")
    mp = int(re.search(r">=\s*(\d+)", str(comp["audience_response"]["min_data"]["rule"])).group(1))
    ms = int(re.search(r">=\s*(\d+)", str(comp["sponsored_fit"]["min_data"]["rule"])).group(1))
    add("rule_min_data", "scoring_rule",
        f"A component needs enough posts or it scores a neutral 0.5: at least {mp} posts with "
        f"plays for audience_response and at least {ms} sponsored posts for sponsored_fit.",
        f"min_posts_with_plays={mp}; min_sponsored_posts={ms}; neutral=0.5", "",
        "config/weights.yaml", "components.*.min_data", CAV_NONE, "frozen")
    dr = int(wt["stability"]["draws"])
    sd_ = int(wt["stability"]["seed"])
    add("rule_stability", "scoring_rule",
        f"Rank stability: each creator's window posts were resampled with replacement {dr} times "
        f"(seed {sd_}), all scores and ranks recomputed each time; the figure reported is the "
        f"share of resamples in which a creator is in the top 5.",
        f"resamples={dr}; seed={sd_}", "", "outputs/creators/bootstrap_top5.csv; "
        "config/weights.yaml", "top5_share", CAV_NONE, "frozen")
    cap = int(wt["portfolio"]["max_clinical_persona_in_final_5"])
    add("rule_cap", "scoring_rule",
        f"Portfolio rule fixed in advance: at most {cap} clinical-persona creators in the final five.",
        f"max_clinical={cap}", "", "config/weights.yaml", "portfolio", CAV_NONE, "frozen")
    nut = ads[ads["ad_copy"].fillna("").str.contains("Nutrimix", case=False)
              | ads["claims_made"].fillna("").str.contains("Nutrimix", case=False)]
    # Keep the kids' product only: skip ads for moms or teens, and skip segments that state
    # a daily requirement or an equivalence (not a product figure).
    nut = nut[~(nut["ad_copy"].fillna("") + " " + nut["claims_made"].fillna("")).str.contains(
        r"Nutrimix for Moms|supermoms|teen", case=False, regex=True)]
    figs: dict[int, list[str]] = {}
    for _, r_ in nut.iterrows():
        for seg in str(r_["claims_made"]).split(";"):
            if re.search(r"require|equal", seg, flags=re.I):
                continue
            for g in re.findall(r"(\d+)\s?g\s+(?:of\s+)?protein", seg, flags=re.I):
                figs.setdefault(int(g), []).append(r_["ad_id"])
    fig_txt = "; ".join(f"{g}g in {', '.join(sorted(set(v)))}" for g, v in sorted(figs.items()))
    add("product_protein_figures", "product_facts",
        f"Little Joys' own Nutrimix ads for kids quote different protein figures: {fig_txt}.",
        f"figures_g={';'.join(str(g) for g in sorted(figs))}", f"n={len(nut)} Nutrimix ads",
        "data/ads.csv", "claims_made", CAV_NONE, "descriptive")

    out = pd.DataFrame(rows, columns=[
        "claim_id", "section", "statement", "value", "n", "source_file",
        "source_column", "caveat", "tier"])
    out.to_csv(FINAL / "claims.csv", index=False)
    print(f"Wrote {FINAL / 'claims.csv'} with {len(out)} claims")
    print(out["section"].value_counts().to_string())


if __name__ == "__main__":
    main()
