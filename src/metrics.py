"""Metric definitions for the Little Joys performance analysis — defined once.

Every rate is a pooled ratio: sum(numerator) / sum(denominator) over the ads in
a group, never an average of per-ad ratios (spend and exposure vary widely, so a
per-ad average would weight a tiny ad the same as a large one). Each pooled call
also returns n_ads, the number of ads behind the rate, so every rate can be
printed with its n. A ratio with a zero denominator sum is returned as NaN.

Column names live here as constants so no other module hardcodes them.
"""

from __future__ import annotations

import math

import pandas as pd

# ---------------------------------------------------------------------------
# Columns
# ---------------------------------------------------------------------------

REVENUE = "revenue_inr"
SPEND = "spend_inr"
IMPRESSIONS = "impressions"
VIDEO_3S = "video_3s_views"
LINK_CLICKS = "link_clicks"
PURCHASES = "purchases"


# ---------------------------------------------------------------------------
# Pooled ratios
# ---------------------------------------------------------------------------

def pooled(df: pd.DataFrame, num_col: str, den_col: str) -> tuple[float, int, int]:
    """Pooled ratio sum(num)/sum(den) over df.

    Returns (rate, n_ads, denominator_sum). rate is NaN when the denominator
    sum is zero. n_ads is the number of ads (rows) behind the rate.
    """
    n_ads = int(len(df))
    den_sum = int(df[den_col].sum()) if n_ads else 0
    num_sum = int(df[num_col].sum()) if n_ads else 0
    rate = (num_sum / den_sum) if den_sum != 0 else math.nan
    return rate, n_ads, den_sum


def pooled_roas(df: pd.DataFrame) -> tuple[float, int, int]:
    """Pooled ROAS = sum(revenue_inr) / sum(spend_inr)."""
    return pooled(df, REVENUE, SPEND)


def pooled_hook_rate(df: pd.DataFrame) -> tuple[float, int, int]:
    """Pooled hook rate = sum(video_3s_views) / sum(impressions)."""
    return pooled(df, VIDEO_3S, IMPRESSIONS)


def pooled_ctr(df: pd.DataFrame) -> tuple[float, int, int]:
    """Pooled CTR = sum(link_clicks) / sum(impressions)."""
    return pooled(df, LINK_CLICKS, IMPRESSIONS)


def pooled_cvr(df: pd.DataFrame) -> tuple[float, int, int]:
    """Pooled CVR = sum(purchases) / sum(link_clicks)."""
    return pooled(df, PURCHASES, LINK_CLICKS)


# ---------------------------------------------------------------------------
# Per-ad ROAS (for the median-based robustness check only)
# ---------------------------------------------------------------------------

def per_ad_roas(df: pd.DataFrame) -> pd.Series:
    """ROAS of each ad individually: revenue_inr / spend_inr."""
    return df[REVENUE] / df[SPEND]


def median_per_ad_roas(df: pd.DataFrame) -> float:
    """Median of the per-ad ROAS; NaN on an empty group."""
    if len(df) == 0:
        return math.nan
    return float(per_ad_roas(df).median())


# ---------------------------------------------------------------------------
# Comparison helpers
# ---------------------------------------------------------------------------

def difference(in_val: float, out_val: float) -> float:
    """In-group minus out-group."""
    return in_val - out_val


def sign(x: float) -> int:
    """+1 / -1 / 0. NaN and exact 0 both return 0 (treated as no agreement)."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return 0
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0
