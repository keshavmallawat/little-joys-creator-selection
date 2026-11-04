"""Post-hoc content scan of creator posts for food/feeding mentions.

POST-HOC, not pre-registered. Prompted by a hand check finding that only 2 of 24
child-and-product example posts in the reading pack show a child eating or
reacting to food: the evidence_fit proxy (children_on_camera AND product_shown)
does not measure feeding content. This scan describes how often each creator's
window posts mention food/feeding terms, lists those posts, and tallies the
brands that appear. It is presentation only: no scores, no ranking, no
recommendation, no causal language.

Outputs (outputs/creators/): food_scan.csv, food_scan_posts.csv, food_scan.md,
brands_by_creator.csv, brands.md, content_scan_summary.md.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"
OUT_DIR = ROOT / "outputs" / "creators"

# Named food/feeding term list. Matched case-insensitively on word boundaries so
# "great" does not match "eat" and "proteins" does not match "protein";
# multi-word terms (e.g. "health drink") match as a phrase.
FOOD_TERMS = [
    "milk", "nutrition", "nutritious", "protein", "weaning", "solids",
    "porridge", "cereal", "puree", "formula", "health drink", "snack",
    "recipe", "tiffin", "lunchbox", "breakfast", "gummy", "gummies",
    "vitamin", "supplement", "complan", "horlicks", "bournvita", "pediasure",
    "gritzo", "cerelac", "malt", "doodh",
]
TERM_RE = {t: re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE)
           for t in FOOD_TERMS}

SCAN_FIELDS = ["topic", "caption", "what_stands_out", "hook_style", "brands_visible"]
DETAIL_MIN_MATCHED = 3  # a creator with this many matched posts joins the detail set
CAPTION_CHARS = 150


def term_slug(t: str) -> str:
    return "term_" + t.replace(" ", "_")


def post_text(row: pd.Series) -> str:
    return " ".join(str(row[f]) for f in SCAN_FIELDS if pd.notna(row[f]))


def matched_terms(text: str) -> list[str]:
    return [t for t in FOOD_TERMS if TERM_RE[t].search(text)]


def one_line(s: str, n: int) -> str:
    return " ".join(str(s).split())[:n] if pd.notna(s) and str(s).strip() else "(none)"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    posts = pd.read_csv(DATA_DIR / "creator_posts.csv")
    posts["posted_on"] = pd.to_datetime(posts["posted_on"])
    rp_posts = pd.read_csv(OUT_DIR / "reading_pack_posts.csv")

    length = int(
        yaml.safe_load((CONFIG_DIR / "weights.yaml").read_text(encoding="utf-8"))
        ["window"]["length_months"]
    )
    anchor = posts["posted_on"].max()
    start = anchor - pd.DateOffset(months=length)
    win = posts[(posts["posted_on"] >= start) & (posts["posted_on"] <= anchor)].copy()

    win["scan_text"] = win.apply(post_text, axis=1)
    win["match_terms"] = win["scan_text"].apply(matched_terms)
    win["is_match"] = win["match_terms"].map(len) > 0

    ids = sorted(win["creator_id"].unique().tolist())
    handle_of = win.groupby("creator_id")["handle"].first()

    # ---- food_scan.csv: all 20 creators ------------------------------------
    scan_rows = []
    for cid in ids:
        cp = win[win["creator_id"] == cid]
        n_win = int(len(cp))
        n_matched = int(cp["is_match"].sum())
        row = {
            "creator_id": cid, "handle": handle_of[cid],
            "n_posts_window": n_win, "n_matched_posts": n_matched,
            "matched_share": round(n_matched / n_win, 4) if n_win else 0.0,
        }
        for t in FOOD_TERMS:
            row[term_slug(t)] = int(cp["scan_text"].apply(
                lambda x: bool(TERM_RE[t].search(x))).sum())
        scan_rows.append(row)
    scan_df = pd.DataFrame(scan_rows)
    scan_df.to_csv(OUT_DIR / "food_scan.csv", index=False)

    # ---- detail set: reading-pack creators UNION (>=3 matched) -------------
    reading_pack = set(rp_posts["creator_id"].unique())
    ge3 = {cid for cid in ids
           if int(win[win["creator_id"] == cid]["is_match"].sum()) >= DETAIL_MIN_MATCHED}
    detail = sorted(reading_pack | ge3)

    dp_rows = []
    for cid in detail:
        cp = win[(win["creator_id"] == cid) & win["is_match"]]
        cp = cp.sort_values(["posted_on", "post_url"])
        for r in cp.itertuples():
            dp_rows.append({
                "creator_id": cid, "handle": handle_of[cid],
                "posted_on": r.posted_on.date().isoformat(),
                "matched_terms": ";".join(r.match_terms),
                "caption_150": one_line(r.caption, CAPTION_CHARS),
                "what_stands_out": r.what_stands_out,
                "is_sponsored": r.is_sponsored,
                "children_on_camera": r.children_on_camera,
                "post_url": r.post_url,
            })
    dp_df = pd.DataFrame(dp_rows, columns=[
        "creator_id", "handle", "posted_on", "matched_terms", "caption_150",
        "what_stands_out", "is_sponsored", "children_on_camera", "post_url",
    ])
    dp_df.to_csv(OUT_DIR / "food_scan_posts.csv", index=False)
    write_food_md(dp_df, detail, reading_pack, ge3, handle_of)

    # ---- brands_by_creator.csv: all 20 creators ----------------------------
    br_rows = []
    for cid in ids:
        cp = win[win["creator_id"] == cid]
        tally: dict[str, dict] = {}
        for r in cp.itertuples():
            if pd.isna(r.brands_visible):
                continue
            brands = {b.strip() for b in str(r.brands_visible).split(";")
                      if b.strip()}
            for b in brands:
                d = tally.setdefault(b, {"n_posts": 0, "n_sponsored": 0})
                d["n_posts"] += 1
                if r.is_sponsored == "yes":
                    d["n_sponsored"] += 1
        for b in sorted(tally):
            br_rows.append({
                "creator_id": cid, "handle": handle_of[cid], "brand": b,
                "n_posts": tally[b]["n_posts"],
                "n_sponsored": tally[b]["n_sponsored"],
            })
    br_df = pd.DataFrame(br_rows, columns=[
        "creator_id", "handle", "brand", "n_posts", "n_sponsored"])
    br_df.to_csv(OUT_DIR / "brands_by_creator.csv", index=False)
    write_brands_md(br_df, ids, handle_of)

    write_summary(scan_df, dp_df, br_df, detail, reading_pack, ge3,
                  start, anchor, len(win))

    print("Wrote to", OUT_DIR)
    for p in ["food_scan.csv", "food_scan_posts.csv", "food_scan.md",
              "brands_by_creator.csv", "brands.md", "content_scan_summary.md"]:
        print(" -", p)


def write_food_md(dp_df, detail, reading_pack, ge3, handle_of) -> None:
    out = ["# Food/feeding content scan — matched posts",
           "", "post-hoc content scan, not pre-registered.", ""]
    out.append("Detail set = the reading-pack creators plus any creator with "
               f">= {DETAIL_MIN_MATCHED} matched posts. Posts whose topic, caption, "
               "what_stands_out, hook_style or brands_visible match a FOOD_TERMS "
               "entry (word boundaries, case-insensitive). Facts only.")
    out.append("")
    for cid in detail:
        tag = ("reading pack + >=3 matched" if cid in reading_pack and cid in ge3
               else "reading pack" if cid in reading_pack else ">=3 matched")
        sub = dp_df[dp_df["creator_id"] == cid]
        out.append(f"## {cid} — {handle_of[cid]} ({tag}): {len(sub)} matched post(s)")
        out.append("")
        for r in sub.itertuples():
            out.append(f"- {r.posted_on} · terms: {r.matched_terms} · "
                       f"is_sponsored={r.is_sponsored}, "
                       f"children_on_camera={r.children_on_camera}")
            out.append(f"  - caption: {r.caption_150}")
            out.append(f"  - what_stands_out: {r.what_stands_out}")
            out.append(f"  - post_url: {r.post_url}")
        out.append("")
    (OUT_DIR / "food_scan.md").write_text("\n".join(out) + "\n", encoding="utf-8")


def write_brands_md(br_df, ids, handle_of) -> None:
    out = ["# Brands visible by creator (window)",
           "", "post-hoc content scan, not pre-registered. brands_visible split "
           "on ';' over window posts; counts carry the number of posts and how "
           "many were sponsored. Facts only.", ""]
    for cid in ids:
        sub = br_df[br_df["creator_id"] == cid]
        out.append(f"## {cid} — {handle_of[cid]}: {len(sub)} distinct brand(s)")
        if len(sub) == 0:
            out.append("- (no brands_visible in window)")
        for r in sub.itertuples():
            out.append(f"- {r.brand}: n_posts={r.n_posts} (sponsored "
                       f"{r.n_sponsored})")
        out.append("")
    (OUT_DIR / "brands.md").write_text("\n".join(out) + "\n", encoding="utf-8")


def write_summary(scan_df, dp_df, br_df, detail, reading_pack, ge3,
                  start, anchor, n_win) -> None:
    n_cre = len(scan_df)
    post_term_checks = n_win * len(FOOD_TERMS)
    out = ["# Creator content scan — post-hoc content scan, not pre-registered",
           ""]
    out.append("Motivation: a hand check found only 2 of 24 child-and-product "
               "example posts show a child eating or reacting to food, so the "
               "evidence_fit proxy (children_on_camera AND product_shown) does "
               "not measure feeding content. Presentation only: no scores, no "
               "ranking, no five selected, no causal language.")
    out.append("")
    out.append(f"Window: {start.date()} to {anchor.date()} inclusive. Window "
               f"posts: n={n_win}. Creators: n={n_cre}.")
    out.append("")
    out.append("## Comparisons run")
    out.append("")
    out.append(f"Total post-term checks: **{post_term_checks}** = {n_win} window "
               f"posts x {len(FOOD_TERMS)} food terms over {len(SCAN_FIELDS)} text "
               f"fields. Brand tallies computed for all {n_cre} creators "
               f"({len(br_df)} creator-brand rows).")
    out.append("")
    out.append("## Per-creator food-term match share (n beside every rate)")
    out.append("")
    for r in scan_df.itertuples():
        out.append(f"- {r.creator_id} ({r.handle}): matched "
                   f"{r.n_matched_posts}/{r.n_posts_window} "
                   f"({r.matched_share:.1%})")
    out.append("")
    out.append("## Detail set (matched posts listed in food_scan_posts.csv / "
               "food_scan.md)")
    out.append("")
    out.append(f"{len(detail)} creators = reading-pack creators "
               f"({len(reading_pack)}) UNION creators with >= {DETAIL_MIN_MATCHED} "
               f"matched posts ({', '.join(sorted(ge3))}): "
               f"{', '.join(detail)}.")
    out.append("")
    out.append("Full detail: food_scan.csv, food_scan_posts.csv, food_scan.md, "
               "brands_by_creator.csv, brands.md.")
    (OUT_DIR / "content_scan_summary.md").write_text(
        "\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
