"""Cross-structure facts for the Little Joys hypothesis groups.

Read-only pass over ads.csv that describes the structure of the hypothesis
groups fixed in config/ before any performance metric is computed: group sizes
at each candidate spend floor, pairwise overlap between groups, label cross-tabs,
per-group splits by product/launch/stop, date-and-form clustering, and the
purchases distribution of the floor set. Writes all findings to outputs/audit/
with an audit_cross_ prefix and a factual summary to audit_cross_summary.md.

This script computes and presents only. It does not interpret, rank, or choose,
and it computes no performance metric (ROAS, CTR, CPA, hook rate) broken down by
any group. Every rate it prints carries its denominator n. No count is typed by
hand: everything is derived from the loaded data and the config files.
"""

from __future__ import annotations

import random
from itertools import combinations
from pathlib import Path

import pandas as pd
import yaml

# ---------------------------------------------------------------------------
# Constants and config
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"
OUT_DIR = ROOT / "outputs" / "audit"

PARAMS = yaml.safe_load((CONFIG_DIR / "params.yaml").read_text(encoding="utf-8"))
HYPS = yaml.safe_load((CONFIG_DIR / "hypotheses.yaml").read_text(encoding="utf-8"))

SEED = int(PARAMS["seed"])
random.seed(SEED)  # project convention; this pass has no randomness

PRIMARY_FLOOR = int(PARAMS["spend_floor_primary"])
SENSITIVITY_FLOORS = [int(f) for f in PARAMS["spend_floor_sensitivity"]]
FLOORS = [PRIMARY_FLOOR] + SENSITIVITY_FLOORS
MIN_GROUP = int(PARAMS["min_group_size"])

TOP_COMBOS = 15  # clustering: number of launch x stop x form combinations shown

# Hypotheses in config order: primary first, then exploratory. Each entry is
# (id, tier, spec), where spec carries name/column/match/value and optional
# restrict.
HYP_LIST: list[tuple[str, str, dict]] = []
for _tier in ("primary", "exploratory"):
    for _hid, _spec in HYPS.get(_tier, {}).items():
        HYP_LIST.append((_hid, _tier, _spec))

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
# Group membership
# ---------------------------------------------------------------------------

def _atomic_labels(cell) -> set[str]:
    """Split a multi-value cell on ';' into the set of its atomic labels."""
    if pd.isna(cell):
        return set()
    return {p.strip() for p in str(cell).split(";") if p.strip() != ""}


def _restrict_mask(ads: pd.DataFrame, expr: str) -> pd.Series:
    """Parse a simple 'column <op> value' restriction into a boolean mask.

    Supports == and != against the whole cell (as string). Used for H2's
    'child_on_screen != none'.
    """
    for op in ("!=", "=="):
        if op in expr:
            col, val = (s.strip() for s in expr.split(op, 1))
            col_str = ads[col].astype(str)
            return col_str != val if op == "!=" else col_str == val
    raise ValueError(f"unsupported restrict expression: {expr!r}")


def membership_mask(ads: pd.DataFrame, spec: dict) -> pd.Series:
    """Boolean mask for ads in a hypothesis group, ignoring spend floor.

    Applies the optional restrict precondition, then the match rule
    (equals = whole-cell equality; contains = atomic label present).
    """
    mask = pd.Series(True, index=ads.index)
    if spec.get("restrict"):
        mask &= _restrict_mask(ads, spec["restrict"])

    col = ads[spec["column"]]
    value = str(spec["value"])
    if spec["match"] == "equals":
        mask &= col.astype(str) == value
    elif spec["match"] == "contains":
        mask &= col.map(lambda cell: value in _atomic_labels(cell))
    else:
        raise ValueError(f"unsupported match rule: {spec['match']!r}")
    return mask


def floor_mask(ads: pd.DataFrame, floor: int) -> pd.Series:
    return ads["spend_inr"] >= floor


# ---------------------------------------------------------------------------
# 1. Group sizes at each floor
# ---------------------------------------------------------------------------

