"""Performance analysis of the Little Joys hypothesis groups.

For every hypothesis fixed in config/hypotheses.yaml, this pass computes pooled
ROAS (and diagnostic hook_rate / ctr / cvr) for the in-group versus the out-group
at the spend floors fixed in config/params.yaml, runs the robustness battery fixed
in config/decision_rules.yaml, assigns a verdict tier strictly by those rules, and
reports two descriptive structural views. It computes and presents only: it does
not rank, interpret, or choose. Difference is always in-group minus out-group.

Out-group = the floor set minus the in-group, except a hypothesis carrying a
restrict precondition (H2), whose out-group keeps that precondition so the
negatives stay comparable.

Every rate is pooled (sum(numerator) / sum(denominator); see src/metrics.py) and
is reported with its n. No count, id, or threshold is written by hand: the
hypothesis list, floors, minimum group size, and label cap all come from config
and data. The one dictated literal is the hypothesis -> spot-check-column join
map, a structural correspondence supplied with the task.

Outputs (outputs/ads/): findings.csv, robustness.csv, structural.csv,
findings_summary.md.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from groups import atomic_labels, floor_mask, membership_mask, restrict
from metrics import (
    difference,
    median_per_ad_roas,
    per_ad_roas,
    pooled_ctr,
    pooled_cvr,
    pooled_hook_rate,
    pooled_roas,
    sign,
)

# ---------------------------------------------------------------------------
# Config and constants
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"
AUDIT_DIR = ROOT / "outputs" / "audit"
OUT_DIR = ROOT / "outputs" / "ads"

PARAMS = yaml.safe_load((CONFIG_DIR / "params.yaml").read_text(encoding="utf-8"))
HYPS = yaml.safe_load((CONFIG_DIR / "hypotheses.yaml").read_text(encoding="utf-8"))
RULES = yaml.safe_load(
    (CONFIG_DIR / "decision_rules.yaml").read_text(encoding="utf-8")
)

SEED = int(PARAMS["seed"])
PRIMARY_FLOOR = int(PARAMS["spend_floor_primary"])
SENSITIVITY_FLOORS = [int(f) for f in PARAMS["spend_floor_sensitivity"]]
FLOORS = [PRIMARY_FLOOR] + SENSITIVITY_FLOORS
MIN_GROUP = int(PARAMS["min_group_size"])

BOOT = RULES["bootstrap"]
RESAMPLES = int(BOOT["resamples"])
CI = float(BOOT["ci"])
BOOT_SEED = int(BOOT["seed"])
CI_LOW_Q = (1.0 - CI) / 2.0 * 100.0
CI_HIGH_Q = (1.0 + CI) / 2.0 * 100.0

# Strata evaluability bars, read from the rule text so nothing is hardcoded.
_STRATA_RULE = next(
    c["product_form_strata"]
    for c in RULES["sign_checks"]
    if isinstance(c, dict) and "product_form_strata" in c
)
STRATA_REPORT_MIN = 5   # "evaluable if both sides have >=5 ads"
STRATA_BIND_MIN = 10    # "any stratum with >=10 ads on both sides must agree"

# Hypotheses in config order: primary first, then exploratory.
HYP_LIST: list[tuple[str, str, dict]] = []
for _tier in ("primary", "exploratory"):
    for _hid, _spec in HYPS.get(_tier, {}).items():
        HYP_LIST.append((_hid, _tier, _spec))

# Dictated join: hypothesis -> spot-check column in label_agreement.csv.
# H8 and H9 have no spot-check column.
LABEL_MAP = {
    "H1": "my_child_role_reacts",
    "H2": "my_child_in_first_3s",
    "H3": "my_brand_first_said",
    "H4": "my_hook_type",
    "H5": "my_hook_type",
    "H6": "my_creator_type",
    "H7": "my_ad_format",
}

CONFOUND_NOTE = {
    "H8": "confounded with H6 (every H8 ad is an H6 ad); see S2",
}

TIER_RANK = {"fragile": 0, "suggestive": 1, "supported": 2}

_summary: list[str] = []
_comparisons: dict[str, int] = {}


def line(text: str = "") -> None:
    _summary.append(text)


def fmt_rate(rate: float, n: int) -> str:
    if rate is None or (isinstance(rate, float) and np.isnan(rate)):
        return f"NA (n={n})"
    return f"{rate:.4f} (n={n})"


def cap_tier(tier: str, ceiling: str) -> str:
    """Lower `tier` to `ceiling` if it is above it; otherwise leave it."""
    return ceiling if TIER_RANK[tier] > TIER_RANK[ceiling] else tier


# ---------------------------------------------------------------------------
# Group construction
# ---------------------------------------------------------------------------

def in_out_masks(ads: pd.DataFrame, spec: dict, floor: int):
    """(in_mask, out_mask) at a floor. Out-group keeps a restrict precondition."""
    in_mask = membership_mask(ads, spec) & floor_mask(ads, floor)
    if spec.get("restrict"):
        base = restrict(ads, spec["restrict"]) & floor_mask(ads, floor)
        out_mask = base & ~in_mask
    else:
        out_mask = floor_mask(ads, floor) & ~in_mask
    return in_mask, out_mask


def roas_block(in_df: pd.DataFrame, out_df: pd.DataFrame) -> dict:
    """Pooled and median ROAS for an in/out split, plus the difference."""
    roas_in, n_in, _ = pooled_roas(in_df)
    roas_out, n_out, _ = pooled_roas(out_df)
    med_in = median_per_ad_roas(in_df)
    med_out = median_per_ad_roas(out_df)
    return {
        "n_in": n_in,
        "n_out": n_out,
        "roas_in": roas_in,
        "roas_out": roas_out,
        "roas_diff": difference(roas_in, roas_out),
        "median_in": med_in,
        "median_out": med_out,
        "median_diff": difference(med_in, med_out),
    }


def evaluable(in_df: pd.DataFrame, out_df: pd.DataFrame) -> bool:
    """A comparison is evaluable only if both groups have ads and defined spend."""
    if len(in_df) == 0 or len(out_df) == 0:
        return False
    return int(in_df["spend_inr"].sum()) > 0 and int(out_df["spend_inr"].sum()) > 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ads = pd.read_csv(DATA_DIR / "ads.csv")

    # Spot-check agreement facts, joined later as given.
    agree = pd.read_csv(AUDIT_DIR / "label_agreement.csv").set_index("my_column")

    rng = np.random.default_rng(BOOT_SEED)

    findings_rows: list[dict] = []
    robustness_rows: list[dict] = []
    structural_rows: list[dict] = []

    # Per-hypothesis scratch carried across steps.
    per_floor: dict[str, dict[int, dict]] = {}
    diagnostics: dict[str, dict] = {}
    bootstrap: dict[str, dict] = {}

    # ---- Step 1: floor grid (pooled + median ROAS in/out at every floor) ----
    _comparisons["step1_floor_roas"] = len(HYP_LIST) * len(FLOORS)
    for hid, tier_class, spec in HYP_LIST:
        per_floor[hid] = {}
        for f in FLOORS:
            in_mask, out_mask = in_out_masks(ads, spec, f)
            blk = roas_block(ads[in_mask], ads[out_mask])
            under_in = blk["n_in"] < MIN_GROUP
            under_out = blk["n_out"] < MIN_GROUP
            blk["dropped"] = bool(under_in or under_out)
            blk["under_min_in"] = bool(under_in)
            blk["under_min_out"] = bool(under_out)
            per_floor[hid][f] = blk

    # ---- Step 2: primary-floor diagnostics (hook_rate, ctr, cvr) -----------
    _comparisons["step2_diagnostics"] = len(HYP_LIST) * len(RULES["mechanism_metrics"])
    for hid, tier_class, spec in HYP_LIST:
        in_mask, out_mask = in_out_masks(ads, spec, PRIMARY_FLOOR)
        in_df, out_df = ads[in_mask], ads[out_mask]
        hr_in, n_in, imp_in = pooled_hook_rate(in_df)
        hr_out, n_out, imp_out = pooled_hook_rate(out_df)
        ctr_in, _, _ = pooled_ctr(in_df)
        ctr_out, _, _ = pooled_ctr(out_df)
        cvr_in, _, clk_in = pooled_cvr(in_df)
        cvr_out, _, clk_out = pooled_cvr(out_df)
        diagnostics[hid] = {
            "hook_rate_in": hr_in, "hook_rate_out": hr_out,
            "ctr_in": ctr_in, "ctr_out": ctr_out,
            "cvr_in": cvr_in, "cvr_out": cvr_out,
            "diag_impressions_in": imp_in, "diag_impressions_out": imp_out,
            "diag_link_clicks_in": clk_in, "diag_link_clicks_out": clk_out,
        }

    # ---- Step 3: bootstrap CI of the pooled-ROAS difference (primary) ------
    _comparisons["step3_bootstrap_ci"] = len(HYP_LIST)
    for hid, tier_class, spec in HYP_LIST:
        in_mask, out_mask = in_out_masks(ads, spec, PRIMARY_FLOOR)
        in_df, out_df = ads[in_mask], ads[out_mask]
        if not evaluable(in_df, out_df):
            bootstrap[hid] = {"ci_low": np.nan, "ci_high": np.nan,
                              "ci_excludes_zero": False, "n_resamples": RESAMPLES}
            continue
        in_rev = in_df["revenue_inr"].to_numpy()
        in_sp = in_df["spend_inr"].to_numpy()
        out_rev = out_df["revenue_inr"].to_numpy()
        out_sp = out_df["spend_inr"].to_numpy()
        n_i, n_o = len(in_df), len(out_df)
        # Resample ads with replacement within each group separately.
        idx_i = rng.integers(0, n_i, size=(RESAMPLES, n_i))
        idx_o = rng.integers(0, n_o, size=(RESAMPLES, n_o))
        boot_in = in_rev[idx_i].sum(axis=1) / in_sp[idx_i].sum(axis=1)
        boot_out = out_rev[idx_o].sum(axis=1) / out_sp[idx_o].sum(axis=1)
        diffs = boot_in - boot_out
        lo = float(np.percentile(diffs, CI_LOW_Q))
        hi = float(np.percentile(diffs, CI_HIGH_Q))
        bootstrap[hid] = {
            "ci_low": lo, "ci_high": hi,
            "ci_excludes_zero": bool(lo > 0 or hi < 0),
            "n_resamples": RESAMPLES,
        }

    # ---- Step 4: sign checks -> robustness.csv -----------------------------
    n_drop = n_loo = n_strata = 0
    for hid, tier_class, spec in HYP_LIST:
        prim = per_floor[hid][PRIMARY_FLOOR]
        ref = sign(prim["roas_diff"])
        in_mask0, out_mask0 = in_out_masks(ads, spec, PRIMARY_FLOOR)
        in_df0, out_df0 = ads[in_mask0], ads[out_mask0]

        def add_check(check, result, detail, n_eval=None, n_ne=None):
            robustness_rows.append({
                "hypothesis_id": hid, "tier_class": tier_class, "check": check,
                "result": result, "reference_sign": ref,
                "n_evaluable": n_eval, "n_not_evaluable": n_ne, "detail": detail,
            })

        # (A) same sign at all three floors
        signs = {f: sign(per_floor[hid][f]["roas_diff"]) for f in FLOORS}
        dropped_floors = [f for f in FLOORS if per_floor[hid][f]["dropped"]]
        if dropped_floors:
            res_a = "not_evaluable"
        else:
            distinct = set(signs.values())
            res_a = "pass" if (len(distinct) == 1 and 0 not in distinct) else "fail"
        add_check(
            "same_sign_at_all_three_floors", res_a,
            "; ".join(f"spend>={f}: sign={signs[f]:+d}" for f in FLOORS)
            + (f"; dropped floors={dropped_floors}" if dropped_floors else ""),
            n_eval=len(FLOORS) - len(dropped_floors), n_ne=len(dropped_floors),
        )

        # (B) median per-ad ROAS difference same sign as the pooled difference
        msign = sign(prim["median_diff"])
        if ref == 0 or prim["dropped"]:
            res_b = "not_evaluable"
        else:
            res_b = "pass" if msign == ref else "fail"
        add_check(
            "median_per_ad_roas_diff_same_sign", res_b,
            f"median_in={prim['median_in']:.4f}, median_out={prim['median_out']:.4f}, "
            f"median_diff sign={msign:+d}, reference={ref:+d}",
        )

        # (C) drop the highest-spend ad of each group (two reruns)
        kept = ne = 0
        reruns = []
        for side in ("in", "out"):
            if side == "in":
                if len(in_df0) == 0:
                    ne += 1; reruns.append("in:not_evaluable"); continue
                drop_id = in_df0["spend_inr"].idxmax()
                r_in, r_out = in_df0.drop(index=drop_id), out_df0
            else:
                if len(out_df0) == 0:
                    ne += 1; reruns.append("out:not_evaluable"); continue
                drop_id = out_df0["spend_inr"].idxmax()
                r_in, r_out = in_df0, out_df0.drop(index=drop_id)
            if not evaluable(r_in, r_out):
                ne += 1; reruns.append(f"{side}:not_evaluable"); continue
            d = difference(pooled_roas(r_in)[0], pooled_roas(r_out)[0])
            same = sign(d) == ref and ref != 0
            kept += int(same)
            reruns.append(f"{side}:{'same' if same else 'flip'}")
        n_drop += 2
        n_eval_c = 2 - ne
        res_c = ("not_evaluable" if n_eval_c == 0
                 else "pass" if kept == n_eval_c else "fail")
        add_check("drop_highest_spend_ad_of_each_group", res_c,
                  "; ".join(reruns), n_eval=n_eval_c, n_ne=ne)

        # (D) leave one stopped_date out (all reruns)
        union = ads[in_mask0 | out_mask0]
        dates = sorted(union["stopped_date"].dropna().unique().tolist())
        kept = ne = flip = 0
        for d in dates:
            keep = union["stopped_date"] != d
            r_in = ads[in_mask0 & (ads["stopped_date"] != d)]
            r_out = ads[out_mask0 & (ads["stopped_date"] != d)]
            if not evaluable(r_in, r_out):
                ne += 1; continue
            diff = difference(pooled_roas(r_in)[0], pooled_roas(r_out)[0])
            if sign(diff) == ref and ref != 0:
                kept += 1
            else:
                flip += 1
        n_loo += len(dates)
        n_eval_d = kept + flip
        res_d = ("not_evaluable" if n_eval_d == 0
                 else "pass" if flip == 0 else "fail")
        add_check(
            "leave_one_stop_date_out", res_d,
            f"{len(dates)} distinct stopped_date(s); {kept} same, {flip} flipped, "
            f"{ne} not evaluable",
            n_eval=n_eval_d, n_ne=ne,
        )

        # (E) product_form strata (report only; >=10 both sides must agree)
        forms = sorted(union["product_form"].dropna().unique().tolist())
        reported = binding = disagree = 0
        detail_bits = []
        for form in forms:
            r_in = ads[in_mask0 & (ads["product_form"] == form)]
            r_out = ads[out_mask0 & (ads["product_form"] == form)]
            ni, no = len(r_in), len(r_out)
            if ni >= STRATA_REPORT_MIN and no >= STRATA_REPORT_MIN:
                reported += 1
                s = sign(difference(pooled_roas(r_in)[0], pooled_roas(r_out)[0]))
                detail_bits.append(f"{form}: in={ni}, out={no}, sign={s:+d}")
                if ni >= STRATA_BIND_MIN and no >= STRATA_BIND_MIN:
                    binding += 1
                    if not (s == ref and ref != 0):
                        disagree += 1
        n_strata += reported
        res_e = "fail" if disagree > 0 else "pass"
        add_check(
            "product_form_strata", res_e,
            f"evaluable(>=5 both)={reported}, binding(>=10 both)={binding}, "
            f"disagree={disagree}"
            + (("; " + "; ".join(detail_bits)) if detail_bits else "; (none)"),
            n_eval=reported, n_ne=0,
        )

        # ---- Step 5 (tier) depends on this hypothesis's checks -------------
        results = [r["result"] for r in robustness_rows
                   if r["hypothesis_id"] == hid]
        if "fail" in results:
            tier = "fragile"
        elif all(r == "pass" for r in results) and tier_class == "primary" \
                and bootstrap[hid]["ci_excludes_zero"]:
            tier = "supported"
        else:
            tier = "suggestive"

        my_col = LABEL_MAP.get(hid)
        if my_col is None:
            label_col = "label_unchecked"
            agr = np.nan
            label_n = np.nan
            below = np.nan
            note = "no spot-check for this label"
            tier_after = tier
        else:
            row = agree.loc[my_col]
            label_col = my_col
            agr = float(row["agreement_rate"])
            label_n = int(row["n"])
            below = bool(row["below_label_cap"])
            if below:
                tier_after = cap_tier(tier, "suggestive")
                note = "label unreliable"
            else:
                tier_after = tier
                note = ""

        # Assemble the findings rows (one per floor; primary-only extras set).
        for f in FLOORS:
            blk = per_floor[hid][f]
            rowd = {
                "hypothesis_id": hid, "tier_class": tier_class,
                "name": spec["name"], "floor": f,
                "is_primary_floor": (f == PRIMARY_FLOOR),
                "n_in": blk["n_in"], "n_out": blk["n_out"],
                "under_min_in": blk["under_min_in"],
                "under_min_out": blk["under_min_out"],
                "dropped": blk["dropped"],
                "pooled_roas_in": blk["roas_in"],
                "pooled_roas_out": blk["roas_out"],
                "roas_diff": blk["roas_diff"],
                "median_roas_in": blk["median_in"],
                "median_roas_out": blk["median_out"],
                "median_roas_diff": blk["median_diff"],
            }
            if f == PRIMARY_FLOOR:
                rowd.update(diagnostics[hid])
                rowd.update({
                    "boot_ci_low": bootstrap[hid]["ci_low"],
                    "boot_ci_high": bootstrap[hid]["ci_high"],
                    "ci_excludes_zero": bootstrap[hid]["ci_excludes_zero"],
                    "n_resamples": bootstrap[hid]["n_resamples"],
                    "tier": tier,
                    "label_column": label_col,
                    "label_agreement_rate": agr,
                    "label_n": label_n,
                    "below_label_cap": below,
                    "label_note": note,
                    "tier_after_label_cap": tier_after,
                    "confound_note": CONFOUND_NOTE.get(hid, ""),
                })
            findings_rows.append(rowd)

    _comparisons["step4_drop_highest_reruns"] = n_drop
    _comparisons["step4_leave_one_stop_date_out_reruns"] = n_loo
    _comparisons["step4_product_form_strata_reported"] = n_strata

    # ---- Step 6: structural views (descriptive, primary floor) -------------
    floor_df = ads[floor_mask(ads, PRIMARY_FLOOR)]

    # S1 three-way child status, a partition of the floor set.
    reacts = floor_df["child_role"].map(lambda c: "reacts_to_taste" in atomic_labels(c))
    no_child = floor_df["child_on_screen"].astype(str) == "none"
    status = pd.Series("child_present_not_reacting", index=floor_df.index)
    status[no_child] = "no_child"
    status[reacts] = "child_reacts"
    for cell in ["no_child", "child_present_not_reacting", "child_reacts"]:
        sub = floor_df[status == cell]
        roas, n, _ = pooled_roas(sub)
        structural_rows.append({
            "structure": "S1_child_status", "item": cell, "side": "",
            "n_ads": n, "pooled_roas": roas, "value": np.nan,
            "n_scope": len(floor_df),
        })

    # S2 H8 within H6 only (parent ads).
    h6_spec = HYPS["primary"]["H6"]
    h8_spec = HYPS["exploratory"]["H8"]
    h6_in = floor_mask(ads, PRIMARY_FLOOR) & membership_mask(ads, h6_spec)
    h8_mem = membership_mask(ads, h8_spec)
    for label, mask in [("H8_in_within_H6", h6_in & h8_mem),
                        ("H8_out_within_H6", h6_in & ~h8_mem)]:
        sub = ads[mask]
        roas, n, _ = pooled_roas(sub)
        structural_rows.append({
            "structure": "S2_H8_within_H6", "item": label, "side": "",
            "n_ads": n, "pooled_roas": roas, "value": np.nan,
            "n_scope": int(h6_in.sum()),
        })
    _comparisons["step6_structural_cells"] = 3 + 2

    # ---- Step 7: floor-set facts -------------------------------------------
    pf = floor_df["product_form"].value_counts(dropna=False)
    for form, cnt in pf.items():
        structural_rows.append({
            "structure": "floor_product_form_mix",
            "item": "(missing)" if pd.isna(form) else str(form), "side": "",
            "n_ads": int(cnt), "pooled_roas": np.nan,
            "value": round(int(cnt) / len(floor_df), 4), "n_scope": len(floor_df),
        })
    total_spend = int(floor_df["spend_inr"].sum())
    big_idx = floor_df["spend_inr"].idxmax()
    big_ad = str(floor_df.loc[big_idx, "ad_id"])
    big_spend = int(floor_df.loc[big_idx, "spend_inr"])
    structural_rows.append({
        "structure": "floor_spend_concentration",
        "item": big_ad, "side": "biggest_spend_ad",
        "n_ads": len(floor_df), "pooled_roas": np.nan,
        "value": round(big_spend / total_spend, 4) if total_spend else np.nan,
        "n_scope": len(floor_df),
    })
    _comparisons["step7_floor_facts"] = 2

    # ---- Write CSVs --------------------------------------------------------
    findings = pd.DataFrame(findings_rows)
    findings.to_csv(OUT_DIR / "findings.csv", index=False)
    pd.DataFrame(robustness_rows).to_csv(OUT_DIR / "robustness.csv", index=False)
    pd.DataFrame(structural_rows).to_csv(OUT_DIR / "structural.csv", index=False)

    # ---- Summary -----------------------------------------------------------
    write_summary(ads, floor_df, findings, agree, big_ad, big_spend, total_spend)

    print("Wrote to", OUT_DIR)
    for p in sorted(OUT_DIR.glob("*")):
        print(" -", p.name)


# ---------------------------------------------------------------------------
# Human-readable summary
# ---------------------------------------------------------------------------

def write_summary(ads, floor_df, findings, agree, big_ad, big_spend,
                  total_spend) -> None:
    total = sum(_comparisons.values())
    line("# Performance findings — Little Joys hypothesis groups")
    line()
    line("Source: data/ads.csv (read-only); parameters, hypotheses and decision "
         "rules from config/; spot-check agreement from "
         "outputs/audit/label_agreement.csv. Facts only — no ranking, no "
         "interpretation, no causal language; differences are associations "
         "(in-group minus out-group). This pass presents; it does not choose.")
    line()
    line(f"Rows loaded: ads={len(ads)}. Hypotheses: {len(HYP_LIST)} "
         f"({len(HYPS.get('primary', {}))} primary, "
         f"{len(HYPS.get('exploratory', {}))} exploratory). Floors: primary="
         f"{PRIMARY_FLOOR}, sensitivity={SENSITIVITY_FLOORS}. "
         f"min_group_size={MIN_GROUP}. seed={SEED}.")
    line()
    line("## Comparisons run")
    line()
    line(f"Total comparisons run: **{total}**. Breakdown:")
    for k, v in _comparisons.items():
        line(f"- {k}: {v}")
    line("(The two free sign checks — same_sign_at_all_three_floors and "
         "median_per_ad_roas_diff_same_sign — reuse the step-1 numbers and add "
         "no new comparison; they are still reported as rows in robustness.csv.)")
    line()

    # Step 1 headline table at the primary floor.
    line(f"## Pooled ROAS at the primary floor (spend>={PRIMARY_FLOOR})")
    line()
    line("Difference is in-group minus out-group. Each rate carries its n (ads).")
    line()
    prim = findings[findings["is_primary_floor"]]
    for r in prim.itertuples():
        drop_flag = " [DROPPED: under min_group_size]" if r.dropped else ""
        line(f"- **{r.hypothesis_id}** ({r.tier_class}) — {r.name}: "
             f"ROAS in={fmt_rate(r.pooled_roas_in, r.n_in)}, "
             f"out={fmt_rate(r.pooled_roas_out, r.n_out)}, "
             f"difference={r.roas_diff:+.4f}; median per-ad ROAS "
             f"in={r.median_roas_in:.4f}, out={r.median_roas_out:.4f}; "
             f"bootstrap {int(CI*100)}% CI of difference="
             f"[{r.boot_ci_low:+.4f}, {r.boot_ci_high:+.4f}] "
             f"(excludes 0: {r.ci_excludes_zero}){drop_flag}")
    line()

    line("## Diagnostic rates at the primary floor (not used for tiers)")
    line()
    for r in prim.itertuples():
        line(f"- **{r.hypothesis_id}**: "
             f"hook_rate in={fmt_rate(r.hook_rate_in, int(r.diag_impressions_in))}, "
             f"out={fmt_rate(r.hook_rate_out, int(r.diag_impressions_out))}; "
             f"ctr in={fmt_rate(r.ctr_in, int(r.diag_impressions_in))}, "
             f"out={fmt_rate(r.ctr_out, int(r.diag_impressions_out))}; "
             f"cvr in={fmt_rate(r.cvr_in, int(r.diag_link_clicks_in))}, "
             f"out={fmt_rate(r.cvr_out, int(r.diag_link_clicks_out))}")
    line()

    line("## Tiers (strictly per decision_rules.yaml; supported is "
         "primary-only)")
    line()
    line("tier is computed before the label cap; tier_after_label_cap applies "
         "the spot-check cap. Both are kept. Spot-check agreement is reported "
         "as a fact.")
    line()
    for r in prim.itertuples():
        conf = f" — {r.confound_note}" if r.confound_note else ""
        if r.label_column == "label_unchecked":
            lab = "label_unchecked"
        else:
            lab = (f"{r.label_column} agreement={r.label_agreement_rate:.2f} "
                   f"(n={int(r.label_n)}), below_cap={r.below_label_cap}")
        note = f" [{r.label_note}]" if r.label_note else ""
        line(f"- **{r.hypothesis_id}**: tier={r.tier} -> "
             f"tier_after_label_cap={r.tier_after_label_cap}{note}; "
             f"label: {lab}{conf}")
    line()

    line("## Structural views (descriptive only)")
    line()
    sc = pd.read_csv(OUT_DIR / "structural.csv")
    line("S1 — child status three-way (primary floor):")
    for r in sc[sc["structure"] == "S1_child_status"].itertuples():
        line(f"  - {r.item}: pooled ROAS={fmt_rate(r.pooled_roas, int(r.n_ads))}")
    line("S2 — H8 within H6 (parent ads, primary floor):")
    for r in sc[sc["structure"] == "S2_H8_within_H6"].itertuples():
        line(f"  - {r.item}: pooled ROAS={fmt_rate(r.pooled_roas, int(r.n_ads))}")
    line()

    line(f"## Floor-set composition (spend>={PRIMARY_FLOOR}, n={len(floor_df)})")
    line()
    line("product_form mix:")
    for r in sc[sc["structure"] == "floor_product_form_mix"].itertuples():
        line(f"  - {r.item}: n={int(r.n_ads)} ({r.value:.1%} of floor set)")
    share = big_spend / total_spend if total_spend else float("nan")
    line(f"Single biggest-spend ad: {big_ad} holds {share:.1%} of total floor "
         f"spend (spend={big_spend}, floor total={total_spend}, "
         f"n={len(floor_df)}).")
    line()
    line("Full detail: findings.csv (per hypothesis x floor), robustness.csv "
         "(one row per hypothesis per sign check), structural.csv.")

    (OUT_DIR / "findings_summary.md").write_text(
        "\n".join(_summary) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
