# Cross-structure facts — Little Joys hypothesis groups

Source: data/ads.csv (read-only). Parameters and hypotheses loaded from config/. Facts only; no interpretation, ranking, or selection. No performance metric (ROAS, CTR, CPA, hook rate) is computed broken down by any group.

Rows loaded: ads=100. Hypotheses: 9 (5 primary, 4 exploratory).

Comparisons run (6 sections): (1) 9 hypotheses x 3 floors = 27 group-size counts; (2) 36 pairwise overlaps at the primary floor; (3) 2 label cross-tabs; (4) 9 groups x 3 dimensions = 27 splits; (5) 2 scopes x (1 distinct-launch count + 1 top-15 combination table); (6) 3 purchases statistics over the primary-floor set.

## 1. Group sizes at each spend floor

Floors tested: primary = 10000, sensitivity = [5000, 25000]. A group with fewer than 10 ads at a floor is flagged [under min_group_size]. share_within_floor = group ads / all ads meeting that floor.

- Ads meeting each floor (denominator for share_within_floor): spend>=10000: n=80; spend>=5000: n=90; spend>=25000: n=57.

- **H1** (primary) — child reacts to taste: child_role contains 'reacts_to_taste'.
  - spend>=10000 (primary floor): n_group=36, 36/80 = 45.0% (n=80)
  - spend>=5000: n_group=38, 38/90 = 42.2% (n=90)
  - spend>=25000: n_group=26, 26/57 = 45.6% (n=57)
- **H2** (primary) — child in first 3s (only ads with a child): child_in_first_3s equals 'yes', restrict child_on_screen != none.
  - spend>=10000 (primary floor): n_group=35, 35/80 = 43.8% (n=80)
  - spend>=5000: n_group=39, 39/90 = 43.3% (n=90)
  - spend>=25000: n_group=23, 23/57 = 40.4% (n=57)
- **H4** (primary) — hook is a question: hook_type equals 'question'.
  - spend>=10000 (primary floor): n_group=19, 19/80 = 23.8% (n=80)
  - spend>=5000: n_group=23, 23/90 = 25.6% (n=90)
  - spend>=25000: n_group=16, 16/57 = 28.1% (n=57)
- **H6** (primary) — creator is parent or caregiver: creator_type equals 'parent_or_caregiver'.
  - spend>=10000 (primary floor): n_group=47, 47/80 = 58.8% (n=80)
  - spend>=5000: n_group=52, 52/90 = 57.8% (n=90)
  - spend>=25000: n_group=32, 32/57 = 56.1% (n=57)
- **H7** (primary) — voiceover montage format: ad_format equals 'voiceover_montage'.
  - spend>=10000 (primary floor): n_group=28, 28/80 = 35.0% (n=80)
  - spend>=5000: n_group=33, 33/90 = 36.7% (n=90)
  - spend>=25000: n_group=20, 20/57 = 35.1% (n=57)
- **H3** (exploratory) — brand named under 3s: brand_first_said equals 'under_3s'.
  - spend>=10000 (primary floor): n_group=30, 30/80 = 37.5% (n=80)
  - spend>=5000: n_group=36, 36/90 = 40.0% (n=90)
  - spend>=25000: n_group=22, 22/57 = 38.6% (n=57)
- **H5** (exploratory) — hook is a story opening: hook_type equals 'story_open'.
  - spend>=10000 (primary floor): n_group=17, 17/80 = 21.2% (n=80)
  - spend>=5000: n_group=18, 18/90 = 20.0% (n=90)
  - spend>=25000: n_group=12, 12/57 = 21.1% (n=57)
- **H8** (exploratory) — proof is creator testimonial: proof_used contains 'creator_testimonial'.
  - spend>=10000 (primary floor): n_group=18, 18/80 = 22.5% (n=80)
  - spend>=5000: n_group=21, 21/90 = 23.3% (n=90)
  - spend>=25000: n_group=13, 13/57 = 22.8% (n=57)
- **H9** (exploratory) — single language: language_mixing equals 'single_language'.
  - spend>=10000 (primary floor): n_group=16, 16/80 = 20.0% (n=80)
  - spend>=5000: n_group=19, 19/90 = 21.1% (n=90)
  - spend>=25000: n_group=13, 13/57 = 22.8% (n=57)

## 2. Pairwise group overlap at the primary floor

All 36 unordered pairs among the 9 hypotheses (primary and exploratory), groups formed at spend>=10000. n_both = ads in both groups; share_of_floor uses the 80-ad floor set as denominator.

