# Decisions

- Audit treats a blank stopped_date as live on 2026-10-26; days_live checked against (stopped_date or 2026-10-26) minus launch_date.
- Audit reports ad counts at candidate spend floors [0, 1000, 5000, 10000, 25000, 50000, 100000]; the spend floor itself is not yet chosen.
- Audit flags posts with likes <= 5 as possible hidden like counts.
- Audit counts a transcript as present when the transcript cell is non-null and non-empty.
- Sponsored share reported against the is_sponsored breakdown (yes/no/unclear), since the field is categorical rather than boolean.
- days_live is used as recorded in the data; no analysis depends on exact day counts.
