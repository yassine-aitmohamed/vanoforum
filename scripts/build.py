#!/usr/bin/env python3
"""Build the static site from guides/*.md.

Usage: python3 scripts/build.py
Requires: pip install markdown
"""
import html, json, re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
REPO = 'https://github.com/yassine-aitmohamed/vanoforum'
FORUM = REPO + '/discussions'
SITE_TITLE = 'VanoForum'
SITE = 'https://yassine-aitmohamed.github.io/vanoforum/'
YEAR = '2026'

CATEGORIES = [('Reading', 'Reading papers'), ('Writing', 'Writing papers'), ('Publishing', 'Publishing'), ('Method', 'Research method'), ('Careers', 'PhD and careers')]

TOOLS = [
    ('VanoAtlas', 'vanoatlas', 'A local research workspace: projects, tasks, meetings, daily routine, notes, papers and LaTeX in one private app.', 'macOS · Windows · Linux'),
    ('VanoLeaf', 'VanoLeaf-LaTeX-Editor', 'A LaTeX editor in the spirit of Overleaf that runs on your own computer: file tree, PDF preview, click-to-jump, offline, and no compile timeout.', 'macOS · Windows · Linux'),
    ('VanoLib Reader', 'vanolib-extension', 'A PDF reader for papers in the browser: click a citation to see the reference, preview figures in place, highlight, annotate and cite in five styles.', 'Chrome · Edge · Brave'),
    ('VanoNote', 'VanoNote', 'A handwritten notebook and classroom whiteboard: pen tablets, PDF annotation, a blackboard mode and a live link for students.', 'macOS · Windows · Linux'),
    ('VanoShelf', 'vanoshelf-extension', 'Order for the Overleaf projects page: sort projects into fields, hide the ones you do not want on screen, blur titles in a shared office.', 'Chrome · Edge · Brave'),
    ('VanoVeil', 'vanoveil', 'A private corner inside Chrome: a password-protected link bar, a hidden workspace for tabs and a one-key privacy veil.', 'Chrome · Edge · Brave'),
    ('VanoLib', 'https://github.com/vanovamaths/vanolib', 'An open mathematics library in the browser: browse, read and annotate arXiv papers, with listings updated every day.', 'Web app', 'https://vanovamaths.github.io/vanolib/'),
]

MARK = ('<svg class="mark" viewBox="0 0 40 40" aria-hidden="true">'
        '<path d="M9 28 Q14 10 20 12" fill="none" stroke="currentColor" stroke-width="1.6" opacity=".55"/>'
        '<path d="M20 12 Q28 14 31 28" fill="none" stroke="currentColor" stroke-width="1.6" opacity=".55"/>'
        '<path d="M31 28 Q20 34 9 28" fill="none" stroke="currentColor" stroke-width="1.6" opacity=".55"/>'
        '<path d="M9 28 Q20 23 31 28" fill="none" stroke="currentColor" stroke-width="1.6" opacity=".55"/>'
        '<circle cx="20" cy="12" r="4" fill="#e07b24"/><circle cx="9" cy="28" r="4" fill="#3fa3dd"/><circle cx="31" cy="28" r="4" fill="#2b4fb3"/></svg>')

MATH_RE = re.compile(r'(```[\s\S]*?```|`[^`\n]+`)|(\$\$[\s\S]+?\$\$|(?<!\\)\$(?!\s)(?:\\.|[^$\\\n])+?(?<!\s)\$)')


def front_matter(text):
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(':')
        meta[k.strip()] = v.strip()
    return meta, text[m.end():]


def md_to_html(src):
    maths = []

    def keep(m):
        if m.group(1):
            return m.group(0)
        maths.append(m.group(0))
        return f'MATHTOKEN{len(maths) - 1}X'
    src = MATH_RE.sub(keep, src)
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'sane_lists', 'toc'],
                           extension_configs={'toc': {'permalink': False}})
    out = md.convert(src)
    out = re.sub(r'MATHTOKEN(\d+)X', lambda m: html.escape(maths[int(m.group(1))], quote=False), out)
    out = out.replace('<li>[ ] ', '<li class="task">').replace('<li>[x] ', '<li class="task done">')
    out = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', out)
    return out, md.toc_tokens