- Pairs sharing at least one ad: 35 of 36. Full matrix in audit_cross_pair_overlap.csv.
- Highest-overlap pairs (n_both, descending):
  - H1 & H2: n_both=26 (26/80 = 32.5% (n=80)); n_a=36, n_b=35, n_union=45
  - H1 & H6: n_both=22 (22/80 = 27.5% (n=80)); n_a=36, n_b=47, n_union=61
  - H6 & H7: n_both=22 (22/80 = 27.5% (n=80)); n_a=47, n_b=28, n_union=53
  - H2 & H6: n_both=22 (22/80 = 27.5% (n=80)); n_a=35, n_b=47, n_union=60
  - H6 & H8: n_both=18 (18/80 = 22.5% (n=80)); n_a=47, n_b=18, n_union=47
  - H6 & H3: n_both=16 (16/80 = 20.0% (n=80)); n_a=47, n_b=30, n_union=61
  - H6 & H5: n_both=15 (15/80 = 18.8% (n=80)); n_a=47, n_b=17, n_union=49
  - H2 & H5: n_both=13 (13/80 = 16.2% (n=80)); n_a=35, n_b=17, n_union=39
  - H1 & H5: n_both=12 (12/80 = 15.0% (n=80)); n_a=36, n_b=17, n_union=41
  - H1 & H3: n_both=12 (12/80 = 15.0% (n=80)); n_a=36, n_b=30, n_union=54

## 3. Label cross-tabs (all ads)

- child_on_screen x child_in_first_3s (n=100), audit_cross_child_onscreen_x_first3s.csv:
    child_on_screen             no         yes         All
    multiple                     5           6          11
    none                        37           0          37
    one                         17          35          52
    All                         59          41         100

- child_role atomic reacts_to_taste x consumes_product (n=100; 'none'/missing child_role fall in the no/no cell), audit_cross_childrole_taste_x_consumes.csv:
    both labels: 38 (38/100 = 38.0% (n=100))
    reacts_to_taste only: 1; consumes_product only: 16
    neither: 45

## 4. Group splits at the primary floor

For each hypothesis group (formed at spend>=10000), counts by product_form, launch month, and stopped_date. Full table in audit_cross_group_splits.csv.

- **H1** — child reacts to taste (n_group=36):
  - by product_form: milk_mix_powder=23; other=8; gummies=5
  - by launch_month: 5 distinct value(s), top = 2026-09=28; 2026-08=5; 2026-07=1
  - by stopped_date: 8 distinct value(s), top = 2026-10-03=13; 2026-08-23=6; 2026-10-17=6
- **H2** — child in first 3s (only ads with a child) (n_group=35):
  - by product_form: milk_mix_powder=23; other=6; gummies=6
  - by launch_month: 3 distinct value(s), top = 2026-09=25; 2026-08=9; 2026-07=1
  - by stopped_date: 6 distinct value(s), top = 2026-10-03=15; 2026-09-26=7; 2026-08-23=7
- **H4** — hook is a question (n_group=19):
  - by product_form: milk_mix_powder=8; gummies=7; other=4
  - by launch_month: 5 distinct value(s), top = 2026-09=12; 2026-08=3; 2026-10=2
  - by stopped_date: 7 distinct value(s), top = 2026-10-23=4; 2026-09-26=4; 2026-10-03=4
- **H6** — creator is parent or caregiver (n_group=47):
  - by product_form: milk_mix_powder=22; other=15; gummies=10
  - by launch_month: 4 distinct value(s), top = 2026-09=33; 2026-08=10; 2026-10=2
  - by stopped_date: 8 distinct value(s), top = 2026-10-03=13; 2026-10-17=9; 2026-09-26=8
- **H7** — voiceover montage format (n_group=28):
  - by product_form: milk_mix_powder=16; gummies=8; other=4
  - by launch_month: 4 distinct value(s), top = 2026-09=19; 2026-08=6; 2026-10=2
  - by stopped_date: 7 distinct value(s), top = 2026-10-03=11; 2026-10-23=5; 2026-08-23=4
- **H3** — brand named under 3s (n_group=30):
  - by product_form: milk_mix_powder=16; gummies=9; other=5
  - by launch_month: 5 distinct value(s), top = 2026-09=20; 2026-08=7; 2026-10=1
  - by stopped_date: 6 distinct value(s), top = 2026-10-03=10; 2026-10-23=6; 2026-08-23=5
- **H5** — hook is a story opening (n_group=17):
  - by product_form: milk_mix_powder=9; other=5; gummies=3
  - by launch_month: 3 distinct value(s), top = 2026-09=14; 2026-08=2; 2026-07=1
  - by stopped_date: 5 distinct value(s), top = 2026-10-03=6; 2026-10-17=4; 2026-09-26=3
