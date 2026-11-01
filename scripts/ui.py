"""Render the README decoration in assets/ui: hero, divider, section headers, stack labels, footer.

Usage: python scripts/ui.py
"""
from pathlib import Path
from xml.sax.saxutils import escape

from common import MONO, SANS, W

ROLES = ["Software Developer", "Backend & Systems Architecture", "Roblox Dev & 3D Modelling"]

# Light theme uses deep violet ink, dark theme uses glowing lavender.
THEME = """
  .t { fill: #4C1D95; } .s { fill: #7C3AED; } .k { stroke: #7C3AED; } .l { stop-color: #7C3AED; }
  .n1 { stop-color: #4C1D95; } .n2 { stop-color: #7C3AED; }
  @media (prefers-color-scheme: dark) {
    .t { fill: #EDE4FF; } .s { fill: #A855F7; } .k { stroke: #A855F7; } .l { stop-color: #A855F7; }
    .n1 { stop-color: #F5EEFF; } .n2 { stop-color: #B98CFF; }
  }
"""

DEFS = """
  <linearGradient id="fl" x1="0" x2="1"><stop offset="0" class="l" stop-opacity="0"/><stop offset="1" class="l" stop-opacity="0.9"/></linearGradient>
  <linearGradient id="fr" x1="0" x2="1"><stop offset="0" class="l" stop-opacity="0.9"/><stop offset="1" class="l" stop-opacity="0"/></linearGradient>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
"""


def svg(h, body, style="", defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">\n'
        f"<style>{THEME}  text {{ font-family: {SANS}; }}\n{style}</style>\n"
        f"<defs>{DEFS}{defs}</defs>\n{body}\n</svg>\n"
    )


def diamond(cx, cy, r):
    return f'<path class="s" d="M{cx} {cy - r} L{cx + r} {cy} L{cx} {cy + r} L{cx - r} {cy} Z"/>'


def rules(cx, cy, gap, length, thickness=1.5):
    """A pair of fading rules either side of a centre gap."""
    return (
        f'<rect x="{cx - gap - length}" y="{cy - thickness / 2}" width="{length}" height="{thickness}" fill="url(#fl)"/>\n'
        f'<rect x="{cx + gap}" y="{cy - thickness / 2}" width="{length}" height="{thickness}" fill="url(#fr)"/>'
    )


def eye(cx, cy, scale=1.0):
    """Small almond eye glyph, the profile's motif."""
    w, h = 17 * scale, 9 * scale
    return (
        f'<g filter="url(#glow)"><path class="k" fill="none" stroke-width="1.4" '
        f'd="M{cx - w} {cy} Q{cx} {cy - h * 1.2} {cx + w} {cy} Q{cx} {cy + h * 1.2} {cx - w} {cy} Z"/>'
        f'<circle class="s" cx="{cx}" cy="{cy}" r="{3.4 * scale}"/></g>'
    )


def hero():
    """Alias in large spaced caps with roles cycling underneath."""
    cx, h = W / 2, 150
    spacing = 20
    roles = "\n".join(
        f'<text class="s role" x="{cx}" y="118" text-anchor="middle" font-size="15" letter-spacing="2" '
        f'font-family="{MONO}" style="animation-delay:{i * 3}s">{escape(r)}</text>'
        for i, r in enumerate(ROLES)
    )
    style = """
  .role { opacity: 0; animation: cycle 9s ease-in-out infinite; }
  @keyframes cycle { 0% { opacity: 0; } 4%, 30% { opacity: 1; } 34%, 100% { opacity: 0; } }
  @media (prefers-reduced-motion: reduce) { .role { animation: none; } .role:first-of-type { opacity: 1; } }
"""
    defs = '<linearGradient id="name" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="n1"/><stop offset="1" class="n2"/></linearGradient>'
    body = (
        f'<text x="{cx + spacing / 2}" y="76" text-anchor="middle" font-size="54" font-weight="700" '
        f'letter-spacing="{spacing}" fill="url(#name)" filter="url(#glow)">KVXTHE</text>\n'
        f"{rules(cx, 56, 196, 190)}\n{diamond(cx - 196, 56, 4)}\n{diamond(cx + 196, 56, 4)}\n"
        f"{roles}"
    )
    return svg(h, body, style, defs)


def divider(h=28):
    """Full-width hairline with the eye motif in the centre."""
    cx, cy = W / 2, h / 2
    body = (
        f"{rules(cx, cy, 34, cx - 34, 1.2)}\n{eye(cx, cy)}\n"
        f'<circle class="s" cx="{cx - 27}" cy="{cy}" r="1.6"/><circle class="s" cx="{cx + 27}" cy="{cy}" r="1.6"/>'
    )
    return svg(h, body)


def header(index, title, h=64):
    """Centered title: small index above, letter-spaced caps, fading rules with diamond ends."""
    cx, cy = W / 2, 40
    half = len(title) * 9.4 + 26  # approximate half-width of the spaced title plus breathing room
    body = (
        f'<text class="s" x="{cx}" y="14" text-anchor="middle" font-size="11" letter-spacing="4" '
        f'font-family="{MONO}">{index}</text>\n'
        f'<text class="t" x="{cx}" y="{cy + 7}" text-anchor="middle" font-size="20" font-weight="600" '
        f'letter-spacing="7" filter="url(#glow)">{escape(title)}</text>\n'
        f"{rules(cx, cy, half, 230)}\n{diamond(cx - half, cy, 4)}\n{diamond(cx + half, cy, 4)}"
    )
    return svg(h, body)


def label(text, h=26):
    """Small mono category label with short fading rules, used inside the stack section."""
    cx, cy = W / 2, 15
    half = len(text) * 5.2 + 14
    body = (
        f'<text class="s" x="{cx}" y="{cy + 4}" text-anchor="middle" font-size="11" letter-spacing="3.5" '
        f'font-family="{MONO}">{escape(text)}</text>\n{rules(cx, cy, half, 90, 1)}'
    )
    return svg(h, body)


def footer(h=64):
    cx = W / 2
    body = (
        f'<text class="t" x="{cx}" y="30" text-anchor="middle" font-size="16" font-weight="600" '
        f'letter-spacing="6" filter="url(#glow)">THANKS FOR VISITING</text>\n'
        f"{rules(cx, 50, 8, 170, 1)}\n{diamond(cx, 50, 3.5)}"
    )
    return svg(h, body)


FILES = {
    "hero.svg": hero(),
    "divider.svg": divider(),
    "header-about.svg": header("01", "ABOUT ME"),
    "header-stack.svg": header("02", "TECH STACK"),
    "header-stats.svg": header("03", "GITHUB ACTIVITY"),
    "label-languages.svg": label("LANGUAGES"),
    "label-backend.svg": label("BACKEND & DATA"),
    "label-tooling.svg": label("CLOUD & TOOLING"),
    "footer.svg": footer(),
}

if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets" / "ui"
    out.mkdir(parents=True, exist_ok=True)
    for name, content in FILES.items():
        (out / name).write_text(content, encoding="utf-8")
    print("wrote", ", ".join(FILES))
