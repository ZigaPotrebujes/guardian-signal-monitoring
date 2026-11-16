"""
Free brand check-up (PROTOTYPE). Looks for accounts and web domains that LOOK like a brand but are not official.

    python checkup.py --demo                                   # offline, fictional brand
    python checkup.py "Umanitek" --official umanitek.ai        # live, free public sources

What "looks like" means here:
  1. contains the brand name:   "Umanitek Support", "umanitek-login.com"
  2. lookalike spelling:        "Umanltek" (l for i), "Umanitek1", "Umanitec", "Umanitekk" (typo-squatting)
It does NOT catch everything: different-looking names, images, or accounts that never use the brand's name.

What it is: a sketch of the "free impersonation check-up" lead magnet. Output is a short report of CANDIDATES
for a human to review. It never claims fraud and never contacts anyone.

Sources (free, no login): Bluesky public account search; certificate-transparency logs via crt.sh (domains
that merely resemble the brand name). Not covered, and where most impersonation really happens: X, Instagram,
TikTok, Telegram, and what AI models say about the brand. A real product needs licensed access to those.
Findings about real organizations are unverified leads: keep them private, check every one by hand.
"""
import argparse
import difflib
import re
from datetime import datetime

import requests

UA = "script:guardian-checkup:0.1 (personal portfolio project)"
RISKY = re.compile(r"support|official|help ?desk|giveaway|airdrop|claim|recover|wallet|invest|customer service|verify", re.I)
SUBS = {"i": ["l", "1"], "l": ["i", "1"], "o": ["0"], "a": ["4"], "e": ["3"]}


def squish(text):
    return re.sub(r"[\W_]", "", text.lower())


def lookalike_keys(key):
    """Typo-squatting variants: look-alike characters (i/l/1, o/0, m/rn), one letter dropped or doubled."""
    if len(key) < 6:
        return set()                                       # too short: variants would match ordinary words
    out = set()
    for i, ch in enumerate(key):
        for rep in SUBS.get(ch, []):
            out.add(key[:i] + rep + key[i + 1:])
        out.add(key[:i] + key[i + 1:])                     # dropped letter
        out.add(key[:i + 1] + ch + key[i + 1:])            # doubled letter
    if "m" in key:
        out.add(key.replace("m", "rn"))
    out.discard(key)
    return out


def match_kind(key, variants, text):
    """'contains' (brand inside the text), 'lookalike' (typo/homoglyph variant or very close spelling), or None."""
    s = squish(text)
    if key in s:
        return "contains"
    if any(v in s for v in variants):
        return "lookalike"
    for token in re.findall(r"[a-z0-9]+", text.lower()):   # whole words/labels that are almost the brand
        if token != key and abs(len(token) - len(key)) <= 2 and difflib.SequenceMatcher(None, key, token).ratio() >= 0.85:
            return "lookalike"
    return None


def is_official_name(name, official):
    name = name.lower().lstrip("*.")
    return any(name == d or name.endswith("." + d) for d in official)


def bluesky_candidates(brand, official, get=requests.get):
    """Accounts whose name or handle resembles the brand. A handle on the brand's own domain is domain-verified."""
    key = squish(brand)
    variants = lookalike_keys(key)
    homoglyphs = sorted(v for v in variants if len(v) == len(key))[:6]
    found = {}
    for q in [brand, f"{brand} support", f"official {brand}"] + homoglyphs:
        r = get("https://public.api.bsky.app/xrpc/app.bsky.actor.searchActors",
                params={"q": q, "limit": 25}, headers={"User-Agent": UA}, timeout=20)
        r.raise_for_status()
        for a in r.json().get("actors", []):
            handle, name, desc = a.get("handle", ""), a.get("displayName", ""), a.get("description", "")
            kind = match_kind(key, variants, f"{handle.split('.')[0]} {name}")
            if not kind or is_official_name(handle, official):
                continue                                   # not brand-like, or domain-verified official
            risky = bool(RISKY.search(f"{name} {desc}"))
            found[handle] = {"platform": "Bluesky", "id": f"@{handle}", "link": f"https://bsky.app/profile/{handle}",
                             "why": ("name/handle contains the brand" if kind == "contains"
                                     else "name/handle is a lookalike spelling of the brand")
                                    + ", handle is not on the official domain"
                                    + ("; profile text uses support/giveaway/recovery-style wording" if risky else ""),
                             "priority": 2 if (risky or kind == "lookalike") else 1}
    return list(found.values())


