# Pakistan Macro Evidence Lab

**Start here:** Open [`research/research_dashboard.html`](research/research_dashboard.html) locally to explore a 40-policy-statement USD/PKR risk audit. Filter individual event windows and inspect the year-by-year comparison. The dashboard works offline. Then open `macro_decision_room.html` for the companion five-case decision exercise. The Python scripts and source data reproduce the results.

**Original finding:** The five earlier case-study decisions averaged a 7.80% maximum absolute USD/PKR reference-rate move over 20 observations; *all 17* listed 2022–2023 policy statements averaged 5.14%. Across every listed 2021–2025 statement (40 dates total), the average difference between policy windows and same-year nonmeeting controls was +0.70 percentage points in the exploratory 2021–2024 years but only **+0.05 percentage points in the 2025 temporal holdout**. This exposes how cherry-picked crises can make a risk signal look stronger than it is. The holdout is only one year; this does not demonstrate a trading strategy or causal effect.

**AI evaluation:** The accompanying evidence-checking pilot has 15 manually verified policy-statement facts turned into 30 related claims. A TF-IDF retrieval and rule-based verifier scores 25/30; its date-mismatch error illustrates why a matched number is not enough to validate a macro claim. There is no measured LLM performance or user-impact claim.

**Uncertainty and horizon checks:** The 2025 event-minus-control differences are +0.014, +0.003 and +0.052 percentage points using 5, 10 and 20 observations. An exact two-sided sign-flip calculation on the **five annual differences** gives p = 0.5625, 0.5625 and 0.0625, respectively. This conditional year-level reference avoids treating overlapping daily windows as independent, but relies on an unverified symmetry/exchangeability assumption and has only five annual units. It does **not** supply a significance test for 2025 alone; a p-value above 0.05 does not prove a zero or negligible effect. The shorter horizons were checked after the 20-observation result and are exploratory.

## Audit design

