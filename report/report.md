# Five creators to test next

_Prepared for the Little Joys Marketing Manager | Keshav Mallawat | 5 November 2026_

> GitHub-readable copy of `Little_Joys_Creator_Decision_Report.docx` and `.pdf`. Same conclusions and the same source IDs; each ID is a row in `outputs/final/claims.csv` or is explained in the source register at the end.

| | | | |
|---|---|---|---|
| **Question** | Which five of 20 creators to test, and what each should say (data_rows: 20) | **Period covered** | Ads launched 2026-06-10 to 2026-10-09 (data_ad_dates), results to 2026-10-26; posts to 2026-10-27 (data_posts_window) |
| **Status** | Final version. Not legal advice. | **Ad figures** | Simulated numbers supplied by Galvor, not Little Joys results |

| **5 + 3** | **2.22 vs 0.92** | **3 of 5** |
|---|---|---|
| creators to test first, plus three backups in order | return per rupee when a child reacts to the taste vs not, on 80 simulated ads (ads_H1: 2.22, 0.92) | picks rank outside the score's top five (6th (cr_CR-01_frozen_rank: 6), 9th (cr_CR-03_frozen_rank: 9), 10th (cr_CR-11_frozen_rank: 10)); I chose them for food content and role |

## 1. The answer

**Five creators to test now, three backups, and one condition: clear legal and exclusivity before anyone films.**

> **Recommendation.** **Test CR-13, CR-03, CR-11, CR-01 and CR-19 first**, in a small controlled round. If one cannot go ahead, use CR-05, CR-09 and CR-16 in that order.
>
> **Why these five:** together they cover the roles a test needs. CR-13 already makes branded family content. CR-03 and CR-01 are doctors who can speak on nutrition with authority. CR-11 is a family vlogger with a child in every recent post. CR-19 already works in milk. I chose them for fit with feeding content and for a spread of roles, not for the score alone.
>
> **This is my judgement, not the score's top five:** the score alone would pick CR-12, CR-15, CR-13, CR-09 and CR-19. Later checks led me to set CR-12 and CR-15 aside and to move CR-09 to backup (section 3).

> **Read this before you rely on it.** **The ad figures are simulated.** They are not Little Joys results or forecasts.
>
> **The labels come from an AI system** and are not always right.
>
> **The ad findings are associations.** They do not prove that an ad style or a creator causes sales.

| Creator | Role | What they bring | Main risk |
|---|---|---|---|
| **CR-13**<br>mumma_and_ridhu | Ad integrator | Already makes branded family content: 60.0% of her 20 recent posts are sponsored (cr_CR-13_sponsored_share: 60.0%, n=20). Top five in 83.5% of 200 resamples (cr_CR-13_bootstrap_top5: 83.5%, n=200); rank moves only from 3 to 2 without comment-for-link posts (cr_CR-13_rank_excl_link: 2, 3). | Only 5.0% of recent posts mention food (cr_CR-13_food_term_share: 5.0%, n=20); feeding content is new for her. No audience data (cr_CR-13_flags). |
| **CR-03**<br>ekamichildcare | Clinical voice | Most food content of the five: 35.0% of recent posts (cr_CR-03_food_term_share: 35.0%, n=20). No comment-for-link posts (cr_CR-03_link_request_share: 0.0%, n=20). Only 10.0% sponsored (cr_CR-03_sponsored_share: 10.0%, n=20). | Flagged for legal review (cr_CR-03_flags: 2). Sponsored a rival, Troovy, on 2026-09-07 (cr_CR-03_competitor_posts: 1 post). Weak stability: top five in 15.0% of resamples (cr_CR-03_bootstrap_top5: 15.0%, n=200). |
| **CR-11**<br>raja_choudhary04 | Family vlog | A child appears in all 20 recent posts (cr_CR-11_child_share: 20 of 20) and 25.0% mention food (cr_CR-11_food_term_share: 25.0%, n=20). No comment-for-link posts (cr_CR-11_link_request_share: 0.0%, n=20). | Sponsored rivals three times: Gritzo twice, Troovy on 2026-10-07 (cr_CR-11_competitor_posts: 3 posts). Lowest stability: 11.5% (cr_CR-11_bootstrap_top5: 11.5%, n=200). A child on camera is not a child tasting (proxy_precision: 3 of 24, 12.5%). |
| **CR-01**<br>drgarima_mehta | Clinical voice | 30.0% of recent posts mention food (cr_CR-01_food_term_share: 30.0%, n=20). Her rank improves from 6 to 4 without comment-for-link posts (cr_CR-01_rank_excl_link: 4, 6). Lightly sponsored at 10.0% (cr_CR-01_sponsored_share: 10.0%, n=20). | Flagged for legal review (cr_CR-01_flags: 2). Too few sponsored posts to judge her sponsored work. Top five in 28.5% of resamples (cr_CR-01_bootstrap_top5: 28.5%, n=200). |
| **CR-19**<br>instamommy_suchi | Milk-category creator | Has already posted milk-nutrition content, including for a rival (P-CR-19). Top five in 50.5% of resamples (cr_CR-19_bootstrap_top5: 50.5%, n=200); 15.0% of posts mention food (cr_CR-19_food_term_share: 15.0%, n=20). | 75.0% of recent posts are sponsored, the most of the five (cr_CR-19_sponsored_share: 75.0%, n=20). Sponsored Bournvita on 2026-08-02 and Complan on 2026-10-06 (cr_CR-19_competitor_posts: 2 posts). |

