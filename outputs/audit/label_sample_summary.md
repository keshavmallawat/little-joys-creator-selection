# Label spot-check sample — Little Joys ads

Source: data/ads.csv (read-only). Floor and stratification read from config/. Sampling and transcription only; no label is inspected, judged, ranked, or selected, and no performance metric is computed.

Primary spend floor: spend_inr >= 10000 (n=80 ads). Seed: 42. Target sample size: 20. Per-side quota: at least 3 ads where the floor set allows.

Strata: H1, H2, H4, H6, H7 (the primary hypotheses). For each, in-group = the hypothesis group at the floor; out-group = floor set minus in-group, except H2 whose out-group keeps its child-present precondition so no-child ads do not pad the negatives.

Ads sampled: 20.

## Achieved composition

Per hypothesis, ads in the sample on each side, out of the floor-set availability for that side:
- **H1** — child reacts to taste:
  - in-group: 10 in sample (available at floor: 36; quota 3) [10/20 = 50.0% (n=20) of sample]
  - out-group: 10 in sample (available at floor: 44; quota 3) [10/20 = 50.0% (n=20) of sample]
- **H2** — child in first 3s (only ads with a child):
  - in-group: 9 in sample (available at floor: 35; quota 3) [9/20 = 45.0% (n=20) of sample]
  - out-group: 6 in sample (available at floor: 17; quota 3) [6/20 = 30.0% (n=20) of sample]
- **H4** — hook is a question:
  - in-group: 5 in sample (available at floor: 19; quota 3) [5/20 = 25.0% (n=20) of sample]
  - out-group: 15 in sample (available at floor: 61; quota 3) [15/20 = 75.0% (n=20) of sample]
- **H6** — creator is parent or caregiver:
  - in-group: 14 in sample (available at floor: 47; quota 3) [14/20 = 70.0% (n=20) of sample]
  - out-group: 6 in sample (available at floor: 33; quota 3) [6/20 = 30.0% (n=20) of sample]
- **H7** — voiceover montage format:
  - in-group: 7 in sample (available at floor: 28; quota 3) [7/20 = 35.0% (n=20) of sample]
  - out-group: 13 in sample (available at floor: 52; quota 3) [13/20 = 65.0% (n=20) of sample]

Full composition in label_sample_composition.csv. Blank my_* columns in label_check.csv are for the reviewer; agreement is computed later by label_error.py.
