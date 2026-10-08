---
name: red-flags
description: Read a company's latest annual or half-year report and recent ASX announcements as an auditor looking for problems. Run before any deeper work on a candidate.
argument-hint: <TICKER> [path or URL to the report]
---

Company: $ARGUMENTS

Run `python3 tools/restricted.py check <TICKER>` first and stop if it is restricted.

Read the latest annual or half-year report (or the file given) and the last six months of ASX announcements as an auditor looking for problems, not an investor looking for reasons to buy.

Goal: every item worth deeper scrutiny across six areas:
1. Revenue quality
2. Margins
3. Working capital
4. Debt and liquidity, including covenant headroom and refinancing dates
5. Accounting changes and restatements
6. Governance: auditor change or modified opinion, key audit matters, going-concern language, director selling (Appendix 3Y notices), and defensive commentary

For each flag give the document, page or note it comes from, why it matters, and the one follow-up question that would resolve it.

Then have the `fact-checker` agent check every flag's figures and page references against the documents. Correct or drop anything that fails.

Done when all six areas are reported, including those where nothing was found, and the fact-check has run. Save to `reports/<TICKER>_red-flags_<YYYY-MM-DD>.md`. If no serious flag remains, suggest `/committee` next.
