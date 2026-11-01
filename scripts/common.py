"""Shared palette, fonts and terminal-window chrome for the profile SVGs."""
from xml.sax.saxutils import escape

USER = "kvxthe@aegis"
W = 830

MONO = "'JetBrains Mono','Cascadia Mono','DejaVu Sans Mono',Menlo,Consolas,'Liberation Mono',monospace"
SANS = "'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"

BG, BAR, EDGE = "#0B0614", "#140B22", "#2A1A40"
SWATCHES = ["#2E1065", "#4C1D95", "#6D28D9", "#7C3AED", "#A855F7", "#C084FC", "#E9D5FF"]

TERMINAL_STYLE = f"""
  .mono {{ font-family: {MONO}; font-size: 13px; }}
  .key  {{ fill: #A855F7; }}
  .val  {{ fill: #E4DAF5; }}
  .dim  {{ fill: #7A6A94; }}
  .usr  {{ fill: #C084FC; font-weight: 700; }}
  .ln   {{ opacity: 0; animation: show .5s ease-out both; }}
  @keyframes show {{ from {{ opacity: 0; transform: translateX(-4px); }} to {{ opacity: 1; transform: none; }} }}
  .cursor {{ animation: blink 1.1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
"""


def text(x, y, parts, delay=None, anchor=None):
    """parts: list of (class, string). Fades in after `delay` seconds when given."""
    spans = "".join(f'<tspan class="{c}">{escape(s)}</tspan>' for c, s in parts)
    a = f' text-anchor="{anchor}"' if anchor else ""
    cls = "mono ln" if delay is not None else "mono"
    st = f' style="animation-delay:{delay:.2f}s"' if delay is not None else ""
    return f'<text x="{x}" y="{y}" class="{cls}"{a}{st} xml:space="preserve">{spans}</text>'


def window(h, title):
    """Rounded terminal window with traffic lights and a centred title."""
    return "\n".join([
        f'  <rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="10" fill="{BG}" stroke="{EDGE}"/>',
        f'  <path d="M0.5 36 V10.5 a10 10 0 0 1 10 -10 H{W - 10.5} a10 10 0 0 1 10 10 V36 Z" fill="{BAR}"/>',
        f'  <line x1="0" y1="36.5" x2="{W}" y2="36.5" stroke="{EDGE}"/>',
        '  <circle cx="22" cy="18.5" r="5.5" fill="#A855F7"/>',
        '  <circle cx="42" cy="18.5" r="5.5" fill="#3B2A55"/>',
        '  <circle cx="62" cy="18.5" r="5.5" fill="#3B2A55"/>',
        f'  {text(W / 2, 23, [("dim", title)], anchor="middle")}',
    ])


def typed(y, command, clip_id="type"):
    """Prompt line whose command types itself in; returns (defs, body)."""
    width = len(command) * 9 + 4
    defs = (
        f'<clipPath id="{clip_id}"><rect x="141" y="{y - 14}" height="20" width="0">'
        f'<animate attributeName="width" from="0" to="{width}" dur="0.8s" begin="0.3s" fill="freeze"/></rect></clipPath>'
    )
    body = (
        f'  {text(24, y, [("usr", USER), ("dim", ":~$ ")])}\n'
        f'  <text x="141" y="{y}" class="mono val" clip-path="url(#{clip_id})">{escape(command)}</text>'
    )
    return defs, body


def prompt(y, delay):
    """Closing prompt with a blinking cursor."""
    return (
        f'  {text(24, y, [("usr", USER), ("dim", ":~$ ")], delay)}\n'
        f'  <rect class="cursor" x="141" y="{y - 11}" width="8" height="14" fill="#C084FC"/>'
    )
