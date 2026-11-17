# Log: what I ran, what went wrong, what I changed

I built the first version in a few hours with Claude, then ran it on live data, labelled the results myself, and fixed what broke.
Everything below is in the order it happened.

## Runs 1 to 3: getting data, then getting signal
1. **Run 1:** 46 items, all from Hacker News. Google News and Reddit returned nothing, silently, because the feed library swallowed errors. Fix: download with `requests` and print every failure.
2. **Run 2:** 231 items but only 1 in the digest. Google News is articles *about* the problem (context, rarely a lead). Reddit r/Scams had real people asking for help, but my keywords only knew "deepfake" vocabulary, so real cases scored 1/5. Fix: broader vocabulary, and a required "person in trouble" signal so generic news cannot reach the digest.
3. **Reddit throttling (HTTP 429):** added a delay, retry with backoff, fewer subreddits and a local cache. Reddit access is fragile by design: the official API needs approval, and a commercial version needs approved access or a licensed provider.
4. **Run 3:** the 10-item digest had 4 Reddit posts and 6 news stories about past victims, and ties were broken by order, so a real lead was pushed out by the cap. Fix: separate sections (leads, market watch, news), each with its own cap.
5. **Recall gaps:** real posts like "opened in my name" scored 1 to 2. I also tuned the word lists on the same items I measured on, which flatters the numbers.

## Run 3, labelled by me: the measurement
I judged each of the 10 leads against what the product does (from public press; to be verified with the company), not against "is this a victim?":
- **1 strong fit** (a fake account using the person's photos and ID), **1 partial** (a scam page listing a friend's phone number), **8 no fit** (financial or government identity fraud: SSN, tax, telecom accounts, bank phone scams, an awareness post).
- My earlier "about 7 of 10 plausible" measured relevance to identity theft. Against product fit, precision was **1/10 strict, 2/10 lenient**. The topic filter worked; there was no product-fit gate.
- Where you listen matters more than the keywords: r/IdentityTheft is mostly financial fraud.

## Run 4: the fit gate
Scoring now also asks "can the product act on this?" (strong, partial, none). A victim the product cannot help is capped below the digest threshold. `python eval.py` reproduces the comparison on 11 labelled posts, shipped as short paraphrases so strangers' details are not republished:

| Scorer | Surfaced | Real fits among them | Precision | Recall of the 3 fits |
|---|---|---|---|---|
| Old (topic only) | 5 | 1 | 20% | 1/3 |
| New (fit gate) | 3 | 3 | 100% | 3/3 |

**Read this with suspicion.** I wrote the fit word lists after reading these posts, so 100% is in-sample. My first gate also lost the partial fit, and I fixed that after seeing it. Recall is only checked on items run 3 already surfaced. I also added safety rails to the lead section: a weak "possible minor" flag, a note to never pitch minors or people in distress, and helpful replies with no pitch as the default.

## Run 4, live
- **Individuals:** Reddit returned only 25 posts (r/Scams was throttled), so this is a tiny sample. Two reached the lead list: the known strong case, and "I sent my driver's license to a scammer", which the gate called strong and I judged partial at best. My pattern "video of me" had matched "a video of me holding it", but the author handed the document over themselves. Of 23 lower-scoring posts I saw no missed fits by title.
- **Organizations:** the news-trigger approach performed poorly. Of 8 account signals, I rated one low (a $129M deepfake-CEO indictment where the victims are described but not named) and the rest were one 2024 story (a $25M deepfake video-call fraud) repeated across outlets. Causes: no date filter, no story merging, and the wrong problem. Wire fraud by a deepfaked executive is a call-authentication problem; Guardian, per public press, covers fake accounts, AI misrepresentation and takedown evidence.
- **A regression in my own change:** letting "a dollar amount" count as an organization made competitors' funding announcements score as incidents.

## Run 5: changes and a live check
I made these changes after seeing the run 4 labels, so they are not independently measured.
- Dated news is dropped past 45 days (organizations) or 180 days (other news); near-duplicate stories are merged; funding news moves to market watch; wire-fraud incidents are down-weighted; self-sent documents downgrade a strong fit to partial.
- **New strongest organization trigger:** the organization or public figure itself warns about impersonators.
- A fresh run fetched 135 items after dropping 278 stale ones, and no story repeated. The new trigger surfaced a public figure warning fans about fake accounts, a good example of the segment Guardian's first release targets. It also surfaced one false positive (account-recovery scams, not impersonation), which I fixed.
- Known remaining false positive: a speech model that mentions voice cloning as a limitation scores as relevant.

## Second lane: organizations
One enterprise account can outweigh many individuals, but the unit is different: an organization, a trigger event and a buyer role, not a person in distress. The digest has an "Account signals" section with triggers for **warnings** (the organization says it is being impersonated), **regulation** and **incidents**, plus an "ecosystem" type (competitor funding) that goes to market watch. Each row suggests a buyer role. Naming the organization is left to a human, because headline parsing is unreliable and a wrong name in a sales workflow is worse than a blank. 
## Run 6: measuring the company lane
I ran it fresh and labelled all 26 company headlines myself (`labeled_accounts.py`, headlines only, rubric in the file).
- **Result:** 2 good (Samyang Foods and Nio, each warning about impersonation of itself), 12 weak (generic phishing or scam advice, for example one bank four times), 12 no (power-cut hoaxes, an outage, a data breach, a 2024-style wire fraud). About 8% good.
- **The scorer surfaced none of the 26** (threshold 3; the best score was 2). It found 0 of the 2 good ones. Samyang scored 2 as an "incident" because the warning pattern needed words like "fake account" and the headline says "impersonation scams". I did not change the rule: fixing it after seeing the label would be in-sample, and one fix does not change the conclusion.
- **Why news is weak here:** the feed follows events (Fraud Awareness Week, Black Friday, a Microsoft outage, a National Grid hoax) that say nothing about whether a company needs this product, and the same organization repeats under different wording (UBA four times).
- **Verdict:** finding companies from news does not work well enough to keep tuning. A more promising signal is structural: companies hiring for trust and safety or brand protection, and the free check-up as the way in. The next test would be a hiring-signal source labelled the same way.
- **Limits:** 26 headlines from one day, labelled from headlines only (the Muhoozi item needs the article opened). It shows the approach is weak, not by exactly how much.
