# Weekly watch routine

Replaces the newsletter's texting agent. It runs once a week, reads `portfolio.md`, and emails you one summary. It never trades, never writes files and never commits.

## Set it up (once, in the web UI)

Create it at claude.ai/code/routines, not from a chat. Routines made by Claude get no repository or connectors.

- **Repository:** personal-stock-analyst
- **Connectors:** Gmail, plus the market-data connector if you added it as a claude.ai connector
- **Schedule:** Sundays at 6:53 pm Sydney time, which is `CRON_TZ=Australia/Sydney 53 18 * * 0` (off the hour, because on-the-hour starts can run late)
- **Prompt:** paste the block below

## Prompt

```
Weekly watch. Read CLAUDE.md and portfolio.md in this repository and follow CLAUDE.md.

Run python3 tools/restricted.py check on every ticker in portfolio.md. If any is restricted, say so at the top of the email and leave it out of everything below.

For each holding and watchlist company, covering the 7 days ahead and the 7 days just gone:
1. Results and dates: results releases, AGMs, ex-dividend and record dates in the next 7 days. Confirm each date on the company's investor calendar or ASX announcements; a connector calendar is only a lead.
2. Announcements: new ASX announcements in the last 7 days, price-sensitive ones first, two lines each on what changed. Check every figure you quote against the announcement itself and tag [VERIFY] anything you could not open.
3. Price zones: last close against the buy-below, buy-more, first-target and stop levels. List only levels crossed.
4. Dates: rows in "Dates to track" falling in the next 10 days.
5. Thesis reviews due: holdings whose newest file in theses/ is more than 90 days old, or that have none.

Send one email to my own Gmail address with the subject "Weekly watch: <date>". Sections: "Act on" (each item names the skill to run next: /earnings, /thesis-review, /committee or /size), then "For information", then "Quiet" (companies with nothing new). If nothing happened at all, send a one-line quiet email.

Do not write or commit files. Do not log in to any broker or place any order.
```

## What it does not do

- **No texts or calls.** Claude Code cannot send SMS or place phone calls, so the summary arrives by email.
- **Weekly price checks only.** Routines can run hourly at most often. Add a second, weekday routine with only step 3 if weekly is too slow.
- **No reading of investor-relations emails.** Check ASX announcements directly instead. They carry the same releases, and Claude does not need access to your inbox.
