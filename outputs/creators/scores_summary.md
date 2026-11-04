# Creator scores — Little Joys creator selection

Source: data/creators.csv and data/creator_posts.csv (read-only); all weights, floors, window length, seed, draw count and jitter bounds from config/weights.yaml. Ranked by composite. This pass presents and ranks; it does not choose or recommend any five. No causal language; every rate carries its n.

Window: 2025-10-27 to 2026-10-27 inclusive (12 months, anchored at the latest post date). Posts in window: n=374. Creators: n=20.

Weights (from config): evidence_fit=0.40, audience_response=0.35, sponsored_fit=0.25 (sum=1.00). Floors: audience_response needs >=10 posts with plays; sponsored_fit needs >=4 sponsored posts.

## Comparisons run

Total: **280** = 20 creators x 3 components (60 component scores) + 20 composite scores + 200 weight-jitter stability re-rankings (seed 42).

## Ranked by composite (no five are selected)

- **1. CR-12** (raising_zohran) — composite=0.7711; followers=22,659 (context only). evidence_fit=0.5000 (n=20 window posts) [score 0.895]; audience_response=0.0112 (n=20 posts w/ plays) [score 0.824]; sponsored_fit=insufficient (n=3 sponsored) [score 0.500]. flags: no_audience_data
- **2. CR-15** (tej.lil.diary) — composite=0.6663; followers=35,280 (context only). evidence_fit=0.4500 (n=20 window posts) [score 0.842]; audience_response=0.0123 (n=19 posts w/ plays) [score 0.941]; sponsored_fit=0.1458 (n=6 sponsored) [score 0.000]. flags: 
- **3. CR-13** (mumma_and_ridhu) — composite=0.6645; followers=115,612 (context only). evidence_fit=0.4000 (n=20 window posts) [score 0.789]; audience_response=0.0047 (n=16 posts w/ plays) [score 0.588]; sponsored_fit=1.6235 (n=12 sponsored) [score 0.571]. flags: no_audience_data
- **4. CR-09** (doc_mama_and_babies) — composite=0.6566; followers=153,896 (context only). evidence_fit=0.2727 (n=11 window posts) [score 0.579]; audience_response=insufficient (n=8 posts w/ plays) [score 0.500]; sponsored_fit=38.5668 (n=8 sponsored) [score 1.000]. flags: hidden_likes, no_audience_data, legal_review
- **5. CR-19** (instamommy_suchi) — composite=0.6531; followers=288,693 (context only). evidence_fit=0.3500 (n=20 window posts) [score 0.737]; audience_response=0.0034 (n=17 posts w/ plays) [score 0.412]; sponsored_fit=18.6236 (n=15 sponsored) [score 0.857]. flags: no_audience_data
- **6. CR-01** (drgarima_mehta) — composite=0.5529; followers=48,906 (context only). evidence_fit=0.3000 (n=20 window posts) [score 0.658]; audience_response=0.0043 (n=20 posts w/ plays) [score 0.471]; sponsored_fit=insufficient (n=2 sponsored) [score 0.500]. flags: no_audience_data, legal_review
- **7. CR-05** (sia_3vedi) — composite=0.5409; followers=2,831,180 (context only). evidence_fit=0.2222 (n=18 window posts) [score 0.474]; audience_response=0.0050 (n=16 posts w/ plays) [score 0.647]; sponsored_fit=insufficient (n=1 sponsored) [score 0.500]. flags: no_audience_data
- **8. CR-16** (paediatrics_decoded) — composite=0.5295; followers=263,188 (context only). evidence_fit=0.1500 (n=20 window posts) [score 0.342]; audience_response=0.0107 (n=18 posts w/ plays) [score 0.765]; sponsored_fit=insufficient (n=0 sponsored) [score 0.500]. flags: no_audience_data, legal_review
- **9. CR-03** (ekamichildcare) — composite=0.5286; followers=164,333 (context only). evidence_fit=0.1000 (n=20 window posts) [score 0.237]; audience_response=0.0115 (n=20 posts w/ plays) [score 0.882]; sponsored_fit=insufficient (n=2 sponsored) [score 0.500]. flags: no_audience_data, legal_review
- **10. CR-11** (raja_choudhary04) — composite=0.5277; followers=196,955 (context only). evidence_fit=0.6500 (n=20 window posts) [score 1.000]; audience_response=0.0007 (n=19 posts w/ plays) [score 0.059]; sponsored_fit=1.2570 (n=7 sponsored) [score 0.429]. flags: no_audience_data
- **11. CR-17** (radhikabansal0908) — composite=0.5039; followers=395,569 (context only). evidence_fit=0.5500 (n=20 window posts) [score 0.947]; audience_response=0.0002 (n=20 posts w/ plays) [score 0.000]; sponsored_fit=insufficient (n=20 sponsored) [score 0.500]. flags: hidden_likes, no_audience_data
- **12. CR-06** (thatkushalmistry) — composite=0.4961; followers=1,706,047 (context only). evidence_fit=0.0000 (n=18 window posts) [score 0.053]; audience_response=0.0123 (n=18 posts w/ plays) [score 1.000]; sponsored_fit=insufficient (n=1 sponsored) [score 0.500]. flags: no_audience_data
- **13. CR-14** (parentingtips_surat) — composite=0.4668; followers=1,120,817 (context only). evidence_fit=0.1000 (n=20 window posts) [score 0.237]; audience_response=0.0084 (n=19 posts w/ plays) [score 0.706]; sponsored_fit=insufficient (n=0 sponsored) [score 0.500]. flags: legal_review
- **14. CR-07** (ohmother.in) — composite=0.4509; followers=34,672 (context only). evidence_fit=0.2632 (n=19 window posts) [score 0.526]; audience_response=0.0014 (n=18 posts w/ plays) [score 0.176]; sponsored_fit=1.6645 (n=4 sponsored) [score 0.714]. flags: no_audience_data
- **15. CR-08** (the_mum_wife_playbook) — composite=0.4251; followers=39,571 (context only). evidence_fit=0.1579 (n=19 window posts) [score 0.421]; audience_response=0.0045 (n=18 posts w/ plays) [score 0.529]; sponsored_fit=0.7908 (n=4 sponsored) [score 0.286]. flags: no_audience_data
- **16. CR-20** (storiesbyvihaa) — composite=0.3854; followers=827,496 (context only). evidence_fit=0.1500 (n=20 window posts) [score 0.342]; audience_response=0.0030 (n=16 posts w/ plays) [score 0.353]; sponsored_fit=insufficient (n=2 sponsored) [score 0.500]. flags: 
- **17. CR-10** (couple_adishiv) — composite=0.3400; followers=48,934 (context only). evidence_fit=0.3000 (n=20 window posts) [score 0.658]; audience_response=0.0013 (n=19 posts w/ plays) [score 0.118]; sponsored_fit=0.7070 (n=7 sponsored) [score 0.143]. flags: no_audience_data
- **18. CR-18** (foodies_by_neha) — composite=0.3211; followers=1,009,385 (context only). evidence_fit=0.0000 (n=9 window posts) [score 0.053]; audience_response=insufficient (n=8 posts w/ plays) [score 0.500]; sponsored_fit=insufficient (n=1 sponsored) [score 0.500]. flags: no_audience_data
- **19. CR-02** (livesimply_withkripa) — composite=0.2911; followers=67,658 (context only). evidence_fit=0.0500 (n=20 window posts) [score 0.158]; audience_response=0.0020 (n=19 posts w/ plays) [score 0.294]; sponsored_fit=insufficient (n=0 sponsored) [score 0.500]. flags: hidden_likes, no_audience_data
- **20. CR-04** (hello_ps8) — composite=0.2284; followers=216,882 (context only). evidence_fit=0.0000 (n=20 window posts) [score 0.053]; audience_response=0.0017 (n=13 posts w/ plays) [score 0.235]; sponsored_fit=insufficient (n=2 sponsored) [score 0.500]. flags: no_audience_data

