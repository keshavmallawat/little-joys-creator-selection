"""Reading pack for the shortlisted creators — presentation only.

For the creators that survived either robustness view, this lays out their
stored scores, their profile text verbatim, their window-post mix, and a few
example posts chosen by fixed rules, so the material can be read directly. It
computes no score, makes no judgement, recommends no creators, and uses no
causal language. Scores and counts are read back from the existing outputs; only
the post-mix counts and the example-post selection are derived, straight from the
post rows.

Outputs (outputs/creators/): reading_pack.md, reading_pack_posts.csv.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"
OUT_DIR = ROOT / "outputs" / "creators"

# Reading-list rule chosen by Keshav after seeing the sensitivity results,
# not a scoring rule.
READING_LIST_MIN_TOP5_SHARE = 0.25

PROFILE_FIELDS = [
    "persona", "persona_description", "voice", "language_use", "catchphrases",
    "themes", "format_habits", "what_feels_native", "what_would_feel_foreign",
    "audience_read", "bio",
]

TRANSCRIPT_CHARS = 500

_md: list[str] = []


def line(text: str = "") -> None:
    _md.append(text)


def has_text(v) -> bool:
    return pd.notna(v) and str(v).strip() != ""


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

    # Inclusion: survived either robustness view.
    included = [
        cid for cid in scores.index
        if sens.loc[cid, "top5_class"] != "none"
        or boot.loc[cid, "top5_share"] >= READING_LIST_MIN_TOP5_SHARE
    ]
    included.sort(key=lambda c: int(scores.loc[c, "composite_rank"]))

    post_rows: list[dict] = []

    line("# Creator reading pack")
    line()
    line("Presentation only. Scores, statuses and counts are read back from "
         "creator_scores.csv, sensitivity.csv and bootstrap_top5.csv; profile "
         "text is quoted verbatim from creators.csv; example posts are selected "
         "by fixed rules. No score is computed here, no creator is recommended, "
         "no causal language is used.")
    line()
    line(f"Window: {start.date()} to {anchor.date()} inclusive ({length_months} "
         f"months). Reading-list inclusion = sensitivity top5_class != 'none' OR "
         f"bootstrap top5_share >= {READING_LIST_MIN_TOP5_SHARE} (a reading-list "
         f"rule chosen after seeing the sensitivity results, not a scoring rule). "
         f"Included: {len(included)} of {len(scores)} creators, in frozen "
         f"composite-rank order.")
    line()

    for cid in included:
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

        # (a) 3 most recent child-and-product posts.
        a = cp[(cp["children_on_camera"] == "yes") & (cp["product_shown"] == "yes")]
        a = a.sort_values(["posted_on", "post_url"], ascending=[False, True]).head(3)
        # (b) 2 highest engagement posts with plays.
        b = cp[cp["engagement_ratio"].notna()].sort_values(
            ["engagement_ratio", "post_url"], ascending=[False, True]).head(2)
        # (c) 2 most recent sponsored posts.
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

    (OUT_DIR / "reading_pack.md").write_text("\n".join(_md) + "\n", encoding="utf-8")

    posts_df = pd.DataFrame(post_rows, columns=[
        "creator_id", "handle", "frozen_rank", "post_url", "posted_on",
        "content_type", "is_sponsored", "children_on_camera", "product_shown",
        "engagement_ratio", "transcript_present", "reasons",
    ]).sort_values(["frozen_rank", "reasons", "post_url"]).reset_index(drop=True)
    posts_df.to_csv(OUT_DIR / "reading_pack_posts.csv", index=False)

    print("Wrote to", OUT_DIR)
    print(" - reading_pack.md")
    print(" - reading_pack_posts.csv")
    print(f"included creators ({len(included)}): {', '.join(included)}")


if __name__ == "__main__":
    main()
