"""Performance screen: risers, fallers, steady performers and dividend payers in an ASX index.

  python3 tools/performance_screen.py --universe <constituents.csv> --asof 2026-09-30 [--top 100] --out reports/

constituents.csv needs columns: code, company, sector, market_cap (A$). Restricted tickers are dropped first.
Prices and dividends: Yahoo Finance chart API, monthly bars, adjusted close (dividends reinvested, pre-tax,
franking credits excluded). Benchmarks: the S&P/ASX 200 index itself (^AXJO, price only, so it excludes
dividends) and STW.AX (SPDR S&P/ASX 200 ETF, distributions reinvested) as the like-for-like total-return comparison.
"""
import argparse
import csv
import json
import math
import sys
import time
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import restricted  # noqa: E402

BENCHMARK = "STW"  # total-return proxy: compares like for like with the stocks' adjusted closes
INDEX = "^AXJO"  # the index as quoted: price only
YEARS = 5


def fetch(code, tries=3):
    symbol = code.replace("^", "%5E") if code.startswith("^") else f"{code}.AX"
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
           "?range=7y&interval=1mo&events=div&includeAdjustedClose=true")
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)["chart"]["result"][0]
        except Exception as e:  # network or missing ticker: retry, then give up and record it
            err = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"{code}: {err}")


def month_ends(raw, asof):
    """[(YYYY-MM, close, adjclose)] for complete months up to and including asof's month."""
    ts = raw.get("timestamp") or []
    off = raw["meta"].get("gmtoffset", 0)  # bars are stamped at local midnight; UTC would push them into the prior month
    q = raw["indicators"]["quote"][0]["close"]
    adj = raw["indicators"]["adjclose"][0]["adjclose"]
    out = {}
    for t, c, a in zip(ts, q, adj):
        m = datetime.fromtimestamp(t + off, timezone.utc).strftime("%Y-%m")
        if c is not None and a is not None and m <= asof[:7]:
            out[m] = (c, a)  # later bars in the same month overwrite earlier ones
    return [(m, *out[m]) for m in sorted(out)]


def dividends(raw, start, end):
    divs = (raw.get("events") or {}).get("dividends") or {}
    off = raw["meta"].get("gmtoffset", 0)
    return sum(d["amount"] for d in divs.values()
               if start < datetime.fromtimestamp(d["date"] + off, timezone.utc).date().isoformat() <= end)


def metrics(bars, raw, asof):
    """Return measures from month-end bars ending at asof's month. Needs 13+ bars."""
    adj = [a for _, _, a in bars]
    n = len(adj)
    ret = lambda k: adj[-1] / adj[-1 - 12 * k] - 1 if n > 12 * k else None  # noqa: E731
    r5 = ret(YEARS)
    monthly = [adj[i] / adj[i - 1] - 1 for i in range(max(1, n - 12 * YEARS), n)]
    mean = sum(monthly) / len(monthly)
    vol = math.sqrt(sum((x - mean) ** 2 for x in monthly) / (len(monthly) - 1)) * math.sqrt(12)
    window = adj[-1 - 12 * YEARS:] if n > 12 * YEARS else adj
    peak, mdd = window[0], 0.0
    for a in window:
        peak = max(peak, a)
        mdd = min(mdd, a / peak - 1)
    years_up = [adj[-1 - 12 * k] / adj[-1 - 12 * (k + 1)] - 1 > 0 for k in range(YEARS) if n > 12 * (k + 1)]
    y = int(asof[:4])
    one_year_ago = f"{y - 1}{asof[4:]}"
    two_years_ago = f"{y - 2}{asof[4:]}"
    div12 = dividends(raw, one_year_ago, asof)
    div_prior = dividends(raw, two_years_ago, one_year_ago)
    price = bars[-1][1]
    return {
        "months": n - 1,
        "r1": ret(1), "r3": ret(3), "r5": r5,
        "cagr5": (1 + r5) ** (1 / YEARS) - 1 if r5 is not None else None,
        "vol": vol, "max_drawdown": mdd,
        "years_up": sum(years_up), "years_counted": len(years_up),
        "price": price, "div12": div12, "yield": div12 / price if price else None,
        "div_cut": div_prior > 0 and div12 < 0.8 * div_prior,
    }


def pct(x):
    return "n/a" if x is None else f"{x * 100:.1f}%"


def table(rows, cols):
    head = "| " + " | ".join(c for c, _ in cols) + " |\n|" + "---|" * len(cols) + "\n"
    return head + "".join("| " + " | ".join(f(r) for _, f in cols) + " |\n" for r in rows)


COLS = [
    ("Code", lambda r: r["code"]), ("Company", lambda r: r["company"]), ("Sector", lambda r: r["sector"]),
    ("5-yr a.a. return", lambda r: pct(r["cagr5"])), ("3-yr return", lambda r: pct(r["r3"])),
    ("1-yr return", lambda r: pct(r["r1"])), ("Volatility", lambda r: pct(r["vol"])),
    ("Max fall", lambda r: pct(r["max_drawdown"])), ("Up years of 5", lambda r: str(r["years_up"])),
    ("Yield", lambda r: pct(r["yield"]) + (" ★" if r.get("div_flag") else "")),
]


