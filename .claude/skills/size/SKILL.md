---
name: size
description: Size a position four ways before the investor places a trade. Use right before any buy or add, including ones the investor feels sure about.
argument-hint: <TICKER> conviction=<high|medium|low> horizon=<months> upside=<%> stop=<%> [win=<probability>]
---

Position: $ARGUMENTS

Run `python3 tools/restricted.py check <TICKER>` first and stop if it is restricted. Take portfolio value and current holdings from `portfolio.md`. If the win probability is missing, ask for it, because it drives the Kelly result; if the investor declines, assume 50% and say so.

Goal: the right position size, checked four ways. Do the arithmetic in Python and show it.
1. **Half-Kelly:** with b = upside ÷ stop and p = win probability, full Kelly f = p − (1 − p) ÷ b; use half of it, and zero if it is negative.
2. **Loss limit:** the size at which hitting the stop costs no more than the investor's maximum loss per trade (1% of the portfolio unless `portfolio.md` says otherwise).
3. **Overlap:** reduce the size for sector and factor overlap with current holdings, and say by how much and why.
4. **Conviction band:** high 3–7%, medium 1–3%, low 0.5–1% of the portfolio.

Deliver one recommended size as a percentage and in dollars, the entry plan, the stop, the first profit target, and the four results side by side. If the four disagree widely, say so: the spread shows how uncertain the trade is.

Done when every assumption about win probability and the loss limit is stated and the arithmetic can be re-run from what is shown.