Run `python research/full_event_study.py` to recalculate the 40-date study from `data/fx_full.csv` and `python research/build_research_dashboard.py` to recreate the shareable dashboard. All statement dates were transcribed from the [official SBP policy-statement catalogue](https://www.sbp.org.pk/our-operations/publications/monetary-policy-statements/501), and the reference-rate archive is linked below. The result JSON lists *each* policy date, first post-release observation, end date, maximum absolute excursion and year-level summary. Controls start at least six calendar days from listed meetings and exclude windows that cross a meeting; overlapping control windows are not independent observations. The question was motivated by prior case selection, so the development result is exploratory; 2025 is a limited temporal check.

The five-case tool described below predates the full audit. Its original exploratory comparison uses a *different* control definition, so its control mean must not be compared directly with the 40-date control means. For methods, source timing and limitations, see [`research/RESEARCH_NOTE.md`](research/RESEARCH_NOTE.md).

## Companion decision exercise

A self-contained, five-decision historical market exercise. Open **macro_decision_room.html** in a browser. No installation, login, service, API key or network connection is required.

The case asks: after reading an actual SBP monetary policy statement, how would you assess the next interval of the USD/PKR historical reference rate? Before the reveal, you also check two claims in a deliberately flawed analyst memo against that statement. The historical price path appears after the decision is locked.

## What is built

- Five documented decisions: April, May, July and August 2022, and a separate September 2023 episode. The 2023 case is explicitly a time jump, not a continuous episode.
- An offline browser interface with a dated research brief, linked primary source, prediction, confidence, optional written thesis, illustrative exposure, source-check challenge, results chart, scoring breakdown, and downloadable personal decisions.
- A Python build pipeline, the limited FX source dataset used in the cases, and checks for unique observations and valid nonzero rate changes. Source dataset and all per-round reference observations are bundled in the HTML.
- A hand-authored adversarial memo. **This is not an LLM integration or automated fact verification.** Its factual traps have answers linked to the original documents. The player's thesis is never automatically scored.
- `research/event_risk.py` compares the reference-rate path over 20 observations after each of the five case decisions against same-year placebo windows that exclude dates close to every 2022–2023 SBP policy meeting. The analysis is **exploratory, not a tradable signal**: its five event dates were selected for the case study after their history was known.
- `research/claims_pilot.py` documents **15 manually checked source facts** and produces 30 related supported/contradicted claim variants. `research/evaluate_claims.py` measures an explicit TF-IDF retrieval plus number/polarity-check baseline and can score predictions supplied by a separate model. `research/run_ollama.py` can test a locally installed LLM, but no LLM is installed, bundled, or claimed to have been tested in this release.
- `research/PILOT_PROTOCOL.md` and `research/pdf_only_test.html` supply an opt-in PDF-versus-tool usability pilot that can be conducted once real users are available. The app and PDF-only sheet download local timed answer records; **no users have been tested yet**, and the app's extra FX task makes direct speed comparisons conservative rather than perfectly equivalent.

## Results from the research extension

For the five selected SBP statements, the mean maximum absolute 20-observation USD/PKR reference-rate move was **7.80%**, compared with **5.03%** averaged over same-year placebo draws. The fraction of placebo draws at least as large was **0.023**, which is **not a valid significance p-value** because the five crisis cases were chosen after some market history was viewed and samples can overlap. It cannot establish a forecast, trade, causal effect, or market edge. Exact methods, policy-date catalogue and all observations are in `research/event_risk.py` and `research/event_risk_results.json`.

On the 30-claim source-derived pilot, the TF-IDF plus numeric/polarity baseline achieved **83.3% verdict accuracy** and abstained **10.0%** of the time. The error list is in `research/claim_pilot_results.json`. The variants are paired and short paraphrased evidence anchors were written by a human, so this result does **not** measure performance on full unseen policy PDFs or a production AI analyst. It is not a claim of a deployed LLM.

## Original observation from the five-case sample

In the August 22–October 10, 2022 window, the reference rate finishes only **1.67% higher** from the first post-decision observation to the final observation before the boundary, yet reaches an interim high **10.66% above** the first observation (September 22). An analyst judged only on the final direction would miss a much larger interim move. This is a descriptive result in one selected interval, not a finding about an executable FX strategy or a causal effect of monetary policy. The five selected windows are a teaching sample, not an unbiased estimate of predictive skill.

## Run and rebuild

Open `macro_decision_room.html` to play. To rebuild using the included data:

```bash
python build.py
```

To use another normalized archival extract with columns `observation_date,pkr_per_usd`:

```bash
python build.py --fx path/to/your_fx.csv --output macro_decision_room.html
```

Standard-library Python only. The file's optional web font is not required offline.

The research extension can be rerun from the project root. The NLP pilot and full test suite require `scikit-learn`:

```bash
python -m pip install -r requirements.txt
python research/event_risk.py
python research/full_event_study.py
python research/build_research_dashboard.py
python research/claims_pilot.py
python research/evaluate_claims.py
python research/build_pdf_condition.py
python -m unittest discover -s tests -v
```

## Source and timing policy

- FX observations: SBP [Banks Floating Average Exchange Rates archive](https://archive.sbp.org.pk/ecodata/BFER_Daily_Arch.xlsx); 154 observations between April–October 2022 and September–October 2023. `data/fx_reference.csv` is a two-column subset normalized from that workbook, to five decimal places in generated HTML. It includes no claims about date of publication.
- Policy statements, each linked within its round: [April 7, 2022](https://www.sbp.org.pk/assets/document/publications/MPS-Apr-2022-Eng.pdf), [May 23, 2022](https://www.sbp.org.pk/assets/document/publications/MPS-May-2022-Eng.pdf), [July 7, 2022](https://www.sbp.org.pk/assets/document/publications/MPS-Jul-2022-Eng.pdf), [August 22, 2022](https://www.sbp.org.pk/assets/document/publications/MPS-Aug-2022-Eng.pdf), [September 14, 2023](https://www.sbp.org.pk/assets/document/publications/MPS-Sep-2023-Eng.pdf).
- A decision takes place after reading that day's policy release; the outcome is the change from the **first available observation strictly after** that date to the **last observation strictly before** the next decision/date boundary. Intraday release time is not established. The policy statement is the only event information presented before the reveal. The original archive does not certify when a given historical daily average was first publicly available, so the historical FX time series is used **only for retrospective outcome assessment** and is never presented to the player before a decision.
- There is no tradability claim. These bank floating **average reference rates** are not executable bid/ask prices; no actual return, backtest, or trading signal is demonstrated. Events between decision and end date can influence the rate, so this exercise does not attribute moves causally to a policy announcement.
- Like most client-side learning exercises, its underlying dataset is inspectable through browser source. The interface hides outcomes until reveal for normal play; it does not claim secure blindness.

## Scoring and exposure math

- Direction: 45 points for the right rise/fall, 15 for “no strong view,” 0 for the wrong direction.
- Confidence: for a directional view, `round(20 × (1 − (p − y)²))`, with `p = 0.5 + 0.08 × confidence` and `y = 1` if correct or `0` if incorrect. The no-view option gets 10 points. This is a simple educational calibration rule, not a statistically valid skill estimate.
- Risk discipline: `round(15 − 0.8 × max(0, exposure − 10))` out of 15. Exposures are chosen from 0–20%.
- Source verification: 20 points for identifying the incorrect statement, else 0.
- The illustrative FX exposure effect is `rate_change_pct × exposure_pct / 100`, with sign flipped for “USD/PKR falls” and zero for no view. This is a sensitivity illustration with no transaction costs, financing, access to the market, or intraperiod drawdown calculation. It is not trading P&L.
- The reveal also reports the maximum and minimum reference-rate changes relative to the first post-decision observation. These endpoints show the path's extent; they do not establish a sequence of executable prices or a trader's drawdown.

## What would make a stronger research submission

The 40-date study adds an honest stress test of a hypothesis suggested by memorable case studies. A stronger AI evaluation would require an independently hand-labelled **100+ claim set across many policy statements**, including unsupported claims and unseen PDFs; a real LLM run with verified exact citations and failure analysis; and real opt-in usability tests. Direct downloads from SBP returned HTTP 403 in this environment, so this release uses manually checked facts linked to five official statements rather than implying a completed 100-document extraction. Do not describe hand-authored traps or the TF-IDF pilot as a frontier LLM.
