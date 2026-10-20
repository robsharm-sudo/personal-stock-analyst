"""Print the ASX 200 section for the repository-backed ChatGPT pipeline."""
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
HEADINGS = ('### Top 5:', '### Bottom 5:', '### Steady performers:',
            '### Highest dividend payers')


def last_month_end(now=None):
    today = (now or datetime.now(ZoneInfo('Australia/Sydney'))).date()
    return (today.replace(day=1) - timedelta(days=1)).isoformat()


def usable(text):
    return (all(h in text for h in HEADINGS) and 'STW' in text and '^AXJO' in text
            and any(line and line[0].isdigit() and not line.startswith('0 ')
                    and ' companies analysed;' in line for line in text.splitlines()))


def run(root=ROOT, asof=None):
    asof = asof or last_month_end()
    reports = root / 'reports'
    universes = sorted(reports.glob('asx200_constituents_*.csv'),
                       key=lambda p: p.stem[-10:])
    reason = 'No constituent snapshot is available.'
    if universes:
        with tempfile.TemporaryDirectory(prefix='chatgpt-asx200-') as out:
            try:
                result = subprocess.run(
                    [sys.executable, str(root / 'tools/performance_screen.py'),
                     '--universe', str(universes[-1]), '--asof', asof, '--out', out],
                    cwd=root, capture_output=True, text=True, timeout=900)
                report = Path(out) / f'performance_screen_{asof}.md'
                if result.returncode == 0 and report.exists():
                    text = report.read_text()
                    if usable(text):
                        return text, 0
                reason = 'Report generation failed or returned incomplete tables/no priced companies.'
                if result.returncode and result.stderr.strip():
                    reason += ' ' + result.stderr.strip().splitlines()[-1][:300]
                # Diagnostic output stays on stderr, separate from the report body.
                print(result.stderr[-2000:], file=sys.stderr)
            except subprocess.TimeoutExpired:
                reason = 'Report generation exceeded the 15-minute timeout.'
            except OSError as exc:
                reason = f'Report generator could not start: {exc}'
    for saved in sorted(reports.glob('performance_screen_*.md'), reverse=True):
        if saved.stem[-10:] > asof:
            continue
        text = saved.read_text()
        if usable(text):
            return (f'# ASX 200 performance\n\n**Saved report — not refreshed this run**\n\n'
                    f'{reason} Requested month end: {asof}. Saved file: {saved.name}.\n\n'
                    + text), 0
    return f'# ASX 200 performance unavailable\n\n{reason}\n', 1


if __name__ == '__main__':
    body, status = run()
    print(body)
    raise SystemExit(status)
