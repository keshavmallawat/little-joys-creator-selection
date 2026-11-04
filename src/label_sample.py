"""Draw a stratified label spot-check sample for the Little Joys ads.

Labels in data/ads.csv are AI-generated and imperfect; config/decision_rules.yaml
caps any hypothesis whose label agreement falls below the label_cap. This script
builds the sheet a human uses to measure that agreement: among ads at the primary
spend floor it draws 20 ads (seed 42), stratified so that for each primary
hypothesis (H1, H2, H4, H6, H7) both the in-group and out-group are represented,
with at least three ads a side where the floor set allows.

It writes outputs/audit/label_check.csv with each ad's video_url, hook_line, the
first 600 characters of its transcript, the stored labels, and blank my_* columns
for the reviewer to fill. A companion summary records the sample composition.

This script samples and transcribes only. It does not inspect, judge, rank, or
choose; it computes no performance metric. No count is typed by hand: everything
is derived from the loaded data and the config files.
"""

from __future__ import annotations

import random
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
PRIMARY_FLOOR = int(PARAMS["spend_floor_primary"])

TARGET_N = 20          # total ads in the sample
PER_SIDE_QUOTA = 3     # minimum ads per hypothesis side, where available
TRANSCRIPT_CHARS = 600  # characters of transcript shown to the reviewer

# Hypotheses that drive the stratification: the five primary hypotheses, read
# from config in file order (no column name is hardcoded here).
STRATA_IDS = list(HYPS.get("primary", {}).keys())

# Gold-label columns copied verbatim into the sheet for the reviewer to see.
LABEL_COLS = [
    "child_role",
    "child_in_first_3s",
    "hook_type",
    "creator_type",
    "ad_format",
    "brand_first_said",
    "language_mixing",
]

# Blank columns the reviewer fills in.
REVIEW_COLS = [
    "my_child_role_reacts",
    "my_child_in_first_3s",
    "my_hook_type",
    "my_creator_type",
    "my_ad_format",
    "my_brand_first_said",
    "notes",
]

OUTPUT_COLS = (
    ["ad_id", "video_url", "hook_line", "transcript_first_600"]
    + LABEL_COLS
    + REVIEW_COLS
)

# Collected lines for the human-readable summary.
_summary: list[str] = []


def line(text: str = "") -> None:
    _summary.append(text)


def pct(num: int, den: int) -> str:
    """Format a rate with its denominator n, guarding against n == 0."""
    if den == 0:
        return "0/0 (n=0)"
    return f"{num}/{den} = {num / den:.1%} (n={den})"


# ---------------------------------------------------------------------------
# Group membership (same rules as the rest of src/)
# ---------------------------------------------------------------------------

def _atomic_labels(cell) -> set[str]:
    """Split a multi-value cell on ';' into the set of its atomic labels."""
    if pd.isna(cell):
        return set()
    return {p.strip() for p in str(cell).split(";") if p.strip() != ""}


def _restrict_mask(ads: pd.DataFrame, expr: str) -> pd.Series:
    """Parse a simple 'column <op> value' restriction into a boolean mask."""
    for op in ("!=", "=="):
        if op in expr:
            col, val = (s.strip() for s in expr.split(op, 1))
            col_str = ads[col].astype(str)
            return col_str != val if op == "!=" else col_str == val
    raise ValueError(f"unsupported restrict expression: {expr!r}")


def membership_mask(ads: pd.DataFrame, spec: dict) -> pd.Series:
    """Boolean mask for ads in a hypothesis group, ignoring spend floor."""
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


def side_masks(ads: pd.DataFrame, hid: str, spec: dict) -> dict[str, pd.Series]:
    """In-group and out-group masks for one hypothesis within the floor set.

    The out-group is the floor set minus the in-group, except for H2: because an
    ad with no child is trivially 'no' on child_in_first_3s, H2's negatives are
    restricted to ads that still satisfy its precondition (a child is present) but
    whose label is 'no', so those trivial cases do not pad the sample.
    """
    in_group = membership_mask(ads, spec)
    if spec.get("restrict"):
        precondition = _restrict_mask(ads, spec["restrict"])
        out_group = precondition & ~in_group
    else:
        out_group = ~in_group
    return {"in": in_group, "out": out_group}


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------

