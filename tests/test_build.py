"""Meaningful invariants of the research case. Run: python -m unittest discover -s tests"""
import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build import STAGES, compile_stages, load_fx  # noqa: E402


class CaseIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = compile_stages(load_fx(ROOT / "data" / "fx_reference.csv"))

    def test_no_fx_observations_on_or_before_decision_or_on_or_after_boundary(self):
        for c in self.cases:
            self.assertGreater(len(c['window']), 1)
            self.assertTrue(all(c['date'] < row['date'] < c['end'] for row in c['window']))
            self.assertEqual(c['window'], sorted(c['window'], key=lambda row: row['date']))

    def test_cases_include_appreciation_and_depreciation(self):
        self.assertIn('up', [c['direction'] for c in self.cases])
        self.assertIn('down', [c['direction'] for c in self.cases])

    def test_interim_movement_can_be_bigger_than_endpoint(self):
        august = next(c for c in self.cases if c['id'] == 'aug22')
        self.assertGreater(august['peak_up_pct'], august['change_pct'] + 8)
        self.assertEqual(august['peak_up_date'], '2022-09-22')

    def test_every_claim_has_an_identified_error_and_a_primary_source(self):
        for c in self.cases:
            self.assertEqual(len(c['claims']), 2)
            self.assertIn(c['false_index'], (0, 1))
            self.assertTrue(c['source'].startswith('https://www.sbp.org.pk/'))
            self.assertIn('paragraph', c['locator'])

    def test_no_duplicate_fx_observations(self):
        with self.assertRaises(ValueError):
            load_fx(self._duplicate_csv())

    @classmethod
    def _duplicate_csv(cls):
        # Existing path uses a temporary file; cleaned in tearDownClass.
        cls.temp = ROOT / 'tests' / 'duplicate_temp.csv'
        with cls.temp.open('w', newline='') as f:
            w=csv.writer(f);w.writerow(['observation_date','pkr_per_usd']);w.writerow(['2022-04-08',187]);w.writerow(['2022-04-08',188])
        return cls.temp

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'temp'):
            cls.temp.unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