def section_group_sizes(ads: pd.DataFrame) -> dict[str, pd.Series]:
    """Report group size for every hypothesis at every candidate floor.

    Returns the primary-floor membership mask per hypothesis for reuse downstream.
    """
    line("## 1. Group sizes at each spend floor")
    line()
    line(f"Floors tested: primary = {PRIMARY_FLOOR}, sensitivity = "
         f"{SENSITIVITY_FLOORS}. A group with fewer than {MIN_GROUP} ads at a "
         f"floor is flagged [under min_group_size]. share_within_floor = group "
         f"ads / all ads meeting that floor.")
    line()

    floor_totals = {f: int(floor_mask(ads, f).sum()) for f in FLOORS}
    line("- Ads meeting each floor (denominator for share_within_floor): "
         + "; ".join(f"spend>={f}: n={floor_totals[f]}" for f in FLOORS) + ".")
    line()

    rows = []
    primary_masks: dict[str, pd.Series] = {}
    for hid, tier, spec in HYP_LIST:
        member = membership_mask(ads, spec)
        primary_masks[hid] = member & floor_mask(ads, PRIMARY_FLOOR)
        restrict = spec.get("restrict", "")
        line(f"- **{hid}** ({tier}) — {spec['name']}: "
             f"{spec['column']} {spec['match']} '{spec['value']}'"
             + (f", restrict {restrict}" if restrict else "") + ".")
        for f in FLOORS:
            n_group = int((member & floor_mask(ads, f)).sum())
            den = floor_totals[f]
            under = n_group < MIN_GROUP
            rows.append({
                "hypothesis_id": hid,
                "tier": tier,
                "name": spec["name"],
                "column": spec["column"],
                "match": spec["match"],
                "value": spec["value"],
                "restrict": restrict,
                "floor": f,
                "n_group": n_group,
                "n_floor_total": den,
                "share_within_floor": round(n_group / den, 4) if den else 0.0,
                "under_min_group_size": under,
            })
            flag = " [under min_group_size]" if under else ""
            tag = " (primary floor)" if f == PRIMARY_FLOOR else ""
            line(f"  - spend>={f}{tag}: n_group={n_group}, "
                 f"{pct(n_group, den)}{flag}")
    write_csv(pd.DataFrame(rows), "audit_cross_group_sizes.csv")
    line()
    return primary_masks


# ---------------------------------------------------------------------------
# 2. Pairwise overlap at the primary floor
# ---------------------------------------------------------------------------

def section_pair_overlap(ads: pd.DataFrame,
                         primary_masks: dict[str, pd.Series]) -> None:
    line("## 2. Pairwise group overlap at the primary floor")
    line()
    floor_total = int(floor_mask(ads, PRIMARY_FLOOR).sum())
    ids = [hid for hid, _, _ in HYP_LIST]
    pairs = list(combinations(ids, 2))
    line(f"All {len(pairs)} unordered pairs among the {len(ids)} hypotheses "
         f"(primary and exploratory), groups formed at spend>={PRIMARY_FLOOR}. "
         f"n_both = ads in both groups; share_of_floor uses the "
         f"{floor_total}-ad floor set as denominator.")
    line()

    rows = []
    for a, b in pairs:
        ma, mb = primary_masks[a], primary_masks[b]
        n_a, n_b = int(ma.sum()), int(mb.sum())
        n_both = int((ma & mb).sum())
        n_union = int((ma | mb).sum())
        rows.append({
            "hyp_a": a, "hyp_b": b,
            "n_a": n_a, "n_b": n_b,
            "n_both": n_both, "n_union": n_union,
            "n_floor_total": floor_total,
            "share_both_of_floor": round(n_both / floor_total, 4)
            if floor_total else 0.0,
        })
    overlap_df = pd.DataFrame(rows)
    write_csv(overlap_df, "audit_cross_pair_overlap.csv")

    line(f"- Pairs sharing at least one ad: "
         f"{int((overlap_df['n_both'] > 0).sum())} of {len(pairs)}. Full matrix "
         f"in audit_cross_pair_overlap.csv.")
    top = overlap_df.sort_values("n_both", ascending=False).head(10)
    line("- Highest-overlap pairs (n_both, descending):")
    for r in top.itertuples():
        line(f"  - {r.hyp_a} & {r.hyp_b}: n_both={r.n_both} "
             f"({pct(r.n_both, floor_total)}); n_a={r.n_a}, n_b={r.n_b}, "
             f"n_union={r.n_union}")
    line()


# ---------------------------------------------------------------------------
# 3. Label cross-tabs over all ads
# ---------------------------------------------------------------------------

