"""Build a small source-checked claim-verification pilot.

Each manually checked FACT has a paraphrased source anchor, document date,
paragraph, a true claim and a deliberately corrupted claim. Claims generated
from the same fact are related and must never be split across train and test.
This 30-item pilot is NOT a 100-claim independent holdout benchmark.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FACTS = [
    # April 2022 statement, paragraphs 2–4.
    ("apr_rate", "2022-04-07", "https://www.sbp.org.pk/assets/document/publications/MPS-Apr-2022-Eng.pdf", "4", "The monetary policy committee increased the policy rate to 12.25 percent by 250 basis points.", "The SBP increased the policy rate to 12.25 percent.", "The SBP increased the policy rate to 15 percent."),
    ("apr_ca", "2022-04-07", "https://www.sbp.org.pk/assets/document/publications/MPS-Apr-2022-Eng.pdf", "2", "The February current account had a deficit of 0.5 billion dollars.", "The February current account was in deficit by 0.5 billion dollars.", "The February current account had a surplus of 0.5 billion dollars."),
    ("apr_fx", "2022-04-07", "https://www.sbp.org.pk/assets/document/publications/MPS-Apr-2022-Eng.pdf", "2", "The rupee depreciated 5 percent since the previous policy meeting.", "SBP said the rupee had depreciated 5 percent since its previous meeting.", "SBP said the rupee had appreciated 5 percent since its previous meeting."),
    # May 2022 statement, paragraphs 1, 3 and 6.
    ("may_rate", "2022-05-23", "https://www.sbp.org.pk/assets/document/publications/MPS-May-2022-Eng.pdf", "1", "The policy rate rose 150 basis points to 13.75 percent.", "The May policy decision set the rate at 13.75 percent.", "The May policy decision set the rate at 12.25 percent."),
    ("may_cpi", "2022-05-23", "https://www.sbp.org.pk/assets/document/publications/MPS-May-2022-Eng.pdf", "3", "Headline inflation in April was 13.4 percent year over year.", "April headline inflation was 13.4 percent year over year.", "April headline inflation was 5 percent year over year."),
    ("may_ca", "2022-05-23", "https://www.sbp.org.pk/assets/document/publications/MPS-May-2022-Eng.pdf", "6", "The April current account recorded a deficit of 623 million dollars.", "The April current account deficit was 623 million dollars.", "The April current account surplus was 623 million dollars."),
    # July 2022 statement, paragraphs 1–3.
    ("jul_rate", "2022-07-07", "https://www.sbp.org.pk/assets/document/publications/MPS-Jul-2022-Eng.pdf", "1", "The policy rate was increased 125 basis points to 15 percent.", "The policy rate rose to 15 percent in July.", "The policy rate was cut to 15 percent in July."),
    ("jul_loan", "2022-07-07", "https://www.sbp.org.pk/assets/document/publications/MPS-Jul-2022-Eng.pdf", "2", "A commercial loan from China of 2.3 billion dollars supported foreign exchange reserves.", "SBP said a 2.3 billion dollar commercial loan from China helped reserves.", "SBP said a 4.3 billion dollar commercial loan from China helped reserves."),
    ("jul_reserves", "2022-07-07", "https://www.sbp.org.pk/assets/document/publications/MPS-Jul-2022-Eng.pdf", "2", "The China loan helped provide support to reserves that had been falling since January.", "SBP said reserves had been falling since January.", "SBP said reserves had been rising since January."),
    # August 2022 statement, paragraphs 1, 2 and 6.
    ("aug_rate", "2022-08-22", "https://www.sbp.org.pk/assets/document/publications/MPS-Aug-2022-Eng.pdf", "1", "The committee left the policy rate at 15 percent.", "SBP held the policy rate at 15 percent.", "SBP raised the policy rate to 16 percent."),
    ("aug_cpi", "2022-08-22", "https://www.sbp.org.pk/assets/document/publications/MPS-Aug-2022-Eng.pdf", "2", "Headline inflation rose to 24.9 percent in July.", "The statement reported July inflation of 24.9 percent.", "The statement reported July inflation of 14.9 percent."),
    ("aug_reserves", "2022-08-22", "https://www.sbp.org.pk/assets/document/publications/MPS-Aug-2022-Eng.pdf", "6", "The bank's foreign exchange reserves were 7.9 billion dollars on August 12.", "On August 12 reserves stood at 7.9 billion dollars.", "On August 12 reserves stood at 16.4 billion dollars."),
    # September 2023 statement, paragraphs 1, 2 and 5.
    ("sep_rate", "2023-09-14", "https://www.sbp.org.pk/assets/document/publications/MPS-Sep-2023-Eng.pdf", "1", "The committee kept the policy rate at 22 percent.", "SBP held its policy rate at 22 percent.", "SBP reduced its policy rate to 20 percent."),
    ("sep_cpi", "2023-09-14", "https://www.sbp.org.pk/assets/document/publications/MPS-Sep-2023-Eng.pdf", "1", "Inflation in August 2023 fell to 27.4 percent from the May peak of 38 percent.", "The statement put August inflation at 27.4 percent.", "The statement put August inflation at 38 percent."),
    ("sep_ca", "2023-09-14", "https://www.sbp.org.pk/assets/document/publications/MPS-Sep-2023-Eng.pdf", "5", "The July 2023 current account balance recorded a deficit of 809 million dollars.", "July 2023 current account deficit was 809 million dollars.", "July 2023 current account surplus was 809 million dollars."),
]


def pilot_records():
    rows = []
    for fid, day, url, paragraph, evidence, supported, contradicted in FACTS:
        for suffix, claim, gold in (("s", supported, "supported"), ("c", contradicted, "contradicted")):
            rows.append({"id": f"{fid}_{suffix}", "fact_id": fid, "document_date": day,
                         "source_url": url, "paragraph": paragraph,
                         "evidence_paraphrase": evidence, "claim": claim, "gold": gold})
    return rows


def main():
    output = ROOT / "claims_pilot.jsonl"
    output.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in pilot_records()), encoding="utf-8")
    print(f"Wrote {len(pilot_records())} derived claims from {len(FACTS)} manually checked facts across 5 documents. This is an initial pilot, not an independent benchmark.")


if __name__ == "__main__":
    main()
