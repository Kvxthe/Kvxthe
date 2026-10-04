#!/usr/bin/env python3
"""Builds README.md, assets/*.svg and the workflows from config.json.

usage: python scripts/build.py [--status online|coding|offline|auto] [--only-status] [--force]
"""
import argparse, datetime as dt, json, math, os, random, re, shutil, sys, urllib.request
from html import escape as esc
from pathlib import Path

C = dict(
    black="#000000", deep="#0D1117", indigo="#4B0082", violet="#8A2BE2",
    sky="#00BFFF", cyan="#00FFFF",
)
FONT = "'JetBrains Mono','DejaVu Sans Mono','Cascadia Mono',Menlo,Consolas,'Liberation Mono',monospace"

STATES = {
    "online":  dict(label="ONLINE",  color=C["cyan"],   text=C["cyan"],   detail="available  /  open to chat", pulse=True),
    "coding":  dict(label="CODING",  color=C["violet"], text=C["sky"],    detail="focus mode", pulse=True),
    "offline": dict(label="OFFLINE", color=C["indigo"], text=C["violet"], detail="away  /  back soon", pulse=False),
}

DEFAULT_CONFIG = {
    "username": "Kvxthe",
    "name": "Kvxthe",
    "host": "Aegis",
    "snake": True,
    "role": "Software Engineering student",
    "neofetch": [
        ["role", "Software Engineering student"],
        ["langs", "Python / Java / JavaScript"],
        ["tools", "Git / GitHub / VS Code"],
        ["focus", "AI / architecture / security"],
        ["build", "Aegis / Forest Fire AI"],
    ],
    "stats": {"status": "curious / building", "uptime": "learning continuously", "location": "online"},
    "languages": [["Python", 100], ["Java", 64], ["JavaScript", 46]],
    "utc_offset": -5,
    "commit_hours": [60, 50, 30, 80, 30, 90, 70, 10, 40, 0, 10, 0, 0, 0, 0, 30, 40, 20, 50, 60, 100, 100, 70, 40],
    "trophies": [
        ["Started Forest Fire AI.", "sensors + ML + early detection"],
        ["Started Aegis.", "local AI + modular agents"],
        ["Started Software Engineering.", "OOP + patterns + architecture"],
        ["Reached target Build.", "learn / build / refactor"],
    ],
    "contact": [["github", "github.com/Kvxthe"], ["location", "online"]],
    "now": ["building Aegis, a local assistant", "forest fire detection with ML", "studying architecture and patterns"],
    "skills": [
        ["languages", "python", "Running", "3y", 85],
        ["languages", "java", "Running", "2y", 78],
        ["languages", "javascript", "Ready", "2y", 70],
        ["tooling", "git", "Running", "3y", 82],
        ["tooling", "github", "Running", "3y", 80],
        ["tooling", "vscode", "Ready", "3y", 76],
        ["ai", "scikit-learn", "Running", "1y", 60],
        ["ai", "local-agents", "Pending", "8mo", 55],
        ["engineering", "architecture", "Running", "2y", 80],
        ["engineering", "design-patterns", "Running", "2y", 75],
        ["engineering", "data-structures", "Ready", "2y", 70],
        ["security", "cybersecurity", "Pending", "1y", 50],
    ],
    "socials": [
        ["GitHub", "https://github.com/Kvxthe", "github"],
    ],
    "status": {
        "mode": "auto",
        "detect_push_minutes": 45,
        "windows": {"coding": ["09-13", "15-18", "20-23"], "online": ["07-09", "13-15", "18-20"]},
    },
}


