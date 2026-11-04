AI-drafted, to be reviewed and edited by Keshav.

# Creator directions (draft)

Every number below is tagged with the `claim_id` it comes from (in claims.csv or manual_checks.csv) with its n. Product facts are quoted only from Little Joys' own ad text (ads.csv `claims_made` / `main_benefit`) and marked "confirm with legal". Creator descriptions are drawn only from post captions and the `what_stands_out` notes in the reading pack — no post has been watched. Performance figures are simulated numbers supplied by Galvor (not Little Joys' real results) and are treated here as the brand's own ad export; the labels were added by Galvor's AI system and are imperfect. Nothing here is causal, only associational.

## Portfolio summary

These five creators are a spread of roles, not a ranking: an ad-integrator who already folds brands into polished family content (CR-13), two clinical voices for authority and reach into health-minded parents (CR-03, CR-01), a family vlog with a child in every window post (CR-11), and a milk-category creator already fluent in milk-mix nutrition messaging (CR-19). The pre-registered scoring in creator_scores.csv remains the primary result; this particular five is a human judgement made after the post-hoc validity checks. Two caveats travel with the whole set: audience demographics exist for only a few creators (limit_audience_coverage: 3 of 20, n=20), and a hand check found the "child + product" example posts rarely show a child actually eating or reacting to food (proxy_precision: 3 of 24, 12.5%, n=24). Read the per-creator "confidence" line with both in mind.

### Backups (in order)

- **CR-05 (sia_3vedi)** — very large child-led account; lands in the top 5 in a minority of resamples (cr_CR-05_bootstrap_top5: 19.5%, n=200 draws) and shows almost no food-term content (cr_CR-05_food_term_share: 5.6%, n=18). Use if a child-led slot opens.
- **CR-09 (doc_mama_and_babies)** — doctor-mom with strong role fit, but carries three flags including hidden likes and legal review (cr_CR-09_flags: hidden_likes, no_audience_data, legal_review, n=3) and is heavily sponsored (cr_CR-09_sponsored_share: 72.7%, n=11); treat its sponsored-fit signal as thin.
- **CR-16 (paediatrics_decoded)** — pediatrician with no sponsored posts in the window (cr_CR-16_sponsored_share: 0.0%, n=20) and modest food-term content (cr_CR-16_food_term_share: 15.0%, n=20); a clean clinical backup, carries legal review (cr_CR-16_flags: no_audience_data, legal_review, n=2).

---

## CR-13 — mumma_and_ridhu (ad-integrator)

**1. Role and why chosen**
- Stable across the robustness resampling: lands in the top 5 in most draws (cr_CR-13_bootstrap_top5: 83.5%, n=200 draws).
- Holds its position when comment-for-link posts are removed (cr_CR-13_rank_excl_link: rank 2, n=20), so the standing is not resting on a link mechanic.
- Already an ad-integrator — most of her window posts are sponsored (cr_CR-13_sponsored_share: 60.0%, n=20), so a branded brief fits her norm; food-feeding content is currently low (cr_CR-13_food_term_share: 5.0%, n=20), which is the gap this brief is meant to fill.

**2. The idea**
A soft-focus, domestic "mom-hack" film that places a Little Joys product inside one real daily routine. Her profile notes that what feels native is "A video that starts with a relatable domestic problem or a festive moment, uses soft-focus cinematic lighting, and integrates the product as a helpful, natural solution within a daily routine," while what would feel foreign is "High-pressure sales language, cold studio lighting, or a script that ignores the cultural context of Indian festivals and family dynamics." Keep it to one problem, one product, one calm resolution.

**3. Three hook options** (her window posts use English with some Hindi; one real observed hook_style from her mix: "text overlay identifying a relatable problem")
- (English) "The 4 PM hunger gap — here's what I keep ready."
- (Hindi) "Shaam ki bhookh aur kuch healthy nahi? Ek simple fix." [The evening hunger and nothing healthy? One simple fix.]
- (English, text-overlay style) "One tin I actually re-order — and why."
- Note: do not lean on a voiceover-montage ad format on the assumption it performs better; that format was fragile in the ad data (ads_H7: fragile, in 1.0212 n=28 vs out 1.7482 n=52, CI includes 0).

