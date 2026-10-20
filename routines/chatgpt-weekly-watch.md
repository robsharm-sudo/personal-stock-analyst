# Standalone ChatGPT pipeline: ASX 200 performance

This is a discrete, repository-backed ChatGPT/Codex pipeline with shell access. Invoke it on its own when the user requests ASX 200 performance tables; it does not depend on the weekly watch, portfolio, Gmail, FMP or Claude. It does not create a scheduled task or change the Claude routine. A ChatGPT task without repository and Python access cannot run this pipeline directly.

**Entry point:** `python3 tools/chatgpt_pipeline.py`

**Output:** Markdown on stdout, ready to include in the ChatGPT response. Diagnostics go to stderr. Temporary generated files are removed after reading; the checkout is unchanged.

## Pipeline prompt

Run `python3 tools/chatgpt_pipeline.py` from the repository root and include its Markdown output in the final ChatGPT response. This entry point calculates the Sydney month end, selects the latest constituent snapshot, runs the generator in temporary storage, and falls back to a clearly labelled saved report on failure. Exit status 1 means no usable report was available; status 0 may include a labelled fallback and does not imply live refresh succeeded.

Read `CLAUDE.md` for the repository's source and restricted-company rules. Work from `/workspace/personal-stock-analyst` in the cloud environment, or the repository root in another runner.

Include an **ASX 200 performance** section in every weekly output, even when the portfolio is quiet or empty. These descriptive tables do not require FMP credentials. Restricted companies may appear only with their `(R)` markers, never as recommendations or action items.

1. Calculate the last completed calendar month end in `Australia/Sydney`. Do not use the current incomplete month or describe these figures as weekly returns.
2. Select the most recent dated `reports/asx200_constituents_*.csv`. Disclose the constituent snapshot's filename and date; it is not necessarily current index membership.
3. Create a fresh temporary output directory outside the checkout and run:

   ```sh
   python3 tools/performance_screen.py \
     --universe <selected-constituents.csv> \
     --asof <last-complete-month-end-YYYY-MM-DD> \
     --out <temporary-output-directory>
   ```

   Python 3 with its standard library is sufficient. HTTPS access to `query1.finance.yahoo.com` is required. Do not overwrite saved reports. Only use `--verified` when a checked-dividend file explicitly matches the reporting period.

4. Read the generated Markdown. Confirm that companies were priced and that the requested as-at date is present. Include all four tables inline in the final ChatGPT output:
   - Top 5 risers.
   - Bottom 5 fallers.
   - Steady performers, or the explicit statement that none qualify.
   - Highest dividend payers.

   Preserve both benchmark lines (STW with dividends reinvested and `^AXJO` price return), restricted-company markers, dates, coverage/failures and verification caveats. Clearly label partial coverage; do not present a subset as a complete index screen. Do not replace the tables with a file link or summary sentence.
5. If generation fails or no companies are priced, use the latest usable saved `reports/performance_screen_*.md`. Label it **Saved report — not refreshed this run**, include its actual as-at and preparation dates, and explain the refresh failure. Preserve its tables and caveats. Never present saved numbers as newly fetched data. If no usable report exists, include **ASX 200 performance unavailable** with the specific reason.
6. Return the tables directly to the user. If invoked as part of a larger report, continue that report afterwards. A quiet portfolio must not suppress this output. Before returning, check for all four tables or explicit no-qualifiers/unavailable explanations.

Do not change the Claude routine, send email, modify a schedule, write repository files or commit as part of this reporting step.

## Validation and activation

Run `python3 -m unittest discover -s tests` from the repository root. Tests cover the calculation and restriction logic; they do not prove live data access or scheduled delivery.

The pipeline owner must attach this step to the actual ChatGPT runner. Editing this file alone does not activate a scheduled task. In cloud environment settings, allow `query1.finance.yahoo.com`; a saved network draft must be applied before live access can be validated.