def section_cross_tabs(ads: pd.DataFrame) -> None:
    line("## 3. Label cross-tabs (all ads)")
    line()
    n = len(ads)

    # --- child_on_screen x child_in_first_3s ---
    a = ads["child_on_screen"].where(ads["child_on_screen"].notna(), "(missing)")
    b = ads["child_in_first_3s"].where(
        ads["child_in_first_3s"].notna(), "(missing)"
    )
    ct = pd.crosstab(a, b, margins=True, margins_name="All")
    ct.to_csv(OUT_DIR / "audit_cross_child_onscreen_x_first3s.csv")
    line(f"- child_on_screen x child_in_first_3s (n={n}), "
         f"audit_cross_child_onscreen_x_first3s.csv:")
    cols = [c for c in ct.columns if c != "All"]
    line(f"    {'child_on_screen':<18}" + "".join(f"{str(c):>12}" for c in cols)
         + f"{'All':>12}")
    for idx in [i for i in ct.index if i != "All"] + ["All"]:
        line(f"    {str(idx):<18}"
             + "".join(f"{int(ct.loc[idx, c]):>12}" for c in cols)
             + f"{int(ct.loc[idx, 'All']):>12}")

    # --- child_role atomic: reacts_to_taste x consumes_product ---
    labels = ads["child_role"].map(_atomic_labels)
    has_taste = labels.map(lambda s: "reacts_to_taste" in s)
    has_consume = labels.map(lambda s: "consumes_product" in s)
    taste_lab = has_taste.map({True: "reacts_to_taste", False: "no_taste"})
    cons_lab = has_consume.map({True: "consumes_product", False: "no_consume"})
    ct2 = pd.crosstab(taste_lab, cons_lab, margins=True, margins_name="All")
    ct2 = ct2.reindex(
        index=["reacts_to_taste", "no_taste", "All"],
        columns=["consumes_product", "no_consume", "All"],
        fill_value=0,
    )
    ct2.to_csv(OUT_DIR / "audit_cross_childrole_taste_x_consumes.csv")
    line()
    line(f"- child_role atomic reacts_to_taste x consumes_product (n={n}; "
         f"'none'/missing child_role fall in the no/no cell), "
         f"audit_cross_childrole_taste_x_consumes.csv:")
    both = int((has_taste & has_consume).sum())
    only_t = int((has_taste & ~has_consume).sum())
    only_c = int((~has_taste & has_consume).sum())
    neither = int((~has_taste & ~has_consume).sum())
    line(f"    both labels: {both} ({pct(both, n)})")
    line(f"    reacts_to_taste only: {only_t}; consumes_product only: {only_c}")
    line(f"    neither: {neither}")
    line()


# ---------------------------------------------------------------------------
# 4. Group splits at the primary floor
# ---------------------------------------------------------------------------

def section_group_splits(ads: pd.DataFrame,
                         primary_masks: dict[str, pd.Series]) -> None:
    line("## 4. Group splits at the primary floor")
    line()
    line(f"For each hypothesis group (formed at spend>={PRIMARY_FLOOR}), counts "
         f"by product_form, launch month, and stopped_date. Full table in "
         f"audit_cross_group_splits.csv.")
    line()

    launch_month = pd.to_datetime(
        ads["launch_date"], errors="coerce"
    ).dt.to_period("M").astype("string")
    stopped = pd.to_datetime(
        ads["stopped_date"], errors="coerce"
    ).dt.date.astype("string")
    dims = {
        "product_form": ads["product_form"].astype("string"),
        "launch_month": launch_month,
        "stopped_date": stopped,
    }

    rows = []
    for hid, _, spec in HYP_LIST:
        mask = primary_masks[hid]
        n_group = int(mask.sum())
        line(f"- **{hid}** — {spec['name']} (n_group={n_group}):")
        for dim_name, series in dims.items():
            counts = series[mask].value_counts(dropna=False).sort_values(
                ascending=False
            )
            for bucket, cnt in counts.items():
                rows.append({
                    "hypothesis_id": hid,
                    "n_group": n_group,
                    "dimension": dim_name,
                    "bucket": "(missing)" if pd.isna(bucket) else str(bucket),
                    "n_ads": int(cnt),
                })
            if dim_name == "product_form":
                shown = "; ".join(
                    f"{'(missing)' if pd.isna(k) else k}={int(v)}"
                    for k, v in counts.items()
                )
                line(f"  - by product_form: {shown if shown else '(none)'}")
            else:
                line(f"  - by {dim_name}: {len(counts)} distinct value(s), "
                     f"top = " + ("; ".join(
                         f"{'(missing)' if pd.isna(k) else k}={int(v)}"
                         for k, v in counts.head(3).items()
                     ) or "(none)"))
    write_csv(
        pd.DataFrame(
            rows,
            columns=["hypothesis_id", "n_group", "dimension", "bucket", "n_ads"],
        ),
        "audit_cross_group_splits.csv",
    )
    line()


# ---------------------------------------------------------------------------
# 5. Date-and-form clustering, two scopes
# ---------------------------------------------------------------------------

