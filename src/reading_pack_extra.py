"""Manual reading-list additions and child-presenter share — presentation only.

POST-HOC, not pre-registered; presentation only; no scores, no ranking, no
recommendation of any five, no causal language. The content scan showed the
reading list under-represented child-led and nutrition-authority creators, so a
few creators are added by hand here in the same four-section reading-pack
layout, and child-presenter share is reported for all 20.

The reading-pack layout helpers that are importable (has_text, the profile-field
list and the transcript length) are imported from src/reading_pack.py; its
section and example-post logic lives inside its main() and is reproduced here
unchanged (the reading-pack script is not edited).

Outputs (outputs/creators/): reading_pack_extra.md, reading_pack_extra_posts.csv,
child_presenter_share.csv.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from reading_pack import PROFILE_FIELDS, TRANSCRIPT_CHARS, has_text

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"
OUT_DIR = ROOT / "outputs" / "creators"

EXTRA_CREATORS = ["CR-03", "CR-05", "CR-20"]
# Added by Keshav after the content scan, because child-led and nutrition-authority
# creators were under-represented in the original reading list.

CHILD_PRESENTER_AGES = {"3-7", "8-12", "13-17"}
# presenter_age buckets treated as a child presenter (the only child buckets in the data).

_md: list[str] = []


def line(text: str = "") -> None:
    _md.append(text)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scores = pd.read_csv(OUT_DIR / "creator_scores.csv").set_index("creator_id")
    sens = pd.read_csv(OUT_DIR / "sensitivity.csv").set_index("creator_id")
    boot = pd.read_csv(OUT_DIR / "bootstrap_top5.csv").set_index("creator_id")
    creators = pd.read_csv(DATA_DIR / "creators.csv").set_index("creator_id")
    posts = pd.read_csv(DATA_DIR / "creator_posts.csv")
    posts["posted_on"] = pd.to_datetime(posts["posted_on"])

    length_months = int(
        yaml.safe_load((CONFIG_DIR / "weights.yaml").read_text(encoding="utf-8"))
        ["window"]["length_months"]
    )
    anchor = posts["posted_on"].max()
    start = anchor - pd.DateOffset(months=length_months)
    win = posts[(posts["posted_on"] >= start) & (posts["posted_on"] <= anchor)].copy()

    post_rows: list[dict] = []

    line("# Creator reading pack — additions")
    line()
    line("post-hoc, not pre-registered; presentation only; no scores, no "
         "ranking, no recommendation of any five. Scores, statuses and counts "
         "are read back from the existing outputs; profile text is quoted "
         "verbatim from creators.csv; example posts are selected by the same "
         "fixed rules as the original reading pack. No causal language.")
    line()
    line(f"Window: {start.date()} to {anchor.date()} inclusive ({length_months} "
         f"months). Added creators (EXTRA_CREATORS): {', '.join(EXTRA_CREATORS)} — "
         f"added by hand after the content scan because child-led and "
         f"nutrition-authority creators were under-represented in the original "
         f"reading list.")
    line()

    for cid in EXTRA_CREATORS:
        s = scores.loc[cid]
        prof = creators.loc[cid]
        cp = win[win["creator_id"] == cid].copy()
        n_win = int(s["n_posts_window"])

        line("---")
        line()
        line(f"## {int(s['composite_rank'])}. {cid} — {s['handle']}")
        line()

        # --- Section 1: scores line (read from CSVs) ---
        flags = [name for name, col in [
            ("hidden_likes", "flag_hidden_likes"),
            ("no_audience_data", "flag_no_audience_data"),
            ("legal_review", "flag_legal_review")] if bool(s[col])]

        def raw(col, n):
            v = s[f"{col}_raw"]
            txt = "NA" if pd.isna(v) else f"{float(v):.4f}"
            return f"{txt} (n={int(n)}, {s[f'{col}_status']})"

        line("**Scores** (read from creator_scores.csv; not recomputed):")
        line(f"- frozen rank {int(s['composite_rank'])}, composite "
             f"{float(s['composite']):.4f}")
        line(f"- evidence_fit {raw('evidence_fit', s['n_posts_window'])}; "
             f"audience_response {raw('audience_response', s['n_posts_with_plays'])}; "
             f"sponsored_fit {raw('sponsored_fit', s['n_sponsored'])}")
        line(f"- flags: {', '.join(flags) if flags else 'none'}; followers "
             f"{int(prof['followers']):,} (context only)")
        line(f"- sensitivity top5_class: {sens.loc[cid, 'top5_class']}; bootstrap "
             f"top5_share: {boot.loc[cid, 'top5_share']:.1%}")
        line()

        # --- Section 2: verbatim profile ---
        line("**Profile (verbatim quotes from creators.csv):**")
        for f in PROFILE_FIELDS:
            v = prof[f]
            if f == "bio" and not has_text(v):
                line(f"- {f}: (no bio)")
            else:
                line(f"- {f}: {v}")
        line()

        # --- Section 3: window-post mix ---
        line(f"**Window-post mix** (n={n_win} window posts):")
        for dim in ["content_type", "language", "hook_style"]:
            vc = cp[dim].value_counts(dropna=False)
            parts = "; ".join(
                f"{'(missing)' if pd.isna(k) else k}={int(v)}" for k, v in vc.items()
            )
            line(f"- {dim}: {parts} (n={n_win})")
        child_yes = int((cp["children_on_camera"] == "yes").sum())
        prod_yes = int((cp["product_shown"] == "yes").sum())
        spon_vc = cp["is_sponsored"].value_counts(dropna=False)
        spon_yes = int(spon_vc.get("yes", 0))
        tr = int(cp["transcript"].map(has_text).sum())
        line(f"- children_on_camera=yes: {child_yes}/{n_win} "
             f"({child_yes / n_win:.1%})" if n_win else "- children_on_camera=yes: n=0")
        line(f"- product_shown=yes: {prod_yes}/{n_win} ({prod_yes / n_win:.1%})")
        line("- is_sponsored: "
             + "; ".join(f"{k}={int(v)}" for k, v in spon_vc.items())
             + f"; yes share {spon_yes}/{n_win} ({spon_yes / n_win:.1%})")
        line(f"- transcripts available: {tr}/{n_win} ({tr / n_win:.1%})")
        line()

        # --- Section 4: example posts chosen by rule ---
        cp["engagement_ratio"] = (
            (cp["comments"] + cp["reshares"]) / cp["plays"]
        ).where(cp["plays"].notna() & (cp["plays"] > 0))

        a = cp[(cp["children_on_camera"] == "yes") & (cp["product_shown"] == "yes")]
        a = a.sort_values(["posted_on", "post_url"], ascending=[False, True]).head(3)
        b = cp[cp["engagement_ratio"].notna()].sort_values(
            ["engagement_ratio", "post_url"], ascending=[False, True]).head(2)
        c = cp[cp["is_sponsored"] == "yes"].sort_values(
            ["posted_on", "post_url"], ascending=[False, True]).head(2)

        selections: dict[str, list[str]] = {}
        order: list[str] = []
        for df_sel, reason in [(a, "a_recent_child_and_product"),
                               (b, "b_top_engagement"),
                               (c, "c_recent_sponsored")]:
            for url in df_sel["post_url"]:
                if url not in selections:
                    selections[url] = []
                    order.append(url)
                selections[url].append(reason)

        line("**Example posts (chosen by rule, not by preference):**")
        line(f"- rule (a) 3 most recent children_on_camera=yes AND "
             f"product_shown=yes: {len(a)} shown.")
        line(f"- rule (b) 2 highest (comments+reshares)/plays among posts with "
             f"plays: {len(b)} shown.")
        n_spon = int((cp['is_sponsored'] == 'yes').sum())
        if n_spon == 0:
            line("- rule (c) 2 most recent sponsored posts: 0 shown (no sponsored "
                 "posts in window).")
        elif n_spon < 2:
            line(f"- rule (c) 2 most recent sponsored posts: {len(c)} shown (only "
                 f"{n_spon} sponsored post in window).")
        else:
            line(f"- rule (c) 2 most recent sponsored posts: {len(c)} shown.")
        line()

        for url in order:
            row = cp[cp["post_url"] == url].iloc[0]
            reasons = selections[url]
            tr_cell = row["transcript"]
            tr_txt = (str(tr_cell)[:TRANSCRIPT_CHARS] if has_text(tr_cell)
                      else "no transcript")
            line(f"- **{row['posted_on'].date()}** · {row['content_type']} · "
                 f"reasons: {', '.join(reasons)}")
            line(f"  - post_url: {url}")
            line(f"  - caption: {row['caption'] if has_text(row['caption']) else '(none)'}")
            line(f"  - what_stands_out: {row['what_stands_out']}")
            line(f"  - transcript (first {TRANSCRIPT_CHARS} chars): {tr_txt}")
            post_rows.append({
                "creator_id": cid, "handle": s["handle"],
                "frozen_rank": int(s["composite_rank"]),
                "post_url": url,
                "posted_on": row["posted_on"].date().isoformat(),
                "content_type": row["content_type"],
                "is_sponsored": row["is_sponsored"],
                "children_on_camera": row["children_on_camera"],
                "product_shown": row["product_shown"],
                "engagement_ratio": ("" if pd.isna(row["engagement_ratio"])
                                     else round(float(row["engagement_ratio"]), 6)),
                "transcript_present": has_text(tr_cell),
                "reasons": ";".join(reasons),
            })
        line()

    pd.DataFrame(post_rows, columns=[
        "creator_id", "handle", "frozen_rank", "post_url", "posted_on",
        "content_type", "is_sponsored", "children_on_camera", "product_shown",
        "engagement_ratio", "transcript_present", "reasons",
    ]).sort_values(["frozen_rank", "reasons", "post_url"]).reset_index(drop=True) \
        .to_csv(OUT_DIR / "reading_pack_extra_posts.csv", index=False)

    # ---- Part 2: child-presenter share, all 20 creators --------------------
    cps_rows = []
    for cid in sorted(scores.index):
        cp = win[win["creator_id"] == cid]
        n_win = int(len(cp))
        is_child = cp["presenter_age"].isin(CHILD_PRESENTER_AGES)
        n_child = int(is_child.sum())
        n_child_spon = int((is_child & (cp["is_sponsored"] == "yes")).sum())
        cps_rows.append({
            "creator_id": cid, "handle": scores.loc[cid, "handle"],
            "n_posts_window": n_win,
            "n_child_presenter": n_child,
            "child_presenter_share": round(n_child / n_win, 4) if n_win else 0.0,
            "n_child_presenter_sponsored": n_child_spon,
        })
    cps_df = pd.DataFrame(cps_rows)
    cps_df.to_csv(OUT_DIR / "child_presenter_share.csv", index=False)

    line("---")
    line()
    line("## Child-presenter share (all 20 creators, window)")
    line()
    line(f"Posts whose presenter_age is in {sorted(CHILD_PRESENTER_AGES)}, over "
         f"the window. Each rate carries its n. Facts only.")
    line()
    line("| creator_id | handle | n_window | n_child_presenter | share | n_sponsored |")
    line("|---|---|---|---|---|---|")
    for r in cps_df.itertuples():
        line(f"| {r.creator_id} | {r.handle} | {r.n_posts_window} | "
             f"{r.n_child_presenter} | {r.child_presenter_share:.1%} | "
             f"{r.n_child_presenter_sponsored} |")
    line()
    line("Full detail: reading_pack_extra_posts.csv, child_presenter_share.csv.")

    (OUT_DIR / "reading_pack_extra.md").write_text(
        "\n".join(_md) + "\n", encoding="utf-8")

    print("Wrote to", OUT_DIR)
    for p in ["reading_pack_extra.md", "reading_pack_extra_posts.csv",
              "child_presenter_share.csv"]:
        print(" -", p)


if __name__ == "__main__":
    main()
