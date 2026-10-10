"""Research safeguards: event timing, controls and citation validation."""
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "research"))
from event_risk import EVENTS, analyze, load_fx, window_after  # noqa: E402
from claims_pilot import pilot_records  # noqa: E402
from evaluate_claims import evaluate  # noqa: E402
from full_event_study import STATEMENTS, analyze as analyze_full, sign_flip_test  # noqa: E402


class ResearchIntegrity(unittest.TestCase):
    def test_event_windows_start_strictly_after_source_statement(self):
        fx=load_fx(ROOT / "data" / "fx_full.csv")
        for date,url in EVENTS:
            r=window_after(fx,date)
            self.assertIsNotNone(r)
            self.assertGreater(r['start'],date)
            self.assertTrue(url.startswith('https://www.sbp.org.pk/'))

    def test_research_is_marked_exploratory_and_deterministic(self):
        fx=load_fx(ROOT / "data" / "fx_full.csv")
        first=analyze(fx);second=analyze(fx)
        self.assertEqual(first['mean_control_draw_max_abs_pct'],second['mean_control_draw_max_abs_pct'])
        self.assertIn('Exploratory',first['design']['design_status'])
        self.assertEqual(first['design']['event_count'],5)

    def test_pilot_labels_are_related_pairs_not_independent_trials(self):
        rows=pilot_records()
        self.assertEqual(len(rows),30)
        self.assertEqual(len({r['fact_id'] for r in rows}),15)
        self.assertEqual(len({r['document_date'] for r in rows}),5)
        self.assertEqual({r['gold'] for r in rows},{'supported','contradicted'})

    def test_wrong_document_evidence_fails_grounded_score(self):
        rows=pilot_records()[:2]
        p=[{'id':r['id'],'verdict':r['gold'],'evidence_fact_id':None} for r in rows]
        result=evaluate(rows,p)
        self.assertEqual(result['accuracy'],1)
        self.assertEqual(result['accuracy_with_correct_fact_anchor'],0)

    def test_complete_policy_date_audit_and_separate_temporal_holdout(self):
        self.assertEqual(sum(map(len, STATEMENTS.values())),40)
        self.assertEqual(len({f'{y}-{md}' for y, dates in STATEMENTS.items() for md in dates}),40)
        result=analyze_full(load_fx(ROOT / 'data' / 'fx_full.csv'))
        self.assertEqual(result['development_years'],[2021,2022,2023,2024])
        self.assertEqual(result['temporal_holdout_year'],2025)
        self.assertEqual(result['year_results']['2025']['n_statements'],8)
        self.assertAlmostEqual(result['holdout_2025_difference_pp'],0.05197765307818572)
        for year, data in result['year_results'].items():
            for event in data['statement_outcomes']:
                self.assertGreater(event['start'],event['anchor'])
                self.assertEqual(event['anchor'][:4],year)

    def test_exact_sign_flip_and_horizons_are_computed_from_distinct_windows(self):
        self.assertEqual(sign_flip_test([2.0,-1.0])['n_permutations'],4)
        self.assertEqual(sign_flip_test([2.0,-1.0])['two_sided_p'],1.0)
        fx=load_fx(ROOT / 'data' / 'fx_full.csv')
        outcomes={h:analyze_full(fx,h) for h in (5,10,20)}
        for h,r in outcomes.items():
            self.assertEqual(r['horizon_observations'],h)
            self.assertEqual(r['statement_date_count'],40)
            self.assertEqual(r['all_year_sign_flip']['n_permutations'],32)
            self.assertEqual(r['development_year_sign_flip']['n_permutations'],16)
        self.assertNotEqual(outcomes[5]['holdout_2025_difference_pp'],outcomes[20]['holdout_2025_difference_pp'])
        with self.assertRaises(ValueError):
            analyze_full(fx,3)


if __name__=='__main__':
    unittest.main()
