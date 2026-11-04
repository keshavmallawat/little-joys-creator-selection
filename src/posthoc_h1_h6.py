"""Post-hoc descriptive cross of H1 membership x H6 membership.

This table is POST-HOC and NOT pre-registered. It is motivated by the 22-ad
overlap between H1 (child reacts to taste) and H6 (creator is parent or
caregiver) reported at the primary floor in
outputs/audit/audit_cross_pair_overlap.csv. H1 and H6 share most of their ads,
so this pass crosses the two memberships to describe how the outcome and
diagnostic rates sit in each corner of the 2x2 — it describes the overlap only.

It assigns no tier, computes no confidence interval, runs no test, ranks
nothing and chooses nothing. Every rate is pooled (sum(numerator) /
sum(denominator); see src/metrics.py) and is reported with its n and its
denominator. Nothing is written by hand: the H1 and H6 specs and the spend
floor are read from config/, and group masks are formed with the shared
helpers in src/groups.py.

Alongside the 2x2 it writes counts-only composition views (n ads by
creator_type and by product_form for individual cells) that carry no
performance metric at all.

Outputs (outputs/ads/): posthoc_h1_h6.csv, posthoc_h1_h6.md.
"""

from __future__ import annotations

import random
from pathlib import Path

import pandas as pd
import yaml

from groups import floor_mask, membership_mask
from metrics import (
    median_per_ad_roas,
    pooled_ctr,
    pooled_cvr,
    pooled_hook_rate,
    pooled_roas,
)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"
OUT_DIR = ROOT / "outputs" / "ads"

PARAMS = yaml.safe_load((CONFIG_DIR / "params.yaml").read_text(encoding="utf-8"))
HYPS = yaml.safe_load((CONFIG_DIR / "hypotheses.yaml").read_text(encoding="utf-8"))

SEED = int(PARAMS["seed"])
random.seed(SEED)  # project convention; this pass has no randomness
PRIMARY_FLOOR = int(PARAMS["spend_floor_primary"])

H1_SPEC = HYPS["primary"]["H1"]
H6_SPEC = HYPS["primary"]["H6"]

MOTIVATION = ("post-hoc, not pre-registered, motivated by the 22-ad H1/H6 "
              "overlap in audit_cross_pair_overlap.csv")

_summary: list[str] = []


def line(text: str = "") -> None:
    _summary.append(text)


def fmt_rate(rate: float, n: int, denom: int | None = None) -> str:
    """Rate with its n (ads) and, when relevant, its denominator."""
    tail = f"n={n}" if denom is None else f"n={n} ads, denom={denom}"
    if rate is None or (isinstance(rate, float) and pd.isna(rate)):
        return f"NA ({tail})"
    return f"{rate:.4f} ({tail})"