def load_guides():
    guides = []
    for f in sorted((ROOT / 'guides').glob('*.md')):
        meta, body = front_matter(f.read_text(encoding='utf-8'))
        meta['source'] = f.name
        meta['body_md'] = body
        guides.append(meta)
    return guides


def page(title, body, rel='', intensity='0.5', offset='0', description='', active='', path=''):
    nav = [('Guides', f'{rel}index.html#guides', 'guides'), ('Sheets', f'{rel}index.html#sheets', 'sheets'),
           ('Resources', f'{rel}resources.html', 'resources'), ('Tools', f'{rel}tools.html', 'tools'), ('Forum', FORUM, 'forum')]
    def link(n, u, k):
        cls = ' class="on"' if k == active else ''
        ext = ' target="_blank" rel="noopener"' if u.startswith('http') else ''
        return f'<a href="{u}"{cls}{ext}>{n}</a>'
    links = ''.join(link(n, u, k) for n, u, k in nav)
    desc = html.escape(description or 'Practical guides for researchers: reading papers, writing them in English, choosing a journal and answering referees. Free sheets, diagrams, tools and an open forum.')
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}{path}">
<meta name="robots" content="index, follow">
<meta name="author" content="Yassine Ait Mohamed">
<meta name="keywords" content="research, how to read a research paper, academic writing in English, PhD abroad, PhD scholarships, contacting a professor, postdoc applications, writing an abstract, writing an introduction, choosing a journal, Q1 journal, peer review, referee report, PhD, mathematics, VanoForum">
<meta property="og:type" content="website">
<meta property="og:site_name" content="VanoForum">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}assets/img/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}assets/img/og.png">
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "WebSite", "name": "VanoForum", "url": SITE, "description": "An open forum for researchers: guides on reading papers, writing them in English and getting them published, with free sheets, diagrams and open-source tools.", "inLanguage": "en", "author": {"@type": "Person", "name": "Yassine Ait Mohamed", "url": "https://yassine-aitmohamed.github.io"}})}</script>
<link rel="icon" href="{rel}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<link rel="stylesheet" href="{rel}assets/css/site.css">
</head>
<body>
<div class="quantum" data-quantum data-intensity="{intensity}" data-offset="{offset}"></div>
<header class="top">
  <a class="brand" href="{rel}index.html">{MARK}<span>{SITE_TITLE}</span></a>
  <nav>{links}<a class="gh" href="{REPO}" target="_blank" rel="noopener" aria-label="GitHub repository">GitHub</a></nav>
</header>
{body}
<footer class="foot">
  <div class="foot-in">
    <p><b>{SITE_TITLE}</b> · an open forum for researchers, by <a href="https://yassine-aitmohamed.github.io" target="_blank" rel="noopener">Yassine Ait Mohamed</a>. Guides and sheets under <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>, code under MIT.</p>
    <p class="about-field">The background is an exact solution of the Schrödinger equation: a superposition of eigenstates of the two-dimensional harmonic oscillator with frequency ratio √2, so the motion never repeats. Hue is the phase of ψ, brightness is |ψ|², the faint curves are level sets of |ψ|², and the particles follow Bohmian trajectories, dx/dt = Im(∇ψ/ψ).</p>
  </div>