def rank(rows, bench, label, index=None):
    full = [r for r in rows if r["cagr5"] is not None]
    short = [r for r in rows if r["cagr5"] is None]
    risers = sorted(full, key=lambda r: -r["cagr5"])[:5]
    fallers = sorted(full, key=lambda r: r["cagr5"])[:5]
    steady = sorted([r for r in full if r["years_up"] == YEARS], key=lambda r: r["vol"])[:5]
    payers = sorted([r for r in rows if r["yield"]], key=lambda r: -r["yield"])[:10]
    for r in rows:
        r["div_flag"] = r in payers
    out = [f"## {label}\n",
           f"{len(rows)} companies analysed; {len(full)} with five full years of prices, "
           f"{len(short)} with less (left out of the five-year rankings).\n",
           f"Benchmark, like for like ({BENCHMARK}, S&P/ASX 200 with dividends reinvested): 5-yr {pct(bench['cagr5'])} a year, "
           f"3-yr {pct(bench['r3'])}, 1-yr {pct(bench['r1'])}, volatility {pct(bench['vol'])}, "
           f"max fall {pct(bench['max_drawdown'])}, yield {pct(bench['yield'])}.\n",
           (f"S&P/ASX 200 index as quoted ({INDEX}, price only): 5-yr {pct(index['cagr5'])} a year, "
            f"3-yr {pct(index['r3'])}, 1-yr {pct(index['r1'])}. It excludes dividends, so compare company returns "
            f"with the line above.\n" if index else ""),
           "### Top 5: largest increase in value over five years\n", table(risers, COLS),
           "\n### Bottom 5: largest decrease or smallest increase over five years\n", table(fallers, COLS),
           "\n### Steady performers: positive in each of the last five years, lowest volatility\n",
           table(steady, COLS) if steady else "None met the test.\n",
           "\n### Highest dividend payers (trailing 12-month cash yield; marked ★ above)\n",
           table(payers, COLS[:3] + [("Dividends, 12 months (A$)", lambda r: f"{r['div12']:.3f}"),
                                     ("Price (A$)", lambda r: f"{r['price']:.2f}"),
                                     ("Yield", lambda r: pct(r["yield"])),
                                     ("Fell >20% on prior year", lambda r: "yes" if r["div_cut"] else "no")]),
           "\n"]
    return "".join(out), {"risers": risers, "fallers": fallers, "steady": steady, "payers": payers}


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--universe", required=True)
    p.add_argument("--asof", required=True, help="last complete month end, YYYY-MM-DD")
    p.add_argument("--top", type=int, action="append", default=[], help="also rank the largest N by market value")
    p.add_argument("--out", default="reports")
    a = p.parse_args(argv)

    codes = restricted.load()
    universe = list(csv.DictReader(open(a.universe)))
    kept = [u for u in universe if restricted.norm(u["code"]) not in codes]
    dropped = len(universe) - len(kept)

    bench_raw = fetch(BENCHMARK)
    bench = metrics(month_ends(bench_raw, a.asof), bench_raw, a.asof)
    index_raw = fetch(INDEX)
    index = metrics(month_ends(index_raw, a.asof), index_raw, a.asof)
    rows, failed = [], []
    for u in kept:
        try:
            raw = fetch(u["code"])
            bars = month_ends(raw, a.asof)
            if len(bars) < 13 or bars[-1][0] != a.asof[:7]:
                failed.append(f"{u['code']} (no price for {a.asof[:7]} or under a year of history)")
                continue
            rows.append({**u, **metrics(bars, raw, a.asof), "market_cap": float(u["market_cap"] or 0)})
        except Exception as e:
            failed.append(f"{u['code']} ({e})")
        time.sleep(0.3)

    out = Path(a.out)
    out.mkdir(exist_ok=True)
    stem = f"performance_screen_{a.asof}"
    report = [f"# Performance screen, as at {a.asof}\n",
              f"Prepared {date.today().isoformat()}. Universe: {a.universe} ({len(universe)} companies). "
              f"{dropped} restricted companies were dropped before ranking. "
              f"{len(failed)} could not be priced: {', '.join(failed) or 'none'}.\n",
              "**How to read this.** Returns are total returns from month-end adjusted closes (dividends reinvested, "
              "pre-tax, franking credits excluded). \"Up years\" counts the five 12-month periods ending on the as-at "
              f"month that rose. Volatility is the annualised standard deviation of monthly returns. Yield is cash "
              f"dividends with ex-dates in the 12 months to {a.asof}, over the price at that date. Past returns describe "
              "what happened; they do not predict what comes next.\n",
              "**Limits.** Prices and dividends come from Yahoo Finance's unofficial API, a secondary source: every "
              "figure is `[VERIFY]` until checked against ASX announcements. Dividend amounts may be in the declaring "
              "currency (USD or NZD for some companies) and may include special dividends. The universe is today's "
              "constituents, so companies that left the index are missing and past returns look better than an "
              "index investor received (survivorship bias).\n"]
    text, picks = rank(rows, bench, "S&P/ASX 200 constituents", index)
    report.append(text)
    for n in a.top:
        big = sorted(rows, key=lambda r: -r["market_cap"])[:n]
        text, _ = rank(big, bench, f"Largest {n} by market value", index)
        report.append(text)
    (out / f"{stem}.md").write_text("\n".join(report))
    fields = ["code", "company", "sector", "market_cap", "months", "r1", "r3", "r5", "cagr5", "vol",
              "max_drawdown", "years_up", "price", "div12", "yield", "div_cut"]
    with open(out / f"{stem}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out / stem}.md and .csv: {len(rows)} priced, {dropped} restricted dropped, {len(failed)} failed")


if __name__ == "__main__":
    main()
