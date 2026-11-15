#!/usr/bin/env python3
"""Build the PDF sheets and the handbook.

Usage: python3 scripts/build_pdf.py
Requires: xelatex (TeX Live), pandoc, rsvg-convert, the fonts TeX Gyre Pagella and Inter.
"""
import re, shutil, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://yassine-aitmohamed.github.io/vanoforum'
OUT = ROOT / 'sheets'
OUT.mkdir(exist_ok=True)

LIST_SECTIONS = ('Checklist', 'Summary', 'In short', 'A minimal setup to start today')
CAT_COLOR = {'Reading': 'sky', 'Writing': 'orange', 'Publishing': 'royal', 'Method': 'royal'}


def front_matter(text):
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(':')
        meta[k.strip()] = v.strip()
    return meta, text[m.end():]


def tex_escape(s):
    out = []
    i = 0
    parts = re.split(r'(\$[^$]+\$)', s)
    for p in parts:
        if p.startswith('$') and p.endswith('$') and len(p) > 1:
            out.append(p)
            continue
        p = p.replace('\\', r'\textbackslash{}')
        for a, b in [('&', r'\&'), ('%', r'\%'), ('#', r'\#'), ('_', r'\_'), ('{', r'\{'), ('}', r'\}'), ('~', r'\textasciitilde{}'), ('^', r'\textasciicircum{}')]:
            p = p.replace(a, b)
        p = p.replace(r'\textbackslash\{\}', r'\textbackslash{}')
        p = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', p)
        p = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'\\emph{\1}', p)
        p = re.sub(r'`([^`]+)`', r'\\texttt{\1}', p)
        p = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', p)
        p = p.replace('"', "''").replace('…', r'\dots{}').replace('→', r'$\to$')
        out.append(p)
    return ''.join(out)


def sections(body):
    secs, cur, name = {}, [], None
    for line in body.splitlines():
        m = re.match(r'^## (.+)$', line)
        if m:
            if name: secs[name] = cur
            name, cur = m.group(1).strip(), []
        elif name:
            cur.append(line)
    if name: secs[name] = cur
    return secs


def checklist(body):
    secs = sections(body)
    names = [k for k in secs if 'checklist' in k.lower()] + [k for k in LIST_SECTIONS if k in secs]
    for s in names:
        if s in secs:
            items = [re.sub(r'^(- \[[ x]\] |- |\d+\. )', '', l).strip() for l in secs[s] if re.match(r'^(- |\d+\. )', l)]
            if items:
                return s, items
    return None, []


def key_points(body, limit=6):
    pts = []
    skip = ('leave out', 'what not', 'before and after', 'example', 'checklist', 'in short', 'summary')
    lines = []
    for name, ls in sections(body).items():
        if not any(k in name.lower() for k in skip):
            lines += ls
    for line in lines:
        m = re.match(r'^(?:- )?\*\*([^*]+?)\*\*[:.]?\s*(.*)$', line)
        if m and m.group(2):
            head = m.group(1).rstrip('.:')
            rest = re.split(r'(?<=[.!?])\s', m.group(2))[0]
            pts.append((head, rest))
    return pts[:limit]


PREAMBLE = r'''\documentclass[10pt]{article}
\usepackage[a4paper,margin=15mm,top=13mm,bottom=14mm]{geometry}
\usepackage{fontspec}
\setmainfont{TeX Gyre Pagella}
\setsansfont{Inter}[Scale=0.92]
\usepackage{xcolor,graphicx,enumitem,multicol,amssymb,amsmath}
\definecolor{royal}{HTML}{2B4FB3}\definecolor{sky}{HTML}{3FA3DD}\definecolor{orange}{HTML}{E07B24}
\definecolor{ink}{HTML}{1F2937}\definecolor{gray}{HTML}{6B7280}
\pagestyle{empty}\setlength{\parindent}{0pt}\setlength{\parskip}{3pt}
\setlength{\columnsep}{9mm}
\newcommand{\vdot}[1]{\raisebox{.15em}{\textcolor{#1}{\rule{0pt}{0pt}\scalebox{1.3}{$\bullet$}}}}
'''