</footer>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
<script defer src="{rel}assets/js/site.js"></script>
<script defer src="{rel}assets/js/quantum.js"></script>
</body>
</html>
'''


def guide_card(g, rel=''):
    return (f'<a class="card" href="{rel}guides/{g["slug"]}.html">'
            f'<span class="tag t-{g["category"].lower()}">{html.escape(g["category"])}</span>'
            f'<h3>{html.escape(g["title"])}</h3><p>{html.escape(g["summary"])}</p>'
            f'<span class="more">Read the guide →</span></a>')


def build_guides(guides):
    for i, g in enumerate(guides):
        body_html, toc = md_to_html(g['body_md'])
        toc_html = ''.join(f'<li><a href="#{t["id"]}">{html.escape(t["name"])}</a></li>' for t in toc)
        prev_g = guides[i - 1] if i > 0 else None
        next_g = guides[i + 1] if i + 1 < len(guides) else None
        pn = '<nav class="pn">'
        pn += f'<a class="prev" href="{prev_g["slug"]}.html"><small>Previous</small>{html.escape(prev_g["title"])}</a>' if prev_g else '<span></span>'
        pn += f'<a class="next" href="{next_g["slug"]}.html"><small>Next</small>{html.escape(next_g["title"])}</a>' if next_g else '<span></span>'
        pn += '</nav>'
        body = f'''<main class="guide">
  <aside class="toc"><div class="toc-in"><p class="toc-h">On this page</p><ol>{toc_html}</ol>
    <p class="toc-h">Guide {i + 1} of {len(guides)}</p>
    <a class="btn small" href="../sheets/{g["slug"]}.pdf">One-page sheet (PDF)</a>
    <a class="btn small ghost" href="{FORUM}" target="_blank" rel="noopener">Discuss on the forum</a></div></aside>
  <article class="panel prose">
    <p class="crumbs"><a href="../index.html#guides">Guides</a> · <span class="tag t-{g["category"].lower()}">{html.escape(g["category"])}</span></p>
    <h1>{html.escape(g["title"])}</h1>
    <p class="lead">{html.escape(g["summary"])}</p>
    <figure class="diagram"><img src="../assets/diagrams/{g["diagram"]}.svg" alt="Diagram: {html.escape(g["title"])}" loading="lazy"></figure>
    {body_html}
    <div class="end-actions"><a class="btn" href="../sheets/{g["slug"]}.pdf">Download the one-page sheet (PDF)</a><a class="btn ghost" href="{FORUM}" target="_blank" rel="noopener">Ask a question on the forum</a></div>
    {pn}
  </article>
</main>'''
        (ROOT / 'guides' / f'{g["slug"]}.html').write_text(
            page(f'{g["title"]} · {SITE_TITLE}', body, rel='../', intensity='0.42', description=g['summary'], active='guides', path=f'guides/{g["slug"]}.html'), encoding='utf-8')


def tool_card(t):
    name, repo, desc, plat = t[:4]
    url = repo if repo.startswith('http') else f'https://github.com/yassine-aitmohamed/{repo}'
    if len(t) > 4:
        second = f'<a href="{t[4]}" target="_blank" rel="noopener">Open the app</a>'
        lic = ''
    else:
        second = f'<a href="{url}/releases/latest" target="_blank" rel="noopener">Download</a>'
        lic = ' · MIT'
    return (f'<div class="card tool"><h3>{html.escape(name)}</h3><p>{html.escape(desc)}</p>'
            f'<p class="plat">{html.escape(plat)}{lic}</p>'
            f'<div class="tool-links"><a href="{url}" target="_blank" rel="noopener">Source on GitHub</a>{second}</div></div>')


def build_index(guides):
    groups = ''
    for key, label in CATEGORIES:
        gs = [g for g in guides if g['category'] == key]
        if gs:
            groups += f'<h3 class="group">{html.escape(label)}</h3><div class="grid">' + ''.join(guide_card(g) for g in gs) + '</div>'
    sheets = ''.join(f'<li><a href="sheets/{g["slug"]}.pdf"><span class="pdf">PDF</span>{html.escape(g["title"])}</a></li>' for g in guides)
    diagrams = ''.join(f'<a class="thumb" href="assets/diagrams/{g["diagram"]}.svg" target="_blank" rel="noopener"><img src="assets/diagrams/{g["diagram"]}.svg" alt="{html.escape(g["title"])}"></a>' for g in guides)
    tools = ''.join(tool_card(t) for t in TOOLS[:3])
    order = ['finding-a-phd-abroad', 'contacting-a-professor', 'choosing-a-supervisor', 'phd-application-documents', 'funding-and-scholarships', 'postdoc-applications']
    careers = ''.join(guide_card(g) for s_ in order for g in guides if g['slug'] == s_)
    body = f'''<main>