COMMON_DEFS = f"""
<radialGradient id="neb" cx="1" cy="0" r=".95"><stop offset="0" stop-color="{C['indigo']}" stop-opacity=".55"/><stop offset=".55" stop-color="{C['indigo']}" stop-opacity=".12"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<radialGradient id="neb2" cx="0" cy="1" r=".8"><stop offset="0" stop-color="{C['violet']}" stop-opacity=".16"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<radialGradient id="halo"><stop offset=".55" stop-color="{C['indigo']}" stop-opacity="0"/><stop offset=".78" stop-color="{C['violet']}" stop-opacity=".55"/><stop offset=".9" stop-color="{C['indigo']}" stop-opacity=".35"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<radialGradient id="ring"><stop offset=".55" stop-color="{C['violet']}" stop-opacity="0"/><stop offset=".78" stop-color="{C['violet']}" stop-opacity=".9"/><stop offset=".92" stop-color="{C['violet']}" stop-opacity=".45"/><stop offset="1" stop-color="{C['violet']}" stop-opacity="0"/></radialGradient>
<radialGradient id="mid"><stop offset=".6" stop-color="{C['cyan']}" stop-opacity="0"/><stop offset=".82" stop-color="{C['cyan']}" stop-opacity=".75"/><stop offset="1" stop-color="{C['sky']}" stop-opacity="0"/></radialGradient>
<radialGradient id="core"><stop offset="0" stop-color="{C['cyan']}" stop-opacity=".9"/><stop offset=".3" stop-color="{C['sky']}" stop-opacity=".95"/><stop offset=".8" stop-color="{C['indigo']}" stop-opacity=".85"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<linearGradient id="bar1" x1="0" x2="1"><stop offset="0" stop-color="{C['violet']}"/><stop offset="1" stop-color="{C['cyan']}"/></linearGradient>
<linearGradient id="bar2" x1="0" x2="1"><stop offset="0" stop-color="{C['indigo']}"/><stop offset="1" stop-color="{C['sky']}"/></linearGradient>
<linearGradient id="bar3" x1="0" x2="1"><stop offset="0" stop-color="{C['indigo']}"/><stop offset="1" stop-color="{C['violet']}"/></linearGradient>
<linearGradient id="col1" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{C['violet']}"/><stop offset="1" stop-color="{C['cyan']}"/></linearGradient>
<filter id="b6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
"""

BASE_CSS = f"""
.m{{font-family:{FONT};font-size:12px}}
.val{{fill:{C['sky']}}} .dim{{fill:{C['violet']}}} .acc{{fill:{C['violet']}}} .cy{{fill:{C['cyan']}}} .sk{{fill:{C['sky']}}}
.usr{{fill:{C['violet']};font-weight:700}} .b{{font-weight:700}}
.cursor{{animation:blink 1.1s steps(1) infinite}} @keyframes blink{{50%{{opacity:0}}}}
.tw{{animation:tw 4.5s ease-in-out infinite}} @keyframes tw{{0%,100%{{opacity:.12}}50%{{opacity:.85}}}}
.r{{opacity:0;animation:show .45s ease-out forwards}} @keyframes show{{from{{opacity:0}}to{{opacity:1}}}}
.core{{transform-box:fill-box;transform-origin:50% 50%;animation:breathe 7s ease-in-out infinite}}
@keyframes breathe{{0%,100%{{transform:scale(1);opacity:.92}}50%{{transform:scale(1.08);opacity:1}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}} .r{{opacity:1!important}} .pend{{display:none}} .done{{opacity:1!important}} .bar,.col{{transform:none!important}}}}
"""


def svg(w, h, title, desc, body, defs="", css="", attrs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="t d"{attrs}>\n'
        f'  <title id="t">{esc(title)}</title>\n  <desc id="d">{esc(desc)}</desc>\n'
        f'  <defs>{COMMON_DEFS}{defs}</defs>\n  <style>{BASE_CSS}{css}</style>\n{body}\n</svg>\n'
    )


def stars(w, h, n, seed, top=36):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(6, w - 6), rnd.uniform(top, h - 6)
        r = rnd.choice([.5, .6, .8, 1.0, 1.3])
        col = rnd.choice([C["violet"], C["violet"], C["cyan"], C["sky"]])
        tw = f' class="tw" style="animation-delay:{rnd.uniform(0, 4.5):.1f}s"' if rnd.random() < .35 else ""
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" opacity="{rnd.uniform(.25, .7):.2f}"{tw}/>')
    return "<g>" + "".join(out) + "</g>"


def window(w, h, title, tb=30, nstars=22, seed=7):
    r = 10
    return f"""<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{r}" fill="{C['black']}"/>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{r}" fill="url(#neb)"/>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{r}" fill="url(#neb2)"/>
{stars(w, h, nstars, seed, tb + 6)}
<path d="M.5 {tb} V{r+.5} a{r} {r} 0 0 1 {r} -{r} H{w-r-.5} a{r} {r} 0 0 1 {r} {r} V{tb} Z" fill="{C['deep']}" fill-opacity=".93"/>
<line x1="0" y1="{tb+.5}" x2="{w}" y2="{tb+.5}" stroke="{C['indigo']}"/>
<circle cx="18" cy="{tb/2}" r="4.5" fill="{C['cyan']}"/><circle cx="34" cy="{tb/2}" r="4.5" fill="{C['violet']}"/><circle cx="50" cy="{tb/2}" r="4.5" fill="{C['indigo']}"/>
<text x="{w/2}" y="{tb/2+4}" text-anchor="middle" class="m dim">{esc(title)}</text>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{r}" fill="none" stroke="{C['indigo']}"/>"""


