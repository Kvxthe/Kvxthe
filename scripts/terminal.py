"""Render assets/terminal.svg: a neofetch-style terminal beside an animated black hole.

Usage: python scripts/terminal.py
"""
import math
import random
from pathlib import Path
from xml.sax.saxutils import escape

from common import SWATCHES, TERMINAL_STYLE, USER, W, prompt, text, typed, window

H = 600
CX, CY = 184, 238  # black hole centre
R = 50  # shadow radius

FIELDS = [
    ("role", "Software Developer"),
    ("focus", "Backend & APIs / Clean Architecture"),
    ("craft", "Design Patterns / Systems Architecture"),
    ("langs", "Python  Java  TypeScript  Luau"),
    ("backend", "FastAPI  PostgreSQL"),
    ("cloud", "AWS S3"),
    ("tools", "Git  Jira"),
    ("gamedev", "Roblox Studio"),
    ("art", "3D Modelling"),
    ("status", "building scalable backend systems"),
    ("mindset", "always learning, always shipping"),
]
CURRENTLY = [
    "designing backend services & APIs",
    "scripting Luau systems in Roblox",
    "modelling 3D assets",
]
CONTACT = [("mail", "kvxthe@gmail.com"), ("github", "github.com/Kvxthe")]
CLOSING = "# clean code. solid architecture. reliable delivery."

STYLE = TERMINAL_STYLE + """
  .orbit { animation: orbit linear infinite; }
  @keyframes orbit { from { stroke-dashoffset: 0; } to { stroke-dashoffset: -200; } }
  .halo { transform-box: fill-box; transform-origin: 50% 50%; animation: breathe 6s ease-in-out infinite; }
  @keyframes breathe { 0%, 100% { opacity: .55; transform: scale(1); } 50% { opacity: .9; transform: scale(1.06); } }
  .photon { animation: flicker 3.2s ease-in-out infinite; }
  @keyframes flicker { 0%, 100% { opacity: .75; } 50% { opacity: 1; } }
  .lens { transform-box: fill-box; transform-origin: 50% 50%; animation: wobble 9s ease-in-out infinite; }
  @keyframes wobble { 0%, 100% { transform: scale(1, 1); } 50% { transform: scale(1.03, .97); } }
  .star { animation: twinkle ease-in-out infinite; }
  @keyframes twinkle { 0%, 100% { opacity: .15; } 50% { opacity: .9; } }
  @media (prefers-reduced-motion: reduce) {
    .ln, .orbit, .halo, .photon, .lens, .star, .cursor { animation: none; opacity: 1; transform: none; }
  }
"""


def stars():
    rnd = random.Random(7)
    out = []
    for _ in range(26):
        x, y = rnd.uniform(28, 340), rnd.uniform(96, 400)
        if (x - CX) ** 2 / 150 ** 2 + (y - CY) ** 2 / 60 ** 2 < 1:  # keep the disk area clean
            continue
        r = rnd.choice([0.6, 0.8, 1.0, 1.3])
        out.append(
            f'<circle class="star" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#E9D5FF" '
            f'style="animation-duration:{rnd.uniform(2.5, 6):.1f}s;animation-delay:-{rnd.uniform(0, 6):.1f}s"/>'
        )
    return "\n    ".join(out)


def disk():
    """Concentric tilted orbits; inner ones spin faster (Keplerian), dashes suggest motion."""
    rings = []
    for i, rx in enumerate(range(R + 22, 158, 9)):
        ry = rx * 0.21
        width = 4.2 - i * 0.32
        opacity = 0.95 - i * 0.075
        dur = 2.4 + i * 1.15
        dash = ["38 10 18 6 46 14 30 38", "22 8 54 12 16 20 40 28", "60 14 20 10 36 60"][i % 3]
        rings.append(
            f'<ellipse class="orbit" cx="{CX}" cy="{CY}" rx="{rx}" ry="{ry:.1f}" pathLength="200" fill="none" '
            f'stroke="url(#diskGrad)" stroke-width="{width:.2f}" stroke-dasharray="{dash}" stroke-linecap="round" '
            f'opacity="{opacity:.2f}" style="animation-duration:{dur:.2f}s"/>'
        )
    return "\n      ".join(rings)


def infall():
    """Particles spiralling into the horizon along precomputed paths."""
    out = []
    for start, dur, delay in [(0, 7, 0), (2.1, 8.5, 2.3), (4.2, 6.2, 4.1), (1.2, 9.5, 5.6)]:
        pts = []
        for s in range(61):
            t = s / 60
            ang = start + t * 5.2
            rad = 160 * (1 - t) ** 1.4 + (R - 2) * t
            pts.append((CX + rad * math.cos(ang), CY + rad * 0.23 * math.sin(ang)))
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        out.append(
            f'<circle r="1.8" fill="#F5EEFF" opacity="0">'
            f'<animateMotion dur="{dur}s" begin="{delay}s" repeatCount="indefinite" path="{d}"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.15;.85;1" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
            f'<animate attributeName="r" values="1.2;2.2;0.4" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
            f"</circle>"
        )
    return "\n    ".join(out)


