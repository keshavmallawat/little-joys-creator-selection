"""Group-membership helpers for the Little Joys hypothesis groups.

These are the same helpers used by the cross-structure pass, lifted here so the
performance analysis forms every group the identical way: atomic-label split,
restrict precondition, membership rule (equals / contains) and the spend floor.
No count, id or threshold is written by hand; callers pass specs loaded from
config/hypotheses.yaml and floors loaded from config/params.yaml.
"""

from __future__ import annotations

import pandas as pd


def atomic_labels(cell) -> set[str]:
    """Split a multi-value cell on ';' into the set of its atomic labels."""
    if pd.isna(cell):
        return set()
    return {p.strip() for p in str(cell).split(";") if p.strip() != ""}


def restrict(ads: pd.DataFrame, expr: str) -> pd.Series:
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
        mask &= restrict(ads, spec["restrict"])

    col = ads[spec["column"]]
    value = str(spec["value"])
    if spec["match"] == "equals":
        mask &= col.astype(str) == value
    elif spec["match"] == "contains":
        mask &= col.map(lambda cell: value in atomic_labels(cell))
    else:
        raise ValueError(f"unsupported match rule: {spec['match']!r}")
    return mask


def floor_mask(ads: pd.DataFrame, floor: int) -> pd.Series:
    return ads["spend_inr"] >= floor