def eye(cx, cy, s=1.0, orbits=True):
    orb = ""
    if orbits:
        orb = f"""<g transform="scale(1 .68)">
  <circle r="118" fill="none" stroke="{C['violet']}" stroke-width="1.4" stroke-dasharray="2 11" opacity=".75"><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="90s" repeatCount="indefinite"/></circle>
  <circle r="92" fill="none" stroke="{C['cyan']}" stroke-width="1.2" stroke-dasharray="1 7" opacity=".5"><animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="60s" repeatCount="indefinite"/></circle>
</g>"""
    rnd = random.Random(42)
    wisps = ""
    for i in range(9):
        a = rnd.uniform(0, 6.283)
        rx, ry = 104 + rnd.uniform(-6, 10), 70 + rnd.uniform(-4, 8)
        px, py = rx * math.cos(a), ry * math.sin(a)
        wisps += (f'<ellipse cx="{px:.0f}" cy="{py:.0f}" rx="{rnd.uniform(10, 22):.0f}" ry="{rnd.uniform(5, 10):.0f}" '
                  f'transform="rotate({a*57.3+90:.0f} {px:.0f} {py:.0f})" fill="{rnd.choice([C["violet"], C["indigo"], C["violet"]])}" opacity="{rnd.uniform(.22, .4):.2f}" filter="url(#b6)"/>')
    return f"""<g transform="translate({cx} {cy}) rotate(-14) scale({s})">
  <ellipse rx="130" ry="88" fill="url(#halo)"/>
  {wisps}
  <ellipse rx="108" ry="74" fill="none" stroke="{C['violet']}" stroke-width="12" opacity=".35" filter="url(#b6)"/>
  <ellipse rx="98" ry="66" fill="url(#ring)"/>
  <ellipse rx="76" ry="52" fill="url(#mid)"/>
  <ellipse class="core" rx="56" ry="40" fill="url(#core)"/>
  {orb}
  <circle r="2.4" fill="{C['cyan']}" filter="url(#glow)"/>
</g>"""


def fmt(n):
    return f"{n:,}" if isinstance(n, int) else str(n)


def recent_push(username, minutes):
    if not username:
        return False
    try:
        req = urllib.request.Request(f"https://api.github.com/users/{username}/events/public?per_page=30",
                                     headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-status"})
        if os.environ.get("GITHUB_TOKEN"):
            req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
        with urllib.request.urlopen(req, timeout=10) as r:
            events = json.load(r)
        now = dt.datetime.now(dt.timezone.utc)
        for e in events:
            if e.get("type") == "PushEvent":
                t = dt.datetime.fromisoformat(e["created_at"].replace("Z", "+00:00"))
                if (now - t).total_seconds() <= minutes * 60:
                    return True
    except Exception:
        pass
    return False


def resolve_status(cfg, override=None):
    s = cfg.get("status", {})
    mode = override or s.get("mode", "auto")
    if mode in STATES:
        return mode
    if s.get("detect_push_minutes") and recent_push(cfg["username"], s["detect_push_minutes"]):
        return "coding"
    h = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=cfg.get("utc_offset", 0))).hour
    for state in ("coding", "online"):
        for win in s.get("windows", {}).get(state, []):
            a, b = map(int, win.split("-"))
            if (a <= h < b) if a < b else (h >= a or h < b):
                return state
    return "offline"