def sheet(i, n, g, body):
    color = CAT_COLOR.get(g['category'], 'royal')
    title, items = checklist(body)
    kp = key_points(body)
    svg = ROOT / 'assets' / 'diagrams' / f"{g['diagram']}.svg"
    tex = PREAMBLE + r'\begin{document}' + '\n'
    tex += (r'{\sffamily\footnotesize\color{gray}\textcolor{' + color + r'}{\textbf{VANOFORUM}} \quad SHEET ' + f'{i}/{n}' +
            r' \quad ' + g['category'].upper() + r'\hfill ' + SITE.replace('https://', '') + r'}\par\vspace{2mm}' + '\n')
    tex += r'{\raggedright\sffamily\bfseries\fontsize{21}{25}\selectfont\color{ink} ' + tex_escape(g['title']) + r'\par}\vspace{1.5mm}' + '\n'
    tex += r'{\color{' + color + r'}\rule{28mm}{1.2pt}}\par\vspace{1mm}' + '\n'
    tex += r'{\large\color{ink} ' + tex_escape(g['summary']) + r'\par}\vspace{3mm}' + '\n'
    tex += r'\begin{center}\includegraphics[width=\linewidth,height=0.30\textheight,keepaspectratio]{diagram.pdf}\end{center}\vspace{1mm}' + '\n'
    tex += r'\begin{multicols}{2}' + '\n'
    if kp:
        tex += r'{\sffamily\bfseries\small\color{' + color + r'} KEY POINTS}\par\vspace{1mm}' + '\n'
        tex += r'\begin{itemize}[leftmargin=4mm,itemsep=2.5pt,topsep=0pt,label={\textcolor{' + color + r'}{\scriptsize$\bullet$}}]' + '\n'
        for h, r in kp:
            tex += r'\item \textbf{' + tex_escape(h) + r'.} ' + tex_escape(r) + '\n'
        tex += r'\end{itemize}' + '\n'
        tex += r'\columnbreak' + '\n'
    tex += r'{\sffamily\bfseries\small\color{' + color + r'} ' + ('Checklist' if title and 'checklist' in title.lower() else (title or 'Checklist')).upper() + r'}\par\vspace{1mm}' + '\n'
    tex += r'\begin{itemize}[leftmargin=5.5mm,itemsep=3pt,topsep=0pt,label={\textcolor{' + color + r'}{$\square$}}]' + '\n'
    for it in items:
        tex += r'\item ' + tex_escape(it) + '\n'
    tex += r'\end{itemize}' + '\n' + r'\end{multicols}' + '\n'
    tex += (r'\vfill{\sffamily\scriptsize\color{gray} ' + SITE.replace('https://', '') + '/guides/' + g['slug'] +
            r'.html \hfill Yassine Ait Mohamed · CC BY 4.0}' + '\n')
    tex += r'\end{document}' + '\n'
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        subprocess.run(['rsvg-convert', '-f', 'pdf', '-o', str(d / 'diagram.pdf'), str(svg)], check=True)
        (d / 'sheet.tex').write_text(tex, encoding='utf-8')
        r = subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error', 'sheet.tex'], cwd=d, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout[-3000:]); raise SystemExit('LaTeX failed for ' + g['slug'])
        pages = int(re.search(r'Output written on sheet.pdf \((\d+) page', r.stdout).group(1))
        shutil.copy(d / 'sheet.pdf', OUT / f"{g['slug']}.pdf")
        return pages


HANDBOOK_HEADER = r'''\usepackage{xcolor}
\definecolor{royal}{HTML}{2B4FB3}\definecolor{sky}{HTML}{3FA3DD}\definecolor{orange}{HTML}{E07B24}
\usepackage{titlesec}
\titleformat{\section}{\sffamily\bfseries\Huge\color{royal}}{}{0pt}{}[\vspace{2pt}{\color{orange}\rule{30mm}{1.2pt}}]
\titleformat{\subsection}{\sffamily\bfseries\large}{}{0pt}{}
\titlespacing*{\section}{0pt}{0pt}{14pt}
\newcommand{\sectionbreak}{\clearpage}
\usepackage{fancyhdr}\pagestyle{fancy}\fancyhf{}\renewcommand{\headrulewidth}{0pt}
\fancyfoot[L]{\sffamily\scriptsize\color{gray} VanoForum · The Research Handbook}\fancyfoot[R]{\sffamily\scriptsize\thepage}
\definecolor{gray}{HTML}{6B7280}
\usepackage{enumitem}\setlist{itemsep=2pt}
\usepackage{tikz}
'''


