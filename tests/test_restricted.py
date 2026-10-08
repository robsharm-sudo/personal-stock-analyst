import io
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import restricted  # noqa: E402

SCRIPT = [sys.executable, str(ROOT / "tools" / "restricted.py")]


def run(*args, stdin=""):
    return subprocess.run(SCRIPT + list(args), input=stdin, capture_output=True, text=True)


class RestrictedTest(unittest.TestCase):
    def test_list_loads_and_normalises(self):
        codes = restricted.load()
        self.assertIn("CBA", codes)
        self.assertNotIn("", codes)
        self.assertEqual(restricted.norm(" asx:cba.ax "), "CBA")

    def test_check_blocks_any_case_and_suffix(self):
        self.assertEqual(run("check", "cba.ax").returncode, 1)
        self.assertEqual(run("check", "XYZ", "ASX:NAB").returncode, 1)
        self.assertEqual(run("check", "XYZ").returncode, 0)

    def test_filter_drops_restricted(self):
        r = run("filter", "XYZ", "CBA", "abc")
        self.assertEqual(r.stdout.split(), ["XYZ", "ABC"])
        self.assertIn("dropped 1", r.stderr)

    def test_hook_blocks_prompt_naming_restricted_ticker(self):
        blocked = run("hook", stdin=json.dumps({"prompt": "/red-flags WBC please"}))
        self.assertEqual(blocked.returncode, 2)
        self.assertIn("WBC", blocked.stderr)
        allowed = run("hook", stdin=json.dumps({"prompt": "Ben asked about an amp; screen XYZ"}))
        self.assertEqual(allowed.returncode, 0)

    def test_hook_fails_closed_without_list(self):
        original = restricted.LIST
        restricted.LIST = ROOT / "missing.txt"
        try:
            sys.stdin = io.StringIO(json.dumps({"prompt": "hello"}))
            self.assertEqual(restricted.main(["hook"]), 2)
        finally:
            restricted.LIST = original
            sys.stdin = sys.__stdin__


if __name__ == "__main__":
    unittest.main()
