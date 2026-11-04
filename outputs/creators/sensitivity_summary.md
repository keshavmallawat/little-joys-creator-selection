# Creator ranking — post-hoc sensitivity, not pre-registered; the frozen result in creator_scores.csv remains the primary ranking

Motivation: CR-09's sponsored_fit ratio rests on 3 non-sponsored posts. The frozen ranking in creator_scores.csv is unchanged; this file only probes its sensitivity. Ranks only — no five are selected, no causal language.

Window: 2025-10-27 to 2026-10-27 inclusive (12 months). Posts in window: n=374. Creators: n=20. All weights, floors, seed and draw count reused from config/weights.yaml via score_creators.

## Comparisons run

Total: **4080** = Part 1: 4 scenarios x 20 creators (80 composites) + Part 2: 200 resamples x 20 creators (4000 composite recomputations, seed 42).

## Part 1 — alternate composites (ranks of all 20)

Scenarios: frozen (0.40/0.35/0.25); A drop sponsored_fit, other two weights renormalised; B sponsored_fit neutral 0.5 for all; C sponsored_fit also needs >=4 non-sponsored posts with plays, else neutral 0.5 (re-ranked among the reduced pool).

- **CR-12** (raising_zohran): ranks frozen=1, A=2, B=2, C=1; top5=all (C sponsored_fit: insufficient, n_nonsponsored_with_plays=14)
- **CR-15** (tej.lil.diary): ranks frozen=2, A=1, B=1, C=3; top5=all (C sponsored_fit: ok, n_nonsponsored_with_plays=12)
- **CR-13** (mumma_and_ridhu): ranks frozen=3, A=3, B=3, C=2; top5=all (C sponsored_fit: ok, n_nonsponsored_with_plays=4)
- **CR-09** (doc_mama_and_babies): ranks frozen=4, A=8, B=8, C=8; top5=some (C sponsored_fit: insufficient, n_nonsponsored_with_plays=1)
- **CR-19** (instamommy_suchi): ranks frozen=5, A=4, B=4, C=5; top5=all (C sponsored_fit: insufficient, n_nonsponsored_with_plays=3)
- **CR-01** (drgarima_mehta): ranks frozen=6, A=5, B=5, C=6; top5=some (C sponsored_fit: insufficient, n_nonsponsored_with_plays=18)
- **CR-05** (sia_3vedi): ranks frozen=7, A=7, B=7, C=7; top5=none (C sponsored_fit: insufficient, n_nonsponsored_with_plays=14)
- **CR-16** (paediatrics_decoded): ranks frozen=8, A=9, B=9, C=9; top5=none (C sponsored_fit: insufficient, n_nonsponsored_with_plays=18)
- **CR-03** (ekamichildcare): ranks frozen=9, A=10, B=10, C=10; top5=none (C sponsored_fit: insufficient, n_nonsponsored_with_plays=18)
- **CR-11** (raja_choudhary04): ranks frozen=10, A=6, B=6, C=4; top5=some (C sponsored_fit: ok, n_nonsponsored_with_plays=12)
- **CR-17** (radhikabansal0908): ranks frozen=11, A=11, B=11, C=12; top5=none (C sponsored_fit: insufficient, n_nonsponsored_with_plays=0)
- **CR-06** (thatkushalmistry): ranks frozen=12, A=12, B=12, C=13; top5=none (C sponsored_fit: insufficient, n_nonsponsored_with_plays=17)
- **CR-14** (parentingtips_surat): ranks frozen=13, A=14, B=14, C=14; top5=none (C sponsored_fit: insufficient, n_nonsponsored_with_plays=19)
- **CR-07** (ohmother.in): ranks frozen=14, A=16, B=16, C=11; top5=none (C sponsored_fit: ok, n_nonsponsored_with_plays=14)
- **CR-08** (the_mum_wife_playbook): ranks frozen=15, A=13, B=13, C=15; top5=none (C sponsored_fit: ok, n_nonsponsored_with_plays=13)
- **CR-20** (storiesbyvihaa): ranks frozen=16, A=17, B=17, C=16; top5=none (C sponsored_fit: insufficient, n_nonsponsored_with_plays=14)
- **CR-10** (couple_adishiv): ranks frozen=17, A=15, B=15, C=17; top5=none (C sponsored_fit: ok, n_nonsponsored_with_plays=12)
- **CR-18** (foodies_by_neha): ranks frozen=18, A=18, B=18, C=18; top5=none (C sponsored_fit: insufficient, n_nonsponsored_with_plays=7)
- **CR-02** (livesimply_withkripa): ranks frozen=19, A=19, B=19, C=19; top5=none (C sponsored_fit: insufficient, n_nonsponsored_with_plays=19)
- **CR-04** (hello_ps8): ranks frozen=20, A=20, B=20, C=20; top5=none (C sponsored_fit: insufficient, n_nonsponsored_with_plays=11)

- top5 under all four: 4 creator(s) — CR-12, CR-15, CR-13, CR-19
- top5 under some four: 3 creator(s) — CR-09, CR-01, CR-11
- top5 under none four: 13 creator(s) — CR-05, CR-16, CR-03, CR-17, CR-06, CR-14, CR-07, CR-08, CR-20, CR-10, CR-18, CR-02, CR-04

## Part 2 — post-sampling uncertainty (200 resamples, seed 42)

Window posts resampled with replacement within each creator (same n), all three components, percentile ranks and the frozen-weight composite recomputed each draw. Share of resamples in the top 5, and rank range.
- CR-12 (raising_zohran): top5 in 99.0% of 200 resamples; rank range 1-7
- CR-13 (mumma_and_ridhu): top5 in 83.5% of 200 resamples; rank range 1-15
- CR-15 (tej.lil.diary): top5 in 76.0% of 200 resamples; rank range 1-19
- CR-09 (doc_mama_and_babies): top5 in 61.0% of 200 resamples; rank range 1-19
- CR-19 (instamommy_suchi): top5 in 50.5% of 200 resamples; rank range 1-20
- CR-16 (paediatrics_decoded): top5 in 34.0% of 200 resamples; rank range 1-16
- CR-01 (drgarima_mehta): top5 in 28.5% of 200 resamples; rank range 2-17
- CR-05 (sia_3vedi): top5 in 19.5% of 200 resamples; rank range 2-18
- CR-03 (ekamichildcare): top5 in 15.0% of 200 resamples; rank range 3-17
- CR-11 (raja_choudhary04): top5 in 11.5% of 200 resamples; rank range 3-17
- CR-14 (parentingtips_surat): top5 in 11.5% of 200 resamples; rank range 2-18
- CR-07 (ohmother.in): top5 in 5.0% of 200 resamples; rank range 4-20
- CR-08 (the_mum_wife_playbook): top5 in 2.5% of 200 resamples; rank range 2-18
- CR-10 (couple_adishiv): top5 in 1.5% of 200 resamples; rank range 4-19
- CR-20 (storiesbyvihaa): top5 in 1.0% of 200 resamples; rank range 3-19
- CR-02 (livesimply_withkripa): top5 in 0.0% of 200 resamples; rank range 11-20
- CR-04 (hello_ps8): top5 in 0.0% of 200 resamples; rank range 17-20
- CR-06 (thatkushalmistry): top5 in 0.0% of 200 resamples; rank range 8-19
- CR-18 (foodies_by_neha): top5 in 0.0% of 200 resamples; rank range 14-20
- CR-17 (radhikabansal0908): top5 in 0.0% of 200 resamples; rank range 7-19

Full detail: sensitivity.csv, bootstrap_top5.csv.