def status_svg(cfg, state, since):
    st = STATES[state]
    col = st["color"]
    w, h = 830, 64
    pulse = ""
    if st["pulse"]:
        pulse = f'<circle cx="352" cy="32" r="5" fill="none" stroke="{col}" stroke-width="1.5"><animate attributeName="r" values="5;15" dur="2.2s" repeatCount="indefinite"/><animate attributeName="opacity" values=".8;0" dur="2.2s" repeatCount="indefinite"/></circle>'
    extra = ""
    if state == "coding":  # equalizer bars: typing rhythm
        for i, d in enumerate((0.0, 0.25, 0.1, 0.4)):
            x = 478 + i * 7
            extra += (f'<rect x="{x}" y="24" width="3" height="16" rx="1.5" fill="{C["cyan"]}" opacity=".85" style="transform-box:fill-box;transform-origin:50% 100%;animation:eq 1.1s ease-in-out {d}s infinite"/>')
    elif state == "online":
        extra = f'<path d="M482 36 q8 -14 16 0" fill="none" stroke="{C["sky"]}" stroke-width="2" stroke-linecap="round" opacity=".9"/><path d="M486 36 q4 -7 8 0" fill="none" stroke="{C["cyan"]}" stroke-width="2" stroke-linecap="round"/>'
    dotfill = col if st["pulse"] else C["black"]
    body = f"""<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="{C['black']}"/>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="url(#neb)"/>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="url(#neb2)"/>
{stars(w, h, 26, 11, 4)}
{eye(38, 32, .2, orbits=False)}
<text x="76" y="27" class="m dim" style="font-size:11px;letter-spacing:3px">MAIN STATUS</text>
<text x="76" y="47" class="m"><tspan class="usr" style="font-size:13px">{esc(cfg['username'])}@{esc(cfg['host'])}</tspan><tspan class="dim" style="font-size:13px">:~$ status</tspan></text>
<rect x="330" y="14" width="190" height="36" rx="18" fill="{C['deep']}" stroke="{col}" stroke-opacity=".85"/>
{pulse}<circle cx="352" cy="32" r="5" fill="{dotfill}" stroke="{col}" stroke-width="1.5" filter="url(#glow)"/>
<text x="370" y="37.5" class="m b" style="font-size:15px;letter-spacing:2.5px" fill="{st['text']}">{st['label']}</text>
{extra}
<text x="812" y="27" text-anchor="end" class="m val" style="font-size:12px">{esc(st['detail'])}</text>
<text x="812" y="47" text-anchor="end" class="m dim" style="font-size:11px">since {since}</text>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="none" stroke="{C['indigo']}"/>"""
    css = "@keyframes eq{0%,100%{transform:scaleY(.3)}50%{transform:scaleY(1)}}"
    return svg(w, h, f"Main status: {st['label']}",
               f"Main status indicator for {cfg['username']}: currently {state}.", body, css=css,
               attrs=f' data-state="{state}"')


def write_status(cfg, assets, state, force=False):
    cur = assets / "status.svg"
    if cur.exists() and not force and f'data-state="{state}"' in cur.read_text(encoding="utf-8"):
        print(f"status unchanged ({state})")
        return state
    since = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cur.write_text(status_svg(cfg, state, since), encoding="utf-8")
    for s in STATES:
        (assets / f"status-{s}.svg").write_text(status_svg(cfg, s, "manual"), encoding="utf-8")
    print(f"status -> {state}")
    return state


def hero(cfg):
    w, h = 830, 424
    rows = [(k, v, "info") for k, v in cfg["neofetch"]]
    rows.append(None)
    rows += [(k, fmt(v), "stat") for k, v in cfg["stats"].items()]
    y = 150
    lines = ""
    i = 0
    for r in rows:
        if r is None:
            lines += f'<line class="r" style="animation-delay:{1.0+i*.14:.2f}s" x1="390" y1="{y-14}" x2="790" y2="{y-14}" stroke="{C["indigo"]}"/>'
            y += 8
            i += 1
            continue
        k, v, kind = r
        vcls = "cy" if kind == "stat" else "val"
        lines += (f'<text class="r m" style="animation-delay:{1.0+i*.14:.2f}s;font-size:13px" x="390" y="{y}">'
                  f'<tspan class="acc b">{esc(k)}</tspan><tspan x="510" class="{vcls}">{esc(str(v))}</tspan></text>')
        y += 24
        i += 1
    blocks = ""
    for j, col in enumerate([C["black"], C["deep"], C["indigo"], C["violet"], C["sky"], C["cyan"]]):
        blocks += f'<rect class="r" style="animation-delay:{2.4+j*.06:.2f}s" x="{390+j*26}" y="{y+2}" width="22" height="14" fill="{col}" stroke="{C["indigo"]}"/>'
    ps1 = f'<tspan class="usr">{esc(cfg["username"])}@{esc(cfg["host"])}</tspan><tspan class="dim">:~$ </tspan>'
    body = f"""{window(w, h, f"{cfg['username']}@{cfg['host']}: ~", 36, 60, 21)}
{eye(190, 218, 1.3)}
<text x="190" y="366" text-anchor="middle" class="m dim" style="font-size:11px;letter-spacing:1px">NGC 7293  /  Helix Nebula</text>
<text x="390" y="70" class="m" style="font-size:13px">{ps1}</text>
<text x="{390+(len(cfg['username']+cfg['host'])+5)*7.8:.0f}" y="70" class="m val" style="font-size:13px" clip-path="url(#type)">neofetch</text>
<text class="r m" style="animation-delay:.9s;font-size:15px" x="390" y="104"><tspan class="usr">{esc(cfg['name'])}</tspan></text>
<text class="r m dim" style="animation-delay:.9s;font-size:12px" x="390" y="122">{'-' * 36}</text>
{lines}{blocks}
<text x="390" y="{y+42}" class="m" style="font-size:13px">{ps1}<tspan class="cursor" fill="{C['cyan']}">&#9608;</tspan></text>"""
    tx = 390 + (len(cfg['username'] + cfg['host']) + 5) * 7.8
    defs = f'<clipPath id="type"><rect x="{tx:.0f}" y="54" height="22" width="0"><animate attributeName="width" from="0" to="80" dur=".8s" begin=".3s" fill="freeze"/></rect></clipPath>'
    return svg(w, h, f"{cfg['username']} terminal",
               f"Terminal running neofetch beside the Helix Nebula. {cfg['name']}, {cfg['role']}. "
               + ", ".join(f"{k}: {v}" for k, v in cfg['neofetch']) + ". "
               + ", ".join(f"{fmt(v)} {k}" for k, v in cfg['stats'].items()) + ".", body, defs)


