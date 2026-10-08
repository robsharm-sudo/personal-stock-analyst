# Personal stock analyst

A Claude Code kit for researching ASX shares from primary sources. It finds candidates in the S&P/ASX 100 or 200, tests them, values them and sizes a position. You make every decision. This is analysis, not advice.

## What it does

| Step | Command | What you get |
|---|---|---|
| Find | `/screen value ASX200 3y` (or `ASX100`) | The top 5 risers and bottom 5 over five years, the steady performers and the highest dividend payers, then the 10 strongest candidates and 3 to avoid. Each is measured against the index |
| Test | `/red-flags XYZ` | An auditor's reading of the latest report and six months of ASX announcements |
| Argue | `/committee LONG XYZ "thesis"` | Bull and bear cases argued by separate agents, then a ruling on the evidence |
| Value | `/dcf XYZ` | A bear, base and bull valuation in an Excel workbook you can change cell by cell |
| Size | `/size XYZ conviction=medium horizon=12 upside=25 stop=10` | One position size, checked four ways |
| Results day | `/earnings XYZ FY26` | Yes or no: does the result change the thesis? |
| Each quarter | `/thesis-review XYZ` | Would you buy it today, at this price? |

For a new idea, run them in that order. Stop at the first step that gives you a reason not to proceed.

A weekly routine emails you on Sunday evenings. It covers results and dividend dates in the week ahead, new ASX announcements, price levels crossed and theses due for review. See `routines/weekly-watch.md`.

## Safeguards

- **Restricted list.** `restricted.txt` holds the companies you supervise at work. A hook blocks any prompt that names one in capitals, every skill checks its ticker before starting, and screens drop restricted names before ranking. If the file goes missing, prompts are blocked until it is restored.
- **Fact-check.** Before a report is final, a separate agent checks every figure taken from an ASX announcement or filing against the document itself.
- **Tags.** Each figure is marked `[E]` (as printed), `[D]` (calculated, with the working shown), `[I]` (inferred) or `[VERIFY]` (not checked against a primary source).
- **No broker access and no payments.** The kit reads public sources only.
- **Keep this repo private.** Your holdings sit in `portfolio.md`.

## Set up

1. Fill in `portfolio.md`.
2. Check `restricted.txt` against your employer's restricted list and add anything missing.
3. Connect market data (see below). The performance lists and price levels work without a key. Screening on fundamentals and the DCF need the FMP key. The other skills work from ASX announcements and company reports.
4. Create the weekly routine from `routines/weekly-watch.md`.
5. Check the guard works: `python3 -m unittest discover -s tests`.

## Market data

Two sources, used for different jobs.

- **Yahoo Finance (no key).** `tools/performance_screen.py` uses it for monthly prices and dividends: the risers, fallers, steady performers and dividend payers in the index, measured against the S&P/ASX 200 (`^AXJO`, price only) and STW (the same index with dividends reinvested). Its API is unofficial and secondary, so every figure is `[VERIFY]` until checked against ASX announcements, and it can change without notice.
- **Financial Modeling Prep (paid key).** Screening on P/E, consensus forecasts and debt, and the DCF inputs, need fundamentals. `.mcp.json` connects FMP's MCP server; set `FMP_API_KEY` in your environment (in a cloud environment's settings, or your shell locally) and never commit the key. The server answered at that address on 8 October 2026. Check its price and its ASX coverage on FMP's pricing page before you subscribe; the newsletter's figure of about US$15 a month is unverified.

Without the key, `/screen` runs the performance lists from Yahoo and stops before the fundamentals table, rather than guessing.

## Limits

- Models can state wrong numbers confidently. Check anything tagged `[VERIFY]`, and any figure you would act on, against the filing first.
- Nothing here shows the kit beats the index. It makes the process more disciplined and catches errors; it does not predict prices.
- Claude Code cannot send texts or place calls, so alerts arrive by email.
- Adapted from "Build Your Own Stock Analyst With ChatGPT and Instinct" (The AI Corner, 7 October 2026). The prompts were rewritten for Claude Code and ASX sources; position sizing and moat ideas follow the original.
