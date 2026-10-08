---
name: committee
description: Test a position before acting on it. A bull and a bear argue separately, then an adjudicator rules on the evidence. Use when the investor is leaning towards buying, adding, trimming or selling.
argument-hint: <LONG|SHORT> <TICKER> "<thesis in 3 to 5 sentences>"
---

Position under test: $ARGUMENTS

The bull and the bear run as separate agents so that neither case is shaped by knowing the other. That independence is the point of this skill, so keep it.

1. Run `python3 tools/restricted.py check <TICKER>` and stop if it is restricted.
2. Build one evidence pack: the latest annual or half-year report, ASX announcements from the last 12 months, the current price and consensus from the connector, and any `reports/` or `theses/` files for this ticker. List each source with its date. Both sides get the same pack.
3. Launch the `bull` and `bear` agents in parallel with the pack and the investor's thesis.
4. Rebuttal round: launch each again with its own case and the other side's three strongest points. One round only.
5. Give the pack, both cases and both rebuttals to the `adjudicator` agent.
6. Have the `fact-checker` agent check the figures the ruling relies on against the announcements and filings. If a ruling rests on a figure that fails, send it back to the adjudicator once.

Deliver, verdict first:
- which side the evidence favours, and why
- the one fact that would flip it
- the payoff if right against the loss if wrong
- what is most likely to make the investor wrong
- both cases and rebuttals at full strength, below the verdict

Done when the adjudicator has ruled on evidence rather than on which side argued better, the fact-check has run, and the bear case appears at full strength. Save to `reports/<TICKER>_committee_<YYYY-MM-DD>.md`.
