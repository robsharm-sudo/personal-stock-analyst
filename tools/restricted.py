"""Restricted-list guard: companies the investor must not research or trade.

  python3 tools/restricted.py check CBA XYZ   exit 1 and name any restricted ticker
  python3 tools/restricted.py filter A B C    print only the unrestricted tickers
  python3 tools/restricted.py hook            UserPromptSubmit hook: block a prompt naming a restricted ticker
"""
import json
import re
import sys
from pathlib import Path

LIST = Path(__file__).resolve().parent.parent / "restricted.txt"


def norm(ticker):
    t = ticker.strip().upper()
    t = t.removeprefix("ASX:").removesuffix(".AX").removesuffix(".ASX")
    return t


def load(path=None):
    text = (path or LIST).read_text()
    return {norm(line.split("#", 1)[0]) for line in text.splitlines() if line.split("#", 1)[0].strip()}


def named_in(text, codes):
    # ponytail: whole-word UPPERCASE match only, so "Ben" or "amp" in prose don't block a prompt.
    # Lower-case tickers slip past the hook; the skills' own `check` step uppercases and catches them.
    return sorted({w for w in re.findall(r"\b[A-Z0-9]{2,6}\b", text) if w in codes})


def main(argv):
    cmd, args = (argv[0], argv[1:]) if argv else ("", [])
    if cmd == "hook":
        try:
            codes = load()
        except OSError:
            print("restricted.txt is missing, so prompts are blocked until it is restored.", file=sys.stderr)
            return 2
        hits = named_in(json.load(sys.stdin).get("prompt", ""), codes)
        if hits:
            print(f"Blocked: {', '.join(hits)} is on your restricted list (restricted.txt). "
                  "This kit does not research companies on your restricted list.", file=sys.stderr)
            return 2
        return 0
    codes = load()
    tickers = [norm(a) for a in args]
    if cmd == "check":
        hits = [t for t in tickers if t in codes]
        print("RESTRICTED: " + ", ".join(hits) if hits else "clear")
        return 1 if hits else 0
    if cmd == "filter":
        kept = [t for t in tickers if t not in codes]
        print(" ".join(kept))
        print(f"dropped {len(tickers) - len(kept)} restricted", file=sys.stderr)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