## Insufficient components

- audience_response: 2 creator(s) scored neutral 0.5 — CR-09, CR-18
- sponsored_fit: 12 creator(s) scored neutral 0.5 — CR-12, CR-01, CR-05, CR-16, CR-03, CR-17, CR-06, CR-14, CR-20, CR-18, CR-02, CR-04

## Stability (200 draws, seed 42)

Share of draws each creator lands in the top 5 (weights jittered by uniform(0.7, 1.3) then renormalised); best and worst rank across draws.
- CR-12 (raising_zohran): top5 in 100.0% of 200 draws; rank range 1-1
- CR-15 (tej.lil.diary): top5 in 100.0% of 200 draws; rank range 2-5
- CR-13 (mumma_and_ridhu): top5 in 100.0% of 200 draws; rank range 2-4
- CR-09 (doc_mama_and_babies): top5 in 100.0% of 200 draws; rank range 2-5
- CR-19 (instamommy_suchi): top5 in 100.0% of 200 draws; rank range 2-5
- CR-01 (drgarima_mehta): top5 in 0.0% of 200 draws; rank range 6-10
- CR-05 (sia_3vedi): top5 in 0.0% of 200 draws; rank range 7-9
- CR-16 (paediatrics_decoded): top5 in 0.0% of 200 draws; rank range 7-11
- CR-03 (ekamichildcare): top5 in 0.0% of 200 draws; rank range 6-12
- CR-11 (raja_choudhary04): top5 in 0.0% of 200 draws; rank range 6-13
- CR-17 (radhikabansal0908): top5 in 0.0% of 200 draws; rank range 7-15
- CR-06 (thatkushalmistry): top5 in 0.0% of 200 draws; rank range 7-15
- CR-14 (parentingtips_surat): top5 in 0.0% of 200 draws; rank range 11-14
- CR-07 (ohmother.in): top5 in 0.0% of 200 draws; rank range 10-15
- CR-08 (the_mum_wife_playbook): top5 in 0.0% of 200 draws; rank range 12-15
- CR-20 (storiesbyvihaa): top5 in 0.0% of 200 draws; rank range 16-17
- CR-10 (couple_adishiv): top5 in 0.0% of 200 draws; rank range 16-19
- CR-18 (foodies_by_neha): top5 in 0.0% of 200 draws; rank range 17-19
- CR-02 (livesimply_withkripa): top5 in 0.0% of 200 draws; rank range 18-19
- CR-04 (hello_ps8): top5 in 0.0% of 200 draws; rank range 20-20

Full detail: creator_scores.csv, stability.csv.
