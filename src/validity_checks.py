"""Post-hoc validity checks on the creator ranking.

POST-HOC, not pre-registered: the frozen result in creator_scores.csv remains the
primary ranking. Prompted by two construct-validity worries seen in the reading
pack: the child-and-product example posts (e.g. CR-12) do not show a child
reacting to food, and several top-engagement posts are "comment for link" posts.

Part 1 flags link-request posts from their captions and recomputes
audience_response with those posts removed, holding evidence_fit and
sponsored_fit at their frozen scores, and reports frozen vs new rank for all 20.
Part 2 lists the child-and-product example posts for manual inspection. It
reports and ranks only: no five are selected, no causal language, no judgement.

All scoring logic and parameters are imported from src/score_creators.py (never
edited). Outputs (outputs/creators/): link_request_posts.csv, link_sensitivity.csv,
proxy_check.md, validity_summary.md.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

import score_creators as sc

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "outputs" / "creators"

# Captions asking viewers to comment to get a link. Matches "Comment for link"
# and variants such as "comment LINK to get it", "Comment LINKS and I'll share".
LINK_REQUEST_REGEX = re.compile(r"\bcomment\b[^\n]{0,40}?\blinks?\b", re.IGNORECASE)

W = sc.W
AUD_MIN_POSTS = sc.AUD_MIN_POSTS
NEUTRAL = sc.NEUTRAL

LABEL = ("post-hoc validity check, not pre-registered; the frozen "
         "creator_scores.csv remains the primary ranking")
MOTIVATION = ("the child-and-product example posts (e.g. CR-12) do not show a "
              "child reacting to food, and several top-engagement posts are "
              "\"comment for link\" posts")

CHILD_PRODUCT_REASON = "a_recent_child_and_product"

_sum: list[str] = []


def sline(text: str = "") -> None:
    _sum.append(text)


def has_text(v) -> bool:
    return pd.notna(v) and str(v).strip() != ""


def rank_desc(comp: pd.Series) -> pd.Series:
    """Rank by composite descending, ties broken by creator_id ascending."""
    order = (comp.rename_axis("creator_id").rename("comp").reset_index()
             .sort_values(["comp", "creator_id"], ascending=[False, True])
             .reset_index(drop=True))
    order["rank"] = np.arange(1, len(order) + 1)
    return order.set_index("creator_id")["rank"]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scores = pd.read_csv(OUT_DIR / "creator_scores.csv").set_index("creator_id")
    rp_posts = pd.read_csv(OUT_DIR / "reading_pack_posts.csv")
    posts = pd.read_csv(DATA_DIR / "creator_posts.csv")
    posts["posted_on"] = pd.to_datetime(posts["posted_on"])

    anchor = posts["posted_on"].max()
    start = anchor - pd.DateOffset(months=sc.LENGTH_MONTHS)
    win = posts[(posts["posted_on"] >= start) & (posts["posted_on"] <= anchor)].copy()

    ids = sorted(scores.index.tolist())

    # ---- Part 1: flag link-request posts -----------------------------------
    cap = win["caption"].fillna("")
    matches = cap.apply(lambda c: LINK_REQUEST_REGEX.search(c))
    win["is_link_request"] = matches.notna()

    lr_rows = []
    for row, m in zip(win.itertuples(), matches):
        if m is None:
            continue
        lr_rows.append({
            "creator_id": row.creator_id, "handle": row.handle,
            "post_url": row.post_url,
            "posted_on": row.posted_on.date().isoformat(),
            "content_type": row.content_type,
            "matched_snippet": m.group().strip(),
        })
    lr_df = pd.DataFrame(lr_rows, columns=[
        "creator_id", "handle", "post_url", "posted_on", "content_type",
        "matched_snippet",
    ]).sort_values(["creator_id", "posted_on", "post_url"]).reset_index(drop=True)
    lr_df.to_csv(OUT_DIR / "link_request_posts.csv", index=False)

    # ---- Part 1: recompute audience_response excluding link-request posts ---
    raw_excl, status_excl, n_excl, n_lr, n_win = {}, {}, {}, {}, {}
    for cid in ids:
        cp = win[win["creator_id"] == cid]
        n_win[cid] = int(len(cp))
        n_lr[cid] = int(cp["is_link_request"].sum())
        kept = cp[~cp["is_link_request"]]
        eng = sc.engagement(kept)              # (comments+reshares)/plays, plays only
        n_excl[cid] = int(len(eng))
        if n_excl[cid] >= AUD_MIN_POSTS:
            raw_excl[cid] = float(eng.median())
            status_excl[cid] = "ok"
        else:
            raw_excl[cid] = np.nan
            status_excl[cid] = "insufficient"

    ar_score_excl = sc.percentile_scores(pd.Series(raw_excl), pd.Series(status_excl))

    ev = scores["evidence_fit_score"]
    sf = scores["sponsored_fit_score"]
    comp_frozen = (W["evidence_fit"] * ev + W["audience_response"] * scores["audience_response_score"]
                   + W["sponsored_fit"] * sf)
    comp_excl = (W["evidence_fit"] * ev + W["audience_response"] * ar_score_excl
                 + W["sponsored_fit"] * sf)
    rank_frozen = rank_desc(comp_frozen)
    rank_excl = rank_desc(comp_excl)

    ls_rows = []
    for cid in ids:
        ls_rows.append({
            "creator_id": cid, "handle": scores.loc[cid, "handle"],
            "n_posts_window": n_win[cid],
            "n_link_request": n_lr[cid],
            "link_request_share": round(n_lr[cid] / n_win[cid], 4) if n_win[cid] else 0.0,
            "n_posts_with_plays_frozen": int(scores.loc[cid, "n_posts_with_plays"]),
            "n_posts_with_plays_excl": n_excl[cid],
            "audience_response_raw_frozen": (
                "" if pd.isna(scores.loc[cid, "audience_response_raw"])
                else round(float(scores.loc[cid, "audience_response_raw"]), 6)),
            "audience_response_raw_excl": (
                "" if pd.isna(raw_excl[cid]) else round(raw_excl[cid], 6)),
            "audience_response_status_excl": status_excl[cid],
            "audience_response_score_frozen": round(float(scores.loc[cid, "audience_response_score"]), 6),
            "audience_response_score_excl": round(float(ar_score_excl[cid]), 6),
            "composite_frozen": round(float(comp_frozen[cid]), 6),
            "rank_frozen": int(rank_frozen[cid]),
            "composite_excl": round(float(comp_excl[cid]), 6),
            "rank_excl": int(rank_excl[cid]),
            "rank_change": int(rank_frozen[cid]) - int(rank_excl[cid]),
        })
    ls_df = (pd.DataFrame(ls_rows).sort_values("rank_frozen").reset_index(drop=True))
    ls_df.to_csv(OUT_DIR / "link_sensitivity.csv", index=False)

    # ---- Part 2: proxy checklist of child-and-product example posts --------
    cp_posts = rp_posts[rp_posts["reasons"].str.contains(CHILD_PRODUCT_REASON)]
    post_lookup = posts.set_index("post_url")
    write_proxy(cp_posts, post_lookup, scores)

    # ---- Summary -----------------------------------------------------------
    write_summary(ls_df, lr_df, cp_posts, start, anchor, len(win))

    print("Wrote to", OUT_DIR)
    for p in ["link_request_posts.csv", "link_sensitivity.csv", "proxy_check.md",
              "validity_summary.md"]:
        print(" -", p)


def write_proxy(cp_posts, post_lookup, scores) -> None:
    lines = ["# Proxy checklist — child-and-product example posts", ""]
    lines.append(LABEL + ".")
    lines.append("")
    lines.append("The posts the reading pack selected under rule (a) "
                 "children_on_camera=yes AND product_shown=yes, listed for manual "
                 "inspection of whether a child is actually shown reacting to the "
                 "product/food. Facts only — no judgement, no score.")
    lines.append("")
    # Group by creator in frozen composite-rank order.
    order = sorted(cp_posts["creator_id"].unique(),
                   key=lambda c: int(scores.loc[c, "composite_rank"]))
    for cid in order:
        sub = cp_posts[cp_posts["creator_id"] == cid]
        handle = sub.iloc[0]["handle"]
        lines.append(f"## {int(scores.loc[cid, 'composite_rank'])}. {cid} — {handle}")
        lines.append("")
        for i, (_, r) in enumerate(sub.iterrows(), start=1):
            row = post_lookup.loc[r["post_url"]]
            caption = str(row["caption"]) if has_text(row["caption"]) else "(none)"
            caption = " ".join(caption.split())[:200]
            lines.append(f"{i}. {cid} post {i} · {r['posted_on']}")
            lines.append(f"   - caption: {caption}")
            lines.append(f"   - what_stands_out: {row['what_stands_out']}")
            lines.append(f"   - post_url: {r['post_url']}")
        lines.append("")
    (OUT_DIR / "proxy_check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_summary(ls_df, lr_df, cp_posts, start, anchor, n_window_posts) -> None:
    n_cre = len(ls_df)
    part1 = n_window_posts + n_cre      # posts scanned + creators re-scored
    part2 = len(cp_posts)
    sline(f"# Creator ranking — {LABEL}")
    sline()
    sline(f"Motivation: {MOTIVATION}. The frozen ranking in creator_scores.csv is "
          f"unchanged; this file only probes its validity. Ranks only — no five "
          f"are selected, no causal language.")
    sline()
    sline(f"Window: {start.date()} to {anchor.date()} inclusive "
          f"({sc.LENGTH_MONTHS} months). Window posts: n={n_window_posts}. "
          f"Creators: n={n_cre}. Scoring functions, weights and the audience "
          f"floor are imported from score_creators.")
    sline()
    sline("## Comparisons run")
    sline()
    sline(f"Total: **{part1 + part2}** = Part 1: {n_window_posts} window posts "
          f"scanned for link-requests + {n_cre} creators re-scored on "
          f"audience_response excluding link-request posts; Part 2: {part2} "
          f"child-and-product posts listed.")
    sline()
    sline("## Part 1 — link-request posts and audience_response sensitivity")
    sline()
    sline(f"Link-request posts flagged by the caption regex "
          f"`{LINK_REQUEST_REGEX.pattern}` (case-insensitive); {len(lr_df)} window "
          f"posts flagged, listed with matched snippets in link_request_posts.csv "
          f"for false-positive review. audience_response recomputed excluding them "
          f"(same median, same >={AUD_MIN_POSTS} posts-with-plays floor, neutral "
          f"0.5 otherwise); evidence_fit and sponsored_fit held at frozen scores.")
    sline()
    for r in ls_df.itertuples():
        ar_fr = (f"{r.audience_response_raw_frozen}"
                 if r.audience_response_raw_frozen != "" else "NA")
        ar_ex = (f"{r.audience_response_raw_excl}"
                 if r.audience_response_raw_excl != "" else "NA")
        sline(f"- **{r.creator_id}** ({r.handle}): link-request "
              f"{r.n_link_request}/{r.n_posts_window} "
              f"({r.link_request_share:.1%}); audience_response median frozen="
              f"{ar_fr} (n={r.n_posts_with_plays_frozen} posts w/ plays) -> excl="
              f"{ar_ex} (n={r.n_posts_with_plays_excl}, {r.audience_response_status_excl}); "
              f"rank {r.rank_frozen} -> {r.rank_excl} (change {r.rank_change:+d})")
    sline()
    sline("## Part 2 — proxy checklist")
    sline()
    sline(f"{part2} child-and-product example posts listed in proxy_check.md for "
          f"manual inspection.")
    sline()
    sline("Full detail: link_request_posts.csv, link_sensitivity.csv, proxy_check.md.")
    (OUT_DIR / "validity_summary.md").write_text("\n".join(_sum) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