def kubectl(cfg):
    sk = cfg["skills"]
    w, row = 830, 22
    y0 = 108
    foot = y0 + len(sk) * row + 10
    h = foot + 52
    smap = {"Running": C["cyan"], "Ready": C["sky"], "Pending": C["violet"], "Completed": C["violet"]}
    cols = dict(ns=20, name=138, st=300, age=420, cap=500)
    rows = ""
    for i, (ns, name, status, age, cap) in enumerate(sk):
        y = y0 + i * row
        d = 2.6 + i * .11
        col = smap.get(status, C["violet"])
        fillw = int(180 * cap / 100)
        grad = "url(#bar1)" if cap >= 75 else ("url(#bar2)" if cap >= 55 else "url(#bar3)")
        rows += (f'<g class="r" style="animation-delay:{d:.2f}s">'
                 f'<text class="m dim" x="{cols["ns"]}" y="{y}">{esc(ns)}</text>'
                 f'<text class="m val b" x="{cols["name"]}" y="{y}">{esc(name)}</text>'
                 f'<circle cx="{cols["st"]+3}" cy="{y-4}" r="3" fill="{col}"/>'
                 f'<text class="m" x="{cols["st"]+14}" y="{y}" fill="{col}">{esc(status)}</text>'
                 f'<text class="m val" x="{cols["age"]}" y="{y}">{esc(age)}</text>'
                 f'<rect x="{cols["cap"]}" y="{y-9}" width="180" height="8" rx="2" fill="{C["indigo"]}" fill-opacity=".4"/>'
                 f'<rect class="bar" x="{cols["cap"]}" y="{y-9}" width="{fillw}" height="8" rx="2" fill="{grad}" '
                 f'style="transform-box:fill-box;transform-origin:0 50%;animation:grow 1.1s cubic-bezier(.2,.8,.2,1) {d+.2:.2f}s both"/>'
                 f'<text class="m cy" x="696" y="{y}">{cap}%</text></g>')
    ready = sum(1 for s in sk if s[2] in ("Running", "Ready"))
    cmd = "kubectl get signals --all-namespaces"
    body = f"""{window(w, h, f"kubectl: {cfg['host'].lower()}-01", 30, 70, 5)}
<text x="20" y="54" class="m" style="font-size:13px"><tspan class="acc b">$</tspan></text>
<text x="36" y="54" class="m val" style="font-size:13px" clip-path="url(#ty)">{cmd}</text>
<g class="r" style="animation-delay:2.2s">
<rect x="12" y="68" width="{w-24}" height="22" fill="{C['indigo']}" fill-opacity=".85"/>
<text class="m val b" x="{cols['ns']}" y="83">NAMESPACE</text><text class="m val b" x="{cols['name']}" y="83">NAME</text>
<text class="m val b" x="{cols['st']+14}" y="83">STATUS</text><text class="m val b" x="{cols['age']}" y="83">AGE</text>
<text class="m val b" x="{cols['cap']}" y="83">CAPACITY</text></g>
{rows}
<text class="r m dim" style="animation-delay:{2.8+len(sk)*.11:.2f}s" x="20" y="{foot+8}"># {len(sk)} signals / {ready} ready / cluster {esc(cfg['host'].lower())}-01</text>
<text x="20" y="{foot+34}" class="m" style="font-size:13px"><tspan class="acc b">$</tspan><tspan class="cursor" x="36" fill="{C['cyan']}">&#9608;</tspan></text>"""
    defs = (f'<clipPath id="ty"><rect x="36" y="40" height="20" width="0"><animate attributeName="width" from="0" to="290" dur="1.7s" begin=".3s" fill="freeze"/></rect></clipPath>')
    css = "@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
    return svg(w, h, "kubectl get signals", "Terminal running kubectl get signals --all-namespaces. Skills as Kubernetes resources: "
               + "; ".join(f"{s[0]}/{s[1]} {s[2]} {s[3]} {s[4]}%" for s in sk), body, defs, css)