_Backups, in order: use the next one if a creator declines or fails the checks in section 5._

| Backup | Why | Main risk |
|---|---|---|
| **CR-05**<br>sia_3vedi | Largest reach of the 20: 2,831,180 followers (cr_CR-05_followers: 2831180). A child appears in all 18 recent posts (cr_CR-05_child_share: 18 of 18). | Only 5.6% of recent posts mention food (cr_CR-05_food_term_share: 5.6%, n=18). Top five in 19.5% of resamples (cr_CR-05_bootstrap_top5: 19.5%, n=200). |
| **CR-09**<br>doc_mama_and_babies | Ranks 4 of 20 on the score (cr_CR-09_frozen_rank: 4 of 20) and is in the top five in 61.0% of resamples (cr_CR-09_bootstrap_top5: 61.0%, n=200). | Three flags: hidden likes, no audience data, legal review (cr_CR-09_flags: 3). 72.7% of her 11 recent posts are sponsored (cr_CR-09_sponsored_share: 72.7%, n=11); she did a sponsored Little Joys post on 2025-07-11 (cr_CR-09_little_joys_posts: 1). |
| **CR-16**<br>paediatrics_decoded | A paediatrician with no sponsored posts in the window (cr_CR-16_sponsored_share: 0.0%, n=20); top five in 34.0% of resamples (cr_CR-16_bootstrap_top5: 34.0%, n=200). | Flagged for legal review (cr_CR-16_flags: 2). A third clinical creator breaks the cap of two (rule_cap: 2); she comes in only if CR-01 or CR-03 drops. |

## 2. What each creator should say

**One idea, one hook and one quoted product line per creator. No line claims a health outcome.**

