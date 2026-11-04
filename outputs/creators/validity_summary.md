# Creator ranking — post-hoc validity check, not pre-registered; the frozen creator_scores.csv remains the primary ranking

Motivation: the child-and-product example posts (e.g. CR-12) do not show a child reacting to food, and several top-engagement posts are "comment for link" posts. The frozen ranking in creator_scores.csv is unchanged; this file only probes its validity. Ranks only — no five are selected, no causal language.

Window: 2025-10-27 to 2026-10-27 inclusive (12 months). Window posts: n=374. Creators: n=20. Scoring functions, weights and the audience floor are imported from score_creators.

## Comparisons run

Total: **418** = Part 1: 374 window posts scanned for link-requests + 20 creators re-scored on audience_response excluding link-request posts; Part 2: 24 child-and-product posts listed.

## Part 1 — link-request posts and audience_response sensitivity

Link-request posts flagged by the caption regex `\bcomment\b[^\n]{0,40}?\blinks?\b` (case-insensitive); 38 window posts flagged, listed with matched snippets in link_request_posts.csv for false-positive review. audience_response recomputed excluding them (same median, same >=10 posts-with-plays floor, neutral 0.5 otherwise); evidence_fit and sponsored_fit held at frozen scores.

- **CR-12** (raising_zohran): link-request 8/20 (40.0%); audience_response median frozen=0.011244 (n=20 posts w/ plays) -> excl=0.007345 (n=12, ok); rank 1 -> 1 (change +0)
- **CR-15** (tej.lil.diary): link-request 9/20 (45.0%); audience_response median frozen=0.012343 (n=19 posts w/ plays) -> excl=0.002939 (n=10, ok); rank 2 -> 14 (change -12)
- **CR-13** (mumma_and_ridhu): link-request 2/20 (10.0%); audience_response median frozen=0.004738 (n=16 posts w/ plays) -> excl=0.004738 (n=14, ok); rank 3 -> 2 (change +1)
- **CR-09** (doc_mama_and_babies): link-request 2/11 (18.2%); audience_response median frozen=NA (n=8 posts w/ plays) -> excl=NA (n=6, insufficient); rank 4 -> 3 (change +1)
- **CR-19** (instamommy_suchi): link-request 2/20 (10.0%); audience_response median frozen=0.003429 (n=17 posts w/ plays) -> excl=0.000662 (n=15, ok); rank 5 -> 7 (change -2)
- **CR-01** (drgarima_mehta): link-request 1/20 (5.0%); audience_response median frozen=0.004292 (n=20 posts w/ plays) -> excl=0.00458 (n=19, ok); rank 6 -> 4 (change +2)
- **CR-05** (sia_3vedi): link-request 0/18 (0.0%); audience_response median frozen=0.005048 (n=16 posts w/ plays) -> excl=0.005048 (n=16, ok); rank 7 -> 6 (change +1)
- **CR-16** (paediatrics_decoded): link-request 0/20 (0.0%); audience_response median frozen=0.010661 (n=18 posts w/ plays) -> excl=0.010661 (n=18, ok); rank 8 -> 5 (change +3)
- **CR-03** (ekamichildcare): link-request 0/20 (0.0%); audience_response median frozen=0.011547 (n=20 posts w/ plays) -> excl=0.011547 (n=20, ok); rank 9 -> 8 (change +1)
- **CR-11** (raja_choudhary04): link-request 0/20 (0.0%); audience_response median frozen=0.00066 (n=19 posts w/ plays) -> excl=0.00066 (n=19, ok); rank 10 -> 9 (change +1)
- **CR-17** (radhikabansal0908): link-request 3/20 (15.0%); audience_response median frozen=0.000215 (n=20 posts w/ plays) -> excl=0.00021 (n=17, ok); rank 11 -> 11 (change +0)
- **CR-06** (thatkushalmistry): link-request 0/18 (0.0%); audience_response median frozen=0.012344 (n=18 posts w/ plays) -> excl=0.012344 (n=18, ok); rank 12 -> 12 (change +0)
- **CR-14** (parentingtips_surat): link-request 0/20 (0.0%); audience_response median frozen=0.008448 (n=19 posts w/ plays) -> excl=0.008448 (n=19, ok); rank 13 -> 10 (change +3)
- **CR-07** (ohmother.in): link-request 1/19 (5.3%); audience_response median frozen=0.001373 (n=18 posts w/ plays) -> excl=0.001337 (n=17, ok); rank 14 -> 15 (change -1)
- **CR-08** (the_mum_wife_playbook): link-request 0/19 (0.0%); audience_response median frozen=0.004455 (n=18 posts w/ plays) -> excl=0.004455 (n=18, ok); rank 15 -> 17 (change -2)
- **CR-20** (storiesbyvihaa): link-request 0/20 (0.0%); audience_response median frozen=0.002997 (n=16 posts w/ plays) -> excl=0.002997 (n=16, ok); rank 16 -> 16 (change +0)
- **CR-10** (couple_adishiv): link-request 10/20 (50.0%); audience_response median frozen=0.001287 (n=19 posts w/ plays) -> excl=NA (n=9, insufficient); rank 17 -> 13 (change +4)
- **CR-18** (foodies_by_neha): link-request 0/9 (0.0%); audience_response median frozen=NA (n=8 posts w/ plays) -> excl=NA (n=8, insufficient); rank 18 -> 18 (change +0)
- **CR-02** (livesimply_withkripa): link-request 0/20 (0.0%); audience_response median frozen=0.002043 (n=19 posts w/ plays) -> excl=0.002043 (n=19, ok); rank 19 -> 19 (change +0)
- **CR-04** (hello_ps8): link-request 0/20 (0.0%); audience_response median frozen=0.001699 (n=13 posts w/ plays) -> excl=0.001699 (n=13, ok); rank 20 -> 20 (change +0)

## Part 2 — proxy checklist

24 child-and-product example posts listed in proxy_check.md for manual inspection.

Full detail: link_request_posts.csv, link_sensitivity.csv, proxy_check.md.
