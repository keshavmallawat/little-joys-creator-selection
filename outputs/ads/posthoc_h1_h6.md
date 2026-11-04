# Post-hoc H1 x H6 descriptive cross (post-hoc, not pre-registered, motivated by the 22-ad H1/H6 overlap in audit_cross_pair_overlap.csv)

Source: data/ads.csv (read-only); H1 and H6 specs and the spend floor from config/. Primary floor only. Descriptive only: no tier, no confidence interval, no test, no ranking, no causal language. Each rate is pooled and carries its n (and its denominator).

Primary floor: spend>=10000 (floor set n=80). H1 = child_role contains 'reacts_to_taste'; H6 = creator_type equals 'parent_or_caregiver'.

Comparisons run: 4 cells x 5 per-cell metrics (pooled ROAS, median per-ad ROAS, pooled hook_rate, ctr, cvr) = **20**, plus 1 product_form breakdown of the H1out_H6in cell. Total = **21**.

## 2x2: H1 membership x H6 membership (primary floor)

- **H1in_H6in** (H1 in, H6 in): n_ads=22; pooled ROAS=1.2085 (n=22); median per-ad ROAS=1.0785 (n=22); hook_rate=0.3175 (n=22 ads, denom=11220482); ctr=0.0097 (n=22 ads, denom=11220482); cvr=0.0249 (n=22 ads, denom=108374)
- **H1in_H6out** (H1 in, H6 out): n_ads=14; pooled ROAS=3.0345 (n=14); median per-ad ROAS=1.5634 (n=14); hook_rate=0.3277 (n=14 ads, denom=13685848); ctr=0.0115 (n=14 ads, denom=13685848); cvr=0.0516 (n=14 ads, denom=157330)
- **H1out_H6in** (H1 out, H6 in): n_ads=25; pooled ROAS=0.7514 (n=25); median per-ad ROAS=0.8940 (n=25); hook_rate=0.3205 (n=25 ads, denom=16866812); ctr=0.0092 (n=25 ads, denom=16866812); cvr=0.0183 (n=25 ads, denom=154785)
- **H1out_H6out** (H1 out, H6 out): n_ads=19; pooled ROAS=1.1597 (n=19); median per-ad ROAS=0.8541 (n=19); hook_rate=0.2856 (n=19 ads, denom=11483049); ctr=0.0088 (n=19 ads, denom=11483049); cvr=0.0296 (n=19 ads, denom=100571)

Cell n sum to 80 (floor set n=80).

## product_form split of the H1out_H6in cell (n per form)

H1out_H6in cell n=25.
- milk_mix_powder: n=11
- other: n=8
- gummies: n=6

Full detail: posthoc_h1_h6.csv.
