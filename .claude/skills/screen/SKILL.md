---
name: screen
description: Shortlist the strongest candidates in the S&P/ASX 100 or 200 (or a sector within it), measured against the index, plus the ones to avoid. Use when the investor asks to find, screen, select or shortlist stocks.
argument-hint: <growth|value|income|momentum> <ASX100|ASX200> [sector] <horizon>
---

Screen: $ARGUMENTS

Goal: the 10 strongest candidates for this style, sector and horizon, plus the 3 to avoid. If style, sector or horizon is missing, assume growth, the S&P/ASX 200 and three years, and say so in one line.

Universe: the current constituents of the index named (S&P/ASX 100 or S&P/ASX 200; "top 100" and "top 200" mean these), or the named sector within it. Take the constituent list from the market-data connector, or failing that a dated public list (such as Wikipedia's S&P/ASX 200 table), and print its source, as-at date and count, tagged `[VERIFY]` if it is not from the connector or the index provider. Never fill gaps in membership from memory. Companies that cannot be priced are often takeovers since the list date: name them. For the whole index, rank across all sectors and show each candidate's GICS sector.

Before ranking, pass every ticker through `python3 tools/restricted.py filter ...` and work only with what it returns. Report how many were dropped, never which. Price every name at the same as-at date and print that date.

Performance lists: save the constituent list as `reports/<index>_constituents_<source>.csv` (columns code, company, sector, market_cap), then run `python3 tools/performance_screen.py --universe <that csv> --asof <last complete month end> --top 100 --out reports`. It drops restricted companies and writes the top 5 risers and bottom 5 over five years, the steady performers (up in each of the last five years, ranked by lowest volatility), and the 10 highest dividend payers, with each measured against the index. Put its tables first in the reply, unchanged. Then have the `fact-checker` agent check each listed dividend payer's last 12 months of dividends against the company's ASX dividend announcements (Appendix 3A.1), and add franking levels from those announcements.

The fundamentals below need the market-data connector. If it is not connected, deliver the performance lists, say the fundamentals table needs `FMP_API_KEY`, and stop there rather than estimate.

Measure each candidate against the index as well as its sector. Print the index's own median P/E, dividend yield and 12-month total return at the same as-at date, so every comparison has its benchmark beside it.

Deliver one table: ticker, GICS sector, market value, P/E against the sector median and the index median, 12-month total return against the index, 5-year revenue CAGR and forward consensus growth, net debt to EBITDA, moat (weak, moderate or strong, with a one-line reason), a bull and a bear 12-month value with the key assumption behind each, and risk on a 1 to 10 scale.

Done when the top 3 each have a one-sentence thesis, the 3 to avoid each have a specific reason, and every figure carries its tag and date. Close with the next step for each top-3 name: `/red-flags <TICKER>`.
