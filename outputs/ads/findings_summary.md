# Performance findings — Little Joys hypothesis groups

Source: data/ads.csv (read-only); parameters, hypotheses and decision rules from config/; spot-check agreement from outputs/audit/label_agreement.csv. Facts only — no ranking, no interpretation, no causal language; differences are associations (in-group minus out-group). This pass presents; it does not choose.

Rows loaded: ads=100. Hypotheses: 9 (5 primary, 4 exploratory). Floors: primary=10000, sensitivity=[5000, 25000]. min_group_size=10. seed=42.

## Comparisons run

Total comparisons run: **179**. Breakdown:
- step1_floor_roas: 27
- step2_diagnostics: 27
- step3_bootstrap_ci: 9
- step4_drop_highest_reruns: 18
- step4_leave_one_stop_date_out_reruns: 72
- step4_product_form_strata_reported: 19
- step6_structural_cells: 5
- step7_floor_facts: 2
(The two free sign checks — same_sign_at_all_three_floors and median_per_ad_roas_diff_same_sign — reuse the step-1 numbers and add no new comparison; they are still reported as rows in robustness.csv.)

## Pooled ROAS at the primary floor (spend>=10000)

Difference is in-group minus out-group. Each rate carries its n (ads).

- **H1** (primary) — child reacts to taste: ROAS in=2.2235 (n=36), out=0.9179 (n=44), difference=+1.3056; median per-ad ROAS in=1.3338, out=0.8831; bootstrap 95% CI of difference=[+0.2243, +2.3453] (excludes 0: True)
- **H2** (primary) — child in first 3s (only ads with a child): ROAS in=1.8013 (n=35), out=1.3379 (n=17), difference=+0.4634; median per-ad ROAS in=1.0205, out=1.4571; bootstrap 95% CI of difference=[-0.5728, +1.6683] (excludes 0: False)
- **H4** (primary) — hook is a question: ROAS in=1.2775 (n=19), out=1.5592 (n=61), difference=-0.2817; median per-ad ROAS in=1.0718, out=0.9698; bootstrap 95% CI of difference=[-1.1931, +0.4523] (excludes 0: False)
- **H6** (primary) — creator is parent or caregiver: ROAS in=0.9228 (n=47), out=2.1377 (n=33), difference=-1.2149; median per-ad ROAS in=0.9127, out=1.0829; bootstrap 95% CI of difference=[-2.2433, -0.1204] (excludes 0: True)
- **H7** (primary) — voiceover montage format: ROAS in=1.0212 (n=28), out=1.7482 (n=52), difference=-0.7270; median per-ad ROAS in=1.0461, out=0.9853; bootstrap 95% CI of difference=[-1.7263, +0.1685] (excludes 0: False)
- **H3** (exploratory) — brand named under 3s: ROAS in=2.2126 (n=30), out=1.1120 (n=50), difference=+1.1007; median per-ad ROAS in=1.1567, out=0.9113; bootstrap 95% CI of difference=[-0.2116, +2.4448] (excludes 0: False)
- **H5** (exploratory) — hook is a story opening: ROAS in=1.9359 (n=17), out=1.2962 (n=63), difference=+0.6398; median per-ad ROAS in=0.7839, out=1.0829; bootstrap 95% CI of difference=[-0.8949, +2.2260] (excludes 0: False)
- **H8** (exploratory) — proof is creator testimonial: ROAS in=1.0016 (n=18), out=1.6235 (n=62), difference=-0.6219; median per-ad ROAS in=0.9154, out=1.0338; bootstrap 95% CI of difference=[-1.4485, +0.3040] (excludes 0: False)
- **H9** (exploratory) — single language: ROAS in=1.6522 (n=16), out=1.4683 (n=64), difference=+0.1840; median per-ad ROAS in=1.4223, out=0.9247; bootstrap 95% CI of difference=[-0.7945, +0.9945] (excludes 0: False)

## Diagnostic rates at the primary floor (not used for tiers)

