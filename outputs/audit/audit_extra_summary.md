# Supplementary data audit — Little Joys

Source: data/ (read-only). Reference live date: 2026-10-26. Facts only; no interpretation, ranking, or selection. No performance metric is computed broken down by label.

Rows loaded: ads=100, creators=20, creator_posts=392.

Comparisons run (5 sections): (1) one two-level days_live diff cross-tabbed on 3 dimensions; (2) 2 distributions + 7 threshold counts; (3) per-creator likes stats + 1 likes/plays ratio distribution; (4) 14 columns x 2 tables (literal + atomic); (5) per-creator transcript coverage + 3 placeholder checks.

## 1. days_live mismatch cross-tabs

diff = days_live - expected, where expected = (stopped_date or 2026-10-26) - launch_date.
Overall diff distribution (n=100): diff=-1: 74; diff=+0: 26.

- By stopped_date_ge_2026-10-26:
  - False (n=100): diff=-1: n=74; diff=+0: n=26
  - True (n=0): diff=-1: n=0; diff=+0: n=0
  - ad_ids per cell in audit_extra_days_live_crosstab.csv.
- By stopped_date:
  - 2026-08-23 (n=12): diff=-1: n=0; diff=+0: n=12
  - 2026-09-26 (n=17): diff=-1: n=17; diff=+0: n=0
  - 2026-10-03 (n=37): diff=-1: n=37; diff=+0: n=0
  - 2026-10-10 (n=8): diff=-1: n=6; diff=+0: n=2
  - 2026-10-16 (n=1): diff=-1: n=0; diff=+0: n=1
  - 2026-10-17 (n=14): diff=-1: n=14; diff=+0: n=0
  - 2026-10-21 (n=1): diff=-1: n=0; diff=+0: n=1
  - 2026-10-23 (n=10): diff=-1: n=0; diff=+0: n=10
  - ad_ids per cell in audit_extra_days_live_crosstab.csv.
- By launch_month:
  - 2026-06 (n=2): diff=-1: n=0; diff=+0: n=2
  - 2026-07 (n=2): diff=-1: n=0; diff=+0: n=2
  - 2026-08 (n=18): diff=-1: n=8; diff=+0: n=10
  - 2026-09 (n=69): diff=-1: n=62; diff=+0: n=7
  - 2026-10 (n=9): diff=-1: n=4; diff=+0: n=5
  - ad_ids per cell in audit_extra_days_live_crosstab.csv.

## 2. Exposure — purchases and link_clicks per ad

- Per-ad distributions (audit_extra_exposure_distributions.csv):
  - purchases: min=0.0, p25=21.75, p50=57.0, p75=123.25, p90=318.9, max=4868.0, mean=168.56 (n=100).
  - link_clicks: min=16.0, p25=792.75, p50=1895.0, p75=4810.25, p90=12010.3, max=69443.0, mean=5273.59 (n=100).
- Ads meeting exposure thresholds:
  - purchases >= 5: 96/100 = 96.0% (n=100).
  - purchases >= 10: 90/100 = 90.0% (n=100).
  - purchases >= 20: 78/100 = 78.0% (n=100).
  - purchases >= 50: 53/100 = 53.0% (n=100).
  - link_clicks >= 100: 98/100 = 98.0% (n=100).
  - link_clicks >= 500: 81/100 = 81.0% (n=100).
  - link_clicks >= 1000: 70/100 = 70.0% (n=100).

## 3. Hidden likes (per creator)

