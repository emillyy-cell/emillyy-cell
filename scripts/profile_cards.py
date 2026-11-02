"""Gera os cards de estatísticas do perfil (SVG) a partir da API GraphQL do GitHub.

Uso:  GITHUB_TOKEN=... python scripts/profile_cards.py <usuario> <pasta_saida>
      python scripts/profile_cards.py --demo <pasta_saida>   (dados fictícios, só para testar o visual)

Usa apenas a biblioteca padrão do Python.
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

BG, BORDER, PINK, TEXT, MUTED, DIM = "#0D0D0D", "#2B1320", "#F7A1C4", "#F2F2F2", "#9E9E9E", "#3D1F2E"
SHADES = ["#F7A1C4", "#E5739F", "#C9567F", "#F9D3E2", "#A8456B", "#7A3D58"]
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'Fira Code', Consolas, 'Courier New', monospace"
MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


# ----------------------------------------------------------------- dados

def graphql(query, variables, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        body = json.load(res)
    if "errors" in body:
        raise RuntimeError(body["errors"])
    return body["data"]


PROFILE_QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        isFork
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}"""

YEAR_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}"""


def fetch(login, token):
    user = graphql(PROFILE_QUERY, {"login": login}, token)["user"]
    today = dt.date.today()
    days, commits = {}, 0
    for year in range(int(user["createdAt"][:4]), today.year + 1):
        col = graphql(YEAR_QUERY, {
            "login": login,
            "from": f"{year}-01-01T00:00:00Z",
            "to": f"{year}-12-31T23:59:59Z",
        }, token)["user"]["contributionsCollection"]
        commits += col["totalCommitContributions"]
        for week in col["contributionCalendar"]["weeks"]:
            for d in week["contributionDays"]:
                if d["date"] <= today.isoformat():
                    days[d["date"]] = d["contributionCount"]

    langs = {}
    repos = user["repositories"]["nodes"]
    for repo in repos:
        if repo["isFork"]:
            continue
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]

    return {
        "commits": commits,
        "prs": user["pullRequests"]["totalCount"],
        "issues": user["issues"]["totalCount"],
        "followers": user["followers"]["totalCount"],
        "repos": user["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "langs": langs,
        "days": dict(sorted(days.items())),
    }


def demo():
    today = dt.date.today()
    days = {}
    for i in range(120, -1, -1):
        d = today - dt.timedelta(days=i)
        days[d.isoformat()] = (i * 7 + 3) % 5 if i % 6 else 0
    return {"commits": 58, "prs": 3, "issues": 1, "followers": 4, "repos": 7, "stars": 2,
            "langs": {"C": 20500, "HTML": 8400, "Python": 2200}, "days": days}


# ----------------------------------------------------------------- utilidades

def fmt_date(iso, year=False):
    d = dt.date.fromisoformat(iso)
    return f"{d.day} {MONTHS[d.month - 1]}" + (f" {d.year}" if year else "")


def streaks(days):
    items = list(days.items())
    longest = run = 0
    long_range = cur_range = (None, None)
    start = None
    for date, count in items:
        if count > 0:
            run += 1
            start = start or date
            if run > longest:
                longest, long_range = run, (start, date)
        else:
            run, start = 0, None
    # sequência atual: o dia de hoje ainda pode estar sem contribuições
    current = 0
    rev = items[::-1]
    if rev and rev[0][1] == 0:
        rev = rev[1:]
    end = rev[0][0] if rev else None
    for date, count in rev:
        if count == 0:
            break
        current += 1
        cur_range = (date, end)
    return current, cur_range, longest, long_range


def frame(w, h, title, body):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="{BG}" stroke="{BORDER}"/>
  <rect x="28" y="0.5" width="44" height="3" rx="1.5" fill="{PINK}"/>
  <text x="28" y="44" font-family="{SANS}" font-size="17" font-weight="600" fill="{PINK}">{escape(title)}</text>
{body}
</svg>
"""


# ----------------------------------------------------------------- cards

