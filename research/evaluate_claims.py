"""Evaluate dated monetary-policy claim checks; no fabricated LLM outputs.

python research/evaluate_claims.py
python research/evaluate_claims.py --predictions path/to/model_outputs.jsonl

Optional model outputs: one JSON object per line with an existing `id`, a
`verdict` of supported|contradicted|abstain, and an `evidence_fact_id` or null.
The evaluator checks that the evidence id belongs to the SAME document.
Only the tiny derived pilot is bundled; held-out model comparisons require an
independently curated evaluation set and actual run outputs.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_jsonl(path):
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def numbers(text):
    return set(re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])", text))


OPPOSITES = [
    ("surplus", "deficit"), ("appreciat", "depreciat"),
    ("rising", "falling"), ("raised", "cut"),
    ("increased", "cut"), ("held", "raised"),
    ("kept", "reduced"), ("rose", "cut"),
]


def opposite(claim, evidence):
    c, e = claim.lower(), evidence.lower()
    return any((a in c and b in e) or (b in c and a in e) for a, b in OPPOSITES)


def baseline(rows):
    # TF-IDF learns only term weights from the unlabeled evidence anchors.
    # Each claim is retrieved against the anchors for its own document.
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    evidence = {(r["document_date"], r["fact_id"]): r["evidence_paraphrase"] for r in rows}
    corpus = list(evidence.values())
    model = TfidfVectorizer(ngram_range=(1, 2), lowercase=True).fit(corpus + [r["claim"] for r in rows])
    outputs = []
    for r in rows:
        candidates = [(key, val) for key, val in evidence.items() if key[0] == r["document_date"]]
        similarities = cosine_similarity(model.transform([r["claim"]]),model.transform([v for _, v in candidates]))[0]
        best_idx = int(similarities.argmax())
        key, anchor = candidates[best_idx]
        if similarities[best_idx] < 0.12:
            verdict = "abstain"
        elif not numbers(r["claim"]).issubset(numbers(anchor)) or opposite(r["claim"], anchor):
            verdict = "contradicted"
        else:
            verdict = "supported"
        outputs.append({"id": r["id"], "verdict": verdict,
                        "evidence_fact_id": key[1], "retrieval_score": round(float(similarities[best_idx]), 3)})
    return outputs


def evaluate(rows, outputs):
    by_id = {r["id"]: r for r in rows}
    if len(outputs) != len(by_id) or set(by_id) != {p["id"] for p in outputs}:
        raise ValueError("Prediction IDs must match benchmark exactly, once each")
    allowed = {"supported", "contradicted", "abstain"}
    counts = Counter()
    errors = []
    for prediction in outputs:
        r = by_id[prediction["id"]]
        if prediction["verdict"] not in allowed:
            raise ValueError(f"Invalid verdict for {r['id']}")
        evidence_id = prediction.get("evidence_fact_id")
        cited = evidence_id == r["fact_id"]
        counts["total"] += 1
        counts["abstentions"] += prediction["verdict"] == "abstain"
        counts["correct"] += prediction["verdict"] == r["gold"]
        counts["correct_and_source_grounded"] += prediction["verdict"] == r["gold"] and cited
        counts["wrong_fact_or_missing_citation"] += not cited
        if prediction["verdict"] != r["gold"] or not cited:
            errors.append({"id": r["id"], "document_date": r["document_date"], "gold": r["gold"],
                           "predicted": prediction["verdict"], "evidence_fact_id": evidence_id,
                           "claim": r["claim"], "source_url": r["source_url"]})
    return {"n": counts["total"], "accuracy": round(counts["correct"] / counts["total"], 3),
            "accuracy_with_correct_fact_anchor": round(counts["correct_and_source_grounded"] / counts["total"], 3),
            "abstention_rate": round(counts["abstentions"] / counts["total"], 3),
            "wrong_or_missing_fact_anchor": counts["wrong_fact_or_missing_citation"],
            "errors": errors,
            "limits": "Pilot contains paraphrased anchors and two closely related claims per fact. No independent holdout, exact PDF passage verification, measured LLM, or production inference."}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims",type=Path,default=ROOT / "claims_pilot.jsonl")
    parser.add_argument("--predictions",type=Path)
    parser.add_argument("--output",type=Path,default=ROOT / "claim_pilot_results.json")
    args=parser.parse_args()
    rows=read_jsonl(args.claims)
    outputs=read_jsonl(args.predictions) if args.predictions else baseline(rows)
    report=evaluate(rows,outputs)
    report["method"]="external supplied predictions" if args.predictions else "TF-IDF within-document retrieval plus numeric and polarity heuristics"
    report["sample"]="30 synthetic contrast claims derived from 15 manually checked facts across five SBP statements; NOT an independent LLM benchmark"
    args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(f"{report['method']}: {report['n']} claims, accuracy {report['accuracy']:.1%}, correct-fact-anchor accuracy {report['accuracy_with_correct_fact_anchor']:.1%}, abstention {report['abstention_rate']:.1%}")


if __name__ == "__main__":
    main()
