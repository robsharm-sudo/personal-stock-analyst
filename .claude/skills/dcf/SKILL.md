---
name: dcf
description: Build a bear, base and bull discounted cash flow valuation in an Excel workbook, with every assumption in its own labelled cell. Use when valuation is the deciding question.
argument-hint: <TICKER>
---

Company: $ARGUMENTS

Run `python3 tools/restricted.py check <TICKER>` first and stop if it is restricted.

Goal: a bear, base and bull DCF in `reports/<TICKER>_dcf_<YYYY-MM-DD>.xlsx` that the investor can audit and change cell by cell. A valuation in a chat reply can only be trusted or ignored, so the workbook is the deliverable. Use the xlsx skill if it is available, otherwise openpyxl.

- **Inputs sheet:** one labelled cell per assumption per scenario: five-year revenue growth, EBIT margin path, tax rate, capex and working capital as a percentage of revenue, terminal growth, WACC and its components (risk-free rate from the Australian 10-year government bond, equity risk premium, beta, cost of debt, weights), net debt and shares on issue. Put the source, date and tag in the next column.
- **Model sheet:** formulas only, referencing Inputs. Implied value per share for each scenario, and the gap to the current price.
- **Sensitivity sheet:** base-case value per share for WACC ±1% and terminal growth ±0.5%, as a 5 × 5 grid of formulas.

openpyxl writes formulas but does not calculate them. Recalculate with LibreOffice (`soffice --headless --convert-to xlsx`) and read the values back. If LibreOffice is unavailable, compute the three values independently in Python and compare.

Done when:
- raising WACC by 1% in Inputs lowers every implied value (test it once, then restore it)
- terminal growth is below WACC in every scenario
- every input is sourced and tagged, and the `fact-checker` agent has checked the inputs taken from filings
- the chat reply gives the three values, the gap to price and the two assumptions the value is most sensitive to, and the workbook has been sent to the investor
