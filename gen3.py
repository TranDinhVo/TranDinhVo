"""Two more blueprint cards: commit rhythm (real data) and journey timeline.

Rhythm is built from the author's own commit timestamps via the GitHub search
API, so it is measured, not decorative.
"""
import datetime as dt
import json
import os
import subprocess
import sys
from collections import Counter

from gen import (
    BASE_CSS, BG, BORDER, INK, MUTED, FAINT,
    BLUE, VIOLET, GREEN, AMBER, ROSE, MONO,
    esc, frame, label, write,
)

NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
USER = "TranDinhVo"
DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
# empty -> busiest
SCALE = ["#eef1f6", "#c7dbfe", "#7aa8f7", "#3b74ef", "#1e40af"]


# --------------------------------------------------------------- data
def fetch_rhythm(token, pages=10):
    """Weekday x hour histogram over the most recent commits."""
    head = ["-H", f"Authorization: Bearer {token}",
            "-H", "Accept: application/vnd.github.cloak-preview+json"]
    stamps = []
    for page in range(1, pages + 1):
        url = (f"https://api.github.com/search/commits?q=author:{USER}"
               f"&per_page=100&page={page}&sort=author-date")
        raw = subprocess.run(["curl", "-s", url] + head,
                             capture_output=True, text=True, encoding="utf-8").stdout
        items = (json.loads(raw) or {}).get("items") or []
        if not items:
            break
        stamps += [i["commit"]["author"]["date"] for i in items]
    grid = Counter()
    for s in stamps:
        t = dt.datetime.fromisoformat(s)
        grid[(t.weekday(), t.hour)] += 1
    return grid, len(stamps)


# ------------------------------------------------------------- rhythm
def rhythm(grid, sampled):
    w = 800
    cell, gapx = 25, 4
    rowh, gapy = 14, 3
    x0, y0 = 60, 46
    h = y0 + 7 * (rowh + gapy) + 54

    peak = max(grid.values()) if grid else 1
    hours = Counter()
    for (d, hh), v in grid.items():
        hours[hh] += v

    inner = [label(w / 2, 26, f"WHEN I COMMIT  ·  LAST {sampled:,} COMMITS", MUTED, 9, "middle", 2.5,
                   cls="in", delay=0.1)]

    for d in range(7):
        ry = y0 + d * (rowh + gapy)
        inner.append(f'<text class="in" style="animation-delay:{0.2 + d * 0.05:.2f}s" x="{x0-10}" y="{ry+10.5}" '
                     f'font-family="{MONO}" font-size="7" fill="{FAINT}" text-anchor="end" '
                     f'letter-spacing="1">{DAYS[d]}</text>')
        for hh in range(24):
            n = grid.get((d, hh), 0)
            frac = n / peak
            lvl = 0 if n == 0 else 1 if frac < 0.2 else 2 if frac < 0.4 else 3 if frac < 0.7 else 4
            cx = x0 + hh * (cell + gapx)
            # wave in from the left
            delay = 0.25 + hh * 0.022 + d * 0.03
            inner.append(f'<rect class="in" style="animation-delay:{delay:.2f}s" x="{cx}" y="{ry}" '
                         f'width="{cell}" height="{rowh}" rx="2.5" fill="{SCALE[lvl]}"/>')

    ly = y0 + 7 * (rowh + gapy) + 14
    for hh in range(0, 24, 3):
        cx = x0 + hh * (cell + gapx) + cell / 2
        inner.append(label(cx, ly, f"{hh:02d}", FAINT, 7, "middle", 0.5, cls="in", delay=0.9))

    # legend
    lx = w - 176
    ly2 = ly + 18
    inner.append(label(lx - 10, ly2 + 4, "LESS", FAINT, 7, "end", 1, cls="in", delay=1.0))
    for i, col in enumerate(SCALE):
        inner.append(f'<rect class="in" style="animation-delay:{1.0 + i * 0.05:.2f}s" x="{lx + i * 15}" '
                     f'y="{ly2-4}" width="11" height="11" rx="2" fill="{col}"/>')
    inner.append(label(lx + 5 * 15 + 4, ly2 + 4, "MORE", FAINT, 7, "start", 1, cls="in", delay=1.25))

    # measured summary, left aligned opposite the legend
    busiest = sorted(hours, key=hours.get, reverse=True)[:3]
    lo, hi = min(busiest), max(busiest)
    quiet = DAYS[min(range(7), key=lambda d: sum(grid.get((d, x), 0) for x in range(24)))]
    inner.append(f'<text class="in" style="animation-delay:1.1s" x="{x0-10}" y="{ly2+4}" font-family="{MONO}" '
                 f'font-size="8" fill="{GREEN}" letter-spacing="1.4">'
                 f'{esc(f"PEAK {lo:02d}:00-{hi:02d}:00  ·  QUIETEST ON {quiet}")}</text>')

    write("rhythm.svg", frame(w, h, NL.join(inner)))


