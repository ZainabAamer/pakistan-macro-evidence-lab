"""Exploratory descriptive event risk audit, not a tradable signal.

This five-event comparison was designed after the case dates and some FX paths
had already been viewed. It is therefore NOT preregistered or out of sample.
The exploratory question asks whether the maximum absolute USD/PKR reference
excursion over the next 20 observations exceeds matched-year placebo dates.

Usage: python research/event_risk.py --fx data/fx_full.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from bisect import bisect_right
from datetime import date
from pathlib import Path
from statistics import mean, median

EVENTS = [
    ("2022-04-07", "https://www.sbp.org.pk/assets/document/publications/MPS-Apr-2022-Eng.pdf"),
    ("2022-05-23", "https://www.sbp.org.pk/assets/document/publications/MPS-May-2022-Eng.pdf"),
    ("2022-07-07", "https://www.sbp.org.pk/assets/document/publications/MPS-Jul-2022-Eng.pdf"),
    ("2022-08-22", "https://www.sbp.org.pk/assets/document/publications/MPS-Aug-2022-Eng.pdf"),
    ("2023-09-14", "https://www.sbp.org.pk/assets/document/publications/MPS-Sep-2023-Eng.pdf"),
]
ALL_POLICY_DATES_2022_2023 = [
    # Official SBP statement catalogue. Used to avoid contaminating placebo
    # windows with OTHER SBP decisions absent from the five-case simulation.
    "2022-01-24", "2022-03-08", "2022-04-07", "2022-05-23", "2022-07-07",
    "2022-08-22", "2022-10-10", "2022-11-25", "2023-01-23", "2023-03-02",
    "2023-04-04", "2023-06-12", "2023-06-26", "2023-07-31", "2023-09-14",
    "2023-10-30", "2023-12-12",
]
DATE_CATALOGUE_SOURCE = "https://www.sbp.org.pk/our-operations/publications/monetary-policy-statements/501"
HORIZON = 20
EXCLUSION_DAYS = 7
SEED = 501613
N_SAMPLES = 10000


def load_fx(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = [(r["observation_date"], float(r["pkr_per_usd"])) for r in csv.DictReader(f)]
    rows.sort()
    if any(p <= 0 for _, p in rows) or len({d for d, _ in rows}) != len(rows):
        raise ValueError("FX rates must be positive and have unique observation dates")
    return rows


def window_after(rows, anchor: str, horizon: int = HORIZON):
    dates = [d for d, _ in rows]
    begin = bisect_right(dates, anchor)
    # Include first strictly POST-announcement observation and 19 following.
    w = rows[begin:begin + horizon]
    if len(w) != horizon or (date.fromisoformat(w[0][0]) - date.fromisoformat(anchor)).days > 7:
        return None
    if any((date.fromisoformat(b[0]) - date.fromisoformat(a[0])).days > 7
           for a, b in zip(w, w[1:])):
        return None
    start = w[0][1]
    moves = [(p / start - 1) * 100 for _, p in w]
    return {"anchor": anchor, "start": w[0][0], "end": w[-1][0],
            "start_rate": start, "end_rate": w[-1][1],
            "endpoint_pct": moves[-1], "max_abs_excursion_pct": max(map(abs, moves)),
            "max_up_pct": max(moves), "max_down_pct": min(moves)}


def analyze(rows):
    events = []
    for when, source in EVENTS:
        w = window_after(rows, when)
        if w is None:
            raise ValueError(f"Missing valid FX window for event {when}")
        events.append({**w, "source": source})
    event_days = [date.fromisoformat(d) for d in ALL_POLICY_DATES_2022_2023]
    controls = {}
    for year in sorted({e["anchor"][:4] for e in events}):
        possible = []
        for d, _ in rows:
            day = date.fromisoformat(d)
            if day.year != int(year) or any(abs((day - event_day).days) <= EXCLUSION_DAYS for event_day in event_days):
                continue
            w = window_after(rows, d)
            # The full control horizon must also end BEFORE the next MPC date.
            # Otherwise the control observation is itself exposed to a decision.
            crosses_policy = w is not None and any(day < event_day <= date.fromisoformat(w["end"])
                                                     for event_day in event_days)
            if w is not None and w["end"][:4] == year and not crosses_policy:
                possible.append(w)
        if not possible:
            raise ValueError(f"No control dates for {year}")
        controls[year] = possible
    observed = mean(e["max_abs_excursion_pct"] for e in events)
    rng = random.Random(SEED)
    draws = [mean(rng.choice(controls[e["anchor"][:4]])["max_abs_excursion_pct"] for e in events)
             for _ in range(N_SAMPLES)]
    result = {"design": {
        "research_question": "Are 20-observation FX reference-rate excursions larger after five selected SBP statements than at same-year non-event dates?",
        "design_status": "Exploratory: designed after viewing event dates and some historical FX movements. Not preregistered, confirmatory, or out of sample.",
        "primary_metric": "Mean of the maximum absolute percentage move relative to the first post-event observation",
        "event_count": len(EVENTS), "horizon_observations": HORIZON,
        "policy_date_catalogue": DATE_CATALOGUE_SOURCE,
        "placebo_year_match": True, "exclude_within_calendar_days": EXCLUSION_DAYS,
        "random_seed": SEED, "placebo_resamples_with_replacement": N_SAMPLES,
        "caution": "Retrospective observational reference-rate comparison, not causal inference or an executable trading backtest. Five hand-selected events; periods selected for the case study."},
        "events": events,
        "control_count_by_year": {y: len(v) for y, v in controls.items()},
        "mean_event_max_abs_pct": observed,
        "mean_control_draw_max_abs_pct": mean(draws),
        "event_minus_mean_control_pct_points": observed - mean(draws),
        "fraction_control_draws_at_least_event": sum(x >= observed for x in draws) / N_SAMPLES,
        "mean_event_abs_endpoint_pct": mean(abs(e["endpoint_pct"]) for e in events),
        "median_event_max_abs_pct": median(e["max_abs_excursion_pct"] for e in events),
        "interpretation": "The control-draw fraction is descriptive and not a valid hypothesis-test p-value: case-study events were selected in hindsight, the samples and 20-observation paths can overlap, and other events also affect FX. No signal, causality, or skill claim follows."}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fx", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "fx_full.csv")
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "event_risk_results.json")
    args = parser.parse_args()
    result = analyze(load_fx(args.fx))
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"events {len(EVENTS)}, mean max excursion {result['mean_event_max_abs_pct']:.2f}%, "
          f"controls {result['mean_control_draw_max_abs_pct']:.2f}%, "
          f"control draw fraction >= event {result['fraction_control_draws_at_least_event']:.3f}")


if __name__ == "__main__":
    main()
