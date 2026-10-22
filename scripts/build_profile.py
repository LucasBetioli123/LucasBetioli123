#!/usr/bin/env python3
"""Generate a GitHub profile with stdlib-only, first-party data collection."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from html import escape
from html.parser import HTMLParser
import json
import math
import os
from pathlib import Path
import re
import tempfile
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
THEMES = {
    "light": {"bg": "#f6f3ec", "ink": "#222720", "muted": "#62685d", "line": "#d8d9ce", "accent": "#b6482c", "soft": "#e6e8de"},
    "dark": {"bg": "#171d1c", "ink": "#f3f0e6", "muted": "#b0baaf", "line": "#39443e", "accent": "#f29a78", "soft": "#29332e"},
}


def text(x, y, value, size=14, fill="currentColor", family="sans-serif", **attrs):
    a = " ".join(f'{k.replace("_", "-")}="{escape(str(v), quote=True)}"' for k, v in attrs.items())
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-family="{family}" {a}>{escape(str(value))}</text>'


def svg(height, title, body, p):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}" role="img" aria-labelledby="title">'
            f'<title id="title">{escape(title)}</title><rect width="1000" height="{height}" rx="10" fill="{p["bg"]}"/>'
            f'<g fill="{p["ink"]}">{body}</g></svg>\n')


def hero(p):
    b = text(42, 40, "LUCAS BETIOLI", 13, p["ink"], "monospace", letter_spacing=2)
    b += text(958, 40, "ENGINEERING / RESEARCH / OPEN SOURCE", 11, p["muted"], "monospace", text_anchor="end")
    b += f'<path d="M42 60 H958" stroke="{p["line"]}"/>'
    b += text(42, 109, "MEDICAL PHYSICS × COMPUTER VISION × MACHINE LEARNING", 11, p["muted"], "monospace")
    b += text(38, 194, "From signals", 74, p["ink"], "Georgia, serif", letter_spacing=-3)
    b += text(38, 275, "to systems.", 74, p["ink"], "Georgia, serif", letter_spacing=-3)
    b += text(42, 327, "AI Engineer at Alliage", 20, p["accent"])
    b += text(42, 357, "Building useful tools at the intersection of science and software.", 14, p["muted"])
    # A conceptual contour field, deliberately not presented as measured data.
    b += f'<defs><clipPath id="field"><rect x="620" y="90" width="340" height="255"/></clipPath></defs><g clip-path="url(#field)">'
    for i in range(16):
        r = 22 + i * 7.7
        pts = []
        for j in range(101):
            t = j * 2 * math.pi / 100
            x = 790 + r * math.cos(t) * (1 + .16 * math.sin(3 * t))
            y = 220 + r * .8 * math.sin(t) * (1 + .14 * math.cos(4 * t))
            pts.append(f'{x:.1f},{y:.1f}')
        b += f'<polyline points="{" ".join(pts)}" stroke="{p["accent"] if i % 4 == 0 else p["line"]}" stroke-width="{1.5 if i % 4 == 0 else 1}" fill="none"/>'
    b += f'<path d="M620 220 H960 M790 90 V345" stroke="{p["muted"]}" opacity=".3" stroke-dasharray="3 5"/>'
    b += f'<circle cx="790" cy="220" r="4" fill="{p["accent"]}"/></g>'
    b += text(958, 370, "A WORKING ATLAS / LB", 10, p["muted"], "monospace", text_anchor="end")
    return svg(400, "Lucas Betioli — From signals to systems. AI Engineer at Alliage.", b, p)


def atlas(p):
    b = ""
    items = [("01", "See", "Computer vision", "Segmentation · Classification"),
             ("02", "Understand", "Medical physics", "Neuroimaging · Tractography"),
             ("03", "Build", "ML systems", "Applications · Inference")]
    for i, (number, verb, domain, detail) in enumerate(items):
        x = i * 333.33 + 28
        if i:
            b += f'<path d="M{x-15} 24 V184" stroke="{p["line"]}"/>'
        b += text(x, 43, number, 12, p["accent"], "monospace")
        b += text(x, 96, verb, 35, p["ink"], "Georgia, serif")
        b += text(x, 132, domain, 18, p["ink"])
        b += text(x, 164, detail, 12, p["muted"])
        if i == 0:
            b += f'<rect x="{x+235}" y="27" width="31" height="22" fill="none" stroke="{p["accent"]}"/><path d="M{x+230} 39 H{x+271} M{x+250} 21 V55" stroke="{p["muted"]}"/>'
        elif i == 1:
            b += f'<path d="M{x+228} 48 Q{x+235} 16 {x+244} 37 T{x+260} 28 M{x+230} 50 Q{x+249} 24 {x+268} 48" fill="none" stroke="{p["accent"]}" stroke-width="1.5"/>'
        else:
            b += f'<path d="M{x+230} 30 H{x+242} V47 H{x+263} M{x+242} 30 H{x+265}" fill="none" stroke="{p["accent"]}" stroke-width="1.5"/>'
            for cx, cy in [(230,30),(263,47),(265,30)]:
                b += f'<circle cx="{x+cx}" cy="{cy}" r="3" fill="{p["accent"]}"/>'
    return svg(210, "A working atlas: See, Understand, Build.", b, p)


def request(url, token="", payload=None):
    # Credentials are sent only to GitHub's API, never to calendar HTML URLs.
    headers = {"User-Agent": "LucasBetioli-profile", "Accept": "application/vnd.github+json"}
    if token and urllib.parse.urlparse(url).hostname == "api.github.com":
        headers["Authorization"] = "Bearer " + token
    body = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode()


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.dates = {}
        self.counts = {}
        self.target = None
        self.buffer = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "data-date" in a and "id" in a:
            self.dates[a["id"]] = a["data-date"]
        if tag == "tool-tip" and "for" in a:
            self.target, self.buffer = a["for"], []

    def handle_data(self, data):
        if self.target is not None:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "tool-tip" and self.target is not None:
            content = "".join(self.buffer).strip()
            m = re.match(r"([\d,]+) contributions?\b", content)
            if m:
                self.counts[self.target] = int(m.group(1).replace(",", ""))
            elif content.startswith("No contributions"):
                self.counts[self.target] = 0
            self.target = None

    def days(self):
        return {d: self.counts[k] for k, d in self.dates.items() if k in self.counts}


def validate_days(days, start, end):
    filtered = {d: n for d, n in days.items() if start.isoformat() <= d <= end.isoformat()}
    if len(filtered) != (end - start).days + 1 or any(not isinstance(n, int) or n < 0 for n in filtered.values()):
        raise ValueError("Incomplete contribution calendar; previous charts were preserved")
    return filtered


def contributions(user, token, today, cache=None):
    start = date(today.year - 1, 1, 1)
    if cache:
        days = {}
        for year in [today.year - 1, today.year]:
            parser = Calendar()
            parser.feed((cache / f"calendar-{year}.html").read_text())
            days.update(parser.days())
        return validate_days(days, start, today)
    if token:
        try:
            days = {}
            query = """query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){contributionsCollection(from:$from,to:$to){contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""
            for year in [today.year - 1, today.year]:
                end = min(today, date(year, 12, 31))
                variables = {"login": user, "from": f"{year}-01-01T00:00:00Z", "to": end.isoformat()+"T23:59:59Z"}
                data = json.loads(request("https://api.github.com/graphql", token, {"query": query, "variables": variables}))
                for week in data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
                    for day in week["contributionDays"]:
                        days[day["date"]] = day["contributionCount"]
            return validate_days(days, start, today)
        except (KeyError, TypeError, ValueError, OSError):
            print("GraphQL unavailable; trying GitHub's public calendar")
    days = {}
    for year in [today.year - 1, today.year]:
        end = min(today, date(year, 12, 31))
        parser = Calendar()
        parser.feed(request(f"https://github.com/users/{user}/contributions?to={end.isoformat()}"))
        days.update(parser.days())
    return validate_days(days, start, today)


def collect(user, token, today, cache):
    if cache:
        repos = json.loads((cache / "repos.json").read_text())
    else:
        repos, page = [], 1
        while True:
            batch = json.loads(request(f"https://api.github.com/users/{user}/repos?per_page=100&page={page}&type=owner", token))
            if not isinstance(batch, list):
                raise ValueError("Invalid repository response")
            repos.extend(batch)
            if len(batch) < 100:
                break
            page += 1
    repos = [r for r in repos if not r["private"] and r["owner"]["login"].lower() == user.lower()]
    originals = [r for r in repos if not r["fork"] and r["name"].lower() != user.lower()]
    def languages(repo):
        if cache:
            return json.loads((cache / (repo["name"] + ".json")).read_text())
        return json.loads(request(repo["languages_url"], token))
    totals = Counter()
    with ThreadPoolExecutor(max_workers=4) as pool:
        for lang in pool.map(languages, originals):
            if not isinstance(lang, dict) or any(not isinstance(n, int) or n < 0 for n in lang.values()):
                raise ValueError("Invalid language response")
            totals.update(lang)
    days = contributions(user, token, today, cache)
    return totals, days, len(originals), sum(r["fork"] for r in repos)


def activity_chart(p, days, today):
    months = defaultdict(int)
    for d, n in sorted(days.items()):
        months[d[:7]] += n
    b = text(32, 39, "PUBLIC FOOTPRINT / ACTIVITY", 12, p["accent"], "monospace", letter_spacing=1)
    b += text(32, 77, f"{today.year-1}–{today.year} / Contributions by month", 25, p["ink"], "Georgia, serif")
    b += text(968, 39, "GITHUB · " + today.isoformat(), 11, p["muted"], "monospace", text_anchor="end")
    max_n = max(1, max(months.values(), default=0))
    ceiling = max(5, math.ceil(max_n / 5) * 5)
    left, top, bottom, width = 60, 115, 265, 900
    for step in range(3):
        v = ceiling * step / 2
        y = bottom - step / 2 * (bottom-top)
        b += f'<path d="M{left} {y} H960" stroke="{p["line"]}"/>'
        b += text(46, y+4, f"{v:g}", 10, p["muted"], "monospace", text_anchor="end")
    step_width = width / len(months)
    for i, (month, count) in enumerate(months.items()):
        x = left + (i + .5) * step_width
        h = count / ceiling * (bottom-top)
        b += f'<path d="M{x:.1f} {bottom} V{bottom-h:.1f}" stroke="{p["accent"]}" stroke-width="{min(18,step_width*.45):.1f}"/>'
        b += f'<circle cx="{x:.1f}" cy="{bottom-h:.1f}" r="3" fill="{p["accent"]}"><title>{escape(month)}: {count} contributions</title></circle>'
        if count:
            b += text(round(x,1), round(bottom-h-10,1), count, 11, p["ink"], "monospace", text_anchor="middle")
        label = datetime.strptime(month, "%Y-%m").strftime("%b")
        if month.endswith("-01"):
            label = month[:4]
        b += text(round(x,1), 289, label, 10, p["muted"], "monospace", text_anchor="middle")
    b += text(32, 326, "Current month is partial · GitHub attribution rules apply · Activity is not a skill score", 11, p["muted"])
    return svg(350, "Monthly GitHub contributions, current and previous calendar year", b, p)


def language_chart(p, totals, originals, forks, today):
    b = text(32, 39, "PUBLIC FOOTPRINT / LANGUAGES", 12, p["accent"], "monospace", letter_spacing=1)
    b += text(32, 77, "What the repositories contain", 25, p["ink"], "Georgia, serif")
    b += text(968, 39, today.isoformat(), 11, p["muted"], "monospace", text_anchor="end")
    count = sum(totals.values())
    if count:
        entries = totals.most_common(5)
        remaining = count - sum(v for _, v in entries)
        if remaining:
            entries.append(("Other", remaining))
        palette = [p["accent"], "#748b74", "#9c8368", "#6b8d9d", "#ae9b63", "#8b8095"]
        cursor = 32
        for i, (name, n) in enumerate(entries):
            w = 604*n/count
            b += f'<rect x="{cursor:.3f}" y="106" width="{w:.3f}" height="14" fill="{palette[i]}"/>'
            cursor += w
            y = 153 + i*25
            b += f'<circle cx="38" cy="{y-4}" r="4" fill="{palette[i]}"/>'
            b += text(53, y, name, 14, p["ink"])
            b += text(630, y, f"{100*n/count:.1f}%", 13, p["muted"], "monospace", text_anchor="end")
    else:
        b += text(32, 150, "No language bytes reported for original public repositories yet.", 14, p["muted"])
    b += f'<path d="M675 106 V272" stroke="{p["line"]}"/>'
    b += text(710, 126, "ORIGINAL PUBLIC REPOS", 11, p["muted"], "monospace")
    b += text(710, 170, originals, 36, p["ink"], "Georgia, serif")
    b += text(710, 211, "PUBLIC FORKS", 11, p["muted"], "monospace")
    b += text(710, 255, forks, 36, p["ink"], "Georgia, serif")
    h = max(350, 210 + 25*len(totals.most_common(6)))
    b += text(32, h-47, "Language bytes · Forks and this profile repository excluded · Not a proficiency ranking", 11, p["muted"])
    b += text(32, h-25, "Jupyter Notebook is GitHub’s file classification; notebooks can contain Python code.", 11, p["muted"])
    return svg(h, "GitHub language bytes in original public repositories, excluding forks", b, p)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, help="Use a complete local public-data snapshot")
    args = parser.parse_args()
    user = os.getenv("PROFILE_USER", "LucasBetioli123")
    if not re.fullmatch(r"[A-Za-z0-9-]{1,39}", user):
        raise ValueError("Invalid GitHub username")
    today = datetime.now(timezone.utc).date()
    totals, days, originals, forks = collect(user, os.getenv("GH_TOKEN", ""), today, args.cache)
    # Fetch and validate everything before replacing any current asset.
    rendered = {}
    for theme, p in THEMES.items():
        rendered[f"hero-{theme}.svg"] = hero(p)
        rendered[f"atlas-{theme}.svg"] = atlas(p)
        rendered[f"activity-{theme}.svg"] = activity_chart(p, days, today)
        rendered[f"languages-{theme}.svg"] = language_chart(p, totals, originals, forks, today)
    out = ROOT / "assets"
    out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out) as temp:
        for name, content in rendered.items():
            Path(temp, name).write_text(content)
        for name in rendered:
            Path(temp, name).replace(out / name)
    print(f"Generated {len(rendered)} SVG assets for {user}; {sum(days.values())} contributions; languages: {dict(totals)}")


if __name__ == "__main__":
    main()
