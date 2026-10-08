---
name: earnings
description: Decide, within a day of a results release, whether it changes the thesis on a holding or watchlist company.
argument-hint: <TICKER> [period, e.g. FY26 or 1H26]
---

Company and period: $ARGUMENTS

Run `python3 tools/restricted.py check <TICKER>` first and stop if it is restricted.

Goal: tell the investor whether this result changes the thesis in the newest `theses/<TICKER>_*.md` file (or the reason in `portfolio.md` if there is no thesis file). Answer yes or no in the first line.

Read the results announcement, the Appendix 4D or 4E, the investor presentation, and the call transcript or webcast notes if published.

Cover: results against consensus and the prior period, guidance changes, segment moves, what management emphasised that was not in the release, analyst questions that got thin answers, and the change in tone from last period.

Then give what a careful short-seller would take from this result, three things to track over the next 90 days, and add, hold, trim or exit with the reasoning.

Have the `fact-checker` agent check every figure taken from the announcement against the announcement itself before finishing.

Done when the first line answers the thesis question and the fact-check has run. Save to `reports/<TICKER>_earnings_<period>_<YYYY-MM-DD>.md`.
