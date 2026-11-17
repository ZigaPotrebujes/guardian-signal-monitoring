# Guardian Signal Monitor (MVP)

A small monitoring agent I built in a few hours as my answer to "show us something you built, even if it is scrappy".

## At a glance
- **What it does:** finds public conversations and news where Guardian could plausibly help, ranks them with reasons, and gives me a short digest to review. It never posts or contacts anyone; a human decides everything.
- **My role:** I chose the concept, specified the behaviour, ran it live, labelled the output and directed every change. Claude wrote the code.
- **Honest result:** my first version surfaced 10 "leads". I judged that only 1 was something the product could act on, because it matched *identity theft*, not *product fit*. I added a fit gate: on my 11 labelled posts the old scorer surfaces 5 (1 real fit), the new one 3 (all fits). Run `python eval.py`.
- **Caveat:** that result is in-sample. I wrote the rules after reading those posts, so the fair test is fresh data labelled blind, which I have not done yet.
- **Second finding:** news about deepfake CEO fraud was a poor way to find companies (one 2024 case repeated about ten times, and not really Guardian's problem). A better trigger is an organization or public figure publicly warning about impersonators.

## Try it
```
pip install -r requirements.txt
python eval.py                # my labelled posts, old vs new scorer. No key, no network
python agent.py --demo        # sample digest, offline
python checkup.py --demo      # prototype of a free brand "impersonation check-up" (fictional data)
python agent.py               # live run (needs internet; Reddit may throttle)
```
Optional: set `ANTHROPIC_API_KEY` to add LLM scoring and draft replies (off by default).

## Repo map
- `agent.py`: the pipeline (fetch, dedupe, score, digest). Start here.
- `config.py`: every setting. `eval.py` and `labeled_leads.py`: the measurement. `checkup.py`: the check-up prototype.
- `sample_output/`: a redacted sample digest and check-up report.
- `LOG.md`: the run-by-run log of what went wrong and what I changed.

## How it works
fetch (Google News, Hacker News, Reddit RSS) → dedupe → free keyword score plus a product-fit gate → optional LLM score → `digest.md`.
- Cheap filter before any LLM, so it works at zero cost; the LLM only sees top candidates, with a hard cap.
- Each source fails independently; post text is treated as untrusted input.
- Free sources only. X is pay-per-use, so I left it out on purpose.

## Limits and what I cut
Keyword scoring is crude. Reddit throttles, so the individuals sample is thin (25 to 50 posts a run). Rules were tuned after seeing results. The product description in `config.py` comes from public press and needs checking with the company. The check-up covers only Bluesky and domain records, not X, Instagram or TikTok. I cut auto-posting, a UI, X and LinkedIn, and tests.

## Before this could be a product
- **Data access:** Reddit's API needs approval and commercial use needs a contract. Scraping is fine for a demo, not for a company.
- **Personal data:** public posts are still personal data (GDPR): lawful basis, minimisation, retention.
- **LLM vendor:** the optional step sends post text to a third party. Which vendors, terms and retention are approved? Off by default.
- **Outreach ethics:** these are people in distress. Human review, disclose affiliation, follow each community's rules, lead with help.
- **Model risk:** drafts must not invent features, and the prompt-injection defence is only partial.

Cost per qualified lead = (monthly source cost + my review time) / leads I verified from that source. Pilot on free sources, then price what a paid source adds.

## Next steps
1. A fresh live run, labelled blind, before touching any rule.
2. Free impersonation reports as a funnel for trigger-selected companies: targeting, human-approved outreach, and partner channels (agencies, insurers, law firms, victim-support groups).
3. Licensed data for X, Instagram and TikTok (needs company access).
4. Hiring signals (trust and safety, brand protection roles) as a buyer trigger.
5. Track which surfaced items lead to a reply or signup, and report cost per qualified lead by source.

More detail: [`LOG.md`](LOG.md) and [`sample_output/digest_sample.md`](sample_output/digest_sample.md).