**4. Five-beat outline (30–45s)**
1. (0–3s) Relatable domestic beat + the Little Joys pack visible, brand named within the first 3 seconds — evidence for early brand naming is only suggestive (ads_H3: suggestive, in 2.2126 n=30 vs out 1.1120 n=50, CI includes 0).
2. (3–10s) The everyday problem in her own words (fussy evening snack / nutrition gap).
3. (10–25s) Product used in the routine; one ingredient/benefit line on screen.
4. (25–38s) Where it fits for a milk-mix product, a beat where her child tastes it and reacts — associated with higher ROAS but not proven, and concentrated in milk-mix powder (ads_H1: supported, child-reacts in 2.2235 n=36 vs out 0.9179 n=44, CI excludes 0; struct_child_reacts: pooled ROAS 2.2235, n=36; floor_mix_milk_mix_powder: 43 of 80, 53.8%, n=80). Reality check: the "child + product" label rarely meant real feeding on inspection (proxy_precision: 3 of 24, n=24), so only film this beat if the child genuinely tastes on camera.
5. (38–45s) Soft CTA, no comment-for-link.

**5. Three sample lines** (Little Joys facts only; confirm with legal)
- "Made with ragi, bajra, almonds and walnuts, sweetened with jaggery and dates." (source: ads.csv `claims_made` — confirm with legal)
- "9g protein in 2 scoops with milk." (source: ads.csv `claims_made`, LJ-009 Nutrimix 7+; other ads state 5g per 2 scoops (LJ-029, LJ-043, LJ-095), so confirm the figure with legal)
- "23 essential vitamins and minerals." (source: ads.csv `claims_made` — confirm with legal)

**6. Avoid**
- Her stated foreign notes: high-pressure sales language, cold studio lighting, scripts that ignore festival/family context.
- Comment-for-link mechanics (she already uses some: cr_CR-13_link_request_share: 10.0%, n=20) — they inflate comments without evidence of purchase.
- Over-relying on the question-hook or voiceover-montage ad formats as if proven (ads_H4: fragile; ads_H7: fragile).