def cell_metrics(df: pd.DataFrame) -> dict:
    """Pooled and median outcome plus pooled diagnostic rates for one cell."""
    roas, n_ads, _ = pooled_roas(df)
    hr, _, imp = pooled_hook_rate(df)
    ctr, _, _ = pooled_ctr(df)
    cvr, _, clk = pooled_cvr(df)
    return {
        "n_ads": n_ads,
        "pooled_roas": roas,
        "median_per_ad_roas": median_per_ad_roas(df),
        "hook_rate": hr,
        "hook_rate_impressions": imp,
        "ctr": ctr,
        "ctr_impressions": imp,
        "cvr": cvr,
        "cvr_link_clicks": clk,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ads = pd.read_csv(DATA_DIR / "ads.csv")

    floor = floor_mask(ads, PRIMARY_FLOOR)
    h1 = membership_mask(ads, H1_SPEC) & floor
    h6 = membership_mask(ads, H6_SPEC) & floor
    n_floor = int(floor.sum())

    cells = {
        "H1in_H6in": (h1 & h6, "in", "in"),
        "H1in_H6out": (h1 & ~h6, "in", "out"),
        "H1out_H6in": (~h1 & h6 & floor, "out", "in"),
        "H1out_H6out": (~h1 & ~h6 & floor, "out", "out"),
    }

    rows: list[dict] = []

    # View 1: the 2x2.
    for cell, (mask, h1_side, h6_side) in cells.items():
        m = cell_metrics(ads[mask])
        rows.append({
            "view": "cross_2x2", "cell": cell, "item": "",
            "h1": h1_side, "h6": h6_side, **m, "n_scope": n_floor,
        })

    # View 2: product_form split of the H1-out / H6-in cell (n per form only).
    h1out_h6in = ads[cells["H1out_H6in"][0]]
    pf = h1out_h6in["product_form"].value_counts(dropna=False)
    for form, cnt in pf.items():
        rows.append({
            "view": "H1out_H6in_by_product_form", "cell": "H1out_H6in",
            "item": "(missing)" if pd.isna(form) else str(form),
            "h1": "out", "h6": "in",
            "n_ads": int(cnt),
            "pooled_roas": "", "median_per_ad_roas": "",
            "hook_rate": "", "hook_rate_impressions": "",
            "ctr": "", "ctr_impressions": "",
            "cvr": "", "cvr_link_clicks": "",
            "n_scope": int(len(h1out_h6in)),
        })

    # View 3: counts-only composition of the H1-in / H6-out cell. No metrics.
    h1in_h6out = ads[cells["H1in_H6out"][0]]
    comp = {
        "H1in_H6out_by_creator_type":
            h1in_h6out["creator_type"].value_counts(dropna=False),
        "H1in_H6out_by_product_form":
            h1in_h6out["product_form"].value_counts(dropna=False),
    }
    for view_name, counts in comp.items():
        for cat, cnt in counts.items():
            rows.append({
                "view": view_name, "cell": "H1in_H6out",
                "item": "(missing)" if pd.isna(cat) else str(cat),
                "h1": "in", "h6": "out",
                "n_ads": int(cnt),
                "pooled_roas": "", "median_per_ad_roas": "",
                "hook_rate": "", "hook_rate_impressions": "",
                "ctr": "", "ctr_impressions": "",
                "cvr": "", "cvr_link_clicks": "",
                "n_scope": int(len(h1in_h6out)),
            })

    cols = ["view", "cell", "item", "h1", "h6", "n_ads", "pooled_roas",
            "median_per_ad_roas", "hook_rate", "hook_rate_impressions",
            "ctr", "ctr_impressions", "cvr", "cvr_link_clicks", "n_scope"]
    pd.DataFrame(rows, columns=cols).to_csv(
        OUT_DIR / "posthoc_h1_h6.csv", index=False
    )

    # Comparison count: 4 cells x 5 per-cell metrics, plus the count-only
    # breakdowns (product_form of H1out_H6in; creator_type and product_form of
    # H1in_H6out). The count-only breakdowns carry no performance metric.
    n_cells = len(cells)
    n_metrics = 5  # ROAS, median per-ad ROAS, hook_rate, ctr, cvr
    n_cell_metrics = n_cells * n_metrics
    n_breakdowns = 1 + len(comp)

    # ---- Summary -----------------------------------------------------------
    line(f"# Post-hoc H1 x H6 descriptive cross ({MOTIVATION})")
    line()
    line("Source: data/ads.csv (read-only); H1 and H6 specs and the spend floor "
         "from config/. Primary floor only. Descriptive only: no tier, no "
         "confidence interval, no test, no ranking, no causal language. Each "
         "rate is pooled and carries its n (and its denominator).")
    line()
    line(f"Primary floor: spend>={PRIMARY_FLOOR} (floor set n={n_floor}). "
         f"H1 = {H1_SPEC['column']} {H1_SPEC['match']} '{H1_SPEC['value']}'; "
         f"H6 = {H6_SPEC['column']} {H6_SPEC['match']} '{H6_SPEC['value']}'.")
    line()
    line(f"Comparisons run: {n_cells} cells x {n_metrics} per-cell metrics "
         f"(pooled ROAS, median per-ad ROAS, pooled hook_rate, ctr, cvr) = "
         f"**{n_cell_metrics}**, plus {n_breakdowns} count-only breakdowns "
         f"(product_form of H1out_H6in; creator_type and product_form of "
         f"H1in_H6out), which carry no performance metric. "
         f"Total = **{n_cell_metrics + n_breakdowns}**.")
    line()

    line("## 2x2: H1 membership x H6 membership (primary floor)")
    line()
    for cell, (mask, h1_side, h6_side) in cells.items():
        m = cell_metrics(ads[mask])
        n = m["n_ads"]
        line(f"- **{cell}** (H1 {h1_side}, H6 {h6_side}): n_ads={n}; "
             f"pooled ROAS={fmt_rate(m['pooled_roas'], n)}; "
             f"median per-ad ROAS={fmt_rate(m['median_per_ad_roas'], n)}; "
             f"hook_rate={fmt_rate(m['hook_rate'], n, m['hook_rate_impressions'])}; "
             f"ctr={fmt_rate(m['ctr'], n, m['ctr_impressions'])}; "
             f"cvr={fmt_rate(m['cvr'], n, m['cvr_link_clicks'])}")
    line()
    n_sum = sum(cell_metrics(ads[mask])["n_ads"] for mask, _, _ in cells.values())
    line(f"Cell n sum to {n_sum} (floor set n={n_floor}).")
    line()

    line("## product_form split of the H1out_H6in cell (n per form)")
    line()
    line(f"H1out_H6in cell n={len(h1out_h6in)}.")
    for form, cnt in pf.items():
        label = "(missing)" if pd.isna(form) else str(form)
        line(f"- {label}: n={int(cnt)}")
    line()

    line("## H1in_H6out cell composition (post-hoc, counts only — no "
         "performance metrics)")
    line()
    line(f"H1in_H6out cell n={len(h1in_h6out)}.")
    line("By creator_type:")
    for cat, cnt in comp["H1in_H6out_by_creator_type"].items():
        label = "(missing)" if pd.isna(cat) else str(cat)
        line(f"- {label}: n={int(cnt)}")
    line("By product_form:")
    for cat, cnt in comp["H1in_H6out_by_product_form"].items():
        label = "(missing)" if pd.isna(cat) else str(cat)
        line(f"- {label}: n={int(cnt)}")
    line()
    line("Full detail: posthoc_h1_h6.csv.")

    (OUT_DIR / "posthoc_h1_h6.md").write_text(
        "\n".join(_summary) + "\n", encoding="utf-8"
    )

    print("Wrote to", OUT_DIR)
    for p in sorted(OUT_DIR.glob("posthoc_h1_h6*")):
        print(" -", p.name)


if __name__ == "__main__":
    main()
