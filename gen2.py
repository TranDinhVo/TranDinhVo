"""Extra blueprint cards: animated terminal, system architecture, awards.

Shares the design tokens / frame helper with gen.py so everything stays
visually consistent. Pure SVG + CSS/SMIL - no scripts, GitHub-safe.
"""
from gen import (
    BASE_CSS, BG, GRID, BORDER, INK, MUTED, FAINT,
    BLUE, VIOLET, GREEN, AMBER, ROSE, MONO,
    esc, frame, label, write,
)

NL = chr(10)
CW = 6.62          # advance width of one monospace char at 11px
GOLD = "#ca8a04"
SILVER = "#7c8899"
BRONZE = "#b45309"


# ============================ 1. TERMINAL ============================
def terminal():
    """A terminal window that types itself out, line by line."""
    w, h = 800, 232
    wx, wy, ww, wh = 24, 24, w - 48, 184
    inner = []

    # window chrome
    inner.append(f'<g class="up">')
    inner.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="6" fill="#ffffff" stroke="{BORDER}"/>')
    inner.append(f'<path d="M{wx} {wy+30} h{ww}" stroke="{BORDER}" stroke-width="1"/>')
    for k, col in enumerate([ROSE, AMBER, GREEN]):
        inner.append(f'<circle cx="{wx + 18 + k * 14}" cy="{wy + 15}" r="4.5" fill="{col}" opacity="0.85"/>')
    inner.append(f'<text x="{wx + ww/2}" y="{wy + 19}" font-family="{MONO}" font-size="9" fill="{FAINT}" '
                 f'text-anchor="middle" letter-spacing="1">tran@github: ~/projects</text>')
    inner.append('</g>')

    # script: (kind, text, colour)   kind: "cmd" types out, "out" fades in
    script = [
        ("cmd", "whoami", None),
        ("out", "Tran Dinh Vo  —  Full-stack Developer  @ UTC2", INK),
        ("cmd", "cat current-focus.txt", None),
        ("out", "Financial systems · Multi-currency · RBAC · Audit log", BLUE),
        ("cmd", "ls ~/stack", None),
        ("out", "spring-boot/   nestjs/   next.js/   postgresql/   docker/", VIOLET),
    ]

    y = wy + 52
    t = 0.45
    last_cmd_end = t
    for i, (kind, text, col) in enumerate(script):
        if kind == "cmd":
            full = "$ " + text
            tw = len(full) * CW
            dur = max(0.35, len(full) * 0.045)
            cid = f"t{i}"
            inner.append(f'<clipPath id="{cid}"><rect x="{wx+16}" y="{y-12}" height="16" width="{tw+2}">'
                         f'<animate attributeName="width" from="0" to="{tw+2}" begin="{t:.2f}s" dur="{dur:.2f}s" '
                         f'fill="freeze" calcMode="discrete" '
                         f'values="{";".join(f"{CW*k:.1f}" for k in range(len(full)+1))}"/></rect></clipPath>')
            inner.append(f'<g clip-path="url(#{cid})">'
                         f'<text x="{wx+16}" y="{y}" font-family="{MONO}" font-size="11">'
                         f'<tspan fill="{GREEN}" font-weight="700">$ </tspan>'
                         f'<tspan fill="{INK}">{esc(text)}</tspan></text></g>')
            # caret rides along while this line types
            inner.append(f'<rect x="{wx+16}" y="{y-11}" width="7" height="13" fill="{GREEN}" opacity="0">'
                         f'<animate attributeName="opacity" values="0;.45;.45;0" keyTimes="0;.01;.99;1" '
                         f'begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
                         f'<animate attributeName="x" from="{wx+16}" to="{wx+16+tw}" begin="{t:.2f}s" '
                         f'dur="{dur:.2f}s" fill="freeze" calcMode="discrete" '
                         f'values="{";".join(f"{wx+16+CW*k:.1f}" for k in range(len(full)+1))}"/></rect>')
            t += dur + 0.12
            last_cmd_end = t
        else:
            inner.append(f'<text class="in" style="animation-delay:{t:.2f}s" x="{wx+16}" y="{y}" '
                         f'font-family="{MONO}" font-size="11" fill="{col}" xml:space="preserve">{esc(text)}</text>')
            t += 0.5
        y += 20

    # final prompt with a caret that blinks forever
    inner.append(f'<text class="in" style="animation-delay:{t:.2f}s" x="{wx+16}" y="{y}" font-family="{MONO}" '
                 f'font-size="11" fill="{GREEN}" font-weight="700">$</text>')
    inner.append(f'<rect x="{wx+30}" y="{y-11}" width="7" height="13" fill="{INK}" opacity="0">'
                 f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.02;.5;.52;1" '
                 f'begin="{t:.2f}s" dur="1.1s" repeatCount="indefinite"/></rect>')

    write("terminal.svg", frame(w, h, NL.join(inner)))


