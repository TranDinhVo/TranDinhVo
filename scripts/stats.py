"""Regenerate assets/stats.svg from live GitHub data.

Runs in GitHub Actions (see .github/workflows/stats.yml).
Token: GH_PAT (includes private contributions) or GITHUB_TOKEN (public only).
"""
import datetime as dt
import json
import os
import sys
import urllib.request

USER = "TranDinhVo"
TOKEN = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
if not TOKEN:
    sys.exit("no token")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "stats.svg")


def gql(query, variables=None):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    if "errors" in data:
        sys.exit(data["errors"])
    return data["data"]


# ---------------------------------------------------------------- data
today = dt.date.today()
created = dt.date.fromisoformat(gql('{ user(login:"%s"){ createdAt } }' % USER)["user"]["createdAt"][:10])

days = {}
year = created.year
while year <= today.year:
    d = gql(
        '''query($u:String!,$f:DateTime!,$t:DateTime!){ user(login:$u){
             contributionsCollection(from:$f,to:$t){ contributionCalendar{
               weeks{ contributionDays{ date contributionCount } } } } } }''',
        {"u": USER, "f": f"{year}-01-01T00:00:00Z", "t": f"{year}-12-31T23:59:59Z"},
    )
    for w in d["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
        for day in w["contributionDays"]:
            days[day["date"]] = day["contributionCount"]
    year += 1

series = sorted((dt.date.fromisoformat(k), v) for k, v in days.items() if dt.date.fromisoformat(k) <= today)

total = sum(v for _, v in series)
since_365 = today - dt.timedelta(days=365)
last_year = sum(v for d, v in series if d > since_365)

longest = cur = 0
l_start = l_end = None
run_start = None
for d, v in series:
    if v > 0:
        cur += 1
        run_start = run_start or d
        if cur > longest:
            longest, l_start, l_end = cur, run_start, d
    else:
        cur = 0
        run_start = None

# current streak: today may still be empty, so allow it to be 0
current = 0
c_start = None
i = len(series) - 1
if series and series[i][1] == 0:
    i -= 1
while i >= 0 and series[i][1] > 0:
    current += 1
    c_start = series[i][0]
    i -= 1


def fmt(d):
    return d.strftime("%b %d, %Y").upper().replace(" 0", " ")


def rng(a, b):
    return f"{a.strftime('%b %d').upper().replace(' 0', ' ')} – {b.strftime('%b %d, %Y').upper().replace(' 0', ' ')}"


items = [
    ("TOTAL CONTRIBUTIONS", f"{total:,}", f"{created.strftime('%b %Y').upper()} – PRESENT", "#d97706"),
    ("LAST 12 MONTHS", f"{last_year:,}", f"{fmt(since_365 + dt.timedelta(days=1))} – TODAY", "#2563eb"),
    ("CURRENT STREAK", str(current), rng(c_start, today) if c_start else "NO ACTIVE STREAK", "#16a34a"),
    ("LONGEST STREAK", str(longest), rng(l_start, l_end) if l_start else "—", "#7c3aed"),
]

# ---------------------------------------------------------------- svg
BG, GRID, BORDER, INK, FAINT = "#fbfcfe", "#e6ebf3", "#cfd8e6", "#0f172a", "#94a3b8"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
CSS = """
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes bracket{from{stroke-dashoffset:28}to{stroke-dashoffset:0}}
.in{opacity:0;animation:fade .6s ease-out forwards}
.grow{transform-box:fill-box;transform-origin:left center;transform:scaleX(0);animation:grow .8s cubic-bezier(.2,.8,.2,1) forwards}
@keyframes blip{0%{opacity:0}2%{opacity:1}7%{opacity:1}9%{opacity:0}100%{opacity:0}}
.blip{opacity:0;animation:blip .8s linear forwards}
.settle{opacity:0;animation:fade .25s ease-out forwards}
.br{stroke-dasharray:28;stroke-dashoffset:28;animation:bracket .7s ease-out forwards}
"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def label(x, y, text, color, size, delay, spacing=2):
    return (f'<text class="in" style="animation-delay:{delay}s" x="{x}" y="{y}" font-family="{MONO}" '
            f'font-size="{size}" fill="{color}" text-anchor="middle" letter-spacing="{spacing}">{esc(text)}</text>')


w, h = 800, 120
colw = (w - 40) / len(items)
parts = []
for i, (lbl, val, sub, col) in enumerate(items):
    cx = 20 + colw * i + colw / 2
    d = 0.2 + i * 0.15
    parts.append(label(cx, 34, lbl, FAINT, 8, d))
    target = int(val.replace(",", ""))
    steps = 18
    for k in range(steps):
        sv = f"{round(target * (k / steps) ** 2):,}"
        parts.append(f'<text class="blip" style="animation-delay:{d + k * 0.06:.2f}s" x="{cx}" y="72" '
                     f'font-family="{MONO}" font-size="30" font-weight="700" fill="{INK}" text-anchor="middle">{sv}</text>')
    parts.append(f'<text class="settle" style="animation-delay:{d + steps * 0.06:.2f}s" x="{cx}" y="72" '
                 f'font-family="{MONO}" font-size="30" font-weight="700" fill="{INK}" text-anchor="middle">{esc(val)}</text>')
    parts.append(f'<line class="grow" style="animation-delay:{d + 0.9}s" x1="{cx - 16}" y1="80" x2="{cx + 16}" y2="80" stroke="{col}" stroke-width="2.5"/>')
    parts.append(label(cx, 98, sub, FAINT, 7.5, d + 1.0, 1))

b, m = 14, 10
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>{CSS}</style>
<defs><pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
<path d="M 20 0 L 0 0 0 20" fill="none" stroke="{GRID}" stroke-width="1"/></pattern></defs>
<rect width="{w}" height="{h}" rx="6" fill="{BG}"/>
<rect width="{w}" height="{h}" rx="6" fill="url(#grid)"/>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="6" fill="none" stroke="{BORDER}"/>
<g fill="none" stroke="{INK}" stroke-width="1.5">
  <path class="br" d="M{m} {m + b} V{m} H{m + b}"/>
  <path class="br" style="animation-delay:.1s" d="M{w - m - b} {m} H{w - m} V{m + b}"/>
  <path class="br" style="animation-delay:.2s" d="M{m} {h - m - b} V{h - m} H{m + b}"/>
  <path class="br" style="animation-delay:.3s" d="M{w - m - b} {h - m} H{w - m} V{h - m - b}"/>
</g>
{chr(10).join(parts)}
<!-- updated {today.isoformat()} -->
</svg>"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"total={total} last12m={last_year} current={current} longest={longest}")