def languages(cfg):
    L = cfg["languages"][:5]
    fills = ["url(#bar1)", "url(#bar2)", "url(#bar3)", C["violet"], C["indigo"]]
    names = bars = tracks = ""
    for i, (n, v) in enumerate(L):
        y = 112 + i * (28 if len(L) >= 5 else 36)
        names += f'<text x="20" y="{y}">{esc(n)}</text>'
        tracks += f'<rect x="120" y="{y-10}" width="260" height="10" rx="2"/>'
        bars += (f'<rect class="bar" x="120" y="{y-10}" width="{260*v/100:.0f}" height="10" rx="2" fill="{fills[i]}" '
                 f'style="transform-box:fill-box;transform-origin:0 50%;animation:fill 8s cubic-bezier(.2,.8,.2,1) {i*.15:.2f}s infinite both"/>')
    body = f"""{window(405, 260, "htop: languages", 30, 26, 3)}
<text x="16" y="54" class="m"><tspan class="acc b">$</tspan><tspan class="val"> htop --sort commits</tspan></text>
<rect x="12" y="66" width="381" height="18" fill="{C['indigo']}"/>
<text x="20" y="79" class="m val b">LANGUAGE</text><text x="120" y="79" class="m val b">COMMITS</text>
<g class="m val">{names}</g><g fill="{C['indigo']}" fill-opacity=".4">{tracks}</g>{bars}
<text x="16" y="248" class="m dim"># {len(L)} languages, sorted by commits</text>"""
    css = "@keyframes fill{0%,4%{transform:scaleX(0)}30%,88%{transform:scaleX(1)}96%,100%{transform:scaleX(0)}}"
    return svg(405, 260, "htop languages", "Languages sorted by commits: " + ", ".join(n for n, _ in L) + ".", body, css=css)


def hours(cfg):
    H = cfg["commit_hours"]
    mx = max(H) or 1
    bars = ""
    for i, v in enumerate(H):
        hh = 10 + 100 * v / mx
        x = 22 + i * 15
        col = "url(#col1)" if v >= 0.85 * mx else (C["violet"] if v >= 0.5 * mx else C["indigo"])
        bars += (f'<rect class="col" x="{x}" y="{196-hh:.0f}" width="10" height="{hh:.0f}" rx="1.5" fill="{col}" '
                 f'style="transform-box:fill-box;transform-origin:50% 100%;animation:rise 8s cubic-bezier(.2,.8,.2,1) {i*.05:.2f}s infinite both"/>')
    runs, cur = [], []
    for i, v in enumerate(H):
        if v >= 0.85 * mx:
            cur.append(i)
        elif cur:
            runs.append(cur); cur = []
    if cur:
        runs.append(cur)
    best = max(runs, key=lambda r: sum(H[i] for i in r)) if runs else []
    lab = lambda hr: f"{hr % 12 or 12}{'am' if hr % 24 < 12 else 'pm'}"
    note = f"busiest {lab(best[0])} to {lab(best[-1]+1)}" if best else "no peak yet"
    ticks = "".join(f'<text x="{27+k*15}" y="214">{k}</text>' for k in (0, 6, 12, 18, 23))
    body = f"""{window(405, 260, "git: commit hours", 30, 26, 4)}
<text x="16" y="54" class="m"><tspan class="acc b">$</tspan><tspan class="val"> git shortlog --by-hour</tspan></text>
<text x="16" y="76" class="m dim"># commits by hour of day (UTC{cfg.get('utc_offset', 0):+d})</text>
<line x1="18" y1="196.5" x2="388" y2="196.5" stroke="{C['indigo']}"/>{bars}
<g class="m dim" text-anchor="middle">{ticks}</g>
<text x="16" y="248" class="m dim"># {note}</text>"""
    css = "@keyframes rise{0%,3%{transform:scaleY(0)}26%,88%{transform:scaleY(1)}96%,100%{transform:scaleY(0)}}"
    return svg(405, 260, "commits by hour", f"Bar chart of commits by hour of day, {note}.", body, css=css)