- Posts with likes <= 5: 10/392 = 2.6% (n=392).
- likes/plays computed only where plays > 0: n=353 of 392 posts (39 excluded for missing or zero plays).
- Per creator (audit_extra_hidden_likes_by_creator.csv):
  - CR-01 (n_posts=20): likes min=19, median=618; likes<=5: 0/20 = 0.0% (n=20); likes/play p50=0.008059 (n=20).
  - CR-02 (n_posts=20): likes min=3, median=40589; likes<=5: 1/20 = 5.0% (n=20); likes/play p50=0.045098 (n=19).
  - CR-03 (n_posts=20): likes min=1120, median=4524.5; likes<=5: 0/20 = 0.0% (n=20); likes/play p50=0.020993 (n=20).
  - CR-04 (n_posts=20): likes min=7641, median=44471; likes<=5: 0/20 = 0.0% (n=20); likes/play p50=0.053784 (n=13).
  - CR-05 (n_posts=20): likes min=80976, median=220130; likes<=5: 0/20 = 0.0% (n=20); likes/play p50=0.055161 (n=18).
  - CR-06 (n_posts=20): likes min=49465, median=205862; likes<=5: 0/20 = 0.0% (n=20); likes/play p50=0.045717 (n=19).
  - CR-07 (n_posts=20): likes min=89, median=295; likes<=5: 0/20 = 0.0% (n=20); likes/play p50=0.005915 (n=19).
  - CR-08 (n_posts=20): likes min=186, median=1600.5; likes<=5: 0/20 = 0.0% (n=20); likes/play p50=0.040197 (n=19).
  - CR-09 (n_posts=20): likes min=3, median=9316.5; likes<=5: 3/20 = 15.0% (n=20); likes/play p50=0.044639 (n=12).
  - CR-10 (n_posts=20): likes min=3089, median=9372; likes<=5: 0/20 = 0.0% (n=20); likes/play p50=0.017986 (n=19).
  - CR-11 (n_posts=20): likes min=4094, median=20415.5; likes<=5: 0/20 = 0.0% (n=20); likes/play p50=0.042271 (n=19).
  - CR-12 (n_posts=20): likes min=62, median=143.5; likes<=5: 0/20 = 0.0% (n=20); likes/play p50=0.009375 (n=20).
  - CR-13 (n_posts=20): likes min=282, median=3249; likes<=5: 0/20 = 0.0% (n=20); likes/play p50=0.023254 (n=16).
  - CR-14 (n_posts=20): likes min=471, median=2508; likes<=5: 0/20 = 0.0% (n=20); likes/play p50=0.009051 (n=19).
  - CR-15 (n_posts=20): likes min=53, median=471; likes<=5: 0/20 = 0.0% (n=20); likes/play p50=0.006516 (n=19).
  - CR-16 (n_posts=20): likes min=282, median=2128; likes<=5: 0/20 = 0.0% (n=20); likes/play p50=0.011041 (n=18).
  - CR-17 (n_posts=20): likes min=3, median=4518.5; likes<=5: 6/20 = 30.0% (n=20); likes/play p50=0.004537 (n=20).
  - CR-18 (n_posts=12): likes min=404, median=3396; likes<=5: 0/12 = 0.0% (n=12); likes/play p50=0.012258 (n=11).
  - CR-19 (n_posts=20): likes min=31, median=5409; likes<=5: 0/20 = 0.0% (n=20); likes/play p50=0.005755 (n=17).
  - CR-20 (n_posts=20): likes min=21254, median=136846; likes<=5: 0/20 = 0.0% (n=20); likes/play p50=0.061922 (n=16).

## 4. Label group sizes (ads.csv)

n = 100 ads. Each value row shows n_ads and, in brackets, the count with spend_inr >= 5000. Values with n_ads < 10 are flagged [low n].
Literal = whole-cell string. Atomic = cells split on ';' into single labels (an ad can contribute to several, so atomic n_ads may sum past 100). Full tables in audit_extra_label_counts_literal.csv and audit_extra_label_counts_atomic.csv.

- **child_on_screen** — 3 literal value(s), 3 atomic label(s).
  - literal:
    - one: n_ads=52 (spend>=5000: 48)
    - none: n_ads=37 (spend>=5000: 32)
    - multiple: n_ads=11 (spend>=5000: 10)
  - atomic: identical to literal (no ';'-compound cells).
- **child_in_first_3s** — 2 literal value(s), 2 atomic label(s).
  - literal:
    - no: n_ads=59 (spend>=5000: 51)
    - yes: n_ads=41 (spend>=5000: 39)
  - atomic: identical to literal (no ';'-compound cells).