- **H8** — proof is creator testimonial (n_group=18):
  - by product_form: milk_mix_powder=8; other=8; gummies=2
  - by launch_month: 4 distinct value(s), top = 2026-09=11; 2026-08=4; 2026-10=2
  - by stopped_date: 7 distinct value(s), top = 2026-10-03=5; 2026-10-17=4; 2026-10-10=3
- **H9** — single language (n_group=16):
  - by product_form: milk_mix_powder=10; gummies=3; other=3
  - by launch_month: 3 distinct value(s), top = 2026-09=11; 2026-08=4; 2026-10=1
  - by stopped_date: 6 distinct value(s), top = 2026-10-03=5; 2026-10-23=4; 2026-09-26=4

## 5. Date-and-form clustering

Two scopes reported side by side: all ads and ads at the primary floor (spend>=10000). Distinct launch_date count, and the top 15 launch_date x stopped_date x product_form combinations by ad count. Full table in audit_cross_clustering.csv.

- **all_ads** (n=100): distinct launch_date = 34; distinct launch x stop x form combinations = 73.
  - top 15 combinations:
     1. 2026-09-07 / 2026-10-03 / milk_mix_powder: 5/100 = 5.0% (n=100)
     2. 2026-09-21 / 2026-10-03 / milk_mix_powder: 4/100 = 4.0% (n=100)
     3. 2026-09-02 / 2026-09-26 / milk_mix_powder: 3/100 = 3.0% (n=100)
     4. 2026-08-20 / 2026-08-23 / milk_mix_powder: 3/100 = 3.0% (n=100)
     5. 2026-09-28 / 2026-10-17 / other: 3/100 = 3.0% (n=100)
     6. 2026-09-29 / 2026-10-03 / other: 3/100 = 3.0% (n=100)
     7. 2026-08-18 / 2026-09-26 / milk_mix_powder: 2/100 = 2.0% (n=100)
     8. 2026-08-18 / 2026-08-23 / milk_mix_powder: 2/100 = 2.0% (n=100)
     9. 2026-06-10 / 2026-08-23 / gummies: 2/100 = 2.0% (n=100)
    10. 2026-09-28 / 2026-10-17 / gummies: 2/100 = 2.0% (n=100)
    11. 2026-09-30 / 2026-10-03 / gummies: 2/100 = 2.0% (n=100)
    12. 2026-09-30 / 2026-10-03 / other: 2/100 = 2.0% (n=100)
    13. 2026-10-09 / 2026-10-10 / other: 2/100 = 2.0% (n=100)
    14. 2026-09-24 / 2026-10-03 / milk_mix_powder: 2/100 = 2.0% (n=100)
    15. 2026-09-17 / 2026-10-03 / gummies: 2/100 = 2.0% (n=100)
- **primary_floor** (n=80): distinct launch_date = 31; distinct launch x stop x form combinations = 62.
  - top 15 combinations:
     1. 2026-09-07 / 2026-10-03 / milk_mix_powder: 5/80 = 6.2% (n=80)
     2. 2026-09-21 / 2026-10-03 / milk_mix_powder: 4/80 = 5.0% (n=80)
     3. 2026-09-02 / 2026-09-26 / milk_mix_powder: 3/80 = 3.8% (n=80)
     4. 2026-08-20 / 2026-08-23 / milk_mix_powder: 3/80 = 3.8% (n=80)
     5. 2026-09-28 / 2026-10-17 / other: 3/80 = 3.8% (n=80)
     6. 2026-09-11 / 2026-09-26 / milk_mix_powder: 2/80 = 2.5% (n=80)
     7. 2026-09-17 / 2026-10-03 / gummies: 2/80 = 2.5% (n=80)
     8. 2026-09-28 / 2026-10-17 / gummies: 2/80 = 2.5% (n=80)
     9. 2026-08-18 / 2026-09-26 / milk_mix_powder: 2/80 = 2.5% (n=80)
    10. 2026-06-10 / 2026-08-23 / gummies: 2/80 = 2.5% (n=80)
    11. 2026-08-14 / 2026-10-21 / other: 1/80 = 1.2% (n=80)
    12. 2026-08-12 / 2026-10-10 / other: 1/80 = 1.2% (n=80)
    13. 2026-08-18 / 2026-08-23 / milk_mix_powder: 1/80 = 1.2% (n=80)
    14. 2026-08-14 / 2026-10-23 / gummies: 1/80 = 1.2% (n=80)
    15. 2026-08-20 / 2026-08-23 / gummies: 1/80 = 1.2% (n=80)

## 6. Purchases among ads passing the primary floor

Distribution of the floor set as a whole (not a per-group metric), audit_cross_floor_purchases.csv:
- min purchases: 0 (n=80).
- median purchases: 75.5 (n=80).
- ads with purchases < 20: 4/80 = 5.0% (n=80).

