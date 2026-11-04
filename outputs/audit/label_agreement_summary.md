# Label spot-check agreement — Little Joys ads

Source: outputs/audit/label_check.csv (read-only here), 20 ads in the sheet. For each label the reviewer's my_* judgment is compared to the stored label; the rate below is agreement with its denominator n. Comparison and presentation only — no verdict or selection is made here.

label_cap threshold (from config/decision_rules.yaml): 0.8. A label with agreement below it is flagged below_label_cap (a fact, not a decision). Reviewer entries of 'unclear' are excluded from n and tallied as n_unclear; blank cells are ads not judged.

## Per-label agreement

- **my_child_role_reacts** vs child_role: n/a (n=0); n_unclear=0
- **my_child_in_first_3s** vs child_in_first_3s: n/a (n=0); n_unclear=0
- **my_hook_type** vs hook_type: n/a (n=0); n_unclear=0
- **my_creator_type** vs creator_type: n/a (n=0); n_unclear=0
- **my_ad_format** vs ad_format: n/a (n=0); n_unclear=0
- **my_brand_first_said** vs brand_first_said: n/a (n=0); n_unclear=0

- **Overall** (micro-average across labels): n/a (n=0); n_unclear=0

No label is below the 0.8 label_cap among judged cells. Full detail in label_agreement.csv; mismatches in label_disagreements.csv.