# ------------------------------------------------------------ journey
def journey():
    w, h = 800, 196
    inner = [label(w / 2, 26, "JOURNEY", MUTED, 9, "middle", 3, cls="in", delay=0.1)]

    stops = [
        ("2023", "STARTED IT @ UTC2", ["First lines of C++,", "first ICPC practice"], AMBER),
        ("2024", "COMPETITIVE PROGRAMMING", ["1st Prize Math Olympiad", "ICPC Asia — Hanoi"], VIOLET),
        ("2025", "FIRST FULL-STACK SYSTEMS", ["SPARK — Spring Boot", "Academix — ASP.NET Core"], BLUE),
        ("2026", "PRODUCTION FINANCE SYSTEMS", ["PayHub · FinanceOS", "TrendScope · MonkeyMail"], GREEN),
    ]
    y = 72
    xs = [108 + i * ((w - 216) / (len(stops) - 1)) for i in range(len(stops))]

    inner.append(f'<line class="grow" style="animation-delay:.35s;animation-duration:1.3s" '
                 f'x1="{xs[0]}" y1="{y}" x2="{xs[-1]}" y2="{y}" stroke="{BORDER}" stroke-width="1.5"/>')

    for i, (year, title, lines, col) in enumerate(stops):
        x = xs[i]
        d = 0.45 + i * 0.2
        inner.append(f'<text class="up" style="animation-delay:{d:.2f}s" x="{x}" y="{y-18}" font-family="{MONO}" '
                     f'font-size="15" font-weight="700" fill="{col}" text-anchor="middle" '
                     f'letter-spacing="1">{year}</text>')
        inner.append(f'<circle class="in" style="animation-delay:{d+0.1:.2f}s" cx="{x}" cy="{y}" r="6" '
                     f'fill="#ffffff" stroke="{col}" stroke-width="2"/>')
        inner.append(f'<circle class="in" style="animation-delay:{d+0.15:.2f}s" cx="{x}" cy="{y}" r="2.5" fill="{col}"/>')
        inner.append(label(x, y + 24, title, INK, 8, "middle", 1.2, cls="up", delay=d + 0.2))
        for k, ln in enumerate(lines):
            inner.append(f'<text class="in" style="animation-delay:{d+0.3+k*0.08:.2f}s" x="{x}" y="{y+40+k*13}" '
                         f'font-family="{MONO}" font-size="7.5" fill="{MUTED}" text-anchor="middle">{esc(ln)}</text>')

    # the marker keeps travelling toward what is next
    inner.append(f'<circle cy="{y}" r="3.5" fill="{GREEN}" opacity="0">'
                 f'<animate attributeName="cx" values="{xs[0]};{xs[-1]}" begin="1.6s" dur="4s" '
                 f'repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.85;1" '
                 f'begin="1.6s" dur="4s" repeatCount="indefinite"/></circle>')

    inner.append(label(w / 2, 180, "NEXT  ·  FULL-STACK INTERNSHIP  ·  GRADUATING OCT 2027", GREEN, 8, "middle", 2,
                       cls="in", delay=1.5))
    write("journey.svg", frame(w, h, NL.join(inner)))


if __name__ == "__main__":
    token = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
    cache = os.path.join(HERE, "rhythm.json")
    if token:
        grid, sampled = fetch_rhythm(token)
        json.dump({f"{k[0]},{k[1]}": v for k, v in grid.items()} | {"_n": sampled},
                  open(cache, "w"))
    elif os.path.exists(cache):
        raw = json.load(open(cache))
        sampled = raw.pop("_n", 1000)
        grid = Counter({tuple(int(p) for p in k.split(",")): v for k, v in raw.items()})
    else:
        sys.exit("no token and no cached rhythm.json")
    rhythm(grid, sampled)
    journey()
