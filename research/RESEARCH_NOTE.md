# Macro Decision Room — evidence and limits

## Research question

Do selected crisis statements exaggerate apparent USD/PKR policy-day risk relative to all listed policy statements? Can a small NLP baseline check claims about those statements while exposing its source errors?

## Full-catalogue check: 40 policy dates

`full_event_study.py` lists all **40 SBP monetary policy statement dates from 2021 through 2025** in the [official catalogue](https://www.sbp.org.pk/our-operations/publications/monetary-policy-statements/501). It takes the first FX reference observation strictly after each date, then the next 19 observations. Its outcome is the largest absolute percentage change relative to the first observation. It compares the mean policy-date outcome with the mean for control dates in the *same year*, more than five calendar days away from any listed meeting and with no meeting through the end of the control window. Each observation and each annual mean appears in `full_event_study_results.json` and the interactive `research_dashboard.html`.

| Year | Statements | Eligible control starts | Event mean | Control mean | Event minus control |
| :-- | --: | --: | --: | --: | --: |
| 2021 | 7 | 75 | 1.94% | 1.83% | +0.11 pp |
| 2022 | 8 | 60 | 5.16% | 4.62% | +0.54 pp |
| 2023 | 9 | 51 | 5.13% | 3.00% | +2.12 pp |
| 2024 | 8 | 45 | 0.14% | 0.09% | +0.05 pp |
| **2025 holdout** | **8** | **52** | **0.27%** | **0.22%** | **+0.05 pp** |

The unrounded mean of the *four annual differences* in 2021–2024 is +0.703 pp; 2025 is +0.052 pp. The five originally selected 2022–2023 cases had mean largest move 7.80%; the full 17-date set for those two years had mean 5.14%. Selecting exceptional episodes after seeing history inflates the appearance of an effect. The earlier five-case control design differs from the full-catalogue comparison and their control figures should not be treated as directly comparable.

The earlier cases inspired the question, so 2021–2024 cannot be claimed as preregistered research. The later year is a *single* temporal check, and 2025's low overall reference-rate movement limits how much it can test about high-volatility regimes. Control paths overlap, policy decisions are endogenous to economic conditions, and the historical reference prices have no verified original publication times or executable quotes. This is a documented sensitivity finding, not a signal, significance test, return, or causal estimate.

### Exact annual sign-flip reference and horizon sensitivity

For each horizon, `sign_flip_test` computes the five year-level policy-minus-control differences, enumerates all 2⁵ possible sign flips, and records the fraction whose absolute average is at least the observed absolute average. The 2021–2024 development-only reference uses 2⁴ flips. Swapping *annual* differences avoids pretending that many overlapping daily controls are independent observations. Its two-sided p-value is meaningful only under the assumed null symmetry/exchangeability of annual difference signs; policy meetings are not randomized, the 2022–2023 regimes are different from 2025, years can be related, and five years leave very low resolution. The one-year 2025 result **cannot** be tested independently by flipping a single annual sign. The 5- and 10-observation horizons were inspected after the original 20-observation result, so treat them as exploratory sensitivity checks.

| Horizon (FX observations) | Development mean annual difference | 2025 difference | All-five-year sign-flip p |
| --: | --: | --: | --: |
| 5 | +0.429 pp | +0.014 pp | 0.5625 |
| 10 | +0.410 pp | +0.003 pp | 0.5625 |
| 20 | +0.703 pp | +0.052 pp | 0.0625 |

The development-only p-values are 0.625, 0.625 and 0.125 respectively. All three 2025 *point estimates* are small, but their sampling uncertainty cannot be reliably estimated from one independent year. A failure to reject a zero-effect null is **not** evidence that the effect is equivalent to zero. Notice that the 20-observation all-year reference p = 0.0625 is close to 0.05, while the shorter-horizon values are not; do not call the result horizon-invariant.

This is an **exploratory study**. The five statements were selected for an educational case after their historical context was known. Neither the event analysis nor the claim pilot is an independent validation of investment skill.

## FX reference-rate analysis

Source: [SBP historical bank floating exchange-rate archive](https://archive.sbp.org.pk/ecodata/BFER_Daily_Arch.xlsx). The included `data/fx_full.csv` contains 3,170 normalized observation dates and USD/PKR reference rates. The original archive does not establish a date of first public availability for each daily observation; rates are used only as retrospective outcomes. These are not executable bid/ask quotes.

For each [SBP policy statement](https://www.sbp.org.pk/our-operations/publications/monetary-policy-statements/501), start with the first available FX observation strictly after the decision and take 20 consecutive observations including that first value. Compare the rate at each observation with the first rate. The primary descriptive statistic is the largest *absolute* percentage change within the window. For reference, draw five matched-year placebo windows, excluding anchors within seven calendar days of **any** recorded 2022–2023 policy decision and excluding control windows that cross a later policy decision. Repeat the draws 10,000 times with a fixed seed; control dates may repeat. The design and exclusions are in `event_risk.py`.

| Policy statement | 20-observation window | Final change | Largest absolute move |
| :-- | :-- | --: | --: |
| [7 Apr 2022](https://www.sbp.org.pk/assets/document/publications/MPS-Apr-2022-Eng.pdf) | 8 Apr–6 May | −0.79% | 3.10% |
| [23 May 2022](https://www.sbp.org.pk/assets/document/publications/MPS-May-2022-Eng.pdf) | 24 May–20 Jun | +4.39% | 4.39% |
| [7 Jul 2022](https://www.sbp.org.pk/assets/document/publications/MPS-Jul-2022-Eng.pdf) | 13 Jul–11 Aug | +5.61% | 15.36% |
| [22 Aug 2022](https://www.sbp.org.pk/assets/document/publications/MPS-Aug-2022-Eng.pdf) | 23 Aug–19 Sep | +9.65% | 9.65% |
| [14 Sep 2023](https://www.sbp.org.pk/assets/document/publications/MPS-Sep-2023-Eng.pdf) | 15 Sep–13 Oct | −6.53% | 6.53% |

**Descriptive result:** average largest absolute move across the five statements was **7.80%**. Across 10,000 same-year placebo draws the corresponding average was **5.03%**; **2.3%** of those draws met or exceeded the event mean. That fraction is **not a significance-test p-value**. The periods were selected in hindsight, controls and event windows may overlap, the sample is tiny, and many other causes move the currency. The script reports 36 eligible control starts in each of 2022 and 2023; these are not 72 independent episodes.

**What the path adds:** The July 2022 window finished +5.61% from its first observation but reached +15.36% earlier. The earlier interactive case uses a different, longer window for August 2022 and finishes +1.67% after reaching +10.66%. These are reference-rate movements, not possible trading returns. The April 2022 case switches from a −0.79% move over 20 observations here to a +6.97% move by the eve of the May policy meeting. A conclusion about direction depends strongly on the horizon selected, which is why a five-event directional “strategy” would be unconvincing.

## Claim checking pilot

Five linked SBP statements supplied **15 manually checked fact anchors**, each expanded into one supported and one intentionally contradicted claim. The resulting **30 related examples are not 30 independent research questions**. `claims_pilot.jsonl` exposes the claim, source URL, paragraph number, short human paraphrase, and answer key.

The measured baseline uses TF-IDF to retrieve a fact anchor from within the same statement and simple number and polarity checks to decide supported, contradicted, or abstain. It uses human-prepared evidence anchors, **not full PDF retrieval**, so its **83.3% accuracy (25/30)** and **10.0% abstention (3/30)** cannot be generalized to an unseen document or described as LLM performance. It makes five mistakes or abstentions. For example, it accepts a wrong August inflation claim using 38% instead of 27.4% because the source anchor also mentions the earlier May peak of 38%; numerical presence alone does not establish a claim's date. The full errors and source links are in `claim_pilot_results.json`.

`run_ollama.py` provides an optional **local** model runner for the pilot; no local model was available in this workspace, so no LLM prediction or result is claimed. `evaluate_claims.py` can also score a JSONL file of independently generated answers while checking that each cited fact belongs to the correct dated statement.

## What still separates this from an A+ submission

1. Independently review at least 100 varied claims from substantially more releases, including unsupported claims and date/unit reversals; keep all claims from one statement in the same train or evaluation split. Avoid producing a “100-claim” dataset by duplicating small fact pairs.
2. Run a real model on full primary documents. Verify that quotations are exact substrings of the dated source, measure verdict accuracy, citation quality, coverage, latency, cost and failure types on **unseen documents**, and compare with a basic retrieval baseline. Refuse unsupported answers instead of filling gaps.
3. Add a market-facing output to the verified data: a documented FX/rates risk scenario with the tested horizon and reference/transaction price distinction, or a backtest with actual executable market data and costs if such data become available. A signal is optional; manufacturing one is harmful.
4. Run the opt-in [pilot protocol](PILOT_PROTOCOL.md) with actual people. Report correct answers and time in both PDF and tool conditions, plus errors and limitations. No user-impact claim can precede actual use.

The present package completes an auditable **first research extension** and specifies exactly what remains. It should be represented on a CV by the facts already achieved, with no claim about unrun models, independent benchmarks, investment returns or users.