def draw_sample(floor: pd.DataFrame) -> tuple[list, dict[str, dict[str, pd.Series]]]:
    """Return the sampled ad_ids and the per-hypothesis side masks.

    Deterministic under SEED: candidate pools are sorted by ad_id before any
    draw, and the scarcest (hypothesis, side) strata are filled first so that
    ads which satisfy several requirements at once keep the total small.
    """
    rng = random.Random(SEED)

    masks: dict[str, dict[str, pd.Series]] = {}
    for hid in STRATA_IDS:
        masks[hid] = side_masks(floor, hid, HYPS["primary"][hid])

    # ad_id for each floor row, so selection is expressed in stable ids.
    id_by_index = floor["ad_id"]

    # Build the ten (hypothesis, side) requirements as sorted candidate id lists.
    requirements: list[tuple[str, str, list]] = []
    for hid in STRATA_IDS:
        for side in ("in", "out"):
            cand_ids = sorted(id_by_index[masks[hid][side]].tolist())
            requirements.append((hid, side, cand_ids))

    # Fill scarcest pools first.
    requirements.sort(key=lambda r: len(r[2]))

    selected: list = []          # ad_ids, insertion order preserved
    selected_set: set = set()

    for _hid, _side, cand_ids in requirements:
        quota = min(PER_SIDE_QUOTA, len(cand_ids))
        have = sum(1 for aid in cand_ids if aid in selected_set)
        need = quota - have
        if need > 0:
            pool = [aid for aid in cand_ids if aid not in selected_set]
            pick = rng.sample(pool, need)
            for aid in pick:
                selected.append(aid)
                selected_set.add(aid)

    # Top up to the target from the remaining floor ads.
    if len(selected_set) < TARGET_N:
        remaining = sorted(
            aid for aid in id_by_index.tolist() if aid not in selected_set
        )
        extra = rng.sample(remaining, TARGET_N - len(selected_set))
        for aid in extra:
            selected.append(aid)
            selected_set.add(aid)

    # Guarantee the quota held on both sides of every hypothesis.
    for hid in STRATA_IDS:
        for side in ("in", "out"):
            cand_ids = set(id_by_index[masks[hid][side]].tolist())
            got = len(selected_set & cand_ids)
            want = min(PER_SIDE_QUOTA, len(cand_ids))
            if got < want:
                raise AssertionError(
                    f"{hid} {side}: have {got} ads, need {want}"
                )

    return selected, masks


# ---------------------------------------------------------------------------
# Sheet construction
# ---------------------------------------------------------------------------

def build_sheet(floor: pd.DataFrame, selected_ids: list) -> pd.DataFrame:
    rows = floor[floor["ad_id"].isin(selected_ids)].copy()

    transcript = rows["transcript"].map(
        lambda c: "" if pd.isna(c) else str(c)[:TRANSCRIPT_CHARS]
    )
    rows = rows.assign(transcript_first_600=transcript)

    for col in REVIEW_COLS:
        rows[col] = ""

    sheet = rows[OUTPUT_COLS].sort_values("ad_id").reset_index(drop=True)
    return sheet


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ads = pd.read_csv(DATA_DIR / "ads.csv")
    floor = ads[ads["spend_inr"] >= PRIMARY_FLOOR].copy()
    n_floor = len(floor)

    selected_ids, masks = draw_sample(floor)
    sheet = build_sheet(floor, selected_ids)
    sheet.to_csv(OUT_DIR / "label_check.csv", index=False)

    selected_set = set(selected_ids)
    id_by_index = floor["ad_id"]

    line("# Label spot-check sample — Little Joys ads")
    line()
    line(f"Source: data/ads.csv (read-only). Floor and stratification read from "
         f"config/. Sampling and transcription only; no label is inspected, "
         f"judged, ranked, or selected, and no performance metric is computed.")
    line()
    line(f"Primary spend floor: spend_inr >= {PRIMARY_FLOOR} (n={n_floor} ads). "
         f"Seed: {SEED}. Target sample size: {TARGET_N}. Per-side quota: at least "
         f"{PER_SIDE_QUOTA} ads where the floor set allows.")
    line()
    line(f"Strata: {', '.join(STRATA_IDS)} (the primary hypotheses). For each, "
         f"in-group = the hypothesis group at the floor; out-group = floor set "
         f"minus in-group, except H2 whose out-group keeps its child-present "
         f"precondition so no-child ads do not pad the negatives.")
    line()
    line(f"Ads sampled: {len(sheet)}.")
    line()
    line("## Achieved composition")
    line()
    line("Per hypothesis, ads in the sample on each side, out of the floor-set "
         "availability for that side:")
    rows_summary = []
    for hid in STRATA_IDS:
        spec = HYPS["primary"][hid]
        line(f"- **{hid}** — {spec['name']}:")
        for side in ("in", "out"):
            avail_ids = set(id_by_index[masks[hid][side]].tolist())
            n_avail = len(avail_ids)
            n_in_sample = len(selected_set & avail_ids)
            want = min(PER_SIDE_QUOTA, n_avail)
            line(f"  - {side}-group: {n_in_sample} in sample "
                 f"(available at floor: {n_avail}; quota {want}) "
                 f"[{pct(n_in_sample, len(sheet))} of sample]")
            rows_summary.append({
                "hypothesis_id": hid,
                "name": spec["name"],
                "side": side,
                "n_available_at_floor": n_avail,
                "quota": want,
                "n_in_sample": n_in_sample,
                "n_sample_total": len(sheet),
            })
    pd.DataFrame(rows_summary).to_csv(
        OUT_DIR / "label_sample_composition.csv", index=False
    )
    line()
    line("Full composition in label_sample_composition.csv. Blank my_* columns "
         "in label_check.csv are for the reviewer; agreement is computed later by "
         "label_error.py.")

    (OUT_DIR / "label_sample_summary.md").write_text(
        "\n".join(_summary) + "\n", encoding="utf-8"
    )

    print("\n".join(_summary))
    print()
    print("Wrote to", OUT_DIR)
    for name in ("label_check.csv", "label_sample_composition.csv",
                 "label_sample_summary.md"):
        print(" -", name)


if __name__ == "__main__":
    main()
