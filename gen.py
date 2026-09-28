"""Generate animated blueprint-style SVG cards for the GitHub profile README.
Output: assets/*.svg  (pure SVG + CSS/SMIL animation, no scripts - GitHub-safe)
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)

# ---- design tokens ----
BG = "#fbfcfe"
GRID = "#e6ebf3"
BORDER = "#cfd8e6"
INK = "#0f172a"
MUTED = "#64748b"
FAINT = "#94a3b8"
BLUE = "#2563eb"
VIOLET = "#7c3aed"
GREEN = "#16a34a"
AMBER = "#d97706"
ROSE = "#e11d48"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "'Segoe UI',Helvetica,Arial,sans-serif"

# Shared CSS animations. Classes: .up (fade + slide up), .in (fade), .pulse, .blink
BASE_CSS = """
@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.35)}}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
@keyframes ping{0%{r:3;opacity:.8}100%{r:11;opacity:0}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes shimmer{from{transform:translateX(-160px)}to{transform:translateX(160px)}}
@keyframes bracket{from{stroke-dashoffset:28}to{stroke-dashoffset:0}}
.up{opacity:0;animation:up .6s ease-out forwards}
.in{opacity:0;animation:fade .6s ease-out forwards}
.pulse{transform-box:fill-box;transform-origin:center;animation:pulse 1.6s ease-in-out infinite}
.blink{animation:blink 1s step-end infinite}
.grow{transform-box:fill-box;transform-origin:left center;transform:scaleX(0);animation:grow .8s cubic-bezier(.2,.8,.2,1) forwards}
.br{stroke-dasharray:28;stroke-dashoffset:28;animation:bracket .7s ease-out forwards}
@keyframes blip{0%{opacity:0}2%{opacity:1}7%{opacity:1}9%{opacity:0}100%{opacity:0}}
.blip{opacity:0;animation:blip .8s linear forwards}
.settle{opacity:0;animation:fade .25s ease-out forwards}
"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def frame(w, h, inner, css=""):
    """Card with grid background, border, corner brackets that draw themselves in."""
    b = 14
    m = 10
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>{BASE_CSS}{css}</style>
<defs>
  <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="{GRID}" stroke-width="1"/>
  </pattern>
</defs>
<rect width="{w}" height="{h}" rx="6" fill="{BG}"/>
<rect width="{w}" height="{h}" rx="6" fill="url(#grid)"/>
<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="6" fill="none" stroke="{BORDER}"/>
<g fill="none" stroke="{INK}" stroke-width="1.5">
  <path class="br" d="M{m} {m+b} V{m} H{m+b}"/>
  <path class="br" style="animation-delay:.1s" d="M{w-m-b} {m} H{w-m} V{m+b}"/>
  <path class="br" style="animation-delay:.2s" d="M{m} {h-m-b} V{h-m} H{m+b}"/>
  <path class="br" style="animation-delay:.3s" d="M{w-m-b} {h-m} H{w-m} V{h-m-b}"/>
</g>
{inner}
</svg>"""


def label(x, y, text, color=FAINT, size=9, anchor="middle", spacing=2, cls="", delay=None):
    st = f' style="animation-delay:{delay}s"' if delay is not None else ""
    c = f' class="{cls}"' if cls else ""
    return (f'<text{c}{st} x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" letter-spacing="{spacing}">{esc(text)}</text>')


def write(name, svg):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)
    print("  wrote", name)


# =============================== HEADER ===============================
def header(followers):
    w, h = 800, 248
    cx = w / 2
    inner = []
    # Title: monospace, bold, letter-spaced -- matches the rest of the blueprint (no
    # system-only fonts like Segoe UI, which fall back to an ugly serif on non-Windows
    # renderers such as GitHub's own image proxy).
    inner.append(f'<text class="up" x="{cx}" y="60" font-family="{MONO}" font-size="28" font-weight="700" '
                 f'fill="{INK}" text-anchor="middle" letter-spacing="1">TRAN DINH VO</text>')
    pill_w = 150
    inner.append(f'<g class="up" style="animation-delay:.2s">')
    inner.append(f'<rect x="{cx-pill_w/2}" y="74" width="{pill_w}" height="20" rx="10" fill="#fff" stroke="{BORDER}"/>')
    inner.append(f'<circle class="pulse" cx="{cx-pill_w/2+14}" cy="84" r="3" fill="{AMBER}"/>')
    inner.append(label(cx + 6, 88, f"GITHUB  ·  {followers} FOLLOWERS", MUTED, 8, "middle", 1.5))
    inner.append('</g>')
    inner.append(f'<line class="grow" style="animation-delay:.4s" x1="{cx-30}" y1="106" x2="{cx+30}" y2="106" stroke="{BLUE}" stroke-width="2"/>')

    # Typewriter title, monospace so every character has the same advance width --
    # a clipPath rect grows continuously left to right (robust: one smooth <animate>,
    # no discrete per-character keyframe list to desync or freeze mid-glyph).
    title = "FULL-STACK DEVELOPER"
    ch = 9.6   # advance width per monospace character at this font-size
    tw = ch * len(title)
    tx = cx - tw / 2
    clip_id = "typeclip"
    inner.append(f'<defs><clipPath id="{clip_id}"><rect x="{tx-2}" y="112" height="24" width="{tw+4}">'
                 f'<animate attributeName="width" from="0" to="{tw+4}" begin="0.6s" dur="1.1s" '
                 f'fill="freeze" calcMode="spline" keySplines=".3 0 .2 1"/></rect></clipPath></defs>')
    inner.append(f'<g clip-path="url(#{clip_id})">'
                 f'<text x="{cx}" y="132" font-family="{MONO}" font-size="16" font-weight="600" '
                 f'fill="{INK}" text-anchor="middle" letter-spacing="1">{title}</text></g>')
    # blinking cursor: slides once to the end of the text, then blinks in place
    inner.append(f'<rect class="blink" style="animation-delay:1.7s" x="{tx}" y="118" width="2" height="16" fill="{BLUE}" opacity="0">'
                 f'<animate attributeName="x" from="{tx}" to="{tx+tw}" begin="0.6s" dur="1.1s" fill="freeze" calcMode="spline" keySplines=".3 0 .2 1"/>'
                 f'<animate attributeName="opacity" to="1" begin="0.6s" dur="0.05s" fill="freeze"/>'
                 f'</rect>')
    inner.append(label(cx, 150, "BACKEND  ·  FRONTEND  ·  DATABASE DESIGN", BLUE, 8.5, cls="in", delay=1.9))

    # timeline with a travelling marker
    y = 186
    steps = ["CODE", "BUILD", "SHIP", "RUN"]
    xs = [160, 320, 480, 640]
    inner.append(f'<line class="grow" style="animation-delay:.5s;animation-duration:1.2s" x1="{xs[0]}" y1="{y}" x2="{xs[-1]}" y2="{y}" stroke="{BORDER}" stroke-width="1.5"/>')
    for i, (x, s) in enumerate(zip(xs, steps)):
        d = 0.7 + i * 0.25
        inner.append(f'<g class="in" style="animation-delay:{d}s">')
        inner.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#fff" stroke="{INK}" stroke-width="1.5"/>')
        inner.append(label(x, y + 18, s, MUTED, 8, "middle", 1.5))
        inner.append('</g>')
    # marker: moves CODE -> RUN, colour shifts, pauses at each stop
    inner.append(f'<circle cy="{y}" r="4" fill="{AMBER}" opacity="0">'
                 f'<animate attributeName="opacity" to="1" begin="1.8s" dur="0.3s" fill="freeze"/>'
                 f'<animate attributeName="cx" begin="1.8s" dur="6s" repeatCount="indefinite" calcMode="spline" '
                 f'values="{xs[0]};{xs[0]};{xs[1]};{xs[1]};{xs[2]};{xs[2]};{xs[3]};{xs[3]};{xs[0]}" '
                 f'keyTimes="0;.15;.3;.45;.6;.75;.9;.97;1" '
                 f'keySplines=".4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1"/>'
                 f'<animate attributeName="fill" begin="1.8s" dur="6s" repeatCount="indefinite" '
                 f'values="{AMBER};{AMBER};{BLUE};{BLUE};{VIOLET};{VIOLET};{GREEN};{GREEN};{AMBER}" keyTimes="0;.15;.3;.45;.6;.75;.9;.97;1"/>'
                 f'</circle>')
    inner.append(f'<circle cy="{y}" r="4" fill="none" stroke="{BLUE}" opacity="0">'
                 f'<animate attributeName="cx" begin="1.8s" dur="6s" repeatCount="indefinite" calcMode="spline" '
                 f'values="{xs[0]};{xs[0]};{xs[1]};{xs[1]};{xs[2]};{xs[2]};{xs[3]};{xs[3]};{xs[0]}" keyTimes="0;.15;.3;.45;.6;.75;.9;.97;1" '
                 f'keySplines=".4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1"/>'
                 f'<animate attributeName="r" values="4;12" begin="1.8s" dur="1.5s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values=".7;0" begin="1.8s" dur="1.5s" repeatCount="indefinite"/>'
                 f'</circle>')
    # rotating tagline
    tags = ["LEARNING  ·  BUILDING  ·  GROWING", "OPEN TO INTERNSHIP OPPORTUNITIES", "SPRING BOOT  ·  NESTJS  ·  NEXT.JS"]
    for i, t in enumerate(tags):
        inner.append(f'<text x="{cx}" y="236" font-family="{MONO}" font-size="8" fill="{GREEN}" text-anchor="middle" letter-spacing="2" opacity="0">'
                     f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.08;.3;.38;1" begin="{2 + i*3}s" dur="9s" repeatCount="indefinite"/>{esc(t)}</text>')
    write("header.svg", frame(w, h, chr(10).join(inner)))


# =============================== BUTTONS ===============================
ICONS = {
    "linkedin": ('<path fill="{c}" d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.55V9h3.57v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/>', "#0A66C2"),
    "github": ('<path fill="{c}" d="M12 .3a12 12 0 0 0-3.8 23.4c.6.1.8-.3.8-.6v-2c-3.3.7-4-1.6-4-1.6-.6-1.4-1.4-1.8-1.4-1.8-1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.7-1.6-2.7-.3-5.5-1.3-5.5-5.9 0-1.3.5-2.4 1.2-3.2-.1-.3-.5-1.5.1-3.2 0 0 1-.3 3.3 1.2a11.5 11.5 0 0 1 6 0c2.3-1.5 3.3-1.2 3.3-1.2.7 1.7.2 2.9.1 3.2.8.8 1.2 1.9 1.2 3.2 0 4.6-2.8 5.6-5.5 5.9.4.4.8 1.1.8 2.2v3.3c0 .3.2.7.8.6A12 12 0 0 0 12 .3"/>', "#0f172a"),
    "gmail": ('<path fill="{c}" d="M24 5.457v13.909c0 .904-.732 1.636-1.636 1.636h-3.819V11.73L12 16.64l-6.545-4.91v9.273H1.636A1.636 1.636 0 0 1 0 19.366V5.457c0-2.023 2.309-3.178 3.927-1.964L5.455 4.64 12 9.548l6.545-4.91 1.528-1.145C21.69 2.28 24 3.434 24 5.457z"/>', "#EA4335"),
}


def button(kind, text, filled=False, delay=0):
    w, h = 180, 50
    icon, col = ICONS[kind]
    bg = BLUE if filled else BG
    fg = "#fff" if filled else INK
    ic = "#fff" if filled else col
    grid = "" if filled else f'<rect width="{w}" height="{h}" rx="6" fill="url(#grid)"/>'
    # a light sweep crosses the button every few seconds
    sweep_col = "#ffffff" if filled else BLUE
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>{BASE_CSS}
@keyframes sweep{{0%{{transform:translateX(-120px)}}30%,100%{{transform:translateX(260px)}}}}
.sweep{{animation:sweep 4s ease-in-out {delay}s infinite}}
</style>
<defs><pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
<path d="M 20 0 L 0 0 0 20" fill="none" stroke="{GRID}" stroke-width="1"/></pattern>
<linearGradient id="sw" x1="0" x2="1"><stop offset="0" stop-color="{sweep_col}" stop-opacity="0"/><stop offset=".5" stop-color="{sweep_col}" stop-opacity="{'.35' if filled else '.12'}"/><stop offset="1" stop-color="{sweep_col}" stop-opacity="0"/></linearGradient>
<clipPath id="clip"><rect width="{w}" height="{h}" rx="6"/></clipPath></defs>
<rect width="{w}" height="{h}" rx="6" fill="{bg}"/>{grid}
<g clip-path="url(#clip)"><rect class="sweep" x="0" y="0" width="80" height="{h}" fill="url(#sw)" transform="skewX(-20)"/></g>
<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="6" fill="none" stroke="{BLUE if filled else BORDER}"/>
<path class="br" d="M{w-12} 1 H{w-1} V12" fill="none" stroke="{'#fff' if filled else INK}" stroke-width="1.5" opacity="0.6"/>
<g class="up" transform="translate(22 13)">{icon.format(c=ic)}</g>
<text class="up" style="animation-delay:.15s" x="58" y="30" font-family="{MONO}" font-size="12" font-weight="600" fill="{fg}" letter-spacing="2">{esc(text)}</text>
</svg>"""
    write(f"btn-{kind}.svg", svg)


# =============================== STATS ===============================
def stats(items):
    w, h = 800, 120
    n = len(items)
    colw = (w - 40) / n
    inner = []
    for i, (lbl, val, sub, col) in enumerate(items):
        cx = 20 + colw * i + colw / 2
        d = 0.2 + i * 0.15
        inner.append(label(cx, 34, lbl, FAINT, 8, cls="in", delay=d))
        # count-up: cycle through intermediate values with a discrete SMIL animation
        # Count-up driven entirely by CSS keyframes. SMIL <set> was unreliable when
        # GitHub renders the SVG, which left the numbers blank; CSS animations render.
        target = int(val.replace(",", ""))
        steps = 18
        for k in range(steps):
            sv = f"{round(target * (k / steps) ** 2):,}"
            inner.append(f'<text class="blip" style="animation-delay:{d + k * 0.06:.2f}s" x="{cx}" y="72" '
                         f'font-family="{MONO}" font-size="30" font-weight="700" fill="{INK}" text-anchor="middle">{sv}</text>')
        inner.append(f'<text class="settle" style="animation-delay:{d + steps * 0.06:.2f}s" x="{cx}" y="72" '
                     f'font-family="{MONO}" font-size="30" font-weight="700" fill="{INK}" text-anchor="middle">{esc(val)}</text>')
        inner.append(f'<line class="grow" style="animation-delay:{d+0.9}s" x1="{cx-16}" y1="80" x2="{cx+16}" y2="80" stroke="{col}" stroke-width="2.5"/>')
        inner.append(label(cx, 98, sub, FAINT, 7.5, "middle", 1, cls="in", delay=d + 1.0))
    write("stats.svg", frame(w, h, "\n".join(inner)))


# =============================== SKILLS ===============================
def skills(rows):
    w = 800
    row_h = 40
    top = 24
    h = top + row_h * len(rows) + 14
    inner = []
    lx = 60
    inner.append(f'<line x1="{lx}" y1="{top}" x2="{lx}" y2="{h-16}" stroke="{BORDER}" stroke-width="1.5" '
                 f'stroke-dasharray="{h}" stroke-dashoffset="{h}"><animate attributeName="stroke-dashoffset" to="0" dur="1s" fill="freeze"/></line>')
    chip_col = {0: (BLUE, "#eef4ff"), 1: (AMBER, "#fff7ea"), 2: (VIOLET, "#f5f0ff"),
                3: (GREEN, "#eefaf1"), 4: (ROSE, "#fff0f3")}
    for i, (name, chips) in enumerate(rows):
        cy = top + row_h * i + row_h / 2
        fg, bgc = chip_col[i % 5]
        d = 0.2 + i * 0.18
        inner.append(label(34, cy + 3, f"L{i+1}", FAINT, 8, "middle", 1, cls="in", delay=d))
        inner.append(f'<path class="pulse" style="animation-delay:{i*0.3}s" d="M{lx} {cy-5} l5 5 -5 5 -5 -5z" fill="{fg}"/>')
        inner.append(label(lx + 16, cy + 3.5, name, fg, 9.5, "start", 2, cls="up", delay=d))
        x = 220
        for j, c in enumerate(chips):
            cw = 8.2 * len(c) + 22
            cd = d + 0.15 + j * 0.08
            inner.append(f'<g class="up" style="animation-delay:{cd:.2f}s">')
            inner.append(f'<rect x="{x}" y="{cy-11}" width="{cw}" height="22" rx="3" fill="{bgc}" stroke="{fg}" stroke-opacity="0.35"/>')
            inner.append(f'<text x="{x+cw/2}" y="{cy+4}" font-family="{MONO}" font-size="11" fill="{INK}" text-anchor="middle">{esc(c)}</text>')
            inner.append('</g>')
            x += cw + 8
    write("skills.svg", frame(w, h, "\n".join(inner)))


# =============================== PROJECT CARD ===============================
def project(slug, idx, name, url_text, stack, badge, badge_col, accent, lines):
    w, h = 190, 200
    d = idx * 0.15
    inner = []
    inner.append(f'<path class="br" d="M{w-12} 1 H{w-1} V12" fill="none" stroke="{INK}" stroke-width="1.5" opacity="0.6"/>')
    inner.append(f'<path class="br" d="M{w-12} {h-1} H{w-1} V{h-12}" fill="none" stroke="{INK}" stroke-width="1.5" opacity="0.6"/>')
    inner.append(f'<path class="pulse" d="M14 14 l4 4 -4 4 -4 -4z" fill="{accent}"/>')
    inner.append(label(24, 21, f"P{idx:02d}", MUTED, 7.5, "start", 1.5, cls="in", delay=d))
    bw = 7 * len(badge) + 18
    bx = w - 14 - bw
    inner.append(f'<g class="in" style="animation-delay:{d+0.2}s">')
    inner.append(f'<rect x="{bx}" y="10" width="{bw}" height="15" rx="7.5" fill="#fff" stroke="{badge_col}"/>')
    inner.append(f'<circle cx="{bx+8}" cy="17.5" r="2" fill="{badge_col}"/>')
    if badge == "PUBLIC":
        inner.append(f'<circle cx="{bx+8}" cy="17.5" r="2" fill="none" stroke="{badge_col}">'
                     f'<animate attributeName="r" values="2;7" dur="1.4s" repeatCount="indefinite"/>'
                     f'<animate attributeName="opacity" values=".8;0" dur="1.4s" repeatCount="indefinite"/></circle>')
    inner.append(label(w - 14 - bw / 2 + 4, 21, badge, badge_col, 7, "middle", 1))
    inner.append('</g>')
    # mock UI with shimmer sweep
    ax, ay, aw, ah = 16, 34, w - 32, 92
    inner.append(f'<g class="up" style="animation-delay:{d+0.1}s">')
    inner.append(f'<rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" rx="4" fill="#fff" stroke="{BORDER}"/>')
    inner.append(f'<rect x="{ax}" y="{ay}" width="{aw}" height="14" rx="4" fill="{accent}" opacity="0.9"/>')
    inner.append(f'<rect x="{ax}" y="{ay+10}" width="{aw}" height="4" fill="{accent}" opacity="0.9"/>')
    for k in range(3):
        inner.append(f'<circle cx="{ax+8+k*8}" cy="{ay+7}" r="2" fill="#fff" opacity="0.8"/>')
    inner.append(f'<rect x="{ax+8}" y="{ay+22}" width="34" height="{ah-30}" rx="2" fill="{accent}" opacity="0.12"/>')
    for k, (lw, op) in enumerate(lines):
        yy = ay + 26 + k * 12
        inner.append(f'<rect class="grow" style="animation-delay:{d+0.4+k*0.1:.2f}s" x="{ax+50}" y="{yy}" width="{lw}" height="6" rx="2" fill="{accent}" opacity="{op}"/>')
    inner.append(f'<clipPath id="mock"><rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" rx="4"/></clipPath>')
    inner.append(f'<g clip-path="url(#mock)"><rect x="{ax}" y="{ay}" width="40" height="{ah}" fill="url(#shine)" '
                 f'style="animation:shimmer 2.8s ease-in-out {d+1}s infinite" transform="skewX(-20)"/></g>')
    inner.append('</g>')
    inner.append(f'<text class="up" style="animation-delay:{d+0.5}s" x="16" y="150" font-family="{MONO}" font-size="13" font-weight="700" fill="{INK}">{esc(name)}</text>')
    inner.append(f'<text class="up" style="animation-delay:{d+0.6}s" x="16" y="166" font-family="{MONO}" font-size="8.5" fill="{MUTED}">{esc(url_text)}</text>')
    inner.append(f'<text class="up" style="animation-delay:{d+0.7}s" x="16" y="184" font-family="{MONO}" font-size="8" fill="{accent}" letter-spacing="0.5">{esc(stack)}</text>')
    defs = (f'<defs><linearGradient id="shine" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="#fff" stop-opacity=".7"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>')
    write(f"proj-{slug}.svg", frame(w, h, defs + "\n".join(inner)))


if __name__ == "__main__":
    import json, subprocess
    u = json.loads(subprocess.run(["curl", "-s", "https://api.github.com/users/TranDinhVo"],
                                  capture_output=True, text=True, encoding="utf-8").stdout)
    header(u["followers"])
    button("linkedin", "LINKEDIN", delay=0)
    button("github", "GITHUB", delay=0.4)
    button("gmail", "GMAIL", delay=0.8)
    stats([
        ("TOTAL CONTRIBUTIONS", "1,822", "JUL 2023 – PRESENT", AMBER),
        ("THIS YEAR", "1,471", "JAN 1 – SEP 28, 2026", BLUE),
        ("LONGEST STREAK", "11", "JUN 30 – JUL 10, 2026", VIOLET),
        ("PUBLIC REPOS", str(u["public_repos"]), "ON GITHUB", GREEN),
    ])
    skills([
        ("FRONTEND", ["React", "Next.js", "TypeScript", "Redux", "Ant Design", "Tailwind"]),
        ("BACKEND", ["Spring Boot", "NestJS", "ASP.NET Core", "Node.js", "Java", "C#"]),
        ("DATABASE", ["PostgreSQL", "MySQL", "Prisma", "JPA"]),
        ("DEVOPS", ["Docker", "Nginx", "GitHub Actions", "Vercel", "GCP Cloud Run"]),
        ("ENGINEERING", ["REST API", "JWT / RBAC", "MVC", "Unit Testing", "Algorithms"]),
    ])
    project("spark", 1, "SPARK", "github.com/TranDinhVo/SPARK", "Spring Boot · React · MySQL",
            "PUBLIC", GREEN, BLUE, [(70, .5), (50, .3), (80, .3), (40, .2), (60, .3)])
    project("payhub", 2, "PayHub", "PayPal order management", "NestJS · Next.js · Prisma",
            "PRIVATE", AMBER, VIOLET, [(60, .5), (80, .3), (45, .3), (70, .2), (50, .3)])
    project("financeos", 3, "FinanceOS", "Accounting platform", "Next.js · Prisma · Antd",
            "PRIVATE", AMBER, GREEN, [(80, .5), (40, .3), (65, .3), (55, .2), (75, .3)])
    project("monkeymail", 4, "MonkeyMail", "Desktop email client", "Tauri · React · Node.js",
            "PRIVATE", AMBER, ROSE, [(50, .5), (75, .3), (60, .3), (80, .2), (45, .3)])
