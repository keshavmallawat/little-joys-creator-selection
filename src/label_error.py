"""Score the Little Joys label spot-check once the reviewer has filled it in.

Reads outputs/audit/label_check.csv (produced by src/label_sample.py and filled
by a human) and, for each label, compares the reviewer's my_* judgment to the
stored label, reporting agreement with its denominator n. config/decision_rules.yaml
caps a hypothesis at "suggestive" when its label agreement falls below the
label_cap; this script flags, as a fact, which labels fall below that threshold.
The threshold is read from config, never typed by hand.

Reviewer entries of "unclear" are excluded from n and from the agreement rate,
are not treated as disagreements, and are tallied separately. Blank my_* cells
are ads the reviewer did not judge and are excluded entirely.

This script compares and presents only. It does not choose winners or creators;
whether an agreement rate is acceptable is decided elsewhere.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import yaml

# ---------------------------------------------------------------------------
# Constants and config
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
OUT_DIR = ROOT / "outputs" / "audit"

DECISION = yaml.safe_load(
    (CONFIG_DIR / "decision_rules.yaml").read_text(encoding="utf-8")
)

UNCLEAR = "unclear"
TRUE_TOKENS = {"yes", "y", "true", "t", "1"}
FALSE_TOKENS = {"no", "n", "false", "f", "0"}

# Reviewer column -> how it is scored against the stored data.
#   kind "bool": gold truth is the presence of `value` among the atomic labels
#                of `gold_col`; reviewer answers yes/no.
#   kind "exact": reviewer value must equal the stored cell (normalized).
COMPARISONS = [
    {"my_col": "my_child_role_reacts", "gold_col": "child_role",
     "kind": "bool", "value": "reacts_to_taste"},
    {"my_col": "my_child_in_first_3s", "gold_col": "child_in_first_3s",
     "kind": "exact"},
    {"my_col": "my_hook_type", "gold_col": "hook_type", "kind": "exact"},
    {"my_col": "my_creator_type", "gold_col": "creator_type", "kind": "exact"},
    {"my_col": "my_ad_format", "gold_col": "ad_format", "kind": "exact"},
    {"my_col": "my_brand_first_said", "gold_col": "brand_first_said",
     "kind": "exact"},
]

_summary: list[str] = []


def line(text: str = "") -> None:
    _summary.append(text)


def rate(num: int, den: int) -> str:
    """Format an agreement rate with its denominator n."""
    if den == 0:
        return "n/a (n=0)"
    return f"{num}/{den} = {num / den:.1%} (n={den})"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _atomic_labels(cell) -> set[str]:
    """Split a multi-value cell on ';' into the set of its atomic labels."""
    if pd.isna(cell):
        return set()
    return {p.strip() for p in str(cell).split(";") if p.strip() != ""}


def _norm(cell) -> str:
    """Lowercased, stripped string form of a cell ('' for missing)."""
    if pd.isna(cell):
        return ""
    return str(cell).strip().lower()


def _label_cap_threshold() -> float:
    """Read the numeric label_cap threshold out of config (no hardcoding)."""
    text = str(DECISION["label_cap"])
    match = re.search(r"\d*\.?\d+", text)
    if not match:
        raise ValueError(
            f"no numeric label_cap threshold found in: {text!r}"
        )
    return float(match.group())


def _to_bool(token: str):
    """Map a normalized yes/no token to True/False, or None if unrecognized."""
    if token in TRUE_TOKENS:
        return True
    if token in FALSE_TOKENS:
        return False
    return None


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_label(sheet: pd.DataFrame, comp: dict, threshold: float) -> dict:
    """Agreement for one label, plus the rows that disagreed or were unparsed."""
    my_col, gold_col, kind = comp["my_col"], comp["gold_col"], comp["kind"]

    n = n_agree = n_unclear = n_unparsed = 0
    disagreements: list[dict] = []

    for _, row in sheet.iterrows():
        raw = row[my_col]
        mine = _norm(raw)
        if mine == "":
            continue                      # not judged
        if mine == UNCLEAR:
            n_unclear += 1
            continue                      # excluded from n and agreement

        if kind == "bool":
            gold_truth = comp["value"] in _atomic_labels(row[gold_col])
            gold_display = "yes" if gold_truth else "no"
            mine_bool = _to_bool(mine)
            if mine_bool is None:
                n_unparsed += 1
                continue
            n += 1
            if mine_bool == gold_truth:
                n_agree += 1
            else:
                disagreements.append({
                    "ad_id": row["ad_id"], "my_column": my_col,
                    "gold_value": gold_display, "my_value": str(raw).strip(),
                })
        else:  # exact
            gold = _norm(row[gold_col])
            n += 1
            if mine == gold:
                n_agree += 1
            else:
                disagreements.append({
                    "ad_id": row["ad_id"], "my_column": my_col,
                    "gold_value": "" if pd.isna(row[gold_col])
                    else str(row[gold_col]).strip(),
                    "my_value": str(raw).strip(),
                })

    agreement = round(n_agree / n, 4) if n else None
    below = bool(agreement is not None and agreement < threshold)
    return {
        "row": {
            "my_column": my_col,
            "gold_column": gold_col,
            "n": n,
            "n_agree": n_agree,
            "agreement_rate": agreement,
            "n_unclear": n_unclear,
            "n_unparsed": n_unparsed,
            "label_cap": threshold,
            "below_label_cap": below,
        },
        "disagreements": disagreements,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # utf-8-sig so the BOM Excel adds when saving "CSV UTF-8" is stripped.
    sheet = pd.read_csv(OUT_DIR / "label_check.csv", encoding="utf-8-sig",
                        dtype=str)
    threshold = _label_cap_threshold()

    label_rows: list[dict] = []
    all_disagreements: list[dict] = []
    for comp in COMPARISONS:
        result = score_label(sheet, comp, threshold)
        label_rows.append(result["row"])
        all_disagreements.extend(result["disagreements"])

    # Overall micro-average across every judged (non-blank, non-unclear) cell.
    tot_n = sum(r["n"] for r in label_rows)
    tot_agree = sum(r["n_agree"] for r in label_rows)
    tot_unclear = sum(r["n_unclear"] for r in label_rows)
    tot_unparsed = sum(r["n_unparsed"] for r in label_rows)
    overall_rate = round(tot_agree / tot_n, 4) if tot_n else None
    overall_row = {
        "my_column": "ALL_LABELS",
        "gold_column": "(micro-average)",
        "n": tot_n,
        "n_agree": tot_agree,
        "agreement_rate": overall_rate,
        "n_unclear": tot_unclear,
        "n_unparsed": tot_unparsed,
        "label_cap": threshold,
        "below_label_cap": bool(
            overall_rate is not None and overall_rate < threshold
        ),
    }

    agreement_df = pd.DataFrame(label_rows + [overall_row])
    agreement_df.to_csv(OUT_DIR / "label_agreement.csv", index=False)

    disagree_df = pd.DataFrame(
        all_disagreements,
        columns=["ad_id", "my_column", "gold_value", "my_value"],
    )
    disagree_df.to_csv(OUT_DIR / "label_disagreements.csv", index=False)

    # --- Summary ---
    n_judged_rows = len(sheet)
    line("# Label spot-check agreement — Little Joys ads")
    line()
    line(f"Source: outputs/audit/label_check.csv (read-only here), "
         f"{n_judged_rows} ads in the sheet. For each label the reviewer's my_* "
         f"judgment is compared to the stored label; the rate below is agreement "
         f"with its denominator n. Comparison and presentation only — no verdict "
         f"or selection is made here.")
    line()
    line(f"label_cap threshold (from config/decision_rules.yaml): {threshold}. "
         f"A label with agreement below it is flagged below_label_cap (a fact, "
         f"not a decision). Reviewer entries of '{UNCLEAR}' are excluded from n "
         f"and tallied as n_unclear; blank cells are ads not judged.")
    line()
    line("## Per-label agreement")
    line()
    for r in label_rows:
        rtxt = rate(r["n_agree"], r["n"])
        extras = f"n_unclear={r['n_unclear']}"
        if r["n_unparsed"]:
            extras += f", n_unparsed={r['n_unparsed']}"
        flag = "  [below label_cap]" if r["below_label_cap"] else ""
        line(f"- **{r['my_column']}** vs {r['gold_column']}: {rtxt}; "
             f"{extras}{flag}")
    line()
    otxt = rate(overall_row["n_agree"], overall_row["n"])
    oflag = "  [below label_cap]" if overall_row["below_label_cap"] else ""
    line(f"- **Overall** (micro-average across labels): {otxt}; "
         f"n_unclear={tot_unclear}"
         + (f", n_unparsed={tot_unparsed}" if tot_unparsed else "") + oflag)
    line()
    below = [r["my_column"] for r in label_rows if r["below_label_cap"]]
    if below:
        line(f"Labels below the {threshold} label_cap: {', '.join(below)}. "
             f"Full detail in label_agreement.csv; mismatches in "
             f"label_disagreements.csv.")
    else:
        line(f"No label is below the {threshold} label_cap among judged cells. "
             f"Full detail in label_agreement.csv; mismatches in "
             f"label_disagreements.csv.")
    line()

    (OUT_DIR / "label_agreement_summary.md").write_text(
        "\n".join(_summary) + "\n", encoding="utf-8"
    )

    print("\n".join(_summary))
    print()
    print("Wrote to", OUT_DIR)
    for name in ("label_agreement.csv", "label_disagreements.csv",
                 "label_agreement_summary.md"):
        print(" -", name)


if __name__ == "__main__":
    main()
