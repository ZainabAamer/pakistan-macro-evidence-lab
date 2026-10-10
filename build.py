"""Build the offline Macro Decision Room from the SBP archival FX series.

Run: python build.py --fx path/to/fx.csv
The input has observation_date and pkr_per_usd columns. The archive's
published_date column is intentionally NOT used as a historical release time.
"""
import argparse
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FX_SOURCE = "https://archive.sbp.org.pk/ecodata/BFER_Daily_Arch.xlsx"
STAGES = [
    {
        "id": "apr22", "episode": "2022 · tightening", "date": "2022-04-07",
        "end": "2022-05-23", "title": "An emergency rate increase",
        "brief": "SBP raised its policy rate by 250 basis points to 12.25%. It cited higher global commodity prices, tighter global financial conditions and risks to external stability. It said the rupee had depreciated 5% since the previous policy meeting.",
        "question": "Between the first FX observation after this decision and the last one before the next policy meeting, does USD/PKR rise or fall?",
        "source": "https://www.sbp.org.pk/assets/document/publications/MPS-Apr-2022-Eng.pdf",
        "locator": "April 7 policy statement, paragraphs 2–4",
        "claims": [
            "SBP increased the policy rate to 12.25%.",
            "SBP said the February current account recorded a $0.5 billion surplus."
        ], "false_index": 1,
        "audit_explanation": "The statement says the February current account had a $0.5 billion DEFICIT (paragraph 2)."
    },
    {
        "id": "may22", "episode": "2022 · tightening", "date": "2022-05-23",
        "end": "2022-07-07", "title": "Inflation and the exchange rate",
        "brief": "SBP raised its policy rate by 150 basis points to 13.75%. It reported April headline inflation of 13.4% year on year and described persistent pressure on the exchange rate.",
        "question": "What happens to the historical USD/PKR reference rate before the July decision?",
        "source": "https://www.sbp.org.pk/assets/document/publications/MPS-May-2022-Eng.pdf",
        "locator": "May 23 policy statement, paragraphs 1–4",
        "claims": [
            "SBP said April headline inflation had fallen below 5%.",
            "SBP raised the policy rate by 150 basis points to 13.75%."
        ], "false_index": 0,
        "audit_explanation": "SBP reported April headline inflation of 13.4% year on year (paragraph 3)."
    },
    {
        "id": "jul22", "episode": "2022 · tightening", "date": "2022-07-07",
        "end": "2022-08-22", "title": "A loan arrives, risks remain",
        "brief": "SBP raised the policy rate by 125 basis points to 15%. Its statement reported a $2.3 billion commercial loan from China, but also warned about inflation, energy imports and pressure on the currency.",
        "question": "Does the historical USD/PKR reference rate rise or fall before the August decision?",
        "source": "https://www.sbp.org.pk/assets/document/publications/MPS-Jul-2022-Eng.pdf",
        "locator": "July 7 policy statement, paragraphs 1–4",
        "claims": [
            "SBP said a $2.3 billion Chinese commercial loan supported reserves.",
            "SBP cut its policy rate to 12.25% at this meeting."
        ], "false_index": 1,
        "audit_explanation": "SBP increased the rate to 15%, rather than cutting it (paragraph 1)."
    },
    {
        "id": "aug22", "episode": "2022 · tightening", "date": "2022-08-22",
        "end": "2022-10-10", "title": "A pause, then a reversal?",
        "brief": "SBP held the policy rate at 15%. It reported that inflation reached 24.9% in July, said the currency had appreciated around 10% during August, and expected an IMF Board meeting later that month.",
        "question": "Across the longer window ending before October 10, does USD/PKR finish higher or lower? Watch the path after you reveal it.",
        "source": "https://www.sbp.org.pk/assets/document/publications/MPS-Aug-2022-Eng.pdf",
        "locator": "August 22 policy statement, paragraphs 1–2",
        "claims": [
            "SBP reported that July inflation was below 10%.",
            "SBP held its policy rate at 15%."
        ], "false_index": 0,
        "audit_explanation": "SBP reported July inflation of 24.9% (paragraph 2)."
    },
    {
        "id": "sep23", "episode": "2023 · reset", "date": "2023-09-14",
        "end": "2023-10-30", "title": "Same country, different direction",
        "brief": "Time jump: September 2023. SBP held the policy rate at 22%. It reported August inflation at 27.4%, higher oil prices, a return to a current account deficit in July, and measures targeting illegal FX market activity.",
        "question": "Does the historical USD/PKR reference rate rise or fall before the October decision?",
        "source": "https://www.sbp.org.pk/assets/document/publications/MPS-Sep-2023-Eng.pdf",
        "locator": "September 14 policy statement, paragraphs 1–2",
        "claims": [
            "SBP held its policy rate at 22%.",
            "SBP said the July current account had remained in surplus."
        ], "false_index": 1,
        "audit_explanation": "SBP said the current account moved into DEFICIT in July after four months in surplus (paragraph 2)."
    },
]


def load_fx(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    result = []
    for row in rows:
        day = row["observation_date"]
        price = float(row["pkr_per_usd"])
        if not (1900 <= int(day[:4]) <= 2100 and math.isfinite(price) and price > 0):
            raise ValueError(f"Invalid FX observation: {row}")
        result.append({"date": day, "rate": round(price, 5)})
    result.sort(key=lambda r: r["date"])
    if len({r["date"] for r in result}) != len(result):
        raise ValueError("Duplicate FX observation dates")
    return result


def compile_stages(fx):
    out = []
    for stage in STAGES:
        window = [r for r in fx if stage["date"] < r["date"] < stage["end"]]
        if len(window) < 2:
            raise ValueError(f"Insufficient reference observations: {stage['id']}")
        first, last = window[0], window[-1]
        change = (last["rate"] / first["rate"] - 1) * 100
        high = max(window, key=lambda r: r["rate"])
        low = min(window, key=lambda r: r["rate"])
        if abs(change) < 0.2:
            raise ValueError(f"Window too close to zero to classify: {stage['id']}")
        out.append({**stage, "window": window,
                    "change_pct": round(change, 3),
                    "peak_up_pct": round((high["rate"] / first["rate"] - 1) * 100, 3),
                    "peak_up_date": high["date"],
                    "peak_down_pct": round((low["rate"] / first["rate"] - 1) * 100, 3),
                    "peak_down_date": low["date"],
                    "direction": "up" if change > 0 else "down"})
    return out


def build(fx_file, output):
    stages = compile_stages(load_fx(fx_file))
    template = (ROOT / "template.html").read_text(encoding="utf-8")
    payload = json.dumps({"stages": stages, "fx_source": FX_SOURCE}, ensure_ascii=False)
    output.write_text(template.replace("/*__CASE_DATA__*/", payload.replace("</", "<\\/")), encoding="utf-8")
    print(f"Built {output}: {len(stages)} rounds, {sum(s['direction']=='down' for s in stages)} down windows")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fx", type=Path, default=ROOT / "data" / "fx_reference.csv")
    p.add_argument("--output", type=Path, default=ROOT / "macro_decision_room.html")
    a = p.parse_args()
    build(a.fx, a.output)
