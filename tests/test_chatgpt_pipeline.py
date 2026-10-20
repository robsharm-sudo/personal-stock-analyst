import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import chatgpt_pipeline as pipeline


class PipelineTest(unittest.TestCase):
    def test_month_end_handles_year_and_leap_boundaries(self):
        self.assertEqual(pipeline.last_month_end(datetime(2026, 1, 4)), '2025-12-31')
        self.assertEqual(pipeline.last_month_end(datetime(2024, 3, 1)), '2024-02-29')

    def test_unavailable_is_nonzero_and_explicit(self):
        with tempfile.TemporaryDirectory() as d:
            body, status = pipeline.run(Path(d), '2026-09-30')
        self.assertEqual(status, 1)
        self.assertIn('performance unavailable', body)

    def test_fallback_preserves_tables_and_discloses_failure(self):
        with patch.object(pipeline.subprocess, 'run', side_effect=OSError('offline')):
            body, status = pipeline.run(asof='2026-09-30')
        self.assertEqual(status, 0)
        self.assertIn('not refreshed this run', body)
        self.assertIn('offline', body)
        self.assertTrue(pipeline.usable(body))

    def test_no_priced_companies_is_not_usable(self):
        text = '\n'.join(pipeline.HEADINGS) + '\nSTW ^AXJO\n0 companies analysed;'
        self.assertFalse(pipeline.usable(text))

    def test_success_uses_new_report_without_fallback(self):
        import subprocess
        expected = (pipeline.ROOT / 'reports/performance_screen_2026-09-30.md').read_text()

        def generate(command, **kwargs):
            Path(command[-1], 'performance_screen_2026-09-30.md').write_text(expected)
            return subprocess.CompletedProcess(command, 0, '', '')

        with patch.object(pipeline.subprocess, 'run', side_effect=generate):
            body, status = pipeline.run(asof='2026-09-30')
        self.assertEqual(status, 0)
        self.assertEqual(body, expected)


if __name__ == '__main__':
    unittest.main()