<section class="hero">
  <div class="hero-in">
    <p class="eyebrow">An open forum for researchers</p>
    <h1>Research, written down and shared.</h1>
    <p class="lead">Practical guides on how to read papers, write them in clear English, choose a journal, answer referees, and find a PhD or a postdoc abroad. Free one-page sheets and diagrams, open-source tools, and a forum to ask the questions nobody teaches.</p>
    <div class="cta"><a class="btn" href="#guides">Read the guides</a><a class="btn ghost" href="{FORUM}" target="_blank" rel="noopener">Join the forum</a></div>
    <ul class="facts"><li><b>{len(guides)}</b> guides</li><li><b>{len(guides) + 1}</b> free PDFs</li><li><b>{len(TOOLS)}</b> open-source tools</li></ul>
  </div>
</section>

<section id="careers" class="band">
  <div class="band-in">
    <h2>Doing a PhD abroad</h2>
    <p class="sub">A complete path for students who want to do a doctorate in another country: where positions are advertised, how to write to a professor, how to choose a supervisor, what goes in the application file, and how to fund it.</p>
    <div class="grid">{careers}</div>
    <p class="all"><a class="btn ghost" href="resources.html">Portals, scholarships and reading list →</a></p>
  </div>
</section>

<section id="guides" class="band">
  <div class="band-in">
    <h2>Guides</h2>
    <p class="sub">From the first reading of a paper to the answer to the referees, and from finding a PhD abroad to the postdoc market. Each guide ends with a checklist and comes with a one-page sheet.</p>
    {groups}
  </div>
</section>

<section id="sheets" class="band">
  <div class="band-in two">
    <div>
      <h2>Sheets and diagrams</h2>
      <p class="sub">Print them, pin them above your desk, share them with your students. Free under CC BY 4.0.</p>
      <a class="handbook" href="sheets/vanoforum-research-handbook.pdf"><span class="pdf big">PDF</span><span><b>The Research Handbook</b><small>All the guides in one typeset document</small></span></a>
      <ul class="sheets">{sheets}</ul>
    </div>
    <div class="thumbs">{diagrams}</div>
  </div>
</section>

<section id="tools" class="band">
  <div class="band-in">
    <h2>Open-source tools</h2>
    <p class="sub">Small, private tools for researchers and teachers. They run on your own computer, need no account, and do one job well.</p>
    <div class="grid three">{tools}</div>
    <p class="all"><a class="btn ghost" href="tools.html">All {len(TOOLS)} tools →</a></p>
  </div>
</section>

<section id="forum" class="band">
  <div class="band-in two">
    <div>
      <h2>The forum</h2>
      <p class="sub">The forum runs on GitHub Discussions: posts and replies in Markdown with LaTeX formulas, reactions, and a free GitHub account is all you need.</p>
      <a class="btn" href="{FORUM}" target="_blank" rel="noopener">Open the forum</a>
    </div>
    <ul class="cats">
      <li><b>Announcements</b><span>New guides, sheets and tools.</span></li>
      <li><b>General</b><span>One thread per guide, and open discussion about research life.</span></li>
      <li><b>Q&amp;A</b><span>Ask about reading, writing, journals or referees. Mark the best answer.</span></li>
      <li><b>Ideas</b><span>Suggest a guide, a sheet or a tool.</span></li>
      <li><b>Show and tell</b><span>Share your own tools, templates and workflows.</span></li>
    </ul>
  </div>