def trophies(cfg):
    T = cfg["trophies"][:4]
    g = ""
    for i, (a, b) in enumerate(T):
        y = 88 + i * 40
        d = i * 1.5
        g += f"""<g class="m"><g class="row" style="animation-delay:{d}s"><text x="84" y="{y}" class="val">{esc(a)}</text><text x="84" y="{y+16}" class="dim">{esc(b)}</text></g>
<text class="pend" style="animation-delay:{d}s" x="16" y="{y}"><tspan class="dim">[ .... ]</tspan></text>
<text class="done" style="animation-delay:{d}s" x="16" y="{y}"><tspan class="dim">[</tspan><tspan class="cy">  OK  </tspan><tspan class="dim">]</tspan></text></g>"""
    body = f"""{window(405, 260, "journalctl: milestones", 30, 26, 5)}
<text x="16" y="54" class="m"><tspan class="acc b">$</tspan><tspan class="val"> journalctl -u milestones</tspan></text>
{g}"""
    css = """.row{opacity:0;animation:rowa 12s infinite both}.pend{opacity:0;animation:pend 12s infinite both}.done{opacity:0;animation:done 12s infinite both}
@keyframes rowa{0%{opacity:0}3%,92%{opacity:1}96%,100%{opacity:0}}@keyframes pend{0%{opacity:0}3%,12%{opacity:1}14%,100%{opacity:0}}@keyframes done{0%,12%{opacity:0}14%,92%{opacity:1}96%,100%{opacity:0}}
@media (prefers-reduced-motion:reduce){.row{opacity:1!important}}"""
    return svg(405, 260, "milestones boot log", "Boot log of milestones: " + "; ".join(a for a, _ in T), body, css=css)


def contact(cfg):
    C1, N = cfg["contact"][:3], cfg["now"][:4]
    u = f'<tspan class="usr">{esc(cfg["username"])}@{esc(cfg["host"])}</tspan><tspan class="dim">:~$</tspan>'
    cx = 16 + (len(cfg["username"]) + len(cfg["host"]) + 4) * 7.2 + 8
    y = 78
    t = ""
    for i, (k, v) in enumerate(C1):
        t += f'<text class="r" style="animation-delay:{.9+i*.25:.2f}s" x="16" y="{y}"><tspan class="acc">{esc(k)}</tspan><tspan x="90" class="val">{esc(v)}</tspan></text>'
        y += 20
    y += 8
    t += f'<text x="16" y="{y}">{u}</text><text x="{cx:.0f}" y="{y}" class="val" clip-path="url(#c2)">cat now.txt</text>'
    ycmd = y
    for i, n in enumerate(N):
        y += 22
        t += f'<text class="r" style="animation-delay:{3.0+i*.3:.2f}s" x="16" y="{y}"><tspan class="dim">&gt;</tspan><tspan x="30" class="val">{esc(n)}</tspan></text>'
    y += 26
    t += f'<g class="r" style="animation-delay:4.4s"><text x="16" y="{y}">{u}</text><rect class="cursor" x="{cx:.0f}" y="{y-11}" width="7" height="13" fill="{C["cyan"]}"/></g>'
    defs = (f'<clipPath id="c1"><rect x="{cx:.0f}" y="40" height="20" width="0"><animate attributeName="width" from="0" to="120" dur=".9s" begin=".1s" fill="freeze"/></rect></clipPath>'
            f'<clipPath id="c2"><rect x="{cx:.0f}" y="{ycmd-14}" height="20" width="0"><animate attributeName="width" from="0" to="90" dur=".8s" begin="2.2s" fill="freeze"/></rect></clipPath>')
    body = f"""{window(405, 260, f"{cfg['username']}@{cfg['host']}: ~", 30, 26, 6)}
<g class="m"><text x="16" y="54">{u}</text><text x="{cx:.0f}" y="54" class="val" clip-path="url(#c1)">cat contact.txt</text>{t}</g>"""
    return svg(405, 260, "contact and now", "Contact: " + ", ".join(f"{k} {v}" for k, v in C1) + ". Now: " + "; ".join(N) + ".", body, defs)


def divider():
    body = f"""<defs><linearGradient id="dv" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="830" y2="0"><stop offset="0" stop-color="{C['black']}"/><stop offset=".25" stop-color="{C['indigo']}"/><stop offset=".5" stop-color="{C['violet']}"/><stop offset=".75" stop-color="{C['indigo']}"/><stop offset="1" stop-color="{C['black']}"/></linearGradient></defs>
<path d="M0 14H830" stroke="url(#dv)" stroke-width="1.2"/>
<g transform="translate(415 14) scale(.16)"><g transform="rotate(-14)"><ellipse rx="130" ry="88" fill="url(#halo)"/><ellipse rx="98" ry="66" fill="url(#ring)"/><ellipse rx="76" ry="52" fill="url(#mid)"/><ellipse rx="56" ry="40" fill="url(#core)"/></g></g>"""
    return svg(830, 28, "divider", "Decorative divider with a small nebula eye.", body)


