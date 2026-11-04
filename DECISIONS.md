# Decisions

- Audit treats a blank stopped_date as live on 2026-10-26; days_live checked against (stopped_date or 2026-10-26) minus launch_date.
- Audit reports ad counts at candidate spend floors [0, 1000, 5000, 10000, 25000, 50000, 100000]; the spend floor itself is not yet chosen.
- Audit flags posts with likes <= 5 as possible hidden like counts.
- Audit counts a transcript as present when the transcript cell is non-null and non-empty.
- Sponsored share reported against the is_sponsored breakdown (yes/no/unclear), since the field is categorical rather than boolean.
- days_live is used as recorded in the data; no analysis depends on exact day counts.
- Supplementary audit reports multi-value label columns both as literal whole-cell values and as atomic labels split on ';' (an ad can carry several atomic labels, so atomic counts may sum past the ad total).
- Supplementary audit flags a transcript as placeholder-looking by three facts: length under 100 characters, identical text repeated across posts, or a sentence of 15+ characters recurring 3 or more times within one transcript.
