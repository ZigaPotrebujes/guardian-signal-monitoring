"""
Company-lane labels: 26 real news headlines from one live run on 2026-11-17 (the 'b2b_news' source), labelled by me.
Headlines are public news, so they are kept as they appeared. Labels use HEADLINES ONLY (I did not open every link).

Rubric:
  good = a named organization or public figure, recent, publicly warning about or reporting impersonation of
         its own brand or person (the kind of company Guardian could plausibly sell to)
  weak = relevant topic, but generic phishing / scam advice, or impersonation of a service the company does not own
  no   = a different problem (outages, hoaxes, breaches, wire fraud) or generic tips

Items marked UNVERIFIED need the article opened before the label can be trusted.
Fields: (label, headline)
"""
LABELED_ACCOUNTS = [
    ("good", "'Buldak Ramen' Posts Record Results... Samyang Foods Warns of Employee Impersonation Scams - 아시아경제"),
    ("good", "Nio warns owners of 'airbag recall' scam texts as other automakers issue similar alerts - CnEVPost"),
    ("weak", "Muhoozi's son Ruhamya disowns social media accounts attacking public figures - Pulse Uganda"),  # UNVERIFIED
    ("weak", "UBA warns customers against phishing scams - Western Post"),
    ("weak", "UBA warns customers against phishing scams as Fraud Awareness Week begins - Head Topics"),
    ("weak", "UBA exposes how fraudsters use cloned websites, fake messages to steal customers' money - Chronicle NG"),
    ("weak", "UBA Intensifies Fight Against Phishing, Scam As 2026 Fraud Awareness Week Begins - LEADERSHIP Newspapers"),
    ("weak", "Monzo issues warning for millions of customers over Black Friday scams - Birmingham Live"),
    ("weak", "SBI Card issues urgent warning against fake refund and online fraud - Latest Key Updates - Zoom News"),
    ("weak", "Warning issued to Aldi shoppers in November as they may 'lose money' - AOL.co.uk"),
    ("weak", "Microsoft Outage Has Given Hackers A New Opportunity To Steal Your Passwords; Company Issues Warning - Mashable"),
    ("weak", "Gardaí issue Microsoft outage scam warning to anyone who uses Teams, Outlook, Excel - Cork Beo"),
    ("weak", "Court in the act: Judge Ledwaba impersonator answers News24 call as 'judge' despite warning - News24"),
    ("weak", "Don't panic over fake Trump post warning of disruptions to food supply, banking services - Snopes.com"),
    ("no", "Asos hackers took more personal details than first revealed, BBC finds - BBC"),
    ("no", "National Grid issues urgent warning to Midlands households over major outage claims - birmingham-now.co.uk"),
    ("no", "National Grid issues statement over UK power outage rumours circulating online - Oxford Mail"),
    ("no", "National Grid issues statement over false UK power outage rumours for November 19 - The Worcester News"),
    ("no", "Will there be a blackout this week?National Grid update as rumours shared online - The Sun"),
    ("no", "November 17 blackout hoax: How a conspiracy theory went viral around the world - Truth or Fake - France 24"),
    ("no", "Phishing attempts are about to surge. 6 ways to protect your business - KESQ"),
    ("no", "Seven clever Black Friday scams and how to spot them - Essex Live"),
    ("no", "Microsoft Down: Outlook, Teams, Copilot And SharePoint Face Global Outage; What Happened? - Mashable India"),
    ("no", "Fraud Alert: How an AI 'Boss' Allegedly Helped Fraudsters Steal US$129mn - Moneylife"),
    ("no", "FaceStealer: FBI Disrupts Fake Video Call Crypto Scam - SOCRadar"),
    ("no", "Fake Police and Bank Scammers: Deloitte Expert Outlines How Kuwait Can Fight Online Fraud - Arab Times Kuwait News"),
]
