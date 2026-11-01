"""Render assets/stats.svg: live GitHub activity in the same terminal style as terminal.svg.

Usage: GITHUB_TOKEN=... python scripts/stats.py
"""
import datetime as dt
import json
import os
import urllib.request
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

from common import TERMINAL_STYLE, USER, W, prompt, text, typed, window

LOGIN = "Kvxthe"
H = 512
CELL, GAP = 12, 2.5
LEVELS = ["#1A1129", "#3B1F6B", "#6D28D9", "#A855F7", "#E9D5FF"]
LANG_COLORS = ["#E9D5FF", "#C084FC", "#A855F7", "#7C3AED", "#5B21B6"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date weekday } }
      }
    }
  }
}
"""

STYLE = TERMINAL_STYLE + """
  .bar  { transform-box: fill-box; transform-origin: 0 50%; animation: grow 1s cubic-bezier(.2,.8,.2,1) both; }
  @keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
  .col  { opacity: 0; animation: show .4s ease-out both; }
  @media (prefers-reduced-motion: reduce) {
    .ln, .bar, .col, .cursor { animation: none; opacity: 1; transform: none; }
  }
"""


def fetch(token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": LOGIN},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    return payload["data"]["user"]


def streaks(days):
    """Current and longest run of days with at least one contribution."""
    best = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        best = max(best, run)
    current = 0
    tail = days[:-1] if days and not days[-1]["contributionCount"] else days  # today may still be empty
    for d in reversed(tail):
        if not d["contributionCount"]:
            break
        current += 1
    return current, best


def level(count, cuts):
    if not count:
        return 0
    return 1 + sum(count > c for c in cuts)


def build(user):
    cc = user["contributionsCollection"]
    weeks = cc["contributionCalendar"]["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    repos = user["repositories"]["nodes"]

    langs = Counter()
    for r in repos:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] += e["size"]
    total_size = sum(langs.values()) or 1
    top = langs.most_common(5)

    current, best = streaks(days)
    active = [d for d in days if d["contributionCount"]]
    by_weekday = Counter()
    by_month = Counter()
    for d in active:
        by_weekday[d["weekday"]] += d["contributionCount"]
        by_month[d["date"][:7]] += d["contributionCount"]
    weekday = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    busiest_day = weekday[by_weekday.most_common(1)[0][0]] if by_weekday else "-"
    busiest_month = (
        dt.date.fromisoformat(by_month.most_common(1)[0][0] + "-01").strftime("%B %Y") if by_month else "-"
    )

    summary = [
        ("contributions", f"{cc['contributionCalendar']['totalContributions']:,}"),
        ("commits", f"{cc['totalCommitContributions']:,}"),
        ("pull requests", f"{cc['totalPullRequestContributions']:,}"),
        ("issues", f"{cc['totalIssueContributions']:,}"),
        ("repositories", f"{user['repositories']['totalCount']:,}"),
        ("stars", f"{sum(r['stargazerCount'] for r in repos):,}"),
        ("streak", f"{current} day{'' if current == 1 else 's'}  (best {best})"),
        ("on github", f"since {user['createdAt'][:4]}"),
    ]

    type_defs, type_body = typed(70, "gh stats --last-year")
    desc = (
        f"GitHub activity for {LOGIN} over the last year: "
        + ", ".join(f"{k} {v}" for k, v in summary)
        + ". Top languages: "
        + ", ".join(f"{n} {s / total_size:.0%}" for n, s in top)
        + "."
    )
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">',
        '  <title id="t">kvxthe github activity</title>',
        f'  <desc id="d">{escape(desc)}</desc>',
        f"  <style>{STYLE}  </style>",
        f"  <defs>{type_defs}</defs>",
        window(H, USER + ": ~/activity"),
        type_body,
    ]

    d = 1.1
    p.append(f'  {text(24, 106, [("dim", "# summary")], d)}')
    for i, (k, v) in enumerate(summary):
        p.append(f'  {text(24, 132 + i * 22, [("key", k.ljust(15)), ("val", v)], d + 0.1 + i * 0.06)}')

    lx = 430
    p.append(f'  {text(lx, 106, [("dim", "# languages by size")], d)}')
    for i, (name, size) in enumerate(top):
        y = 132 + i * 22
        share = size / total_size
        delay = d + 0.1 + i * 0.06
        p.append(f'  {text(lx, y, [("val", name)], delay)}')
        p.append(f'  <rect x="548" y="{y - 9}" width="200" height="8" rx="2" fill="#1E1433"/>')
        p.append(
            f'  <rect class="bar" style="animation-delay:{delay + 0.1:.2f}s" x="548" y="{y - 9}" '
            f'width="{max(2, 200 * share):.1f}" height="8" rx="2" fill="{LANG_COLORS[i]}"/>'
        )
        p.append(f'  {text(W - 24, y, [("dim", f"{share:.0%}")], delay, anchor="end")}')
    if not top:
        p.append(f'  {text(lx, 132, [("dim", "no public code yet")], d + 0.1)}')

    hy = 132 + 6 * 22
    p.append(f'  {text(lx, hy, [("dim", "# rhythm")], d + 0.4)}')
    p.append(f'  {text(lx, hy + 22, [("key", "busiest day".ljust(15)), ("val", busiest_day)], d + 0.46)}')
    p.append(f'  {text(lx, hy + 44, [("key", "busiest month".ljust(15)), ("val", busiest_month)], d + 0.52)}')

    # contribution heatmap
    gy = 362
    p.append(f'  {text(24, 334, [("dim", "# contributions, last 12 months")], d + 0.6)}')
    cuts = sorted(x["contributionCount"] for x in active)
    cuts = [cuts[int(len(cuts) * q)] for q in (0.25, 0.5, 0.75)] if cuts else [0, 0, 0]
    last_month, last_x = None, -99
    for wi, w in enumerate(weeks):
        x = 24 + wi * (CELL + GAP)
        month = w["contributionDays"][-1]["date"][:7]
        if month != last_month:
            last_month = month
            if x - last_x >= 36 and wi < len(weeks) - 2:  # skip labels that would collide
                label = dt.date.fromisoformat(month + "-01").strftime("%b")
                p.append(f'  <text x="{x:.1f}" y="{gy - 7}" class="mono dim" style="font-size:10px">{label}</text>')
                last_x = x
        cells = "".join(
            f'<rect x="{x:.1f}" y="{gy + day["weekday"] * (CELL + GAP):.1f}" width="{CELL}" height="{CELL}" rx="2" '
            f'fill="{LEVELS[level(day["contributionCount"], cuts)]}"/>'
            for day in w["contributionDays"]
        )
        p.append(f'  <g class="col" style="animation-delay:{d + 0.7 + wi * 0.015:.2f}s">{cells}</g>')

    ly = 325  # legend sits on the heatmap title row
    lx2 = W - 24 - 5 * (CELL + GAP) - 34
    p.append(f'  {text(lx2 - 8, ly + 9, [("dim", "less")], d + 1.5, anchor="end")}')
    for i, c in enumerate(LEVELS):
        p.append(f'  <rect class="ln" style="animation-delay:{d + 1.5:.2f}s" x="{lx2 + i * (CELL + GAP):.1f}" y="{ly}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
    p.append(f'  {text(lx2 + 5 * (CELL + GAP) + 6, ly + 9, [("dim", "more")], d + 1.5)}')

    fy = H - 22
    p.append(prompt(fy, d + 1.7))
    p.append(f'  {text(W - 24, fy, [("dim", "# synced " + days[-1]["date"])], d + 1.7, anchor="end")}')
    p.append("</svg>")
    return "\n".join(p) + "\n"


if __name__ == "__main__":
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("set GITHUB_TOKEN (or GH_TOKEN) to query the GitHub API")
    out = Path(__file__).resolve().parent.parent / "assets" / "stats.svg"
    out.write_text(build(fetch(token)), encoding="utf-8")
    print(f"wrote {out.name}")