# ========================== 2. ARCHITECTURE ==========================
def architecture():
    """The shape of the systems in the featured projects, with live packets."""
    w, h = 800, 210
    inner = []
    inner.append(label(w / 2, 26, "TYPICAL SYSTEM ARCHITECTURE", MUTED, 9, "middle", 2.5, cls="in", delay=0.1))

    # dashed deployment boundary
    inner.append(f'<rect class="in" style="animation-delay:.2s" x="20" y="44" width="760" height="118" rx="6" '
                 f'fill="none" stroke="{BORDER}" stroke-width="1.2" stroke-dasharray="5 4"/>')
    inner.append(f'<rect class="in" style="animation-delay:.2s" x="34" y="38" width="150" height="13" fill="{BG}"/>')
    inner.append(label(109, 48, "DOCKER COMPOSE", FAINT, 7.5, "middle", 1.5, cls="in", delay=0.25))

    boxes = [
        ("CLIENT", "Next.js SSR", BLUE),
        ("API", "NestJS · Spring", VIOLET),
        ("SERVICE", "Business logic", AMBER),
        ("ORM", "Prisma · JPA", GREEN),
        ("DATABASE", "PostgreSQL", ROSE),
    ]
    bw, bh, by = 124, 56, 66
    gap = (760 - 28 - bw * len(boxes)) / (len(boxes) - 1)
    xs = [34 + i * (bw + gap) for i in range(len(boxes))]
    cy = by + bh / 2

    # connectors first so boxes sit on top
    for i in range(len(boxes) - 1):
        x0, x1 = xs[i] + bw, xs[i + 1]
        d = 0.5 + i * 0.12
        inner.append(f'<line class="grow" style="animation-delay:{d:.2f}s" x1="{x0}" y1="{cy}" x2="{x1-5}" y2="{cy}" '
                     f'stroke="{BORDER}" stroke-width="1.5"/>')
        inner.append(f'<path class="in" style="animation-delay:{d+0.3:.2f}s" d="M{x1-6} {cy-3.5} l5 3.5 -5 3.5z" fill="{BORDER}"/>')
        # a request packet travelling downstream, one per hop, staggered
        inner.append(f'<circle cy="{cy}" r="3" fill="{boxes[i][2]}" opacity="0">'
                     f'<animate attributeName="cx" from="{x0}" to="{x1-6}" begin="{1.4 + i*0.28}s" dur="2.8s" '
                     f'repeatCount="indefinite" calcMode="spline" keySplines=".4 0 .6 1"/>'
                     f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.12;.8;1" '
                     f'begin="{1.4 + i*0.28}s" dur="2.8s" repeatCount="indefinite"/></circle>')

    for i, (name, tech, col) in enumerate(boxes):
        x = xs[i]
        d = 0.3 + i * 0.1
        inner.append(f'<g class="up" style="animation-delay:{d:.2f}s">')
        inner.append(f'<rect x="{x}" y="{by}" width="{bw}" height="{bh}" rx="5" fill="#ffffff" stroke="{col}" stroke-opacity=".45"/>')
        inner.append(f'<path d="M{x+5} {by} h{bw-10} a5 5 0 0 1 5 5 v0 h-{bw} v0 a5 5 0 0 1 5 -5z" fill="{col}"/>')
        inner.append(f'<rect x="{x}" y="{by}" width="{bw}" height="4" fill="{col}"/>')
        inner.append(f'<text x="{x+bw/2}" y="{by+29}" font-family="{MONO}" font-size="10.5" font-weight="700" '
                     f'fill="{INK}" text-anchor="middle" letter-spacing="1">{esc(name)}</text>')
        inner.append(f'<text x="{x+bw/2}" y="{by+44}" font-family="{MONO}" font-size="8" fill="{MUTED}" '
                     f'text-anchor="middle">{esc(tech)}</text>')
        inner.append('</g>')

    # guard annotation pointing at the API box
    gx = xs[1] + bw / 2
    inner.append(f'<path class="in" style="animation-delay:1.1s" d="M{gx} {by-4} V{by-16}" stroke="{VIOLET}" '
                 f'stroke-width="1.2" stroke-dasharray="3 3"/>')
    inner.append(f'<circle class="pulse" cx="{gx}" cy="{by-18}" r="2.5" fill="{VIOLET}"/>')
    inner.append(f'<rect class="in" style="animation-delay:1.15s" x="{gx+2}" y="42" width="196" height="13" fill="{BG}"/>')
    inner.append(label(gx + 100, by - 15, "JWT · RBAC GUARD · ZOD VALIDATION", VIOLET, 7.5, "middle", 1.2, cls="in", delay=1.2))

    inner.append(label(w / 2, 152, "NGINX REVERSE PROXY  ·  HEALTHCHECKS  ·  MIGRATIONS ON BOOT", FAINT, 7.5, "middle", 1.5, cls="in", delay=1.0))
    inner.append(label(w / 2, 186, "LAYERED · TESTABLE · EVERY MONEY VALUE IN DECIMAL", GREEN, 8, "middle", 2, cls="in", delay=1.4))

    write("architecture.svg", frame(w, h, NL.join(inner)))