**7. Competitor note**
Her shown brands are not direct child-nutrition competitors (cr_CR-13_brands: Ariel, Aretto, Bare Anatomy, Johnson's Baby, Prega News, …, n=15). Low conflict risk. Suggestion for the manager: a standard category-exclusivity clause for the campaign window covering kids' nutrition/health-mix brands.

**8. Primary metric + test**
Watch post-click purchase conversion (purchases ÷ link clicks). Simple test: hold CR-13 fixed, run two cuts of the same brief — brand-named-in-first-3s on vs off — and compare post-click purchase conversion. No cost metrics, since there is no pricing data (limit_pricing: 0 pricing columns found, n/a). Ad-level purchase-conversion gap figure: ads H1 and H3 (ads_H1_cvr_in: 0.0407, n=265704 link clicks; ads_H1_cvr_out: 0.0228, n=255356 link clicks; ads_H3_cvr_in: 0.0462, n=186596 link clicks; ads_H3_cvr_out: 0.0240, n=334464 link clicks).

**9. Legal:** not flagged in the data; confirm all claims with legal.

**10. Confidence: Medium.** Her standing is stable across resampling (cr_CR-13_bootstrap_top5: 83.5%, n=200) and survives removing link posts (cr_CR-13_rank_excl_link: 2); the main uncertainty is her very low current food-feeding content (cr_CR-13_food_term_share: 5.0%, n=20), plus absent audience data (cr_CR-13_flags: no_audience_data).

---

## CR-03 — ekamichildcare (clinical voice)

**1. Role and why chosen**
- Highest food/feeding content of the five (cr_CR-03_food_term_share: 35.0%, n=20), so a nutrition brief sits naturally in his feed.
- No comment-for-link posts in the window (cr_CR-03_link_request_share: 0.0%, n=20), so engagement is not propped up by a link mechanic.
- Lightly sponsored (cr_CR-03_sponsored_share: 10.0%, n=20), so a Little Joys collaboration would read as selective rather than one of many ads.

**2. The idea**
A calm clinical explainer that treats the product as one option inside a balanced diet, not a cure. His profile says what feels native is "A sponsored post must feel like a clinical consultation or a myth-busting segment. It should feature the creator in his professional attire, using text overlays to highlight key medical takeaways or product benefits," and what would feel foreign is "High-energy, influencer-style transitions, overly casual slang, or a lack of medical context … A script that reads like a generic advertisement rather than a doctor's recommendation will break trust." His own Troovy post already framed a mix as "a convenient addition to the diet … not a replacement for a balanced diet" — mirror that framing.

**3. Three hook options** (his window posts are Hindi + English; one real observed hook_style: "Direct address posing a common parenting question")
- (Hindi) "Bachcha khaana kha raha hai — par kya use sahi nutrition mil raha hai?" [The child is eating — but is he getting the right nutrition?]
- (Hindi) "Growing years mein sirf calories kaafi nahi." [In the growing years, calories alone are not enough.]
- (English) "What actually goes into your child's daily nutrition — a quick checklist."
- Note: his native hook is the direct question, but do not assume question hooks perform better — that signal was fragile in the ad data (ads_H4: fragile, in 1.2775 n=19 vs out 1.5592 n=61, CI includes 0).

**4. Five-beat outline (30–45s)**
1. (0–3s) Clinical framing + pack visible, brand named early — early naming is only suggestive (ads_H3: suggestive, CI includes 0).
2. (3–12s) The nutrition-gap question, posed plainly.
3. (12–28s) Ingredient-led explanation with on-screen text; product as "a convenient addition, not a replacement".
4. (28–38s) A child-tastes beat fits him weakly (his feed rarely shows a child eating on camera); include only if authentic — the association is unproven and concentrated in milk-mix powder (ads_H1: supported; floor_mix_milk_mix_powder: 43 of 80, n=80; proxy_precision: 3 of 24, n=24).
5. (38–45s) "Check the label, consult your pediatrician" close — no link-bait.

**5. Three sample lines** (Little Joys facts only; confirm with legal)
- "Made with millets and dry fruits, sweetened with jaggery and dates — no refined sugar." (source: ads.csv `claims_made` — confirm with legal)
- "1 scoop (15g) contains 12g plant protein from pea, brown rice and soy; roti taste stays unchanged." (source: ads.csv `claims_made` — confirm with legal)
- "No added sugar, no preservatives." (source: ads.csv `claims_made`, e.g. LJ-036 — confirm with legal)

**6. Avoid**
- His stated foreign notes: influencer transitions, casual slang, generic-ad scripts with no medical context.
- Any disease, treatment, or health-outcome claim (see item 9).
- Assuming the question-hook format is a winner (ads_H4: fragile).

**7. Competitor note**
He has shown a direct category competitor (cr_CR-03_brands: Areoveda, Little Tummys, Troovy, …, n=5 — Troovy is a kids' nutrition mix). Conflict risk is real. Suggestion for the manager: an exclusivity clause excluding competing kids' nutrition-mix brands (e.g. Troovy) for the campaign window and a cool-off period — a suggestion to weigh, not a rule.

**8. Primary metric + test**
Post-click purchase conversion (purchases ÷ link clicks). Test: hold CR-03 fixed and compare an "ingredient checklist" cut vs a "one-product-in-context" cut on post-click purchase conversion. No cost metrics (limit_pricing: 0 pricing columns). Ad-level gap: ads H1 and H3 (ads_H1_cvr_in: 0.0407, n=265704 link clicks; ads_H1_cvr_out: 0.0228, n=255356 link clicks; ads_H3_cvr_in: 0.0462, n=186596 link clicks; ads_H3_cvr_out: 0.0240, n=334464 link clicks).

**9. Legal**
CR-03 is flagged for legal review (cr_CR-03_flags: no_audience_data, legal_review, n=2). No medical claims, no health-outcome or efficacy claims, no "doctor recommends for [condition]" framing. Keep product language to ingredients and general benefit wording, and route the script through legal before shoot.

**10. Confidence: Medium.** Strongest food/feeding fit of the five (cr_CR-03_food_term_share: 35.0%, n=20) and clean of link mechanics (0.0%, n=20); the main uncertainty is the legal-review requirement, absent audience data, and low standing in resampling (cr_CR-03_bootstrap_top5: 15.0%, n=200).

---

## CR-11 — raja_choudhary04 (family vlog)

**1. Role and why chosen**
- A child appears in every window post (children_on_camera: 20 of 20, reading_pack.md) and feeding content is present (cr_CR-11_food_term_share: 25.0%, n=20), a plausible fit for a milk-mix "child tastes it" story; a child appearing is not the same as a child tasting (proxy_precision: 3 of 24, n=24).
- No comment-for-link posts in the window (cr_CR-11_link_request_share: 0.0%, n=20).
- Moderately sponsored (cr_CR-11_sponsored_share: 35.0%, n=20), so brand integration is familiar without being saturated.

**2. The idea**
A candid mini-vlog where the product enters a real moment of the child's day. His profile says native is "A video that starts with a candid, unscripted moment of family interaction or a child playing, followed by a natural, low-pressure mention of a product as part of the daily routine," and foreign is "High-production studio lighting, overly formal or scripted product claims, and a lack of family presence in the frame." His Gritzo post already framed milk as "too important to leave behind" on a trip — keep that low-pressure, first-person-child voice.

**3. Three hook options** (his window posts are mostly Hindi; one real observed hook_style: "A personal moment between the creator and a child")
- (Hindi) "Aaj subah uthte hi main bahut excited tha — bataun kyun?" [The moment I woke up today I was so excited — shall I tell you why?]
- (Hindi) "Mamma ke morning milk wale natak ka ek solution." [A fix for the morning-milk drama with Mumma.]
- (Hindi/English) "Packing for the trip — aur ek cheez main kabhi nahi bhoolta." [… and one thing I never forget.]
- Note: his native format is a candid child vlog; do not assume a scripted story-opening format performs better — that signal was fragile in the ad data (ads_H5: fragile, in 1.9359 n=17 vs out 1.2962 n=63, CI includes 0).

**4. Five-beat outline (30–45s)**
1. (0–3s) Candid child moment + pack in frame, brand named early — suggestive only (ads_H3: suggestive, CI includes 0).
2. (3–12s) The everyday "I don't want plain milk / boring breakfast" beat in the child's voice.
3. (12–26s) Product mixed in as the fun fix.
4. (26–40s) Child tastes it and reacts on camera — this fits him well and is associated with higher ROAS, though unproven and mostly seen in milk-mix powder (ads_H1: supported, in 2.2235 n=36 vs out 0.9179 n=44, CI excludes 0; floor_mix_milk_mix_powder: 43 of 80, 53.8%, n=80; proxy_precision: 3 of 24, n=24 — only count it if the taste-and-react is genuine).
5. (40–45s) Back to play; soft CTA, no link-bait.

**5. Three sample lines** (Little Joys facts only; confirm with legal)
- "Made with millets and dry fruits." (source: ads.csv `claims_made` — confirm with legal)
- "9g protein in 2 scoops with milk." (source: ads.csv `claims_made`, LJ-009 Nutrimix 7+; other ads state 5g per 2 scoops (LJ-029, LJ-043, LJ-095), so confirm the figure with legal)
- "Sweetened with jaggery and dates, no refined sugar." (source: ads.csv `claims_made` — confirm with legal)

**6. Avoid**
- His stated foreign notes: studio lighting, formal/scripted product claims, frames without family.
- Comment-for-link mechanics (none currently: cr_CR-11_link_request_share: 0.0%, n=20 — keep it that way).
- Treating a scripted story-open or question hook as proven (ads_H5: fragile; ads_H4: fragile).

**7. Competitor note**
He has shown two direct milk/nutrition competitors (cr_CR-11_brands: Gritzo, Troovy Foods, …, n=14). Conflict risk is high. Suggestion for the manager: a firm exclusivity clause excluding kids'-milk/nutrition brands (Gritzo, Troovy and peers) for the campaign and a cool-off window — a suggestion to decide on, given he has run both recently.

**8. Primary metric + test**
Post-click purchase conversion (purchases ÷ link clicks). Test: hold CR-11 fixed and compare "child tastes and reacts" beat on vs off, on post-click purchase conversion. No cost metrics (limit_pricing: 0 pricing columns). Ad-level gap: ads H1 and H3 (ads_H1_cvr_in: 0.0407, n=265704 link clicks; ads_H1_cvr_out: 0.0228, n=255356 link clicks; ads_H3_cvr_in: 0.0462, n=186596 link clicks; ads_H3_cvr_out: 0.0240, n=334464 link clicks).

**9. Legal:** not flagged in the data; confirm all claims with legal.

**10. Confidence: Low–Medium.** Role fit (a child in every window post; cr_CR-11_food_term_share: 25.0%, n=20) and no link mechanics; the main uncertainty is weak standing in resampling (cr_CR-11_bootstrap_top5: 11.5%, n=200), and absent audience data.

---

## CR-01 — drgarima_mehta (clinical voice)

**1. Role and why chosen**
- Solid food/feeding content (cr_CR-01_food_term_share: 30.0%, n=20) for a pediatric-nutrition angle.
- Improves when link posts are set aside (cr_CR-01_rank_excl_link: rank 4 vs frozen 6, n=20), so her standing does not rest on a link mechanic; almost no link posts anyway (cr_CR-01_link_request_share: 5.0%, n=20).
- Lightly sponsored (cr_CR-01_sponsored_share: 10.0%, n=20), so a Little Joys brief would stand out rather than blend into an ad stream.

**2. The idea**
A split-screen doctor explainer in Hindi with English product/medical terms, treating the product as an informed everyday choice. Her profile says native is "A video featuring the doctor in her clinical setting or a clean, bright space, using a split-screen format to explain the science behind a product's safety or efficacy," and foreign is "High-production studio lighting, scripted sales pitches that lack medical context, or English-only audio without Hindi explanations." Keep the Hindi-led explanation with English terms.

**3. Three hook options** (her window posts are English-captioned with Hindi audio; one real observed hook_style: "direct question addressing a common parenting mistake")
- (Hindi) "Bachchon ki daily protein zaroorat — aap sahi se poori kar rahe hain?" [Your child's daily protein need — are you meeting it properly?]
- (Hindi) "Snacks ke label padhna kyun zaroori hai, 20 second mein." [Why reading the snack label matters, in 20 seconds.]
- (English) "What I check before any food becomes my child's daily habit."
- Note: her native hook is the direct question, but do not assume question hooks perform better — fragile in the ad data (ads_H4: fragile, CI includes 0).

**4. Five-beat outline (30–45s)**
1. (0–3s) Clean/clinical frame + pack visible, brand named early — suggestive only (ads_H3: suggestive, CI includes 0).
2. (3–12s) The common nutrition question, in Hindi.
3. (12–28s) Split-screen: label / ingredients explained with English terms; product as an informed option.
4. (28–38s) A child-tastes beat fits her weakly (her feed is explainer-led, child rarely eating on camera) — include only if authentic; association unproven and mostly milk-mix (ads_H1: supported; floor_mix_milk_mix_powder: 43 of 80, n=80; proxy_precision: 3 of 24, n=24).
5. (38–45s) "Read the label, ask your pediatrician" close.

**5. Three sample lines** (Little Joys facts only; confirm with legal)
- "Sweetened only with jaggery and dates — no refined sugar, no artificial sweeteners." (source: ads.csv `claims_made` — confirm with legal)
- "12g plant protein per scoop; roti taste stays unchanged." (source: ads.csv `claims_made` — confirm with legal)
- "Specially made for children; can be easily mixed into idli, dosa or roti." (source: ads.csv `claims_made`, LJ-012 — confirm with legal)

**6. Avoid**
- Her stated foreign notes: studio lighting, scripted sales pitches lacking medical context, English-only audio.
- Any medical / health-outcome claim (see item 9).
- Assuming the question-hook format is a winner (ads_H4: fragile).

**7. Competitor note**
Her shown brands are mostly pharma/skincare, not direct LJ-category competitors (cr_CR-01_brands: Calpol, Meftal, Carepure, Chupa Chups, …, n=10). Moderate-to-low category conflict. Suggestion for the manager: category-exclusivity for kids' nutrition-mix brands during the window, and confirm no pharma conflict with any medical disclaimer she runs.

**8. Primary metric + test**
Post-click purchase conversion (purchases ÷ link clicks). Test: hold CR-01 fixed and compare "ingredient explainer" vs "label-check checklist" cuts on post-click purchase conversion. No cost metrics (limit_pricing: 0 pricing columns). Ad-level gap: ads H1 and H3 (ads_H1_cvr_in: 0.0407, n=265704 link clicks; ads_H1_cvr_out: 0.0228, n=255356 link clicks; ads_H3_cvr_in: 0.0462, n=186596 link clicks; ads_H3_cvr_out: 0.0240, n=334464 link clicks).

**9. Legal**
CR-01 is flagged for legal review (cr_CR-01_flags: no_audience_data, legal_review, n=2). No medical, diagnostic, or health-outcome claims; no "pediatrician-recommended for [condition]" framing. Keep to ingredients and general benefit language, and clear the script with legal before shoot.

**10. Confidence: Medium.** Good food/feeding fit (cr_CR-01_food_term_share: 30.0%, n=20) and she improves without link posts (cr_CR-01_rank_excl_link: 4, n=20); the main uncertainty is the legal-review requirement, absent audience data, and modest resampling standing (cr_CR-01_bootstrap_top5: 28.5%, n=200).

---

## CR-19 — instamommy_suchi (milk-category creator)

**1. Role and why chosen**
- Lands in the top 5 about half the resampling draws (cr_CR-19_bootstrap_top5: 50.5%, n=200 draws) and is already fluent in milk-mix nutrition messaging.
- Food/feeding content present (cr_CR-19_food_term_share: 15.0%, n=20), including a recent milk-nutrition post.
- Heavily sponsored (cr_CR-19_sponsored_share: 75.0%, n=20) — the highest of the five — so brand integration is her norm; this is also the caution (see confidence).

**2. The idea**
A household-prop explainer that makes the milk upgrade visible. Her profile says native is "A video that starts with a relatable parenting problem, uses a household prop to demonstrate a solution, and includes a clear, informative explanation of the product's benefits or ingredients," and foreign is "A highly scripted, cold, or overly corporate advertisement that lacks a personal narrative or fails to show the product being used in a real-world domestic setting." Her own post used a magnifying glass over a glass of milk — a strong, ownable device.

**3. Three hook options** (her window posts are English + Hindi; one real observed hook_style: "visual curiosity using a magnifying glass to inspect a glass of milk")
- (Hindi) "Growing years mein nutrition ka dhyaan rakhna toh banta hai." [In the growing years, paying attention to nutrition is a must.]
- (English, prop-led) "Let's actually look at what's in this glass of milk."
- (Hindi) "Bachche ke milk mein main kya add karti hoon — aur kyun." [What I add to my child's milk — and why.]
- Note: she uses prop-led and direct-address hooks; do not assume a voiceover-montage ad format performs better — that signal was fragile in the ad data (ads_H7: fragile, CI includes 0).

**4. Five-beat outline (30–45s)**
1. (0–3s) Magnifying-glass-on-milk prop + pack visible, brand named early — suggestive only (ads_H3: suggestive, in 2.2126 n=30 vs out 1.1120 n=50, CI includes 0).
2. (3–12s) The "is my child's milk enough" question.
3. (12–26s) Mix added to milk; one ingredient/benefit line.
4. (26–40s) Child tastes the milk and reacts on camera — fits her milk-category content and is associated with higher ROAS, though unproven and mostly milk-mix powder (ads_H1: supported, in 2.2235 n=36 vs out 0.9179 n=44, CI excludes 0; struct_child_reacts: pooled ROAS 2.2235, n=36; floor_mix_milk_mix_powder: 43 of 80, 53.8%, n=80; proxy_precision: 3 of 24, n=24 — film only if the reaction is genuine).
5. (40–45s) Warm close; no comment-for-link.

**5. Three sample lines** (Little Joys facts only; confirm with legal)
- "Add it to your child's milk — 9g protein in 2 scoops." (source: ads.csv `claims_made`, LJ-009 Nutrimix 7+; other ads state 5g per 2 scoops (LJ-029, LJ-043, LJ-095), so confirm the figure with legal)
- "23 essential vitamins and minerals; sweetened with jaggery and dates." (source: ads.csv `claims_made` — confirm with legal)
- "Contains ragi, bajra, almonds and walnuts." (source: ads.csv `claims_made` — confirm with legal)

**6. Avoid**
- Her stated foreign notes: cold/corporate scripted ads with no personal narrative or real domestic use.
- Comment-for-link mechanics (she uses some: cr_CR-19_link_request_share: 10.0%, n=20).
- Treating the voiceover-montage ad format as proven (ads_H7: fragile).

**7. Competitor note**
She has shown two direct milk/nutrition competitors (cr_CR-19_brands: Complan, Bournvita, …, n=18). Conflict risk is high — these are head-on category rivals. Suggestion for the manager: a strong exclusivity clause excluding malt/health-drink and kids'-nutrition brands (Complan, Bournvita and peers) for the campaign and a clear cool-off period — a suggestion to decide on given her recent collaborations.

**8. Primary metric + test**
Post-click purchase conversion (purchases ÷ link clicks). Test: hold CR-19 fixed and compare the magnifying-glass prop cut vs a plain demo cut on post-click purchase conversion. No cost metrics (limit_pricing: 0 pricing columns). Ad-level gap: ads H1 and H3 (ads_H1_cvr_in: 0.0407, n=265704 link clicks; ads_H1_cvr_out: 0.0228, n=255356 link clicks; ads_H3_cvr_in: 0.0462, n=186596 link clicks; ads_H3_cvr_out: 0.0240, n=334464 link clicks).

**9. Legal:** not flagged in the data; confirm all claims with legal.

**10. Confidence: Medium.** Reasonable resampling standing (cr_CR-19_bootstrap_top5: 50.5%, n=200) and a natural milk-category fit; the main uncertainty is her very high sponsored load (cr_CR-19_sponsored_share: 75.0%, n=20), which can dilute a single brand, plus absent audience data.
