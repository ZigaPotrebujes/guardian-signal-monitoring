"""All the knobs in one place. Retargeting the agent = editing this file only."""

# ------------------------------------------------------------ LANE 1: individuals
# What we search for. Mix of "person in trouble" phrasing and topic phrasing.
QUERIES = [
    "deepfake of me",
    "voice cloning scam",
    "someone impersonating me online",
    "AI impersonation fraud",
    "fake profile using my photos",
]

# Communities where people ask for help. ASSUMPTION: check each name exists, and add your own.
# r/RomanceScams is removed: it exists but is closed to this kind of access (spam protection).
# Run 3 finding: r/IdentityTheft is mostly FINANCIAL fraud (bank, SSN, credit), which Guardian does not
# address. Fake-account complaints are more likely in platform help communities. Verify names first.
SUBREDDITS = ["IdentityTheft", "Scams"]
REDDIT_DELAY_SECONDS = 8   # pause between subreddit requests
HN_MAX_AGE_DAYS = 90       # ignore Hacker News posts older than this

# What the product does. Based on public press coverage (SecurityBrief, Feb 2026). VERIFY with the company.
# The LLM is told to use ONLY this, so it can't invent features.
PRODUCT_CONTEXT = (
    "Guardian is a subscription service that monitors for fake accounts and impersonation on social "
    "networks, watches what AI models say about a person or brand, and produces evidence packs that "
    "support takedown requests. It does NOT resolve financial identity fraud (credit, SSN, tax, bank or "
    "telecom accounts), recover money, or fix government records."
)

# Fit rubric used by the LLM step (the keyword gate in agent.py mirrors it).
FIT_RUBRIC = (
    "strong = a fake account/profile, deepfake or voice clone of the author (or their brand) that "
    "evidence collection and takedown requests address. "
    "partial = misuse of the author's identity details on a platform (scam page listing their number), "
    "or a mixed case. "
    "none = financial or government identity fraud, scams where the victim was tricked into paying, "
    "general questions, news, marketing."
)

# ------------------------------------------------------------ LANE 2: organizations (B2B)
# One enterprise account can outweigh many individuals, but the unit is an ORGANIZATION plus a TRIGGER
# EVENT plus a buyer role, not a person in distress. These queries look for triggers in the news.
# Run 4 finding: "deepfake CEO wire fraud" queries returned one famous 2024 case many times, and that problem
# (call authentication) is not Guardian's. Best signal: organizations that THEMSELVES warn about impersonators.
B2B_QUERIES = [
    "warns customers fake accounts impersonating the brand",
    "issues warning fake social media accounts pretending to be our company",
    "beware fake profiles using our name official accounts only",
    "scam alert fake accounts impersonating company executives social media",
    "Take It Down Act platform compliance deepfake",
    "deepfake detection startup raises funding",
]
B2B_MAX_AGE_DAYS = 45      # a trigger event must be recent
NEWS_MAX_AGE_DAYS = 180    # general news and context can be older
B2B_SOURCES = {"b2b_news"}
B2B_N = 8                  # max account signals in the digest
B2B_MIN_SCORE = 3

# ------------------------------------------------------------ Pipeline settings
MIN_SCORE_TO_KEEP = 3      # only items scoring >= this reach the digest
TOP_N = 10                 # max leads in the digest
CONTEXT_N = 5              # max news/context items in the digest
MARKET_SOURCES = {"hacker_news"}   # builders and products: competitors, ecosystem (not leads)
MARKET_N = 5
MARKET_MIN_SCORE = 2       # market items only need a topic match, not a person in pain
LEAD_SOURCES = {"reddit"}   # sources where individuals post their OWN problems (= potential leads)
LLM_CANDIDATE_MIN = 2      # keyword score needed before we spend an LLM call
MAX_LLM_ITEMS = 30         # hard cap on LLM calls per run (cost control)
DB_PATH = "seen.db"        # SQLite file used for dedupe
