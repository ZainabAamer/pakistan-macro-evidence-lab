"""Optional local-LLM runner. No model is bundled; no model has been tested here.

Install/run your own Ollama model locally, then execute:
python research/run_ollama.py --model YOUR_LOCAL_MODEL
python research/evaluate_claims.py --predictions research/ollama_predictions.jsonl

The pilot only supplies manually paraphrased FACT anchors, not complete SBP
documents. Do not interpret this pilot as verification of an exact PDF quote.
"""
import argparse
import json
import urllib.request
from pathlib import Path

from evaluate_claims import ROOT, read_jsonl


def run(model, endpoint, out):
    if not endpoint.startswith("http://127.0.0.1:") and not endpoint.startswith("http://localhost:"):
        raise ValueError("Only a local Ollama endpoint is supported")
    claims = read_jsonl(ROOT / "claims_pilot.jsonl")
    groups = {}
    for r in claims:
        groups.setdefault(r["document_date"], {})[r["fact_id"]] = r["evidence_paraphrase"]
    answers=[]
    for r in claims:
        anchors=groups[r["document_date"]]
        prompt=("Check the claim against ONLY the SOURCE-DERIVED PARAPHRASES below. "
                "Respond with compact JSON using verdict supported|contradicted|abstain, "
                "and evidence_fact_id equal to a displayed fact id or null. "
                "Abstain if the excerpts cannot decide. Do not claim you read the full PDF.\n"
                f"Statement date: {r['document_date']}\n"
                f"Excerpts: {json.dumps(anchors)}\nClaim: {r['claim']}\n")
        payload=json.dumps({"model":model,"prompt":prompt,"stream":False,"format":"json","options":{"temperature":0}}).encode()
        req=urllib.request.Request(endpoint, data=payload,headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=120) as response:
            raw=json.load(response)
        parsed=json.loads(raw["response"])
        verdict=parsed.get("verdict", "abstain")
        fact_id=parsed.get("evidence_fact_id")
        if fact_id not in anchors: fact_id=None
        if verdict not in {"supported","contradicted","abstain"}: verdict="abstain"
        answers.append({"id":r["id"],"verdict":verdict,"evidence_fact_id":fact_id,"model":model})
        print(f"{len(answers)}/{len(claims)} {r['id']} {verdict}")
        # Keep successful completed requests even if a later one fails.
        out.write_text("".join(json.dumps(x)+"\n" for x in answers),encoding="utf-8")
    print(f"Completed {len(answers)} pilot claims. Now run evaluate_claims.py --predictions {out}")


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model",required=True)
    p.add_argument("--endpoint",default="http://127.0.0.1:11434/api/generate")
    p.add_argument("--out",type=Path,default=ROOT / "ollama_predictions.jsonl")
    a=p.parse_args()
    run(a.model,a.endpoint,a.out)