def black_hole():
    return f"""
  <g>
    <circle class="halo" cx="{CX}" cy="{CY}" r="165" fill="url(#halo)"/>
    {stars()}
    <g clip-path="url(#back)" filter="url(#glow)">
      {disk()}
    </g>
    <g class="lens" filter="url(#glow)">
      <path d="M{CX - R - 6} {CY + 2} A{R + 6} {R + 9} 0 0 1 {CX + R + 6} {CY + 2}" fill="none" stroke="url(#lensGrad)" stroke-width="8" stroke-linecap="round"/>
      <path d="M{CX - R - 13} {CY + 4} A{R + 13} {R + 16} 0 0 1 {CX + R + 13} {CY + 4}" fill="none" stroke="#C084FC" stroke-width="1.2" opacity=".45"/>
      <path d="M{CX - R - 3} {CY + 1} A{R + 3} {R + 5} 0 0 0 {CX + R + 3} {CY + 1}" fill="none" stroke="#A855F7" stroke-width="2.6" opacity=".7"/>
    </g>
    <circle cx="{CX}" cy="{CY}" r="{R}" fill="#000"/>
    <circle class="photon" cx="{CX}" cy="{CY}" r="{R + 1.5}" fill="none" stroke="#F3EBFF" stroke-width="1.6" filter="url(#glow)"/>
    <g clip-path="url(#front)" filter="url(#glow)">
      {disk()}
    </g>
    {infall()}
  </g>"""


def build():
    type_defs, type_body = typed(70, "neofetch")
    desc = (
        "A terminal window running neofetch beside an animated black hole with a spinning accretion disk. "
        "Kvxthe is a software developer focused on backend and APIs, clean architecture and design patterns, "
        "working with Python, Java, TypeScript, Luau, FastAPI, PostgreSQL, AWS S3, Git and Jira, plus Roblox "
        "game development and 3D modelling. Contact: kvxthe@gmail.com or github.com/Kvxthe."
    )
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">',
        '  <title id="t">kvxthe terminal</title>',
        f'  <desc id="d">{escape(desc)}</desc>',
        f"  <style>{STYLE}  </style>",
        f"""  <defs>
    <radialGradient id="halo"><stop offset="0" stop-color="#7C3AED" stop-opacity=".55"/><stop offset=".45" stop-color="#5B21B6" stop-opacity=".22"/><stop offset="1" stop-color="#2E1065" stop-opacity="0"/></radialGradient>
    <linearGradient id="diskGrad" x1="0" x2="1"><stop offset="0" stop-color="#6D28D9" stop-opacity="0"/><stop offset=".18" stop-color="#A855F7"/><stop offset=".42" stop-color="#FBF7FF"/><stop offset=".62" stop-color="#D8B4FE"/><stop offset=".85" stop-color="#7C3AED"/><stop offset="1" stop-color="#4C1D95" stop-opacity="0"/></linearGradient>
    <linearGradient id="lensGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FBF7FF"/><stop offset=".35" stop-color="#C084FC"/><stop offset=".6" stop-color="#7C3AED" stop-opacity=".5"/><stop offset="1" stop-color="#A855F7" stop-opacity=".85"/></linearGradient>
    <filter id="glow" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <clipPath id="back"><rect x="0" y="0" width="{W}" height="{CY}"/></clipPath>
    <clipPath id="front"><rect x="0" y="{CY}" width="{W}" height="{H}"/></clipPath>
    {type_defs}
  </defs>""",
        window(H, USER + ": ~"),
        type_body,
        black_hole(),
    ]

    # neofetch info
    x, y, d = 380, 112, 1.1
    p.append(f'  {text(x, y, [("usr", USER)], d)}')
    p.append(f'  {text(x, y + 18, [("dim", "-" * len(USER))], d + 0.05)}')
    y += 44
    for i, (k, v) in enumerate(FIELDS):
        p.append(f'  {text(x, y + i * 22, [("key", k.ljust(9)), ("val", v)], d + 0.12 + i * 0.07)}')

    # lower panels
    ly = 432
    d2 = d + 0.12 + len(FIELDS) * 0.07 + 0.1
    p.append(f'  {text(24, ly, [("dim", "# currently")], d2)}')
    for i, line in enumerate(CURRENTLY):
        p.append(f'  {text(24, ly + 24 + i * 20, [("key", "> "), ("val", line)], d2 + 0.08 + i * 0.07)}')
    p.append(f'  {text(x, ly, [("dim", "# contact")], d2)}')
    for i, (k, v) in enumerate(CONTACT):
        p.append(f'  {text(x, ly + 24 + i * 20, [("key", k.ljust(9)), ("val", v)], d2 + 0.08 + i * 0.07)}')
    for i, c in enumerate(SWATCHES):
        p.append(
            f'  <rect class="ln" style="animation-delay:{d2 + 0.3 + i * 0.05:.2f}s" x="{x + i * 26}" y="{ly + 62}" '
            f'width="24" height="12" rx="2" fill="{c}"/>'
        )

    fy = H - 26
    p.append(f'  {text(24, fy - 26, [("dim", CLOSING)], d2 + 0.6)}')
    p.append(prompt(fy, d2 + 0.7))
    p.append("</svg>")
    return "\n".join(p) + "\n"


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets" / "terminal.svg"
    out.write_text(build(), encoding="utf-8")
    print(f"wrote {out.name}")
