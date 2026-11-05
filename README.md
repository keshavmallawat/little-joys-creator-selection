# Little Joys: which 5 creators, and what should each say

This repo answers Galvor's take-home question for the kids' nutrition brand Little Joys: which 5 of 20 creators should it work with next, and what should each of them say. Everything comes from the data Galvor supplied (100 ads, 20 creators, 392 creator posts, audience data for 3 creators).

## The answer

Work with CR-13, CR-03, CR-11, CR-01 and CR-19. If one drops out, the backups in order are CR-05, CR-09 and CR-16. Roles: CR-13 is an ad integrator, CR-03 and CR-01 are clinical voices, CR-11 is a family vlog with a child in every post, and CR-19 already makes milk-category content. The write-up for the marketing manager is in `report/` (an editable Word file, a six-page A4 PDF and `report.md`, which carry the same conclusions and source IDs), and a brief for each creator (hooks, a five-beat outline, sample lines, what to avoid, a competitor note, one metric to watch) is in `outputs/final/directions_draft.md`.

The scoring I fixed in advance put CR-12 and CR-15 at the top, and I did not pick them. When I set aside posts that say "comment for a link", CR-15 falls from rank 2 to 14, and 9 of its 20 recent posts are of that kind. CR-12 stays at rank 1, but none of its 20 posts mentions food or feeding. So the final five is my own judgement after those checks. `outputs/creators/creator_scores.csv` is still the result of the pre-set scoring and I have not edited it.

## What the ads show

Using the 80 ads with spend of at least 10,000:

- Ads where a child reacts to the taste returned 2.22 per rupee of spend against 0.92 for the rest (36 ads against 44).
- Ads that name the brand in the first 3 seconds returned 2.21 against 1.11 (30 ads against 50). The gap's interval includes zero, so this is a lead, not a result.
- Both gaps keep their direction at all three spend floors, in the median-ad comparison, without the highest-spend ad of each group, and leaving out each of the 8 stop-date batches in turn. The child-reacts gap reverses inside gummies (5 ads against 14), too few to count as a check. Ads fronted by a parent or caregiver returned less (0.92 against 2.14), but that group overlaps heavily with the child-reacts group, so the report does not count it separately.
- The ads sit in only 8 stop-date batches, so the confidence intervals are narrower than they should be. Treat these as leads, not proof.

The ads carry no creator ID, so these findings are about ad styles. They cannot be tied back to a specific creator.

## How it was done

- The hypotheses, the spend floor and the decision rules are in `config/` and were committed before any performance number was computed. The creator scoring weights were committed before the scores. The git history shows the order.
- Anything I added after seeing results is labelled post-hoc, and the original result stays as the main one.
- Every number in `outputs/final/claims.csv` is read from a script's output, never typed. `src/check_numbers.py` checks a text file against that table.
- Results are stated as differences between groups, never as causes, and every rate carries its n. The random seed is 42 everywhere.
- Decisions are logged one line each in `DECISIONS.md`.

## Layout

| Path | What is in it |
|---|---|
| `config/` | Hypotheses, parameters, decision rules, scoring weights, `requirements.txt` |
| `src/` | One script per step, plus `run_all.py` and `check_numbers.py` |
| `outputs/audit/` | Data checks and the label spot-check |
| `outputs/ads/` | Ad findings, robustness checks, the post-hoc H1 by H6 table |
| `outputs/creators/` | Scores, sensitivity runs, reading packs, content and brand scans |
| `outputs/final/` | `claims.csv`, `manual_checks.csv`, creator directions |
| `DECISIONS.md` | The decision log |

## Run it

The data is not in this repo. Take the four CSVs from Galvor's `little-joys-data.zip` (`ads.csv`, `creators.csv`, `creator_posts.csv`, `creator_audience.csv`) and put them in a `data/` folder at the repo root.

```
pip install -r config/requirements.txt
python src/run_all.py
python src/check_numbers.py outputs/final/directions_draft.md
```

The full run takes about 20 seconds on Python 3.10. A clean re-run from scratch on Linux gave the same numbers as my Windows run. Only the row order of tied values and line endings differed.

The label spot-check is a manual step. `src/label_sample.py` writes a blank sheet of 20 ads, an AI assistant pre-filled it and I reviewed it, and `src/label_error.py` scores it. `run_all.py` leaves `label_sample.py` out so it cannot overwrite a filled sheet, and it uses the committed `outputs/audit/label_agreement.csv` when the filled sheet is absent.

`report/creator_explorer.html` is a single page (built by `python src/build_explorer.py`) that lists all 20 creators with their score rank, rank stability, food share, sponsored share and comment-for-link share. It sorts, filters and searches, and opens in any browser with no server.

To check the headline figures independently, run `python src/verify_independent.py`. It does not import the pipeline: it reads `data/` and `outputs/`, recomputes the spend-floor set, the H1, H3 and H6 ROAS and purchase rates, a fresh bootstrap interval for each, the post window, the follower total and one rank, and compares them with what the pipeline wrote (26 checks).

## What this does not cover

- The performance numbers were made up by Galvor for the exercise. I treated them as the brand's own ad account export.
- The labels come from Galvor's AI system. My review sheet matched 114 of 120 label judgements (an AI assistant pre-filled the sheet and I reviewed it, so this is not a blind check), and the hypotheses that depend on a label are capped at "suggestive" if agreement is low.
- There is no pricing data, so nothing here speaks to cost per creator.
- Audience data exists for 3 of 20 creators.
- I did not watch the videos. Creator descriptions come from captions, labels and the profile text.
- The feeding proxy in the scoring (a child on camera and the product shown) is weak. In a hand check of 24 such posts, 3 showed a child eating or reacting to food.
- Reach is not scored. The five creators have 814,499 followers between them, while CR-05 alone has 2,831,180.
- One protein figure conflicts inside Little Joys' own ads: "9g per 2 scoops" in some, "5g" in others. Legal should confirm before any script is shot.

I used AI tools while building this. The prompts and session logs go to Galvor with the submission, outside this repo.