def stats_card(s):
    rows = [
        ("Commits (total)", s["commits"]),
        ("Repositórios públicos", s["repos"]),
        ("Pull requests", s["prs"]),
        ("Issues", s["issues"]),
        ("Estrelas recebidas", s["stars"]),
    ]
    body = ""
    for i, (label, value) in enumerate(rows):
        y = 84 + i * 28
        body += (f'  <circle cx="33" cy="{y - 5}" r="3.5" fill="{PINK}"/>\n'
                 f'  <text x="46" y="{y}" font-family="{SANS}" font-size="14" fill="{MUTED}">{label}</text>\n'
                 f'  <text x="452" y="{y}" text-anchor="end" font-family="{MONO}" font-size="14" fill="{TEXT}">{value}</text>\n')
    return frame(480, 230, "Estatísticas no GitHub", body)


def langs_card(s):
    total = sum(s["langs"].values()) or 1
    top = sorted(s["langs"].items(), key=lambda kv: -kv[1])[:6]
    x, bar = 28.0, ""
    for i, (name, size) in enumerate(top):
        w = 424 * size / total
        bar += f'    <rect x="{x:.1f}" y="66" width="{w:.1f}" height="10" fill="{SHADES[i]}"/>\n'
        x += w
    bar = (f'  <clipPath id="b"><rect x="28" y="66" width="424" height="10" rx="5"/></clipPath>\n'
           f'  <rect x="28" y="66" width="424" height="10" rx="5" fill="{DIM}"/>\n'
           f'  <g clip-path="url(#b)">\n{bar}  </g>\n')
    items = ""
    for i, (name, size) in enumerate(top):
        cx = 28 + (i % 2) * 220
        y = 110 + (i // 2) * 30
        items += (f'  <circle cx="{cx + 5}" cy="{y - 5}" r="5" fill="{SHADES[i]}"/>\n'
                  f'  <text x="{cx + 18}" y="{y}" font-family="{SANS}" font-size="14" fill="{TEXT}">{escape(name)}'
                  f' <tspan fill="{MUTED}">{100 * size / total:.1f}%</tspan></text>\n')
    if not top:
        items = f'  <text x="28" y="110" font-family="{SANS}" font-size="14" fill="{MUTED}">Sem dados de linguagens ainda.</text>\n'
    return frame(480, 230, "Linguagens mais usadas", bar + items)


def streak_card(s):
    days = s["days"]
    total = sum(days.values())
    current, cur_r, longest, long_r = streaks(days)
    first = next(iter(days)) if days else dt.date.today().isoformat()

    def rng(r):
        return f"{fmt_date(r[0])} – {fmt_date(r[1])}" if r[0] else "—"

    cols = [
        (160, str(total), "Contribuições", f"{fmt_date(first, True)} – hoje", TEXT),
        (480, str(current), "Sequência atual", rng(cur_r), PINK),
        (800, str(longest), "Maior sequência", rng(long_r), TEXT),
    ]
    body = (f'  <line x1="320" y1="70" x2="320" y2="190" stroke="{BORDER}"/>\n'
            f'  <line x1="640" y1="70" x2="640" y2="190" stroke="{BORDER}"/>\n'
            f'  <circle cx="480" cy="118" r="40" fill="none" stroke="{PINK}" stroke-width="4"/>\n')
    for cx, num, label, sub, color in cols:
        ny = 132 if cx == 480 else 128
        body += (f'  <text x="{cx}" y="{ny}" text-anchor="middle" font-family="{SANS}" font-size="30" font-weight="600" fill="{color}">{num}</text>\n'
                 f'  <text x="{cx}" y="{186 if cx == 480 else 162}" text-anchor="middle" font-family="{SANS}" font-size="14" fill="{PINK if cx == 480 else TEXT}">{label}</text>\n'
                 f'  <text x="{cx}" y="{206 if cx == 480 else 184}" text-anchor="middle" font-family="{SANS}" font-size="12" fill="{MUTED}">{sub}</text>\n')
    return frame(960, 230, "Sequência de contribuições", body)


def activity_card(s):
    last = list(s["days"].items())[-31:]
    w, h, left, right, top, bottom = 960, 300, 64, 32, 70, 250
    peak = max([c for _, c in last] + [4])
    step = (w - left - right) / max(len(last) - 1, 1)

    def pt(i, c):
        return left + i * step, bottom - (bottom - top) * c / peak

    pts = [pt(i, c) for i, (_, c) in enumerate(last)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{left},{bottom} {line} {pts[-1][0]:.1f},{bottom}" if pts else ""
    grid = ""
    for k in range(5):
        v = round(peak * k / 4)
        y = bottom - (bottom - top) * k / 4
        grid += (f'  <line x1="{left}" y1="{y:.1f}" x2="{w - right}" y2="{y:.1f}" stroke="{BORDER}" stroke-dasharray="{"0" if k == 0 else "3 5"}"/>\n'
                 f'  <text x="{left - 12}" y="{y + 4:.1f}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">{v}</text>\n')
    labels = ""
    for i, (date, _) in enumerate(last):
        if i % 5 == 0 or i == len(last) - 1:
            labels += f'  <text x="{pts[i][0]:.1f}" y="{bottom + 22}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}">{fmt_date(date)}</text>\n'
    dots = "".join(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{BG}" stroke="{PINK}" stroke-width="1.5"/>\n' for x, y in pts)
    body = (f'  <defs><linearGradient id="a" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{PINK}" stop-opacity="0.35"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/>'
            f'</linearGradient></defs>\n{grid}'
            f'  <polygon points="{area}" fill="url(#a)"/>\n'
            f'  <polyline points="{line}" fill="none" stroke="{PINK}" stroke-width="2" stroke-linejoin="round"/>\n'
            f'{dots}{labels}')
    return frame(w, h + 10, "Atividade nos últimos 31 dias", body)


TROPHIES = [  # (rótulo, chave, limites para os níveis 1 a 5)
    ("Commits", "commits", [1, 10, 50, 100, 500]),
    ("Repositórios", "repos", [1, 5, 10, 30, 50]),
    ("Contribuições", "total", [1, 50, 100, 500, 1000]),
    ("Linguagens", "nlangs", [1, 3, 5, 8, 10]),
    ("Pull requests", "prs", [1, 10, 25, 50, 100]),
    ("Seguidores", "followers", [1, 10, 50, 100, 500]),
]


def trophies_card(s):
    values = dict(s, total=sum(s["days"].values()), nlangs=len(s["langs"]))
    body = ""
    for i, (label, key, limits) in enumerate(TROPHIES):
        v = values[key]
        level = sum(v >= t for t in limits)
        cx = 28 + 76 + i * 151
        color = PINK if level else DIM
        stars = "".join(
            f'<circle cx="{cx - 24 + k * 12}" cy="150" r="3.5" fill="{PINK if k < level else DIM}"/>' for k in range(5))
        body += (f'  <circle cx="{cx}" cy="98" r="30" fill="none" stroke="{color}" stroke-width="2"/>\n'
                 f'  <text x="{cx}" y="105" text-anchor="middle" font-family="{SANS}" font-size="20" font-weight="600" fill="{TEXT if level else MUTED}">{v}</text>\n'
                 f'  {stars}\n'
                 f'  <text x="{cx}" y="180" text-anchor="middle" font-family="{SANS}" font-size="13" fill="{TEXT if level else MUTED}">{label}</text>\n')
    return frame(960, 210, "Troféus", body)


def main():
    if sys.argv[1] == "--demo":
        data, out = demo(), Path(sys.argv[2])
    else:
        data, out = fetch(sys.argv[1], os.environ["GITHUB_TOKEN"]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    cards = {
        "stats.svg": stats_card(data),
        "top-langs.svg": langs_card(data),
        "streak.svg": streak_card(data),
        "activity.svg": activity_card(data),
        "trophies.svg": trophies_card(data),
    }
    for name, svg in cards.items():
        (out / name).write_text(svg, encoding="utf-8")
    print("cards gerados:", ", ".join(cards))


if __name__ == "__main__":
    main()