# ============================= 3. AWARDS =============================
def awards():
    w, h = 800, 158
    inner = []
    inner.append(label(w / 2, 26, "AWARDS & COMPETITIVE PROGRAMMING", MUTED, 9, "middle", 2.5, cls="in", delay=0.1))

    items = [
        ("1", GOLD, "FIRST PRIZE", "VN Mathematical Olympiad", "2024"),
        ("2", SILVER, "SECOND PRIZE", "VN Mathematical Olympiad", "2026"),
        ("3", BRONZE, "THIRD PRIZE", "VN Informatics Olympiad", "2024"),
        ("◆", BLUE, "ICPC ASIA REGIONAL", "Hanoi · Ho Chi Minh City", "2024 · 2025"),
    ]
    colw = (w - 60) / len(items)
    for i, (mark, col, title, sub, year) in enumerate(items):
        cx = 30 + colw * i + colw / 2
        d = 0.2 + i * 0.15
        my = 60
        inner.append(f'<g class="up" style="animation-delay:{d:.2f}s">')
        # ribbon
        inner.append(f'<path d="M{cx-7} {my+8} l-4 16 6 -3 5 3 -3 -16z" fill="{col}" opacity=".55"/>')
        inner.append(f'<path d="M{cx+7} {my+8} l4 16 -6 -3 -5 3 3 -16z" fill="{col}" opacity=".8"/>')
        # medal
        inner.append(f'<circle cx="{cx}" cy="{my}" r="15" fill="#ffffff" stroke="{col}" stroke-width="2.5"/>')
        inner.append(f'<circle cx="{cx}" cy="{my}" r="10.5" fill="{col}" opacity=".13"/>')
        inner.append(f'<text x="{cx}" y="{my+5}" font-family="{MONO}" font-size="13" font-weight="700" '
                     f'fill="{col}" text-anchor="middle">{esc(mark)}</text>')
        inner.append('</g>')
        # halo on the gold medal only
        if i == 0:
            inner.append(f'<circle cx="{cx}" cy="{my}" r="15" fill="none" stroke="{col}">'
                         f'<animate attributeName="r" values="15;26" dur="2.2s" repeatCount="indefinite"/>'
                         f'<animate attributeName="opacity" values=".55;0" dur="2.2s" repeatCount="indefinite"/></circle>')
        inner.append(label(cx, 104, title, col, 8.5, "middle", 1.2, cls="in", delay=d + 0.15))
        inner.append(f'<text class="in" style="animation-delay:{d+0.25:.2f}s" x="{cx}" y="119" font-family="{MONO}" '
                     f'font-size="8" fill="{MUTED}" text-anchor="middle">{esc(sub)}</text>')
        inner.append(label(cx, 134, year, FAINT, 7.5, "middle", 1, cls="in", delay=d + 0.35))

    write("awards.svg", frame(w, h, NL.join(inner)))


if __name__ == "__main__":
    terminal()
    architecture()
    awards()
