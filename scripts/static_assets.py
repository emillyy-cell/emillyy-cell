"""Gera banner, rodapé e cards de projeto (SVG) para o README do perfil."""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(sys.argv[1])
(OUT / "cards").mkdir(parents=True, exist_ok=True)

BG, BORDER, PINK, TEXT, MUTED = "#0D0D0D", "#2B1320", "#F7A1C4", "#F2F2F2", "#9E9E9E"
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'Fira Code', Consolas, 'Courier New', monospace"

banner = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="320" viewBox="0 0 1200 320" role="img" aria-label="Emilly Lorrany Alves dos Santos — Transformando curiosidade em conhecimento e ideias em soluções.">
  <defs>
    <radialGradient id="glow" cx="88%" cy="10%" r="60%">
      <stop offset="0" stop-color="{PINK}" stop-opacity="0.22"/>
      <stop offset="1" stop-color="{PINK}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="line" x1="0" x2="1">
      <stop offset="0" stop-color="{PINK}"/>
      <stop offset="1" stop-color="{PINK}" stop-opacity="0"/>
    </linearGradient>
    <style>
      .cursor {{ animation: blink 1.1s steps(1) infinite; }}
      @keyframes blink {{ 50% {{ opacity: 0; }} }}
    </style>
  </defs>
  <rect width="1200" height="320" rx="18" fill="{BG}"/>
  <rect width="1200" height="320" rx="18" fill="url(#glow)"/>
  <g fill="none" stroke="{PINK}" stroke-width="1.2">
    <path d="M760 320 C 880 220, 980 260, 1200 120" stroke-opacity="0.28"/>
    <path d="M840 320 C 940 250, 1040 280, 1200 190" stroke-opacity="0.18"/>
    <path d="M920 320 C 1000 280, 1100 300, 1200 255" stroke-opacity="0.1"/>
  </g>
  <rect x="0.5" y="0.5" width="1199" height="319" rx="18" fill="none" stroke="{BORDER}"/>

  <g>
    <text x="80" y="92" font-family="{MONO}" font-size="17" fill="{PINK}">~/emillyy-cell</text>
    <rect class="cursor" x="226" y="78" width="9" height="18" fill="{PINK}"/>
  </g>
  <text x="78" y="160" font-family="{SANS}" font-size="50" font-weight="600" fill="{TEXT}" letter-spacing="-0.5">Emilly Lorrany Alves dos Santos</text>
  <text x="80" y="198" font-family="{SANS}" font-size="19" fill="{MUTED}">Análise e Desenvolvimento de Sistemas  ·  Desenvolvedora em formação</text>
  <g>
    <rect x="80" y="236" width="56" height="2" fill="url(#line)"/>
    <text x="150" y="244" font-family="{SANS}" font-size="20" font-style="italic" fill="{PINK}">Transformando curiosidade em conhecimento e ideias em soluções.</text>
  </g>
</svg>
"""

footer = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="120" viewBox="0 0 1200 120" role="img" aria-label="Obrigada pela visita.">
  <defs>
    <linearGradient id="fl" x1="0" x2="1">
      <stop offset="0" stop-color="{PINK}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{PINK}"/>
      <stop offset="1" stop-color="{PINK}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="120" rx="18" fill="{BG}"/>
  <rect x="300" y="0" width="600" height="2" fill="url(#fl)"/>
  <text x="600" y="58" text-anchor="middle" font-family="{SANS}" font-size="22" fill="{TEXT}">Obrigada pela visita.</text>
  <text x="600" y="88" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{MUTED}">Emilly Lorrany  ·  <tspan fill="{PINK}">github.com/emillyy-cell</tspan></text>
</svg>
"""

# Descrições tiradas dos READMEs/arquivos reais de cada repositório.
PROJECTS = [
    ("menu-utilitarios-python", "Menu de Utilitários",
     ["Programa com menu de três utilitários: verificador",
      "de número (par/ímpar e sinal), calculadora das",
      "quatro operações e tabuada de 1 a 10."],
     "Python", None),
    ("Algoritmos-e-Pensamento-Computacional", "Algoritmos e Pensamento Computacional",
     ["Repositório de trabalhos da disciplina de",
      "Algoritmos, com fluxogramas de uma calculadora",
      "feitos no Flowgorithm."],
     "Flowgorithm", "Fork"),
    ("Lista-de-Compras", "Lista de Compras",
     ["Página interativa que organiza itens por categoria,",
      "com adição e remoção feitas pela manipulação",
      "do DOM, sem bibliotecas."],
     "HTML · CSS · JavaScript", None),
    ("Sensor-de-Temperatura-em-C-", "Sensor de Temperatura",
     ["Simula leituras de um sensor, encerra após três",
      "leituras seguidas acima do limite e gera relatório",
      "com média, máxima, mínima e percentual."],
     "C", None),
    ("ordena-o-notas", "Ordenação de Notas",
     ["Ordena as notas de uma turma com Bubble Sort e",
      "Quick Sort e compara o número de comparações e",
      "trocas de cada algoritmo."],
     "C", None),
    ("bubble-sort-farmacia", "Validade de Medicamentos",
     ["Ordena o estoque de uma farmácia pelos dias até o",
      "vencimento com Bubble Sort e classifica cada item",
      "como OK, ATENÇÃO ou URGENTE."],
     "C", "Em grupo"),
]


def card(repo, title, lines, lang, tag):
    desc = "\n".join(
        f'    <text x="28" y="{98 + i * 21}" font-family="{SANS}" font-size="13.5" fill="{MUTED}">{escape(l)}</text>'
        for i, l in enumerate(lines))
    tag_svg = ""
    if tag:
        w = 14 + len(tag) * 7.2
        tag_svg = (f'  <rect x="{452 - w}" y="24" width="{w:.0f}" height="22" rx="11" fill="none" stroke="{PINK}" stroke-opacity="0.55"/>\n'
                   f'  <text x="{452 - w / 2:.0f}" y="39" text-anchor="middle" font-family="{SANS}" font-size="11.5" fill="{PINK}">{escape(tag)}</text>\n')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="480" height="210" viewBox="0 0 480 210" role="img" aria-label="{escape(title)}">
  <rect x="0.5" y="0.5" width="479" height="209" rx="14" fill="{BG}" stroke="{BORDER}"/>
  <rect x="28" y="0.5" width="44" height="3" rx="1.5" fill="{PINK}"/>
  <text x="28" y="44" font-family="{MONO}" font-size="12" fill="{PINK}" fill-opacity="0.75">{escape(repo)}</text>
  <text x="28" y="70" font-family="{SANS}" font-size="20" font-weight="600" fill="{TEXT}">{escape(title)}</text>
{tag_svg}{desc}
  <circle cx="33" cy="180" r="5" fill="{PINK}"/>
  <text x="46" y="184.5" font-family="{SANS}" font-size="13" fill="{TEXT}">{escape(lang)}</text>
  <text x="452" y="184.5" text-anchor="end" font-family="{SANS}" font-size="13" fill="{PINK}">Ver repositório →</text>
</svg>
"""


(OUT / "banner.svg").write_text(banner, encoding="utf-8")
(OUT / "footer.svg").write_text(footer, encoding="utf-8")
for p in PROJECTS:
    (OUT / "cards" / f"{p[0]}.svg").write_text(card(*p), encoding="utf-8")
print("ok", sorted(x.name for x in OUT.rglob("*.svg")))
