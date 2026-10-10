"""Broad SBP statement-date FX-risk audit with a calendar-year holdout.

All 2021–2025 statement dates come from the SBP statements catalogue. The
five-case educational game and earlier exploratory study influenced this
question, so 2021–2024 is DEVELOPMENT, not independent discovery. 2025 is
reserved for an untouched temporal check. The source is a historical average
FX reference, NOT an executable trade quote or a verified release-time feed.

Before first run: primary outcome = largest absolute percent change from the
first post-statement FX observation in the next 20 observations. Comparison =
same-year reference-day controls at least 5 calendar days from any statement,
with no statement during the following 20 observations. Aggregate at the YEAR
level. Secondary outcome = absolute 20-observation endpoint change. Report
year 2025 separately regardless of outcome; no post-hoc threshold changes.
"""
import json
from collections import defaultdict
from datetime import date
from itertools import product
from pathlib import Path
from statistics import mean, median

from event_risk import load_fx, window_after

ROOT=Path(__file__).resolve().parent
CATALOGUE="https://www.sbp.org.pk/our-operations/publications/monetary-policy-statements/501"
STATEMENTS={
2021:["01-22","03-19","05-28","07-27","09-20","11-19","12-14"],
2022:["01-24","03-08","04-07","05-23","07-07","08-22","10-10","11-25"],
2023:["01-23","03-02","04-04","06-12","06-26","07-31","09-14","10-30","12-12"],
2024:["01-29","03-18","04-29","06-10","07-29","09-12","11-04","12-16"],
2025:["01-27","03-10","05-05","06-16","07-30","09-15","10-27","12-15"],
}

def sign_flip_test(differences):
    """Exact two-sided sign-flip reference over year-level paired differences.

    Exchangeable year-level signs under a zero-effect null are an assumption,
    not a claim that meeting dates or overlapping daily windows are randomized.
    """
    observed=abs(mean(differences))
    null=[abs(mean(sign*d for sign,d in zip(signs,differences)))
          for signs in product((-1,1),repeat=len(differences))]
    return {"two_sided_p":sum(v>=observed-1e-12 for v in null)/len(null),
            "n_years":len(differences),"n_permutations":len(null)}


def analyze(rows,horizon=20):
    if horizon not in (5,10,20):
        raise ValueError('Allowed sensitivity horizons: 5, 10, 20 observations')
    days=sorted(date.fromisoformat(f"{year}-{md}") for year,v in STATEMENTS.items() for md in v)
    grouped=defaultdict(list)
    for meeting in days:
        obs=window_after(rows,meeting.isoformat(),horizon)
        if obs is None:
            raise ValueError(f"Policy statement has no {horizon}-observation window: {meeting}")
        grouped[meeting.year].append(obs)
    controls=defaultdict(list)
    for day_str,_ in rows:
        day=date.fromisoformat(day_str)
        if day.year not in STATEMENTS or any(abs((day-m).days)<=5 for m in days):
            continue
        obs=window_after(rows,day_str,horizon)
        if obs is None:continue
        last=date.fromisoformat(obs['end'])
        if any(day<m<=last for m in days):continue
        controls[day.year].append(obs)
    by_year={}
    for y in STATEMENTS:
        events=grouped[y]; c=controls[y]
        if not c:raise ValueError(f"No eligible nonmeeting controls in {y}")
        by_year[str(y)]={
            "n_statements":len(events),"n_control_anchors":len(c),
            "mean_statement_max_excursion_pct":mean(x['max_abs_excursion_pct'] for x in events),
            "mean_control_max_excursion_pct":mean(x['max_abs_excursion_pct'] for x in c),
            "statement_minus_control_pp":mean(x['max_abs_excursion_pct'] for x in events)-mean(x['max_abs_excursion_pct'] for x in c),
            "median_statement_max_excursion_pct":median(x['max_abs_excursion_pct'] for x in events),
            "median_control_max_excursion_pct":median(x['max_abs_excursion_pct'] for x in c),
            "mean_statement_abs_endpoint_pct":mean(abs(x['endpoint_pct']) for x in events),
            "mean_control_abs_endpoint_pct":mean(abs(x['endpoint_pct']) for x in c),
            "statement_outcomes":events,
        }
    dev=[by_year[str(y)]['statement_minus_control_pp'] for y in range(2021,2025)]
    all_years=dev+[by_year['2025']['statement_minus_control_pp']]
    return {"source_catalogue":CATALOGUE,"horizon_observations":horizon,
            "development_years":[2021,2022,2023,2024],"temporal_holdout_year":2025,
            "statement_date_count":len(days),"year_results":by_year,
            "development_mean_of_year_differences_pp":mean(dev),
            "holdout_2025_difference_pp":by_year['2025']['statement_minus_control_pp'],
            "development_year_sign_flip":sign_flip_test(dev),
            "all_year_sign_flip":sign_flip_test(all_years),
            "holdout_direction_matches_development":(mean(dev)>0)==(by_year['2025']['statement_minus_control_pp']>0),
            "limitations":["The study question was motivated by examining the five earlier case-study windows; development years are not preregistered.",
                           "Control dates in a year have overlapping 20-observation windows and are not independent trials.",
                           "Policy meetings are scheduled in response to economic conditions; this is not a causal estimate.",
                           "FX series consists of retrospective bank-average reference observations, not tradable bid/ask quotes or verified real-time data.",
                           "Calendar 2025 is a single temporal holdout year; it cannot validate a trading strategy.",
                           "Year-level sign-flip reference needs exchangeable signs under a zero-effect null; five calendar years do not establish that assumption or test 2025 on its own.",
                           "A non-significant p-value is not evidence of equivalence or zero effect."]}

if __name__=='__main__':
    rows=load_fx(ROOT.parent/'data'/'fx_full.csv')
    out=analyze(rows)
    out['horizon_sensitivity']={str(h):{
        'development_mean_of_year_differences_pp':v['development_mean_of_year_differences_pp'],
        'holdout_2025_difference_pp':v['holdout_2025_difference_pp'],
        'development_year_sign_flip':v['development_year_sign_flip'],
        'all_year_sign_flip':v['all_year_sign_flip'],
        'year_results':{y:{k:yr[k] for k in ('n_statements','n_control_anchors','mean_statement_max_excursion_pct','mean_control_max_excursion_pct','statement_minus_control_pp')}
                        for y,yr in v['year_results'].items()}}
        for h,v in ((h,analyze(rows,h)) for h in (5,10,20))}
    path=ROOT/'full_event_study_results.json';path.write_text(json.dumps(out,indent=2)+'\n')
    for y,v in out['year_results'].items():
        print(f"{y}: {v['n_statements']} meetings, {v['n_control_anchors']} controls, difference {v['statement_minus_control_pp']:+.2f} pp")
    print('development average year difference',round(out['development_mean_of_year_differences_pp'],2),'pp; 2025 holdout',round(out['holdout_2025_difference_pp'],2),'pp')
    for h,v in out['horizon_sensitivity'].items():
        print(h,'observations: dev',round(v['development_mean_of_year_differences_pp'],3),'pp, 2025',round(v['holdout_2025_difference_pp'],3),'pp; exact year sign-flip p (all years)',v['all_year_sign_flip']['two_sided_p'])
