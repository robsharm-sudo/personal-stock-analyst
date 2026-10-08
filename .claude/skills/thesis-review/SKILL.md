---
name: thesis-review
description: Quarterly check on a holding. Would the investor buy it today at this price? Use for every holding each quarter, and whenever a price zone in portfolio.md is crossed.
argument-hint: <TICKER>
---

Holding: $ARGUMENTS

Run `python3 tools/restricted.py check <TICKER>` first and stop if it is restricted.

Inputs: the holding's line in `portfolio.md` (cost, weight, zones), the newest thesis in `theses/`, the current price from the connector, and ASX announcements since that thesis was written.

Goal: decide whether the investor would buy this today at this price. People tend to value what they already own more highly than the same thing on offer, so challenge the position rather than protect it.

Cover what has changed since purchase, which assumptions were never tested, and where the position is being held from inertia or attachment rather than evidence.

Have the `fact-checker` agent check figures taken from announcements against the announcements.

Done when there is an updated one-line thesis, a new value range, a conviction score from 1 to 10, and hold, add, trim or exit. Save the new thesis as `theses/<TICKER>_<YYYY-MM-DD>.md` and leave earlier ones untouched.
