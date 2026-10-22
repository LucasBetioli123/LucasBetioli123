#!/usr/bin/env python3
"""Refresh the classic profile's contribution chart manually (stdlib only)."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path
import build_profile as core

ROOT = Path(__file__).resolve().parents[1]

def chart(days: dict[str, int], today: date) -> str:
    end = today.year * 12 + today.month - 1
    months = [(i // 12, i % 12 + 1) for i in range(end - 11, end + 1)]
    totals = Counter()
    for day, count in days.items():
        totals[(int(day[:4]), int(day[5:7]))] += count
    values = [totals[m] for m in months]
    ceiling = max(4, ((max(values, default=0) + 3) // 4) * 4)
    body = ['<rect x=".5" y=".5" width="839" height="209" rx="6" fill="#0d1117" stroke="#30363d"/>',
            '<text x="24" y="30" fill="#58a6ff" font-size="18" font-weight="600">Public contribution activity</text>',
            f'<text x="816" y="29" text-anchor="end" fill="#8b949e" font-size="11">Updated {today.isoformat()}</text>']
    for i in range(5):
        y = 162 - i * 25
        body += [f'<path d="M48 {y}H816" stroke="#21262d"/>',
                 f'<text x="36" y="{y+4}" fill="#8b949e" font-size="10" text-anchor="end">{ceiling*i//4}</text>']
    for i, ((year, month), value) in enumerate(zip(months, values)):
        x = 64 + i * 63
        height = value / ceiling * 100
        label = date(year, month, 1).strftime('%b')
        body += [f'<rect x="{x}" y="{162-height:.2f}" width="31" height="{height:.2f}" rx="3" fill="#58a6ff"><title>{label} {year}: {value} public contributions</title></rect>',
                 f'<text x="{x+15.5}" y="{154-height:.2f}" fill="#c9d1d9" font-size="11" text-anchor="middle">{value}</text>',
                 f'<text x="{x+15.5}" y="181" fill="#8b949e" font-size="11" text-anchor="middle">{label}</text>']
    first, last = date(*months[0], 1).strftime('%b %Y'), today.strftime('%b %Y')
    body += [f'<text x="48" y="200" fill="#8b949e" font-size="10">{first} – {last} · Current month is partial</text>']
    title = escape(f'Public GitHub contributions by month, {first} to {last}. Updated {today.isoformat()}.')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="840" height="210" viewBox="0 0 840 210" role="img"><title>{title}</title><g font-family="Segoe UI,Arial,sans-serif">{"".join(body)}</g></svg>\n'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--today', type=date.fromisoformat, default=date.today())
    parser.add_argument('--cache', type=Path, help='Optional public calendar HTML cache')
    args = parser.parse_args()
    days = core.contributions('LucasBetioli123', '', args.today, args.cache)
    output = ROOT / 'assets' / 'contributions-classic.svg'
    output.write_text(chart(days, args.today))
    print(f'Wrote {output.name} from public GitHub data')

if __name__ == '__main__':
    main()