- **child_role** — 15 literal value(s), 7 atomic label(s).
  - literal:
    - none: n_ads=37 (spend>=5000: 32)
    - speaks; consumes_product; reacts_to_taste: n_ads=19 (spend>=5000: 18)
    - + 13 value(s) each with n_ads < 10 [low n], covering 44 ads (see CSV)
  - atomic:
    - consumes_product: n_ads=54 (spend>=5000: 50)
    - reacts_to_taste: n_ads=39 (spend>=5000: 38)
    - none: n_ads=37 (spend>=5000: 32)
    - speaks: n_ads=25 (spend>=5000: 24)
    - on_screen_silent: n_ads=23 (spend>=5000: 20)
    - (missing): n_ads=2 (spend>=5000: 2) [low n]
    - shows_result: n_ads=2 (spend>=5000: 2) [low n]
- **brand_said_aloud** — 2 literal value(s), 2 atomic label(s).
  - literal:
    - yes: n_ads=70 (spend>=5000: 64)
    - no: n_ads=30 (spend>=5000: 26)
  - atomic: identical to literal (no ';'-compound cells).
- **brand_first_said** — 7 literal value(s), 7 atomic label(s).
  - literal:
    - under_3s: n_ads=40 (spend>=5000: 36)
    - 15_to_30s: n_ads=27 (spend>=5000: 25)
    - 5_to_10s: n_ads=15 (spend>=5000: 13)
    - + 4 value(s) each with n_ads < 10 [low n], covering 18 ads (see CSV)
  - atomic: identical to literal (no ';'-compound cells).
- **hook_type** — 11 literal value(s), 11 atomic label(s).
  - literal:
    - question: n_ads=28 (spend>=5000: 23)
    - story_open: n_ads=22 (spend>=5000: 18)
    - problem_statement: n_ads=14 (spend>=5000: 14)
    - + 8 value(s) each with n_ads < 10 [low n], covering 36 ads (see CSV)
  - atomic:
    - question: n_ads=28 (spend>=5000: 23)
    - story_open: n_ads=22 (spend>=5000: 18)
    - problem_statement: n_ads=14 (spend>=5000: 14)
    - visual_action: n_ads=7 (spend>=5000: 7) [low n]
    - educational_explainer: n_ads=6 (spend>=5000: 6) [low n]
    - direct_product: n_ads=6 (spend>=5000: 5) [low n]
    - personal_testimony: n_ads=6 (spend>=5000: 6) [low n]
    - pattern_interrupt: n_ads=3 (spend>=5000: 3) [low n]
    - bold_claim: n_ads=3 (spend>=5000: 3) [low n]
    - result_reveal: n_ads=3 (spend>=5000: 3) [low n]
    - (missing): n_ads=2 (spend>=5000: 2) [low n]
- **creator_type** — 8 literal value(s), 8 atomic label(s).
  - literal:
    - parent_or_caregiver: n_ads=57 (spend>=5000: 52)
    - none_visible: n_ads=15 (spend>=5000: 14)
    - multiple: n_ads=10 (spend>=5000: 7)
    - + 5 value(s) each with n_ads < 10 [low n], covering 18 ads (see CSV)
  - atomic:
    - parent_or_caregiver: n_ads=57 (spend>=5000: 52)
    - none_visible: n_ads=15 (spend>=5000: 14)
    - multiple: n_ads=10 (spend>=5000: 7)
    - child_presenter: n_ads=9 (spend>=5000: 9) [low n]
    - professional_presenter: n_ads=5 (spend>=5000: 5) [low n]
    - peer_reviewer: n_ads=2 (spend>=5000: 2) [low n]
    - medical_professional: n_ads=1 (spend>=5000: 1) [low n]
    - food_or_chef: n_ads=1 (spend>=5000: 0) [low n]
- **language_mixing** — 5 literal value(s), 5 atomic label(s).
  - literal:
    - occasional_borrowing: n_ads=54 (spend>=5000: 50)
    - single_language: n_ads=25 (spend>=5000: 19)
    - sentence_level_switching: n_ads=12 (spend>=5000: 12)
    - + 2 value(s) each with n_ads < 10 [low n], covering 9 ads (see CSV)
  - atomic: identical to literal (no ';'-compound cells).
- **ad_format** — 8 literal value(s), 8 atomic label(s).
  - literal:
    - voiceover_montage: n_ads=36 (spend>=5000: 33)
    - explainer_to_camera: n_ads=25 (spend>=5000: 22)
    - skit: n_ads=15 (spend>=5000: 13)
    - + 5 value(s) each with n_ads < 10 [low n], covering 24 ads (see CSV)
  - atomic: identical to literal (no ';'-compound cells).