def section_clustering(ads: pd.DataFrame) -> None:
    line("## 5. Date-and-form clustering")
    line()
    line(f"Two scopes reported side by side: all ads and ads at the primary "
         f"floor (spend>={PRIMARY_FLOOR}). Distinct launch_date count, and the "
         f"top {TOP_COMBOS} launch_date x stopped_date x product_form "
         f"combinations by ad count. Full table in audit_cross_clustering.csv.")
    line()

    scopes = {
        "all_ads": ads,
        "primary_floor": ads[floor_mask(ads, PRIMARY_FLOOR)],
    }

    combo_rows = []
    for scope_name, frame in scopes.items():
        n = len(frame)
        n_distinct_launch = int(frame["launch_date"].nunique(dropna=True))
        combo = (
            frame.groupby(["launch_date", "stopped_date", "product_form"],
                          dropna=False)
            .size()
            .reset_index(name="n_ads")
            .sort_values("n_ads", ascending=False)
        )
        n_distinct_combo = len(combo)
        top = combo.head(TOP_COMBOS)
        for rank, r in enumerate(top.itertuples(), start=1):
            combo_rows.append({
                "scope": scope_name,
                "rank": rank,
                "launch_date": r.launch_date,
                "stopped_date": r.stopped_date,
                "product_form": r.product_form,
                "n_ads": int(r.n_ads),
                "n_scope_total": n,
            })
        line(f"- **{scope_name}** (n={n}): distinct launch_date = "
             f"{n_distinct_launch}; distinct launch x stop x form combinations = "
             f"{n_distinct_combo}.")
        line(f"  - top {min(TOP_COMBOS, len(top))} combinations:")
        for rank, r in enumerate(top.itertuples(), start=1):
            line(f"    {rank:>2}. {r.launch_date} / {r.stopped_date} / "
                 f"{r.product_form}: {pct(int(r.n_ads), n)}")
    write_csv(
        pd.DataFrame(
            combo_rows,
            columns=["scope", "rank", "launch_date", "stopped_date",
                     "product_form", "n_ads", "n_scope_total"],
        ),
        "audit_cross_clustering.csv",
    )
    line()


# ---------------------------------------------------------------------------
# 6. Purchases distribution of the primary-floor set
# ---------------------------------------------------------------------------

def section_floor_purchases(ads: pd.DataFrame) -> None:
    line("## 6. Purchases among ads passing the primary floor")
    line()
    floor = ads.loc[floor_mask(ads, PRIMARY_FLOOR), "purchases"]
    n = int(floor.notna().sum())
    p_min = int(floor.min())
    p_median = float(floor.median())
    n_lt20 = int((floor < 20).sum())
    rows = [
        {"metric": "purchases_min", "value": p_min, "n_floor_total": n},
        {"metric": "purchases_median", "value": p_median, "n_floor_total": n},
        {"metric": "n_purchases_lt_20", "value": n_lt20, "n_floor_total": n},
        {"metric": "share_purchases_lt_20",
         "value": round(n_lt20 / n, 4) if n else 0.0, "n_floor_total": n},
    ]
    write_csv(pd.DataFrame(rows), "audit_cross_floor_purchases.csv")
    line(f"Distribution of the floor set as a whole (not a per-group metric), "
         f"audit_cross_floor_purchases.csv:")
    line(f"- min purchases: {p_min} (n={n}).")
    line(f"- median purchases: {p_median:g} (n={n}).")
    line(f"- ads with purchases < 20: {pct(n_lt20, n)}.")
    line()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ads = pd.read_csv(DATA_DIR / "ads.csv")

    n_hyp = len(HYP_LIST)
    n_pairs = n_hyp * (n_hyp - 1) // 2

    line("# Cross-structure facts — Little Joys hypothesis groups")
    line()
    line(f"Source: data/ads.csv (read-only). Parameters and hypotheses loaded "
         f"from config/. Facts only; no interpretation, ranking, or selection. "
         f"No performance metric (ROAS, CTR, CPA, hook rate) is computed broken "
         f"down by any group.")
    line()
    line(f"Rows loaded: ads={len(ads)}. Hypotheses: {n_hyp} "
         f"({len(HYPS.get('primary', {}))} primary, "
         f"{len(HYPS.get('exploratory', {}))} exploratory).")
    line()
    line(f"Comparisons run (6 sections): (1) {n_hyp} hypotheses x {len(FLOORS)} "
         f"floors = {n_hyp * len(FLOORS)} group-size counts; (2) {n_pairs} "
         f"pairwise overlaps at the primary floor; (3) 2 label cross-tabs; "
         f"(4) {n_hyp} groups x 3 dimensions = {n_hyp * 3} splits; (5) 2 scopes "
         f"x (1 distinct-launch count + 1 top-{TOP_COMBOS} combination table); "
         f"(6) 3 purchases statistics over the primary-floor set.")
    line()

    primary_masks = section_group_sizes(ads)
    section_pair_overlap(ads, primary_masks)
    section_cross_tabs(ads)
    section_group_splits(ads, primary_masks)
    section_clustering(ads)
    section_floor_purchases(ads)

    (OUT_DIR / "audit_cross_summary.md").write_text(
        "\n".join(_summary) + "\n", encoding="utf-8"
    )

    print("Wrote to", OUT_DIR)
    for p in sorted(OUT_DIR.glob("audit_cross_*")):
        print(" -", p.name)


if __name__ == "__main__":
    main()