def readme(cfg, state):
    u = cfg["username"]
    st = STATES[state]
    snake = ""
    if cfg.get("snake"):
        snake = (f'\n<img src="https://raw.githubusercontent.com/{u}/{u}/output/snake.svg" width="830" '
                 f'alt="Contribution graph snake in purple and cyan">\n')
    badges = "\n".join(
        f'<a href="{esc(url)}"><img src="https://img.shields.io/badge/{esc(name)}-4B0082?style=for-the-badge&logo={logo}&logoColor=00FFFF&labelColor=000000" alt="{esc(name)}"></a>'
        for name, url, logo in cfg["socials"])
    n = len(cfg["skills"])
    return f"""<div align="center">

<img src="assets/status.svg" width="830" alt="Main status: {st['label']}">
<br>
<img src="assets/terminal.svg" width="830" alt="{esc(cfg['name'])}: {esc(cfg['role'])}. {esc(', '.join(f'{k}: {v}' for k, v in cfg['neofetch']))}.">
<br>
<img src="assets/kubectl.svg" width="830" alt="kubectl get signals --all-namespaces: {n} skills listed as Kubernetes resources.">
<br>
<img src="assets/languages.svg" width="405" alt="Languages by commits: {esc(', '.join(l for l, _ in cfg['languages']))}.">
<img src="assets/hours.svg" width="405" alt="Commits by hour of day.">
<br>
<img src="assets/trophies.svg" width="405" alt="Trophies: {esc('; '.join(t for t, _ in cfg['trophies']))}">
<img src="assets/contact.svg" width="405" alt="Contact and what I am doing now.">
<br>
<img src="assets/divider.svg" width="830" alt="">
{snake}
{badges}

<br>

<sub><code>{esc(u)}@{esc(cfg['host'])}:~$ echo "keep building."</code></sub>

</div>
"""


def workflows(cfg, root):
    wf = root / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf / "snake.yml").write_text(f"""name: generate snake animation

on:
  schedule:
    - cron: "0 */12 * * *"
  workflow_dispatch:
  push:
    branches:
      - main

jobs:
  generate:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: generate snake.svg
        uses: Platane/snk@v3
        id: snake-gif
        with:
          github_user_name: {cfg['username']}
          outputs: |
            dist/snake.svg?palette=github-dark&color_snake=#00FFFF&color_dots=#0D1117,#4B0082,#8A2BE2,#00BFFF,#00FFFF

      - name: push to output branch
        uses: crazy-max/ghaction-github-pages@v4
        with:
          target_branch: output
          build_dir: dist
        env:
          GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
""", encoding="utf-8")
    (wf / "status.yml").write_text("""name: update main status

on:
  schedule:
    - cron: "*/30 * * * *"
  workflow_dispatch:
    inputs:
      status:
        description: "Status"
        type: choice
        default: auto
        options: [auto, online, coding, offline]
  push:
    paths: [config.json]

jobs:
  status:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: render status
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python scripts/build.py --only-status --status "${{ github.event.inputs.status || 'auto' }}"
      - name: commit if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add assets/status*.svg
          git diff --staged --quiet || (git commit -m "chore: update main status" && git push)
""", encoding="utf-8")


def dump_config(cfg):
    text = json.dumps(cfg, indent=2, ensure_ascii=False)
    return re.sub(r"\[([^\[\]]*)\]", lambda m: "[" + re.sub(r"\s*\n\s*", " ", m.group(1)).strip() + "]", text) + "\n"


def main():
    here = Path(__file__).resolve()
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", help="project root (default: parent of scripts/ or script folder)")
    ap.add_argument("--status", default=None, choices=["auto", "online", "coding", "offline"])
    ap.add_argument("--only-status", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else (here.parent.parent if here.parent.name == "scripts" else here.parent)
    cfgp = root / "config.json"
    if not cfgp.exists():
        cfgp.write_text(dump_config(DEFAULT_CONFIG), encoding="utf-8")
        print("wrote config.json")
    cfg = json.loads(cfgp.read_text(encoding="utf-8"))
    for k, v in DEFAULT_CONFIG.items():
        cfg.setdefault(k, v)

    assets = root / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    state = resolve_status(cfg, None if a.status in (None, "auto") else a.status)

    if a.only_status:
        write_status(cfg, assets, state, a.force)
        return

    dest = root / "scripts" / "build.py"
    if here != dest:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(here, dest)

    write_status(cfg, assets, state, True)
    files = {
        "terminal.svg": hero(cfg), "kubectl.svg": kubectl(cfg), "languages.svg": languages(cfg),
        "hours.svg": hours(cfg), "trophies.svg": trophies(cfg), "contact.svg": contact(cfg), "divider.svg": divider(),
    }
    for name, content in files.items():
        (assets / name).write_text(content, encoding="utf-8")
    (root / "README.md").write_text(readme(cfg, state), encoding="utf-8")
    workflows(cfg, root)
    print(f"done: {len(files) + 4} assets + README.md + 2 workflows in {root}")


if __name__ == "__main__":
    sys.exit(main())
