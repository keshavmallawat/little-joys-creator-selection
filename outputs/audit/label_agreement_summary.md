# Label spot-check agreement — Little Joys ads

Source: outputs/audit/label_check.csv (read-only here), 20 ads in the sheet. For each label the reviewer's my_* judgment is compared to the stored label; the rate below is agreement with its denominator n. Comparison and presentation only — no verdict or selection is made here.

label_cap threshold (from config/decision_rules.yaml): 0.8. A label with agreement below it is flagged below_label_cap (a fact, not a decision). Reviewer entries of 'unclear' are excluded from n and tallied as n_unclear; blank cells are ads not judged.

## Per-label agreement

- **my_child_role_reacts** vs child_role: 20/20 = 100.0% (n=20); n_unclear=0
- **my_child_in_first_3s** vs child_in_first_3s: 18/20 = 90.0% (n=20); n_unclear=0
- **my_hook_type** vs hook_type: 20/20 = 100.0% (n=20); n_unclear=0
- **my_creator_type** vs creator_type: 18/20 = 90.0% (n=20); n_unclear=0
- **my_ad_format** vs ad_format: 20/20 = 100.0% (n=20); n_unclear=0
- **my_brand_first_said** vs brand_first_said: 18/20 = 90.0% (n=20); n_unclear=0

- **Overall** (micro-average across labels): 114/120 = 95.0% (n=120); n_unclear=0

No label is below the 0.8 label_cap among judged cells. Full detail in label_agreement.csv; mismatches in label_disagreements.csv.

