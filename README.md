# Guardian Signal Monitor (MVP)

Built in one afternoon, with AI assistance (Claude), as a small growth-engineering experiment. I directed it, ran it on live
data, labeled the results by hand, and wrote down what went wrong. That log matters more to me than the code.

## At a glance
- **What it is:** an agent that finds public conversations and news where Guardian could plausibly help, ranks them, and
  hands a human a short digest with reasons. It never posts or contacts anyone.
- **First honest measurement:** of 10 "leads" my first version surfaced, only 1 was something the product could act on
  (it matched *identity theft*, not *product fit*). I added a fit gate; see `python eval.py`.
- **A second finding:** news about deepfake CEO fraud was a poor way to find companies (one famous 2024 case repeated about
  ten times, and that problem is not Guardian's). I added date limits, story merging, and a better trigger: organizations or
  public figures that publicly warn about impersonators.
- **A prototype of the next step:** `python checkup.py --demo` shows a free brand "impersonation check-up", a possible lead magnet.
- **What I would do next:** see "Next steps" at the end.
- **Limits, stated up front:** small samples, rules tuned after seeing results, free sources only, and the check-up covers
  only Bluesky and domain records, not X, Instagram or TikTok.

## The problem
Guardian helps people who are dealing with identity misuse (deepfakes, impersonation).
Those people are already posting about it publicly, in pain, asking what to do.
**Hypothesis:** catching someone at the moment of pain is a warmer, higher-intent
acquisition moment than cold outreach. But nobody can read the whole internet manually.

## What it does
Every run it produces `digest.md`: a short ranked list of public posts where a real person
seems to have this problem, with a one-line reason and (with an LLM key) a draft reply.

```
fetch (Google News, Hacker News, Reddit RSS, plus B2B news queries)
  -> dedupe (SQLite)
  -> cheap keyword score (free) + product-fit gate (individuals) or trigger scoring (organizations)
  -> LLM score + draft reply (only on promising items, capped)
  -> digest.md for a human to review
```
Lane 1 finds individuals the product could help. Lane 2 finds organizations with a trigger event. Both end in a human's hands.

## Design decisions
- **Human in the loop.** It drafts and surfaces; it never posts. Auto-replying is spam, breaks platform rules, and damages trust in a security product.
- **Cheap filter before the LLM.** Keywords remove most noise for free; the LLM only sees the top candidates, with a hard cap per run. Works at zero cost without an API key.
- **Free sources only.** The X API is now pay-per-use, so X is deliberately left out of the MVP.
- **One broken source never kills a run.** Fetchers fail independently.
- **Post content is treated as untrusted.** The prompt tells the model to ignore instructions found inside posts (prompt injection from public text is a real risk).
- **Everything tunable lives in `config.py`.** Retargeting to another product means editing one file.

## Run it
```
pip install -r requirements.txt
python agent.py --demo                      # offline, sample data
python agent.py                             # live, keyword scoring (also saves last_fetch.json)
python agent.py --cached                    # re-score the last fetch without any network, for tuning
python eval.py                              # precision against hand labels, no network, no API key
python checkup.py --demo                    # prototype of the free brand check-up (fictional data)
python checkup.py "Brand" --official brand.com   # live: lookalike accounts (Bluesky) and domains (crt.sh), candidates only
ANTHROPIC_API_KEY=... python agent.py       # live + LLM scoring and drafts
```

## What I cut (on purpose) and why
No X/LinkedIn, no auto-posting, no UI, no database beyond dedupe, no tests,
no author enrichment. For an MVP the goal was to prove the loop end to end first.

## Known limitations
- Keyword scoring is crude: it misses paraphrases and can reward noisy posts.
- Reddit RSS may be rate-limited or blocked; results vary.
- Precision was measured once, by hand, on 10 items (see the iteration log). The fit gate was tuned on those same items, so treat the result as a first signal, not a benchmark.
- The product description in `config.py` comes from public press coverage and must be verified with the company; the fit rules depend on it.

## How I'd upgrade it, in order
1. **Measure quality.** Mark each digest item good/bad (a simple thumbs file), track precision. Without this, I'm guessing.
2. **Delivery + scheduling.** Daily digest to Telegram/Slack via a GitHub Actions cron.
3. **Feedback loop.** Feed labeled examples back into the prompt as few-shot examples.
4. **More sources.** Bluesky/Mastodon search, relevant subreddits, forums.
5. **Enrichment.** Summarize the author's recent posts to judge fit (the bridge to a full lead pipeline).
6. **Track outcomes.** Log which surfaced items led to a reply, a visit, a signup, to find which queries and sources actually convert.
7. **X as an optional module** behind a flag, with a cost budget (pay-per-use).

## Metrics I'd watch
Precision of the digest (% of items a human agrees are real leads), items reviewed per day,
replies sent, replies that led to a visit or signup, cost per qualified lead.

## Findings from the first live runs (iteration log)
1. **Run 1:** 46 items, all from Hacker News. Google News and Reddit returned nothing, silently.
   Cause: the feed library swallowed errors. Fix: download with `requests`, print every failure.
2. **Run 2:** 231 items (178 Google News, 3 HN, 50 Reddit), but only 1 in the digest.
   - Google News = articles *about* the problem. Useful context, almost never a lead.
   - Reddit r/Scams = real people asking for help, exactly the target. But my keywords only knew
     "deepfake" vocabulary, so it scored real identity-misuse cases as 1/5 ("someone is using my
     friend's phone number", "fake TikTok account", "my home listed fraudulently").
   - Fix: broadened the topic vocabulary and required a "person in trouble" signal, so generic news can't reach the digest.
3. **Reddit throttling (HTTP 429):** unauthenticated feeds allow very few requests. Added a delay,
   retry with backoff, fewer subreddits, and a local cache so tuning doesn't re-hit Reddit.
4. **Reddit access is fragile by design.** The official API now needs Reddit's approval, and unauthenticated
   access is increasingly blocked. Reddit is therefore a best-effort source here. A commercial version needs
   approved access or a licensed data provider (a real cost/compliance decision, not a coding detail).
5. **Run 3 (231 items):** the first digest had 10 items: 4 from Reddit, 6 news stories about *past* victims.
   Because ties were broken by order and news came first, a real Reddit lead scoring 4 was pushed out by the
   10-item cap. Fix: the digest now has separate sections (leads / market watch / news) with their own caps and thresholds.
6. **Recall gaps:** real r/IdentityTheft posts scored 1-2 ("opened in my name", "someone is using my email",
   "I sent my drivers license to a scammer"). Keywords can't cover every phrasing; this is where the LLM step should
   earn its cost. Idea: give each community a prior (everything in r/IdentityTheft is on-topic by definition).
   Caution: I tuned the word lists on the same 231 items I measured on, which flatters the numbers. The honest test is fresh data.
7. **Run 3 labeled by hand (the measurement).** I judged each of the 10 leads against what the product actually does
   (public press description; to be verified with the company), not against "is this a victim?":
   - 1 strong fit (a fake account using the person's photos and ID, stalking family), 1 partial (a scam page listing a
     friend's phone number), **8 with no fit** (financial or government identity fraud: SSN, IRS and SSA, telecom accounts,
     bank phone scams, a public awareness post).
   - My earlier "about 7 of 10 plausible" measured *relevance to identity theft*. Measured against *product fit*, precision was
     **1/10 strict, 2/10 lenient**. The topic filter worked; there was no product-fit gate. A growth team that chased all 10
     would have spent 80% of its effort on people the product cannot help.
   - Second finding: **where you listen matters more than the keywords.** r/IdentityTheft is mostly financial fraud.
8. **Run 4: fit gate.** Scoring now asks a second question, "can the product act on this?", with three outcomes
   (strong / partial / none). A victim the product cannot help is capped below the digest threshold. The labeled set is in
   `labeled_leads.py` and `python eval.py` reproduces the before/after with no network or API key:

   | Scorer | Surfaced | Strong+partial among them | Precision | Recall of the 2 fits |
   |---|---|---|---|---|
   | v1 topic only | 7 | 1 | 14% | 1/2 |
   | v2 fit gate | 2 | 2 | 100% | 2/2 |

   (This table is from the original verbatim posts at the time. The repo now ships short paraphrases so strangers' details are not
   republished, plus the run 4 post, 11 items in all. On that set `python eval.py` prints v1 = 5 surfaced, 1 of them a fit (20%);
   v2 = 3 surfaced, all fits (100%). The fit gate behaves the same on both; the old scorer's count moves because paraphrasing changes wording.)

   **Read this with suspicion.** I wrote the fit word lists after reading these same 10 posts, so 100% is an in-sample number.
   My first version of the gate also *lost* the partial fit (it scored 1/5 under the old topic list); I fixed that, again
   after seeing it. The real test is the next live run, on posts the lists have never seen, labeled by hand before I look at scores.
   Recall is only checked on items run 3 already surfaced: posts the old scorer missed are unlabeled, so true recall is unknown.
9. **Safety rails added to the lead section:** a "possible minor" flag (weak regex, so it is a prompt for a human, not a guarantee),
   a note to never pitch to minors or people in acute distress, and a default of helpful replies with no pitch.
10. **Run 4 live results (351 items; hand-labeled by a human, not by me).**
    - *Individuals:* Reddit returned only 25 posts (r/Scams was rate-limited), so this is a tiny sample. 2 reached the lead list:
      the already-known strong case, and one new post ("I sent my driver's license to a scammer") that the gate called strong
      and a human judged **partial at best**. Cause: my pattern "video/photo of me" matched "a video of me holding it", but the
      author handed the document over themselves, and the damage is done. Of the 23 posts that scored 1-2, I see no missed
      fits by title (most are financial fraud or account takeover); 3 titles are too vague to judge. Independent precision: n=1, not meaningful.
    - *Organizations:* **the news-trigger approach performed poorly.** Of 8 account signals, the human rated one low (the
      $129M deepfake-CEO indictment: victims described but not named) and the rest were one 2024 story (Arup, a $25M deepfake
      video-call fraud) repeated across outlets. That is 2 distinct stories, one of them 21 months old. Three structural causes:
      1. **No date filter**, so a Feb 2024 story looked like a fresh trigger.
      2. **No story merging**, so one event filled the whole section.
      3. **Wrong problem.** Wire fraud by deepfaked executives is a call-authentication problem. Guardian (per public press)
         covers fake accounts, AI-model misrepresentation and evidence for takedowns. The query set targeted a neighbouring product.
      Also, **a regression I introduced**: allowing "a dollar amount" to count as an organization made funding announcements
      for competitors (Reality Defender, GetReal, Loti AI) score as incidents. And the crowd of vendors in that list is itself
      evidence for the human's point: anyone named in a famous incident is already being pitched by many detection vendors.
11. **Run 5 changes (made AFTER seeing the run 4 labels, so the next test is contaminated again).**
    News items carry a date and are dropped past 45 days (B2B) or 180 days (other news); near-duplicate stories are merged
    ("covered by N outlets"); funding news moves to market watch; wire-fraud incidents are down-weighted; a new strongest
    organization trigger, **"the organization itself warns about impersonators"**; self-sent documents downgrade a strong fit to partial.
    Offline check on 12 real headlines from run 4: the Arup cluster collapses from 6 rows to 1, funding rows leave the account
    list, and the Rituals brand-impersonation warning ranks first. That is a sanity check, not a measurement.
12. **Next:** a fresh live run labeled blind, with Reddit access fixed. Then the LLM step on the same cached data against the same labels.
    Beyond tuning: the news-trigger lane is low-yield by design, so organization discovery should move to structural signals
    (hiring posts, public impersonation audits, AI-misrepresentation audits). Ideas and trade-offs are in the project notes.

## Second lane: organizations (B2B)
Individuals on Reddit are low-value, high-volume, and ethically delicate. One enterprise account can outweigh many of them,
but it needs a different unit of work: an **organization + a trigger event + a buyer role**, not a person in distress.
The digest has a separate "Account signals" section, fed by its own news queries (`B2B_QUERIES` in `config.py`):
- **Incident trigger:** an organization hit by a deepfake, voice clone or impersonation, ideally with a quantified loss
  (an amount scores higher: it signals budget and urgency).
- **Regulatory trigger:** new rules creating duties for platforms or companies (verify each law before citing it).
- **Ecosystem signal:** competitor or partner funding and launches. Intel, not an account.
Each row suggests a likely buyer role (security or fraud, brand protection, trust and safety, communications, legal).
**Naming the organization is deliberately left to a human** (or to the LLM step, when enabled): headline parsing is unreliable
and a wrong company name in a sales workflow is worse than a blank. The agent never contacts anyone.
**Not yet validated:** the B2B scorer has only been checked on a handful of example headlines, not on labeled live data.
Limitation: Google News surfaces incidents *after* they are public. A real version would add hiring signals
(trust and safety roles), conference and regulator announcements, and a CRM check so known accounts are not re-surfaced.

## Before this could be a product: risks and questions for the company
- **Data access.** Reddit's official API needs approval, and commercial use needs a contract. Scraping feeds is acceptable for a
  personal demo, not for a company. Budget for a licensed route and ask legal.
- **Personal data.** Public posts by individuals are still personal data (GDPR if EU residents are involved). Questions: lawful basis,
  minimisation (store only what is needed), retention (`seen.db` and `last_fetch.json` currently keep everything), who can access it.
- **LLM vendor.** The optional LLM step sends post text to a third-party API (`score_llm`, one function, easy to swap).
  Questions: which providers are approved, data-processing terms, retention and training policy, region, logging, or a self-hosted model.
  It is off by default; the keyword path works with no vendor at all.
- **Outreach ethics.** These are people in distress. Human review, no auto-posting, disclose affiliation, follow each community's rules,
  lead with help. An identity-protection brand has more to lose from one tone-deaf reply than from one missed lead.
- **Model risk.** Drafts must not invent product features (prompt restricts to a fixed description), and post text is untrusted
  (prompt-injection defence is partial, not complete).

## How I'd judge whether a paid source is worth it
Cost per qualified lead = (monthly source cost + review time) / human-verified leads that source produced.
Track per source: leads per week, precision, replies sent, replies that led to a visit or signup. Pilot on free sources first,
then compare what the paid source adds that free sources did not.

## Run 5 live check, and a small fix
A fresh run fetched 135 items after the date filter dropped 278 stale ones, and the digest no longer repeated one story.
The new "organization warns about impersonators" trigger surfaced a public figure publicly warning fans about fake accounts
impersonating him, a good example of the segment Guardian's first release targets (high-profile people). It also surfaced one false
positive ("beware of scams for recovering accounts", about account-recovery scams, not impersonation), so I tightened that
pattern to require "fake" or "impersonat...". That fix was made after seeing the result, so it is not independently measured.
Known remaining false positive: an open-source speech model that *mentions* voice cloning as a limitation scores as relevant.
The bigger limit: Reddit returned only 25-50 posts per run because of throttling, so the individuals lane is a thin sample.

## Next steps (what I would do with more than an afternoon)
1. **AI-misrepresentation audit.** Ask public AI assistants factual questions about target companies, compare with ground truth,
   and flag wrong or defamatory answers. This is Guardian's second risk surface and few competitors sell it. Sample repeatedly,
   record model and date, verify by hand before any claim.
2. **Licensed data.** The free check-up only sees Bluesky and domain records. X, Instagram and TikTok need licensed access or partners.
3. **Hiring signals.** Companies hiring trust-and-safety or brand-protection roles show pain, budget and a named buyer.
4. **Outreach policy, designed with the company's legal team.** One plain-text message to the right role, evidence inline, no
   tracking links, sent from the company's domain, a human approves every send. Never auto-send.
5. **Close the loop.** Log which surfaced items led to a reply, a visit or a signup, and report cost per qualified lead per source.