</section>
</main>'''
    (ROOT / 'index.html').write_text(page(SITE_TITLE + ' · Guides, sheets and tools for researchers', body, intensity='1', offset='2.6'), encoding='utf-8')


def build_tools():
    cards = ''.join(tool_card(t) for t in TOOLS)
    body = f'''<main>
<section class="band first">
  <div class="band-in">
    <h1 class="page-h">Open-source tools</h1>
    <p class="sub">Free tools for researchers and teachers. Everything runs on your own computer or in your own browser: no account, no tracking, no server.</p>
    <div class="grid three">{cards}</div>
    <p class="sub small">Found a bug or have an idea? Open an issue on the tool's repository, or post in the <a href="{FORUM}" target="_blank" rel="noopener">Show and tell</a> category of the forum.</p>
  </div>
</section>
</main>'''
    (ROOT / 'tools.html').write_text(page('Tools · ' + SITE_TITLE, body, intensity='0.55', active='tools', path='tools.html'), encoding='utf-8')


RESOURCES = [
    ('Finding a PhD or a postdoc', [
        ('EURAXESS', 'https://euraxess.ec.europa.eu/', 'The European Commission portal for research jobs, funding and mobility in Europe, with practical help for researchers moving country.'),
        ('FindAPhD', 'https://www.findaphd.com/', 'A large search engine for doctoral projects, strongest for the United Kingdom and Europe.'),
        ('jobs.ac.uk', 'https://www.jobs.ac.uk/', 'Academic and research vacancies, including funded PhD studentships, mainly in the United Kingdom.'),
        ('AcademicPositions', 'https://academicpositions.com/', 'International listings of PhD, postdoc and faculty positions, with many European universities.'),
        ('ADUM', 'https://adum.fr/', 'The platform used by many French doctoral schools to publish thesis offers and manage applications.'),
        ('MathJobs', 'https://www.mathjobs.org/', 'The American Mathematical Society system for academic mathematics positions, mainly in the United States and Canada.'),
    ]),
    ('Scholarships and funding', [
        ('DAAD', 'https://www.daad.de/en/', 'The German Academic Exchange Service: scholarships and a searchable database of doctoral programmes in Germany.'),
        ('Marie Skłodowska-Curie Actions', 'https://marie-sklodowska-curie-actions.ec.europa.eu/', 'European Union funding for doctoral networks and postdoctoral fellowships, open to all nationalities.'),
        ('Mitacs Globalink', 'https://www.mitacs.ca/', 'Research internships in Canada for undergraduates abroad, often a first step towards graduate study there.'),
        ('Campus France', 'https://www.campusfrance.org/en', 'The official guide to studying in France, with a catalogue of doctoral schools and scholarship information.'),
    ]),
    ('Classic essays on research and writing', [
        ('Career advice, by Terence Tao', 'https://terrytao.wordpress.com/career-advice/', 'A long collection of short essays on how to work, learn, write and build a research career in mathematics.'),
        ('You and your research, by Richard Hamming', 'https://www.cs.princeton.edu/~jrex/teaching/spring2005/fft/hamming.html', 'A famous talk on why some scientists do important work and others do not: courage, open doors, and the important problems of your field.'),
        ('How to write mathematics, by Paul Halmos', 'https://faculty.washington.edu/heagerty/Courses/b572/public/HalmosHowToWrite.pdf', 'The classic short essay on mathematical exposition: say something, know your reader, write in spirals.'),
        ('How to read a paper, by S. Keshav', 'https://doi.org/10.1145/1273445.1273458', 'The two-page note that introduced the three-pass method for reading research papers.'),
    ]),
    ('Newsletters on Substack', [
        ('Research Writing', 'https://varanya.substack.com/', 'Varanya Chaubey writes on how to structure and revise academic prose.'),
        ('Research Freedom', 'https://lennartnacke.substack.com/', 'Lennart Nacke writes on academic writing workflows, productivity and publishing, aimed at early-career researchers.'),
        ('About academic writing', 'https://aboutacademicwritingandzo.substack.com/', 'Femke de Jong writes on the craft and habits of academic writing.'),
        ('Write what you like', 'https://writewhatyoulike.substack.com/', 'Essays on writing habits and the writing life of researchers.'),
    ]),
    ('Finding and organising papers', [
        ('arXiv', 'https://arxiv.org/', 'The open preprint server for mathematics, physics, computer science and neighbouring fields.'),
        ('zbMATH Open', 'https://zbmath.org/', 'A free and open database of reviews of the mathematical literature since the nineteenth century.'),
        ('Google Scholar', 'https://scholar.google.com/', 'Broad search with citation counts and the list of papers citing each work.'),
        ('Semantic Scholar', 'https://www.semanticscholar.org/', 'A free search engine with citation graphs, author pages and paper alerts.'),
        ('Connected Papers', 'https://www.connectedpapers.com/', 'A visual graph of papers related to one starting paper, useful for a literature review.'),
        ('Zotero', 'https://www.zotero.org/', 'A free, open-source reference manager that exports to BibTeX.'),
    ]),
    ('Choosing a trustworthy journal', [
        ('Think. Check. Submit.', 'https://thinkchecksubmit.org/', 'A checklist to decide whether a journal or a publisher can be trusted.'),
        ('DOAJ', 'https://doaj.org/', 'The Directory of Open Access Journals, a curated list of reputable open-access journals.'),
        ('SCImago Journal Rank', 'https://www.scimagojr.com/', 'Journal rankings and quartiles (Q1 to Q4) by subject area, based on Scopus data.'),
    ]),
]


def build_resources():
    secs = ''
    for head, items in RESOURCES:
        lis = ''.join(f'<li><a href="{u}" target="_blank" rel="noopener"><b>{html.escape(n)}</b></a><span>{html.escape(d)}</span></li>' for n, u, d in items)
        secs += f'<h3 class="group">{html.escape(head)}</h3><ul class="cats res">{lis}</ul>'
    body = f'''<main>