| Creator | Content idea | Suggested hook | Product line (from Little Joys' ads) |
|---|---|---|---|
| **CR-13** | A home-routine film in her own style: a relatable evening-hunger problem, one product as the quiet fix, a soft close with no comment-for-link. Add a child-tastes beat only if her child really reacts (P-CR-13).<br>**Avoid:** high-pressure sales language, cold studio lighting, and anything that ignores festivals and family context. | "The 4 PM hunger gap: here's what I keep ready." | "Made with ragi, bajra, almonds and walnuts, sweetened naturally with jaggery and dates." (LJ-007) |
| **CR-03** | A calm doctor explainer on the nutrition gap, with on-screen text. The product is one option in a balanced diet, never a cure. Close: "check the label, ask your paediatrician" (P-CR-03).<br>**Avoid:** influencer-style transitions, casual slang, and a script that reads like an advert. | "Bachcha khaana kha raha hai, par kya use sahi nutrition mil raha hai?" (He is eating, but is he getting the right nutrition?) | "No added sugar, no preservatives." Mixes into meals like roti and pancakes (LJ-036) |
| **CR-11** | A candid mini-vlog of the child's morning-milk moment: the mix goes in, the child tastes it and reacts on camera. Film that beat only if the reaction is real (P-CR-11).<br>**Avoid:** studio lighting, formal scripted claims, and frames with no family in them. | "Mamma ke morning milk wale natak ka ek solution." (A fix for the morning-milk drama.) | "Made with millets and dry fruits, sweetened with jaggery and dates." (LJ-009) |
| **CR-01** | A split-screen doctor explainer in Hindi with English product terms: read the ingredient label, then show what is in the pack. Ingredients and general benefit only (P-CR-01).<br>**Avoid:** English-only audio and a sales pitch with no medical context. | "What I check on a food label before it becomes my child's daily habit." | "Sweetened with jaggery and dates, with zero refined sugar or artificial sweeteners." (LJ-072) |
| **CR-19** | A household-prop explainer in her style (she often uses props such as magnifying glasses (P-CR-19)): plain milk next to milk with the mix, then the child tastes and reacts. Do not reuse the magnifying-glass-over-milk visual from her Complan post (cr_CR-19_competitor_posts).<br>**Avoid:** a cold, corporate advert feel; show the product used at home. | "Bachche ke milk mein main kya add karti hoon, aur kyun?" (What I add to my child's milk, and why.) | "No artificial sweeteners, naturally sweetened with jaggery and dates." (LJ-022) |

> **Before any of this goes live.** Hooks are suggestions to adapt in each creator's voice. None names the brand yet: the first-3-seconds test in section 5 adds that in one cut.
>
> **The Hindi lines need a native-speaker check.**
>
> Product lines are quoted from Little Joys' own ad text and **need legal sign-off.** Leave protein figures out until legal confirms them: the Nutrimix ads quote 5g, 6g and 9g (product_protein_figures: 5, 6, 9), and the mix in LJ-036 quotes 12g per scoop.
>
> No line should mention disease, treatment or a health outcome.

## 3. How the shortlist was chosen

**The score picked a different five. I overruled it where the data was weakest, and I show what that costs.**

**The scoring rule was fixed and committed before any creator was scored.** Each creator got three parts, and each part was ranked against the other 19 creators.

| Part of the score | Weight | What it measures |
|---|---|---|
| **Evidence fit** | 0.40 (rule_weights: 0.40) | How often recent posts show a child with the product. |
| **Audience response** | 0.35 (rule_weights: 0.35) | Comments and reshares per play. |
| **Sponsored fit** | 0.25 (rule_weights: 0.25) | How sponsored posts do next to ordinary ones. |

"Recent" means the 12 months to 2026-10-27, which is 374 of the 392 posts (data_posts_window: 12, 374, 392). A part with too little data scores a neutral 0.5: it needs at least 10 posts with plays, or at least 4 sponsored posts (rule_min_data: 10, 4, 0.5). A portfolio rule, also set in advance, allows at most 2 clinical-persona creators in the final five (rule_cap: 2).

**Checks added after I saw the ranking are post-hoc and not part of the score:**

- Rank stability: I resampled each creator's recent posts 200 times, re-scored everyone each time, and counted how often a creator stays in the top five (rule_stability: 200). A creator who stays in most runs is a steady pick; one who rarely does depends on which posts happen to fall in the window.
- Food content: the share of recent posts mentioning food or feeding terms.
- Comment-for-link posts: the share of posts asking viewers to "comment for a link", which can inflate comment counts and so overstate audience response.
- A hand check of 24 posts tagged "child and product": only 3 showed a child eating or reacting to food, so the score's feeding measure is weak (proxy_precision: 3 of 24, 12.5%).

**Where my judgement changed the score-only result:**

- **CR-12 (score rank 1) and CR-15 (rank 2) are out.** Comment-for-link posts are 40.0% of CR-12's recent posts (cr_CR-12_link_request_share: 40.0%, n=20) and 45.0% of CR-15's (cr_CR-15_link_request_share: 45.0%, n=20). Without them CR-15 falls from rank 2 to 14 (cr_CR-15_rank_excl_link: 14, 2), but CR-12 stays at rank 1 (cr_CR-12_rank_excl_link: 1). CR-12 is out for a different reason: none of its recent posts mention food (cr_CR-12_food_term_share: 0.0%, n=20).
- **CR-09 moves to backup.** Ranked 4 on the score (cr_CR-09_frozen_rank: 4), but with three flags (cr_CR-09_flags: 3), a 72.7% sponsored share on only 11 recent posts (cr_CR-09_sponsored_share: 72.7%, n=11) and an earlier sponsored Little Joys post (cr_CR-09_little_joys_posts: 1).
- **CR-20 is not on the list.** The audience record for CR-20 shows 70.1% men (cr_CR-20_audience: 70.1%) and lists Little Joys among the brands it worked with in the past year. It ranks 16 on the score (cr_CR-20_frozen_rank: 16) and none of its recent posts mention food (cr_CR-20_food_term_share: 0.0%, n=20). One thing does not line up: no recent post shows Little Joys (cr_CR-20_little_joys_posts: 0, n=20), so check whether that partnership is still running before ruling CR-20 out for good.
- CR-01 (ranked 6 (cr_CR-01_frozen_rank: 6)), CR-03 (9 (cr_CR-03_frozen_rank: 9)) and CR-11 (10 (cr_CR-11_frozen_rank: 10)) come in **for food content and a spread of roles, not for score.** With the cap of two clinical creators, CR-03 beats CR-16 (15.0% food (cr_CR-16_food_term_share: 15.0%), no sponsored posts) and CR-05 has almost no food content, so CR-11 takes the last place. 
- The cost: CR-03 and CR-11 are less stable than CR-16, CR-05 and CR-09. I also re-scored with three alternate weightings (sponsored fit dropped, set to neutral for everyone, or needing at least 4 non-sponsored posts). Counting the original score as one of four versions, CR-13 and CR-19 are in the top five in all 4 (cr_CR-13_weightings_top5: 4) (cr_CR-19_weightings_top5: 4), CR-01 in 2 (cr_CR-01_weightings_top5: 2), CR-11 in 1 (cr_CR-11_weightings_top5: 1) and CR-03 in none (cr_CR-03_weightings_top5: 0). So **CR-03 is on the list for his food content and clinical role, not for score.**

| Creator | Score rank (of 20) | Rank stability (share of 200 resamples in the top five) | Food content (recent posts) | Sponsored share (recent posts) |
|---|---|---|---|---|
| **CR-13** mumma_and_ridhu | 3 (cr_CR-13_frozen_rank: 3 of 20) | 83.5% (cr_CR-13_bootstrap_top5: 83.5%) | 5.0% (cr_CR-13_food_term_share: 5.0%) | 60.0% (cr_CR-13_sponsored_share: 60.0%) |
| **CR-19** instamommy_suchi | 5 (cr_CR-19_frozen_rank: 5 of 20) | 50.5% (cr_CR-19_bootstrap_top5: 50.5%) | 15.0% (cr_CR-19_food_term_share: 15.0%) | 75.0% (cr_CR-19_sponsored_share: 75.0%) |
| **CR-01** drgarima_mehta | 6 (cr_CR-01_frozen_rank: 6 of 20) | 28.5% (cr_CR-01_bootstrap_top5: 28.5%) | 30.0% (cr_CR-01_food_term_share: 30.0%) | 10.0% (cr_CR-01_sponsored_share: 10.0%) |
| **CR-03** ekamichildcare | 9 (cr_CR-03_frozen_rank: 9 of 20) | 15.0% (cr_CR-03_bootstrap_top5: 15.0%) | 35.0% (cr_CR-03_food_term_share: 35.0%) | 10.0% (cr_CR-03_sponsored_share: 10.0%) |
| **CR-11** raja_choudhary04 | 10 (cr_CR-11_frozen_rank: 10 of 20) | 11.5% (cr_CR-11_bootstrap_top5: 11.5%) | 25.0% (cr_CR-11_food_term_share: 25.0%) | 35.0% (cr_CR-11_sponsored_share: 35.0%) |
| Set aside: CR-12 | 1 (cr_CR-12_frozen_rank: 1 of 20) | 99.0% (cr_CR-12_bootstrap_top5: 99.0%) | 0.0% (cr_CR-12_food_term_share: 0.0%) | 15.0% (cr_CR-12_sponsored_share: 15.0%) |
| Set aside: CR-15 | 2 (cr_CR-15_frozen_rank: 2 of 20) | 76.0% (cr_CR-15_bootstrap_top5: 76.0%) | 10.0% (cr_CR-15_food_term_share: 10.0%) | 30.0% (cr_CR-15_sponsored_share: 30.0%) |

_Stability colour: green is 50% or more of resamples, amber 20% to 49%, red under 20%._

## 4. What the ads show

**One ad pattern holds up: a child reacting to the taste, most strongly when a child leads. One is only a lead: the brand named early. Neither can be tied to a creator.**

**How to read the table:**

- Return per rupee (ROAS) is revenue divided by ad spend. A value of 2.22 means the ads in that group brought in about Rs 2.22 for every Rs 1 spent. A value under 1, such as 0.92, means they brought back less than they cost (ads_H1: 2.22, 0.92).
- Each group is pooled (total revenue over total spend), so a high-spend ad counts for more than a small one. Purchase rate is purchases divided by link clicks.
- The 95% interval (ads_H1: 95) is the range of gaps that resampling the ads would give. If it includes zero, the gap could be chance.
- All figures use the 80 ads with at least 10,000 rupees of spend (data_floor_set: 80, 100, 10000), and every label used is present for all 80 (data_floor_label_coverage: 80).

| Finding | With it: return per rupee | Without it | Gap and 95% interval | Purchase rate per link click, with vs without |
|---|---|---|---|---|
| **1. A child reacts to the taste**<br>Tier: **supported** | 2.22 on 36 ads (ads_H1: 2.22, n=36) | 0.92 on 44 ads (ads_H1: 0.92, n=44) | +1.31, from 0.22 to 2.35. Excludes zero (ads_H1: 1.31, 0.22, 2.35) | 4.07% vs 2.28% (ads_H1_cvr_in: 4.07%) (ads_H1_cvr_out: 2.28%) |
| **2. The brand is named in the first 3 seconds** (ads_H3: 3)<br>Tier: **suggestive** | 2.21 on 30 ads (ads_H3: 2.21, n=30) | 1.11 on 50 ads (ads_H3: 1.11, n=50) | +1.10, from -0.21 to 2.44. Includes zero (ads_H3: 1.10, -0.21, 2.44) | 4.62% vs 2.40% (ads_H3_cvr_in: 4.62%) (ads_H3_cvr_out: 2.40%) |

Both gaps keep their direction under every check I fixed before looking at results: three different spend floors, medians instead of totals, dropping the highest-spend ad from each group, and leaving out each of the 8 stop-date batches in turn (ads_robust_H1: 5 of 5, 8 of 8) (ads_robust_H3: 5 of 5, 8 of 8). Three limits stay. Finding 1 reverses inside gummies (5 ads with a reacting child, 14 without), too few to count as a check (ads_robust_H1_strata: 5, 14), and 43 of the 80 ads are milk-mix powder (floor_mix_milk_mix_powder: 43 of 80), so it is mostly a milk-mix result. Finding 1's interval starts only 0.22 above zero, and finding 2's includes zero, so **treat finding 2 as a lead.** The ads sit in only 8 stop-date batches (limit_stopped_date_batches: 8), so the true intervals are wider than shown.

A third result, that ads presented by a parent or caregiver return less (0.92 against 2.14 on 47 and 33 ads (ads_H6: 0.92, 2.14, 47, 33)), overlaps with finding 1: 22 ads sit in both groups (posthoc_H1in_H6in: 22). I did not count it as a separate finding. Splitting the two shows what sits underneath finding 1:

| Child reacts to the taste | Parent or caregiver presents | Return per rupee | Ads |
|---|---|---|---|
| **Yes** | **No** | **3.03** (posthoc_H1in_H6out: 3.03) | 14 (posthoc_H1in_H6out: n=14) |
| Yes | Yes | 1.21 (posthoc_H1in_H6in: 1.21) | 22 (posthoc_H1in_H6in: n=22) |
| No | Yes | 0.75 (posthoc_H1out_H6in: 0.75) | 25 (posthoc_H1out_H6in: n=25) |
| No | No | 1.16 (posthoc_H1out_H6out: 1.16) | 19 (posthoc_H1out_H6out: n=19) |

**The lift sits in one corner.** When a child reacts and someone other than a parent presents, return is 3.03. When a parent presents and the child reacts, it is 1.21, close to the 1.16 of ads with neither feature. Nine of those 14 ads have a child presenting (posthoc_H1in_H6out_child_presenter: 9, 14). This split is post-hoc and descriptive: there is no interval, the cells are small, and most of the ads are milk-mix powder. My reading is that the lift goes with a child-led format, not with the reaction shot alone.

**What this means for the shortlist.** Four of my five creators are adult presenters (two doctors, two mothers); only CR-11 films a child as the lead. The ads carry no creator ID (limit_ads_no_creator_id), so they cannot say how any creator would do. I kept the five, and I added a child-led cut for every creator to the test in section 5. Finding 1 was one of five hypotheses set before I saw the results; finding 2 was one of four exploratory ones (9 in all). The 179 comparisons counts every rerun and check (comparisons_ad_findings: 179), but with that many looks some gaps will be luck. Use these findings as things to test, not rules.

## 5. Limits and next steps

**The data cannot show price, audience fit or cause. These steps close the gaps, and these facts would change my answer.**

**What could be wrong:**

- The performance numbers are simulated and I treated them as the brand's own ad export. They are not a forecast. The AI labels matched the answers on my review sheet in 114 of 120 judgements (label_ALL_LABELS: 114 of 120, 95.0%) on 20 ads (label_my_hook_type: 20). An AI assistant pre-filled that sheet and I reviewed it, so it is a weaker check than a sheet filled in blind. I did not watch any video; creator descriptions come from captions, profile text and labels.
- Audience data exists for only 3 of 20 creators (limit_audience_coverage: 3, n=20), none of the five. There is no pricing data (limit_pricing), so nothing here says what a creator costs. Reach is context, not scored: the five have 814,499 followers together (five_total_followers: 814499), less than CR-05 alone.
- The hand check covered 24 posts (proxy_precision: 24), none from CR-03, so I do not know how often he shows a child eating. Rank stability is weak for CR-03, CR-11 and CR-01. 39 of 392 posts have no play count (limit_missing_plays: 39, 392); days_live is one day short in 74 of 100 ads and is not used (data_ad_dates: 74, 100).
- Data check against the source files: 100 ads, 20 creators, 392 posts, 3 audience records (data_rows: 100, 20, 392, 3); money in rupees; the 80 ads over the spend floor hold 98.5% of spend (data_floor_set: 80, 98.5%) and return 1.50 per rupee together (data_floor_roas: 1.50). A separate script in the repo, src/verify_independent.py, recomputes the headline figures from the raw files with its own code, and all 26 checks match.

**What would change my answer:**

- A creator says a competing deal is open, or will not give category exclusivity: move to the next backup in order.
- Legal rejects a clinical creator's claims or disclosure: drop that creator, and do not fill the slot with CR-16 if it would make three clinical creators.
- Audience data, once bought, shows a creator's followers are mostly outside the buyer you want: drop that creator.
- Creator rates make a pick cost far more than the others: re-rank on cost per test, which this data cannot do.

**Next steps, in order:**

1. **Product and legal review.** Legal confirms every product line and the protein figure. Clinical creators CR-03 and CR-01 are flagged for review; ASCI's influencer guidelines expect a disclosure label on paid posts and, for health and nutrition advice, qualifications stated upfront (EXT-ASCI). Legal should also read the 2022 central guidelines on misleading advertisements and endorsements (EXT-DCA), and confirm who signs for CR-11, whose bio lists a manager.
2. **Exclusivity checks.** CR-03, CR-11 and CR-19 have each posted for a rival recently. Ask each of the five whether a competing deal is open, and ask for category exclusivity with a cool-off period. Check the history of CR-09's Little Joys post before any approach. The rival brands named here (Gritzo, Troovy, Complan, Bournvita) are my reading of the category; the data does not mark rivals.
3. **A small controlled test.** Fix the creator and the product, change one thing per cut ("Little Joys" said in the first 3 seconds (ads_H3: 3) or later; child-tastes beat on or off; a child-led version or an adult-led one), spend the same on each cut, and judge by purchase rate per link click. Write the pass mark down before launch. One test will not settle a creator.
4. **Fill the gaps:** audience panels for the five, creator rates, and a creator ID on each ad.

## Source register

_Every claim ID is also a row in outputs/final/claims.csv, with its n and caveat. Code and rebuild steps: github.com/keshavmallawat/little-joys-creator-selection (README)._

| ID | What it is | Where it comes from |
|---|---|---|
| cr_CR-13_bootstrap_top5 (same pattern for every creator and measure) | Per-creator figures: score rank, rank stability, food share, sponsored share, comment-for-link share, rank without those posts, child-on-camera share, rival and past Little Joys posts, followers, flags | outputs/creators/*.csv, data/creator_posts.csv |
| ads_H1, ads_H3, ads_H6, ads_H1_cvr_in | Ad-group comparisons: return per rupee, confidence interval, purchase rate | outputs/ads/findings.csv |
| ads_robust_H1, floor_mix_milk_mix_powder, posthoc_H1in_H6in | Robustness checks, floor-set mix, post-hoc table | outputs/ads/robustness.csv, structural.csv, posthoc_h1_h6.csv |
| rule_weights, rule_cap | Scoring rule fixed before scoring | config/weights.yaml |
| data_rows, limit_pricing, comparisons_ad_findings, five_total_followers | Row counts, dates, units, missing values, spend floor, limits, number of tests run | data/*.csv, outputs/audit/ |
| label_ALL_LABELS, proxy_precision | Keshav's review of the AI labels (sheet pre-filled by an AI assistant) and his own check of child-and-product posts | outputs/audit/, outputs/final/manual_checks.csv |
| LJ-007 (and other ad IDs), product_protein_figures | Text of the Little Joys ad with that ID, field claims_made | data/ads.csv |
| P-CR-13 (and other creator IDs) | Profile and caption text for that creator (AI-written labels, not watched) | data/creators.csv, data/creator_posts.csv |
| EXT-ASCI | ASCI, Guidelines for Influencer Advertising in Digital Media, with the 17 Aug 2023 health addendum; read 2026-11-05 | ascionline.in/wp-content/uploads/2023/08/GUIDELINES-FOR-INFLUENCER-ADVERTISING-IN-DIGITAL-MEDIA.pdf |
| EXT-DCA | Department of Consumer Affairs note on endorsements, which names the 2022 misleading-advertisements guidelines; named only, not summarised | consumeraffairs.gov.in, "Endorsement Know-Hows" (PDF) |