- **H1**: hook_rate in=0.3231 (n=24906330), out=0.3064 (n=28349861); ctr in=0.0107 (n=24906330), out=0.0090 (n=28349861); cvr in=0.0407 (n=265704), out=0.0228 (n=255356)
- **H2**: hook_rate in=0.3503 (n=30713625), out=0.2600 (n=9073031); ctr in=0.0103 (n=30713625), out=0.0092 (n=9073031); cvr in=0.0343 (n=315215), out=0.0312 (n=83165)
- **H4**: hook_rate in=0.2687 (n=10733787), out=0.3257 (n=42522404); ctr in=0.0097 (n=10733787), out=0.0098 (n=42522404); cvr in=0.0317 (n=103750), out=0.0320 (n=417310)
- **H6**: hook_rate in=0.3193 (n=28087294), out=0.3085 (n=25168897); ctr in=0.0094 (n=28087294), out=0.0102 (n=25168897); cvr in=0.0210 (n=263159), out=0.0430 (n=257901)
- **H7**: hook_rate in=0.3042 (n=17986798), out=0.3193 (n=35269393); ctr in=0.0090 (n=17986798), out=0.0102 (n=35269393); cvr in=0.0249 (n=162755), out=0.0351 (n=358305)
- **H3**: hook_rate in=0.2806 (n=18242539), out=0.3317 (n=35013652); ctr in=0.0102 (n=18242539), out=0.0096 (n=35013652); cvr in=0.0462 (n=186596), out=0.0240 (n=334464)
- **H5**: hook_rate in=0.3381 (n=17968629), out=0.3020 (n=35287562); ctr in=0.0105 (n=17968629), out=0.0094 (n=35287562); cvr in=0.0347 (n=188815), out=0.0303 (n=332245)
- **H8**: hook_rate in=0.3289 (n=11252664), out=0.3103 (n=42003527); ctr in=0.0086 (n=11252664), out=0.0101 (n=42003527); cvr in=0.0234 (n=96416), out=0.0338 (n=424644)
- **H9**: hook_rate in=0.2714 (n=7999804), out=0.3218 (n=45256387); ctr in=0.0103 (n=7999804), out=0.0097 (n=45256387); cvr in=0.0370 (n=82421), out=0.0310 (n=438639)

## Tiers (strictly per decision_rules.yaml; supported is primary-only)

tier is computed before the label cap; tier_after_label_cap applies the spot-check cap. Both are kept. Spot-check agreement is reported as a fact.

- **H1**: tier=supported -> tier_after_label_cap=supported; label: my_child_role_reacts agreement=1.00 (n=20), below_cap=False
- **H2**: tier=fragile -> tier_after_label_cap=fragile; label: my_child_in_first_3s agreement=0.90 (n=20), below_cap=False
- **H4**: tier=fragile -> tier_after_label_cap=fragile; label: my_hook_type agreement=1.00 (n=20), below_cap=False
- **H6**: tier=supported -> tier_after_label_cap=supported; label: my_creator_type agreement=0.90 (n=20), below_cap=False
- **H7**: tier=fragile -> tier_after_label_cap=fragile; label: my_ad_format agreement=1.00 (n=20), below_cap=False
- **H3**: tier=suggestive -> tier_after_label_cap=suggestive; label: my_brand_first_said agreement=0.90 (n=20), below_cap=False
- **H5**: tier=fragile -> tier_after_label_cap=fragile; label: my_hook_type agreement=1.00 (n=20), below_cap=False
- **H8**: tier=suggestive -> tier_after_label_cap=suggestive [no spot-check for this label]; label: label_unchecked — confounded with H6 (every H8 ad is an H6 ad); see S2
- **H9**: tier=fragile -> tier_after_label_cap=fragile [no spot-check for this label]; label: label_unchecked

## Structural views (descriptive only)

S1 — child status three-way (primary floor):
  - no_child: pooled ROAS=0.9839 (n=28)
  - child_present_not_reacting: pooled ROAS=0.8537 (n=16)
  - child_reacts: pooled ROAS=2.2235 (n=36)
S2 — H8 within H6 (parent ads, primary floor):
  - H8_in_within_H6: pooled ROAS=1.0016 (n=18)
  - H8_out_within_H6: pooled ROAS=0.8738 (n=29)

## Floor-set composition (spend>=10000, n=80)

product_form mix:
  - milk_mix_powder: n=43 (53.8% of floor set)
  - gummies: n=19 (23.8% of floor set)
  - other: n=18 (22.5% of floor set)
Single biggest-spend ad: LJ-004 holds 9.2% of total floor spend (spend=659494, floor total=7157419, n=80).

Full detail: findings.csv (per hypothesis x floor), robustness.csv (one row per hypothesis per sign check), structural.csv.
