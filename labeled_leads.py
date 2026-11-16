"""
Human-labeled evaluation set: 11 posts that reached the lead list in runs 3 and 4 (2026-11-16).

PRIVACY: these are SHORT PARAPHRASES written for this repo, not the original posts, so that strangers' personal
details are not republished. The scorer was first measured on the verbatim posts; the paraphrases keep the same
kind of wording, and eval.py gives the same per-item outcome on them (checked when this file was written).
Treat the set as a demo of the method, not as a benchmark.

Label = could Guardian act on this? (judged against public descriptions of the product; verify with the company)
  strong  = fake account/profile/deepfake of the author that evidence + takedown requests address
  partial = identity details misused on a platform, a mixed case, or a weak/after-the-fact fit
  none    = financial/government identity fraud, tricked-into-paying scams, or not a personal case

CAVEAT: the fit-gate word lists were written AFTER seeing these posts, so scores on this set are optimistic.
The honest test is a fresh run on posts the lists have never seen (see README).
"""

LABELED = [
    ("1", "none", "Disability payments cut off by wage fraud under a relative's SSN (IRS, SSA, employer)",
     "My sister receives SSI payments but she is a victim of identity theft. We filed the IRS form and an FTC and police "
     "report, and closed some fraudulent accounts on her credit record. Her payments keep stopping because someone "
     "fraudulently working under her name keeps claiming wages. The SSA told me to call the employer, but I only have a "
     "name and a PO box address. How do I stop the wages being claimed under her name?"),
    ("2", "none", "Friend kept my laptop, phone and SIM and registered the SIM with my social security details",
     "I lent a friend my laptop, phone and SIM card for exams. He kept using my email and got the SIM registered in his name "
     "using my social security info from my laptop. He has a history of stalking. I am afraid he accessed my photos and "
     "is using my identity for something illegal. What should I do?"),
    ("3", "none", "Phone scammers posing as the bank's fraud department coached me to withdraw cash",
     "Someone impersonating the fraud department at my bank gained access to my bank account with security questions and "
     "coached me through withdrawing cash and transferring it. So far I froze my credit, closed the affected bank accounts, "
     "filed an FTC report, and reported to the SSA. Our joint credit card is maxed out and I am worried about my "
     "spouse's credit score."),
    ("4", "none", "Stolen wallet led to a fraudulent telecom account and a benefits application",
     "My wallet was stolen with my ID, social security card and bank cards. Later I found a fraudulent mobile phone account "
     "in my name with thousands in charges, and a fraudulent benefits application using photos of my real ID. I have filed "
     "FTC identity theft reports and police reports and have surveillance photos of people using the benefits card. "
     "Is it worth pushing the police to investigate?"),
    ("5", "none", "Bank email says new info was linked to my SSN after I left the US",
     "I used a US checking account and got an SSN during a work and travel program, then closed the account and moved "
     "abroad. I got an email from my former bank that new info was linked to my social security number. I cannot check my "
     "credit reports from outside the US. Does this mean someone used my SSN to open a financial account?"),
    ("6", "none", "Telecom wireless account opened in my name, collections calling",
     "A wireless account was opened with my personal information, with two devices and thousands in charges. I found out "
     "from a collections letter and now get calls every day. The carrier's fraud investigation never confirmed the debt was "
     "removed, and the credit bureau said the account reports correctly. I placed a fraud alert. Did a complaint to "
     "the telecom ombudsman help anyone?"),
    ("7", "strong", "Fake account about me posting my driver's license and edited pics, stalking family's Facebook",
     "can i get the cops involved if someone is making a fake account about me and posts me and my drivers license even if "
     "it doesn't show the numbers and has an account posting pics of me that are edited and stalks my family's Facebook"),
    ("8", "partial", "Scam page on Facebook lists my friend's phone number as its contact",
     "A scam page on Facebook has listed my friend's phone number as its contact. She has nothing to do with the page but "
     "gets angry calls all day from people who were scammed. We reported the page many times and filed a police report "
     "and the page is still up. Is there any way to reach an actual human at Meta?"),
    ("9", "none", "Public awareness post about unauthorised complaints filed in a person's name with a regulator",
     "Awareness alert: complaints were registered in my name with a financial regulator's ombudsman portal without my "
     "knowledge or permission and forwarded to a bank. Citizens should monitor alerts, verify complaints made in their "
     "name and keep records against identity misuse. #CitizenAwareness #IdentityMisuse"),
    ("10", "none", "Emails about account changes at a bank for an account that is not mine",
     "I am getting emails from a bank about an updated email address, phone number and password, and a linked merchant, "
     "but my own account looks fine and is not linked to this email. The debit card and credit card people could not see "
     "any activity. Is it possible someone mistakenly added my email to their account?"),
    ("11", "partial", "I sent my ID to a scammer (selfie and video holding it)",
     "I have sent my drivers license to a scammer through a selfie and a video of me holding it. What should I do now? "
     "Please someone help"),
]