<section class="band first">
  <div class="band-in">
    <h1 class="page-h">Resources</h1>
    <p class="sub">A curated list of portals, scholarships, classic essays, newsletters and tools for researchers. Every link was checked by hand. Suggest a new one in the <a href="{FORUM}" target="_blank" rel="noopener">forum</a>.</p>
    {secs}
  </div>
</section>
</main>'''
    (ROOT / 'resources.html').write_text(page('Resources for researchers · ' + SITE_TITLE, body, intensity='0.55', active='resources', path='resources.html', description='Curated resources for researchers: PhD and postdoc portals, scholarships, classic essays on research and writing, newsletters, paper search tools and journal checklists.'), encoding='utf-8')


if __name__ == '__main__':
    gs = load_guides()
    build_guides(gs)
    build_index(gs)
    build_tools()
    build_resources()
    (ROOT / 'guides' / 'index.json').write_text(json.dumps([{k: g[k] for k in ('title', 'slug', 'category', 'summary', 'diagram', 'source')} for g in gs], indent=2), encoding='utf-8')
    import datetime
    today = datetime.date.today().isoformat()
    urls = [('', '1.0'), ('resources.html', '0.8'), ('tools.html', '0.8')] + [(f'guides/{g["slug"]}.html', '0.9') for g in gs] + [('sheets/vanoforum-research-handbook.pdf', '0.7')] + [(f'sheets/{g["slug"]}.pdf', '0.5') for g in gs]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += ''.join(f'  <url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod><priority>{p}</priority></url>\n' for u, p in urls)
    sm += '</urlset>\n'
    (ROOT / 'sitemap.xml').write_text(sm, encoding='utf-8')
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n', encoding='utf-8')
    print('built', len(gs), 'guides')
