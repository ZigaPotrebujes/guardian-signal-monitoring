"""
Measure the scorer against human labels. No network, no API key.

    python eval.py

Compares version 1 (topic only, runs 1-3) with version 2 (topic + product-fit gate, run 4) on the
labeled run-3 leads. "Surfaced" = would reach the lead list (score >= MIN_SCORE_TO_KEEP, and for v2 a fit).
"""
import agent
import config
from labeled_leads import LABELED


def main():
    rows = []
    for pid, label, title, text in LABELED:
        item = agent.make_item("reddit", "", f"https://example.com/{pid}", text)
        v1 = agent.score_topic_only(item)
        v2 = agent.score_keywords(item)
        rows.append({"id": pid, "label": label, "title": title,
                     "v1_score": v1["score"], "v1_in": v1["score"] >= config.MIN_SCORE_TO_KEEP,
                     "v2_score": v2["score"], "v2_fit": v2["fit"],
                     "v2_in": v2["score"] >= config.MIN_SCORE_TO_KEEP and v2["fit"] in ("strong", "partial")})

    print(f"{'#':>2} {'label':8} {'v1':>3} {'v1 in':6} {'v2':>3} {'fit':8} {'v2 in':6}  title")
    for r in rows:
        print(f"{r['id']:>2} {r['label']:8} {r['v1_score']:>3} {str(r['v1_in']):6} {r['v2_score']:>3} "
              f"{r['v2_fit']:8} {str(r['v2_in']):6}  {r['title'][:55]}")

    def summary(name, key):
        shown = [r for r in rows if r[key]]
        strong = sum(r["label"] == "strong" for r in shown)
        good = sum(r["label"] in ("strong", "partial") for r in shown)
        n = len(shown)
        total_good = sum(r["label"] in ("strong", "partial") for r in rows)
        print(f"{name}: surfaced {n} | strong {strong} | strong+partial {good} | "
              f"precision {good}/{n} = {good / n:.0%} | recall {good}/{total_good}" if n else f"{name}: surfaced 0")

    exact = sum(r["label"] == r["v2_fit"] for r in rows)
    print(f"\nExact fit-label agreement (v2 vs human): {exact}/{len(rows)}   "
          "(stricter than precision: it also catches 'partial' called 'strong')")
    print()
    summary("v1 topic only      ", "v1_in")
    summary("v2 with fit gate   ", "v2_in")
    print("\nCaveat: v2 word lists were written after seeing these posts, so this is optimistic.")
    print("Recall here covers only items already surfaced in run 3; posts the old scorer missed are unlabeled.")


if __name__ == "__main__":
    main()