COVER = r"""
\begin{titlepage}
\thispagestyle{empty}
\vspace*{30mm}
\begin{tikzpicture}[scale=1.25]
\draw[gray!70,line width=0.9pt] (0,0) .. controls (0.6,1.9) .. (1.4,1.6);
\draw[gray!70,line width=0.9pt] (1.4,1.6) .. controls (2.4,1.5) .. (2.8,0);
\draw[gray!70,line width=0.9pt] (2.8,0) .. controls (1.4,-0.7) .. (0,0);
\draw[gray!70,line width=0.9pt] (0,0) .. controls (1.4,0.55) .. (2.8,0);
\fill[orange] (1.4,1.6) circle (0.17); \fill[sky] (0,0) circle (0.17); \fill[royal] (2.8,0) circle (0.17);
\end{tikzpicture}
\vspace{18mm}

{\sffamily\bfseries\fontsize{40}{46}\selectfont\color{royal} The Research\\[2mm] Handbook\par}
\vspace{6mm}
{\color{orange}\rule{40mm}{1.5pt}}
\vspace{8mm}

{\Large Reading papers, writing them in clear English,\\[1mm] and getting them published\par}
\vfill
{\sffamily\large Yassine Ait Mohamed\par}
\vspace{2mm}
{\sffamily\small\color{gray} VanoForum · SITEURL\\ Free under CC BY 4.0 · November 2026\par}
\end{titlepage}
"""


def handbook(guides):
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        md = ''
        for g in guides:
            svg = ROOT / 'assets' / 'diagrams' / f"{g['diagram']}.svg"
            pdf = d / f"{g['diagram']}.pdf"
            subprocess.run(['rsvg-convert', '-f', 'pdf', '-o', str(pdf), str(svg)], check=True)
            body = g['body']
            md += f"# {g['title']}\n\n*{g['summary']}*\n\n![]({pdf.name}){{width=100%}}\n\n{body}\n\n"
        md = re.sub(r'\]\(((?!https?://)[^)]+?)\.html\)', r'](#)', md)
        md = md.replace('](#)', ']()')
        (d / 'handbook.md').write_text(md, encoding='utf-8')
        (d / 'header.tex').write_text(HANDBOOK_HEADER, encoding='utf-8')
        (d / 'cover.tex').write_text(COVER.replace('SITEURL', SITE.replace('https://', '')), encoding='utf-8')
        cmd = ['pandoc', 'handbook.md', '-o', 'handbook.pdf', '--pdf-engine=xelatex', '-H', 'header.tex',
               '--shift-heading-level-by=0', '--toc', '--toc-depth=1',
               '-V', 'documentclass=article', '-V', 'papersize=a4', '-V', 'geometry:margin=24mm',
               '-V', 'mainfont=TeX Gyre Pagella', '-V', 'sansfont=Inter', '-V', 'fontsize=11pt',
               '-V', 'colorlinks=true', '-V', 'linkcolor=royal', '-V', 'urlcolor=royal', '-V', 'toccolor=black',
               '-B', 'cover.tex',
               '-f', 'markdown+task_lists-implicit_figures']
        r = subprocess.run(cmd, cwd=d, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr[-3000:]); raise SystemExit('pandoc failed')
        shutil.copy(d / 'handbook.pdf', OUT / 'vanoforum-research-handbook.pdf')


if __name__ == '__main__':
    guides = []
    for f in sorted((ROOT / 'guides').glob('*.md')):
        meta, body = front_matter(f.read_text(encoding='utf-8'))
        meta['body'] = body
        guides.append(meta)
    for i, g in enumerate(guides, 1):
        p = sheet(i, len(guides), g, g['body'])
        print(g['slug'], p, 'page(s)')
    handbook(guides)
    print('handbook ok')
