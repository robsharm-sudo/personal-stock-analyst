import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import performance_screen as ps  # noqa: E402

SYDNEY = 36000  # UTC+10: local midnight on the 1st is the prior day in UTC


def synthetic(months=73, growth=0.01, dividend_dates=()):
    """Monthly bars from Oct 2020 to Oct 2026, stamped at Sydney midnight, rising `growth` a month."""
    ts, close = [], []
    y, m = 2020, 10
    for i in range(months):
        ts.append(int(datetime(y, m, 1, tzinfo=timezone.utc).timestamp()) - SYDNEY)
        close.append(10 * (1 + growth) ** i)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    divs = {str(i): {"amount": 0.5, "date": int(datetime.fromisoformat(d).replace(tzinfo=timezone.utc).timestamp()) - SYDNEY}
            for i, d in enumerate(dividend_dates)}
    return {"meta": {"gmtoffset": SYDNEY}, "timestamp": ts,
            "indicators": {"quote": [{"close": close}], "adjclose": [{"adjclose": close}]},
            "events": {"dividends": divs}}


class PerformanceScreenTest(unittest.TestCase):
    def test_steady_growth_reads_back_exactly(self):
        raw = synthetic(dividend_dates=["2025-09-15", "2026-03-15", "2026-09-15", "2026-10-02"])
        bars = ps.month_ends(raw, "2026-09-30")
        self.assertEqual(bars[-1][0], "2026-09")  # October excluded; months not shifted by the UTC stamp
        m = ps.metrics(bars, raw, "2026-09-30")
        self.assertAlmostEqual(m["cagr5"], 1.01 ** 12 - 1, places=9)
        self.assertAlmostEqual(m["r1"], 1.01 ** 12 - 1, places=9)
        self.assertAlmostEqual(m["vol"], 0.0, places=9)
        self.assertEqual(m["max_drawdown"], 0.0)
        self.assertEqual((m["years_up"], m["years_counted"]), (5, 5))
        self.assertAlmostEqual(m["div12"], 1.0)  # Mar and Sep 2026 only: Sep 2025 is prior year, Oct 2026 is after
        self.assertFalse(m["div_cut"])

    def test_short_history_has_no_five_year_return(self):
        raw = synthetic(months=24)
        m = ps.metrics(ps.month_ends(raw, "2022-09-30"), raw, "2022-09-30")
        self.assertIsNone(m["cagr5"])

    def test_rank_returns_every_list(self):
        rows = [{"code": c, "company": c, "sector": "x", "cagr5": 0.1, "r1": 0, "r3": 0, "vol": 0.1,
                 "max_drawdown": 0, "years_up": 5, "yield": 0.05, "div12": 1, "price": 20, "div_cut": False}
                for c in ("AAA", "BBB")]
        text, picks = ps.rank(rows, rows[0], "test")
        self.assertEqual(len(picks["risers"]), 2)
        self.assertIn("AAA", text)


if __name__ == "__main__":
    unittest.main()
