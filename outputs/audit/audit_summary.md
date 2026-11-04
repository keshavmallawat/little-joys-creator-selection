# Data audit — Little Joys

Source: data/ (read-only). Reference live date: 2026-10-26. Facts only; no interpretation or recommendations.

Rows loaded: ads=100, creators=20, creator_posts=392, creator_audience=3.

## 1. Schema

**ads.csv** — 100 rows, 56 columns.
- Columns in README guide present: 56/56.
- Missing (in guide, absent from file): none.
- Extra (in file, not in guide): none.
- Columns with any nulls: ad_copy, hook_type, hook_text_on_screen, ad_format, story_structure, creator_age, child_role, brand_first_said (per-column counts in schema_ads.csv).

**creators.csv** — 20 rows, 21 columns.
- Columns in README guide present: 16/16.
- Missing (in guide, absent from file): none.
- Extra (in file, not in guide): creator_id, name, profile_url, posts_in_file, persona_description.
- Columns with any nulls: bio (per-column counts in schema_creators.csv).

**creator_posts.csv** — 392 rows, 32 columns.
- Columns in README guide present: 29/29.
- Missing (in guide, absent from file): none.
- Extra (in file, not in guide): creator_id, handle, transcript_language.
- Columns with any nulls: duration_s, caption, plays, hook_style, child_ages, brands_visible, on_screen_text, transcript, transcript_language (per-column counts in schema_creator_posts.csv).

**creator_audience.csv** — 3 rows, 10 columns.
- Columns in README guide present: 7/7.
- Missing (in guide, absent from file): none.
- Extra (in file, not in guide): creator_id, handle, platform.
- Columns with any nulls: brands_in_past_year (per-column counts in schema_creator_audience.csv).

## 2. ads.csv integrity

- Duplicate ad_id rows: 0 (distinct ad_id values: 100 of 100). See ads_duplicate_ad_id.csv.
- Blank stopped_date (treated as live on 2026-10-26): 0 of 100.
- stopped_date before launch_date: 0.
- days_live inconsistent with dates: 74 (expected = (stopped_date or 2026-10-26) - launch_date). See ads_date_issues.csv.
  - Mismatch diff distribution (recorded minus expected): diff=-1: 74.
- Funnel ordering violations: 0.
- revenue_inr > 0 with 0 purchases: 0. See ads_revenue_no_purchase.csv.
- spend_inr = 0: 0. See ads_zero_spend.csv.

## 3. Exposure

- Distributions of spend_inr, impressions, days_live written to exposure_distributions.csv. Key values:
  - spend_inr: min=298.0, p50=31737.0, p90=186421.1, max=659494.0, mean=72642.28 (n=100).
  - impressions: min=2095.0, p50=227322.0, p90=1291626.7, max=5718650.0, mean=540335.49 (n=100).
  - days_live: min=1.0, p50=17.5, p90=44.0, max=74.0, mean=20.06 (n=100).
- Ads meeting candidate spend floors (n=100 total):
  - spend_inr >= 0: 100/100 = 100.0% (n=100).
  - spend_inr >= 1000: 99/100 = 99.0% (n=100).
  - spend_inr >= 5000: 90/100 = 90.0% (n=100).
  - spend_inr >= 10000: 80/100 = 80.0% (n=100).
  - spend_inr >= 25000: 57/100 = 57.0% (n=100).
  - spend_inr >= 50000: 37/100 = 37.0% (n=100).
  - spend_inr >= 100000: 21/100 = 21.0% (n=100).

## 4. Creators (posts)

- Creators with at least one post: 20 of 20.
- Posts total: 392. Per-creator detail in creators_posts_summary.csv.
- Post date range overall: 2022-03-03 to 2026-10-27.
- Posts with a transcript: 113/392 = 28.8% (n=392).
- Sponsored posts (is_sponsored = 'yes'): 105/392 = 26.8% (n=392). Values yes/no/unclear: 105/278/9.
- Posts with likes <= 5 (possible hidden likes): 10/392 = 2.6% (n=392).

## 5. creator_audience coverage

- Creators with audience data: 3/20 = 15.0% (n=20).
- With data: CR-14, CR-15, CR-20.
- Without data: CR-01, CR-02, CR-03, CR-04, CR-05, CR-06, CR-07, CR-08, CR-09, CR-10, CR-11, CR-12, CR-13, CR-16, CR-17, CR-18, CR-19.
- See creator_audience_coverage.csv.