- **proof_used** — 57 literal value(s), 14 atomic label(s).
  - literal:
    - + 57 value(s) each with n_ads < 10 [low n], covering 100 ads (see CSV)
  - atomic:
    - ingredient_dosage: n_ads=34 (spend>=5000: 30)
    - ingredient_potency: n_ads=33 (spend>=5000: 30)
    - texture_demonstration: n_ads=31 (spend>=5000: 29)
    - creator_testimonial: n_ads=23 (spend>=5000: 21)
    - child_visible_result: n_ads=14 (spend>=5000: 13)
    - clinical_specifications: n_ads=11 (spend>=5000: 8)
    - texture_sensory_visuals: n_ads=9 (spend>=5000: 8) [low n]
    - scientific_lab_visuals: n_ads=8 (spend>=5000: 8) [low n]
    - customer_review: n_ads=6 (spend>=5000: 6) [low n]
    - data_statistics: n_ads=6 (spend>=5000: 6) [low n]
    - lab_tested_certified: n_ads=6 (spend>=5000: 6) [low n]
    - none: n_ads=5 (spend>=5000: 5) [low n]
    - expert_endorsement: n_ads=1 (spend>=5000: 0) [low n]
    - other: n_ads=1 (spend>=5000: 1) [low n]
- **cta_type** — 8 literal value(s), 8 atomic label(s).
  - literal:
    - buy_now: n_ads=58 (spend>=5000: 54)
    - none: n_ads=32 (spend>=5000: 29)
    - + 6 value(s) each with n_ads < 10 [low n], covering 10 ads (see CSV)
  - atomic:
    - buy_now: n_ads=58 (spend>=5000: 54)
    - none: n_ads=32 (spend>=5000: 29)
    - social_interface_referral: n_ads=3 (spend>=5000: 3) [low n]
    - comment_for_link: n_ads=3 (spend>=5000: 1) [low n]
    - learn_more: n_ads=1 (spend>=5000: 1) [low n]
    - comment: n_ads=1 (spend>=5000: 0) [low n]
    - other: n_ads=1 (spend>=5000: 1) [low n]
    - visit_store: n_ads=1 (spend>=5000: 1) [low n]
- **offer** — 2 literal value(s), 2 atomic label(s).
  - literal:
    - none: n_ads=97 (spend>=5000: 87)
    - + 1 value(s) each with n_ads < 10 [low n], covering 3 ads (see CSV)
  - atomic: identical to literal (no ';'-compound cells).
- **product_form** — 3 literal value(s), 3 atomic label(s).
  - literal:
    - milk_mix_powder: n_ads=51 (spend>=5000: 48)
    - other: n_ads=26 (spend>=5000: 22)
    - gummies: n_ads=23 (spend>=5000: 20)
  - atomic: identical to literal (no ';'-compound cells).
- **demo_shown** — 33 literal value(s), 8 atomic label(s).
  - literal:
    - mixing_prep; child_consuming: n_ads=21 (spend>=5000: 19)
    - product_feature_demo: n_ads=13 (spend>=5000: 10)
    - none: n_ads=11 (spend>=5000: 10)
    - + 30 value(s) each with n_ads < 10 [low n], covering 55 ads (see CSV)
  - atomic:
    - child_consuming: n_ads=56 (spend>=5000: 52)
    - mixing_prep: n_ads=47 (spend>=5000: 45)
    - product_feature_demo: n_ads=27 (spend>=5000: 23)
    - taste_test: n_ads=25 (spend>=5000: 24)
    - live_use: n_ads=20 (spend>=5000: 17)
    - none: n_ads=11 (spend>=5000: 10)
    - tutorial: n_ads=7 (spend>=5000: 6) [low n]
    - comparison: n_ads=2 (spend>=5000: 2) [low n]

## 5. Transcripts (per creator)

- Posts with a transcript: 113/392 = 28.8% (n=392).
- Per creator in audit_extra_transcripts_by_creator.csv.
- Placeholder-looking transcripts (of 113 with text), audit_extra_transcript_flags.csv:
  - very short (< 100 chars): 4.
  - repeated across posts (identical text on >1 post): 0.
  - repeated within a post (a sentence >= 15 chars recurring >= 3x): 4.