def lookalike_domains(brand, official, get=requests.get):
    """Certificate-transparency logs: domains resembling the brand name that are not the official domain."""
    key = squish(brand)
    variants = lookalike_keys(key)
    queries = [key] + sorted(v for v in variants if len(v) == len(key))[:3]
    seen = {}
    for q in queries:
        try:
            r = get("https://crt.sh/", params={"q": f"%{q}%", "output": "json"}, headers={"User-Agent": UA}, timeout=40)
            r.raise_for_status()
            rows = r.json()
        except Exception:
            if q == key:
                raise                                      # the main query failing is worth reporting
            continue
        for row in rows:
            for name in str(row.get("name_value", "")).split("\n"):
                name = name.strip().lower().lstrip("*.")
                kind = match_kind(key, variants, name)
                if kind and not is_official_name(name, official):
                    first = str(row.get("not_before", ""))[:10]
                    if name not in seen or (first and first < seen[name][0]):
                        seen[name] = (first, kind)
    return [{"platform": "Web domain", "id": n, "link": "https://crt.sh/?q=" + n,
             "priority": 2 if kind == "lookalike" else 1,
             "why": ("domain contains the brand name" if kind == "contains" else "domain is a lookalike spelling of the brand")
                    + f" (certificate first seen {first or 'unknown'})"}
            for n, (first, kind) in sorted(seen.items(), key=lambda kv: kv[1][0], reverse=True)[:25]]


def write_report(brand, official, findings, errors, path, demo=False):
    findings = sorted(findings, key=lambda f: -f["priority"])
    L = [f"# Impersonation check-up: {brand}", "",
         f"_Prototype report, {datetime.now().strftime('%Y-%m-%d')}. " + ("FICTIONAL DEMO DATA. " if demo else "")
         + "Candidates for human review, not conclusions._", "",
         f"**Official domains given:** {', '.join(official) or '(none)'}", "",
         "**What \"similar\" means:** the name contains the brand, or is a close typo / lookalike spelling of it "
         "(for example an \"l\" in place of an \"i\"). Different-looking names are not caught.", "",
         f"## Candidates ({len(findings)})", ""]
    if findings:
        L += ["| Priority | Where | Identifier | Why it was flagged |", "|---|---|---|---|"]
        L += [f"| {f['priority']} | {f['platform']} | [{f['id']}]({f['link']}) | {f['why']} |" for f in findings]
    else:
        L += ["_Nothing found on the free sources checked. That does NOT mean the brand is safe: see coverage below._"]
    if errors:
        L += ["", "## Sources that failed this run", ""] + [f"- {e}" for e in errors]
    L += ["", "## How to read this", "",
          "- A candidate only means a name looks similar. Many are fans, parodies, unrelated people or unrelated businesses.",
          "- Verify each one by hand before saying anything to anyone. Never claim fraud from this list alone.",
          "", "## What this check does NOT cover", "",
          "X, Instagram, TikTok, Facebook, Telegram, marketplaces, app stores, and what AI assistants say about the brand. "
          "Those need licensed data or platform partnerships, which is the part a real product provides.",
          "", "## Before any outreach", "",
          "A human reviews every finding. One plain-text message to the right role (brand protection, comms, security), "
          "evidence inline, no tracking links or attachments, sent from the company's own domain. "
          "Check local rules on business email with the company's legal or privacy team."]
    open(path, "w", encoding="utf-8").write("\n".join(L))
    return path


DEMO_FINDINGS = [
    {"platform": "Bluesky", "id": "@acme-bank-support.example", "link": "https://bsky.app/profile/example", "priority": 2,
     "why": "name/handle contains the brand, handle is not on the official domain; profile text uses support-style wording"},
    {"platform": "Bluesky", "id": "@acrne-bank.example", "link": "https://bsky.app/profile/example3", "priority": 2,
     "why": "name/handle is a lookalike spelling of the brand (\"rn\" in place of \"m\"), handle is not on the official domain"},
    {"platform": "Bluesky", "id": "@acmebankfan.example", "link": "https://bsky.app/profile/example2", "priority": 1,
     "why": "name/handle contains the brand, handle is not on the official domain"},
    {"platform": "Web domain", "id": "acmebank-login.example", "link": "https://crt.sh/?q=example", "priority": 1,
     "why": "domain contains the brand name (certificate first seen 2026-10-30)"},
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brand", nargs="?", default="")
    ap.add_argument("--official", nargs="*", default=[], help="the brand's real domains, e.g. umanitek.ai")
    ap.add_argument("--demo", action="store_true", help="fictional data, no network")
    args = ap.parse_args()
    if args.demo:
        path = write_report("Acme Bank (fictional)", ["acmebank.example"], DEMO_FINDINGS, [], "checkup_demo.md", demo=True)
        print(f"Wrote {path}")
        return
    if not args.brand:
        ap.error("give a brand name, or use --demo")
    official = [d.lower() for d in args.official]
    findings, errors = [], []
    for name, fn in (("Bluesky search", bluesky_candidates), ("crt.sh domains", lookalike_domains)):
        try:
            findings += fn(args.brand, official)
        except Exception as e:                           # one failing source must not kill the report
            errors.append(f"{name}: {e}")
    slug = re.sub(r"\W", "", args.brand.lower())
    path = write_report(args.brand, official, findings, errors, "checkup_" + slug + ".md")
    print(f"{len(findings)} candidate(s), {len(errors)} source error(s) -> {path}")


if __name__ == "__main__":
    main()
