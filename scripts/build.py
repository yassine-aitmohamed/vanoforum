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

PATHS = [
    ('Applying for a PhD abroad', 'From the first search to a funded offer.',
     ['finding-a-phd-abroad', 'contacting-a-professor', 'choosing-a-supervisor', 'phd-application-documents', 'funding-and-scholarships']),
    ('Starting your PhD', 'The habits of the first year: expectations, reading, working on a problem.',
     ['managing-your-phd', 'phd-expectations', 'reading-a-paper', 'skimming-a-paper', 'research-methodology', 'research-taste']),
    ('Writing your first paper', 'From the anatomy of a paper to the last revision.',
     ['first-paper-in-english', 'writing-the-abstract', 'writing-the-introduction', 'presenting-results', 'revising-paragraphs', 'writing-with-a-voice', 'academic-phrasebook']),
    ('Getting it published', 'The preprint, the journal, the referees and the talk.',
     ['posting-on-arxiv', 'choosing-a-journal', 'submission-and-peer-review', 'understanding-peer-review', 'giving-a-research-talk', 'conferences-and-networking']),
    ('Finishing and moving on', 'The thesis, the academic market and the postdoc.',
     ['writing-the-thesis', 'academic-career', 'postdoc-applications', 'collaboration-and-authorship', 'becoming-a-good-writer']),
]

# Comments under each guide (giscus, backed by GitHub Discussions).
# Fill both ids from https://giscus.app to switch them on; while empty, guides link to the forum instead.
GISCUS = {'repo': 'yassine-aitmohamed/vanoforum', 'repo_id': '', 'category': 'General', 'category_id': ''}

WIDGETS = {
    'writing-the-abstract': '''<section class="widget" id="abstract-checker" aria-labelledby="ac-h">
  <h2 id="ac-h">Check your abstract</h2>
  <p>Paste an abstract. The checker applies the rules of this guide: it flags the openings, verbs, symbols and lengths discussed above. It is a first filter, not a referee, and nothing leaves your browser.</p>
  <textarea id="ac-in" rows="7" spellcheck="true" placeholder="We prove that ..."></textarea>
  <div class="ac-bar"><span id="ac-count">0 words</span><button type="button" class="btn small ghost" id="ac-demo">Try the “before” example</button></div>
  <ul id="ac-out" class="ac-out" aria-live="polite"></ul>
</section>''',
}

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
                           extension_configs={'toc': {'permalink': '#', 'permalink_class': 'anchor', 'permalink_title': 'Link to this section'}})
    out = md.convert(src)
    out = re.sub(r'MATHTOKEN(\d+)X', lambda m: html.escape(maths[int(m.group(1))], quote=False), out)
    out = out.replace('<li>[ ] ', '<li class="task">').replace('<li>[x] ', '<li class="task done">')
    out = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', out)
    return out, md.toc_tokens


def plain(md):
    t = re.sub(r'```[\s\S]*?```', ' ', md)
    t = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', t)
    t = re.sub(r'^\s*(>|\d+\.|[-*]\s(\[[ x]\]\s)?)\s*', '', t, flags=re.M)
    t = re.sub(r'[*_`#|]', '', t)
    return re.sub(r'\s+', ' ', t).strip()


def sections(md, toc):
    """Split a guide at its level-2 headings, with the ids that the toc extension gave them."""
    parts = re.split(r'^## +(.+)$', md, flags=re.M)
    ids = [t['id'] for t in toc]
    out = [{'id': '', 'name': '', 'text': plain(parts[0])}]
    for k in range(1, len(parts), 2):
        out.append({'id': ids[(k - 1) // 2] if (k - 1) // 2 < len(ids) else '', 'name': parts[k].strip(), 'text': plain(parts[k + 1])})
    return out


def load_guides():
    guides = []
    for f in sorted((ROOT / 'guides').glob('*.md')):
        meta, body = front_matter(f.read_text(encoding='utf-8'))
        meta['source'] = f.name
        meta['body_md'] = body
        meta['minutes'] = max(1, round(len(plain(body).split()) / 220))
        meta['tasks'] = len(re.findall(r'^- \[[ x]\] ', body, flags=re.M))
        guides.append(meta)
    for n, (name, _, slugs) in enumerate(PATHS):
        for k, s in enumerate(slugs):
            for g in guides:
                if g['slug'] == s:
                    g['path'] = (n, k)
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
<link rel="alternate" type="application/atom+xml" title="VanoForum: new guides" href="{SITE}feed.xml">
</head>
<body data-root="{rel}">
<a class="skip" href="#main">Skip to content</a>
<div class="quantum" data-quantum data-intensity="{intensity}" data-offset="{offset}"></div>
<header class="top">
  <a class="brand" href="{rel}index.html">{MARK}<span>{SITE_TITLE}</span></a>
  <button type="button" class="search-btn" data-search aria-label="Search the guides"><svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.5" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M13 13l4.5 4.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg><span>Search guides</span><kbd>/</kbd></button>
  <button type="button" class="menu-btn" aria-expanded="false" aria-controls="site-nav" aria-label="Menu"><span></span><span></span><span></span></button>
  <nav id="site-nav">{links}<a class="gh" href="{REPO}" target="_blank" rel="noopener" aria-label="GitHub repository">GitHub</a></nav>
</header>
{body}
<footer class="foot">
  <div class="foot-in">
    <p><b>{SITE_TITLE}</b> · an open forum for researchers, by <a href="https://yassine-aitmohamed.github.io" target="_blank" rel="noopener">Yassine Ait Mohamed</a>. Guides and sheets under <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>, code under MIT. <a href="{SITE}feed.xml">Atom feed</a> · <a href="{REPO}/blob/main/CONTRIBUTING.md" target="_blank" rel="noopener">Contribute</a></p>
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
    return (f'<a class="card" href="{rel}guides/{g["slug"]}.html" data-cat="{g["category"].lower()}" data-slug="{g["slug"]}">'
            f'<span class="tag t-{g["category"].lower()}">{html.escape(g["category"])}</span>'
            f'<h3>{html.escape(g["title"])}</h3><p>{html.escape(g["summary"])}</p>'
            f'<span class="more"><span>Read the guide →</span><span class="meta">{g["minutes"]} min</span></span></a>')


def by_slug(guides, s):
    return next(g for g in guides if g['slug'] == s)


def path_nav(guides, g):
    if 'path' not in g:
        return ''
    n, k = g['path']
    name, _, slugs = PATHS[n]
    steps = ''.join(
        f'<li class="{"here" if j == k else ""}"><a href="{s_}.html" data-slug="{s_}"><i></i>{html.escape(by_slug(guides, s_)["title"])}</a></li>'
        for j, s_ in enumerate(slugs))
    nxt = ''
    if k + 1 < len(slugs):
        ng = by_slug(guides, slugs[k + 1])
        nxt = f'<a class="btn small ghost" href="{ng["slug"]}.html">Next in this path: {html.escape(ng["title"])} →</a>'
    return (f'<section class="pathbox" aria-label="Learning path"><p class="toc-h">Path · {html.escape(name)} · step {k + 1} of {len(slugs)}</p>'
            f'<ol class="steps">{steps}</ol>{nxt}</section>')


def discussion(g):
    q = html.escape(g['title']).replace(' ', '+')
    if GISCUS['repo_id'] and GISCUS['category_id']:
        return (f'<section class="discuss" id="discussion"><h2>Discussion</h2>'
                f'<script src="https://giscus.app/client.js" data-repo="{GISCUS["repo"]}" data-repo-id="{GISCUS["repo_id"]}" '
                f'data-category="{GISCUS["category"]}" data-category-id="{GISCUS["category_id"]}" data-mapping="pathname" data-strict="1" '
                f'data-reactions-enabled="1" data-emit-metadata="0" data-input-position="top" data-theme="transparent_dark" data-lang="en" '
                f'data-loading="lazy" crossorigin="anonymous" async></script></section>')
    return (f'<section class="discuss" id="discussion"><h2>Discussion</h2>'
            f'<p>Questions, corrections and your own experience are welcome. Comments live in the forum, on GitHub Discussions, with Markdown and LaTeX.</p>'
            f'<div class="discuss-links"><a class="btn ghost" href="{FORUM}?discussions_q={q}" target="_blank" rel="noopener">See the thread for this guide</a>'
            f'<a class="btn ghost" href="{FORUM}/new?category=q-a" target="_blank" rel="noopener">Ask a new question</a></div></section>')


def build_guides(guides):
    for i, g in enumerate(guides):
        body_html, toc = md_to_html(g['body_md'])
        g['toc'] = toc
        toc_html = ''.join(f'<li><a href="#{t["id"]}">{html.escape(t["name"])}</a></li>' for t in toc)
        toc_html += '<li><a href="#discussion">Discussion</a></li>'
        prev_g = guides[i - 1] if i > 0 else None
        next_g = guides[i + 1] if i + 1 < len(guides) else None
        pn = '<nav class="pn">'
        pn += f'<a class="prev" href="{prev_g["slug"]}.html"><small>Previous</small>{html.escape(prev_g["title"])}</a>' if prev_g else '<span></span>'
        pn += f'<a class="next" href="{next_g["slug"]}.html"><small>Next</small>{html.escape(next_g["title"])}</a>' if next_g else '<span></span>'
        pn += '</nav>'
        tasks = f' · <span data-checkcount>{g["tasks"]}-item checklist</span>' if g['tasks'] else ''
        widget = WIDGETS.get(g['slug'], '')
        edit = f'{REPO}/edit/main/guides/{g["source"]}'
        body = f'''<div class="progress" aria-hidden="true"><span></span></div>
<main id="main" class="guide" data-guide="{g["slug"]}">
  <aside class="toc"><div class="toc-in"><p class="toc-h">On this page</p><ol>{toc_html}</ol>
    <p class="toc-h">Guide {i + 1} of {len(guides)}</p>
    <a class="btn small" href="../sheets/{g["slug"]}.pdf">One-page sheet (PDF)</a>
    <a class="btn small ghost" href="#discussion">Discuss this guide</a>
    <a class="edit" href="{edit}" target="_blank" rel="noopener">Suggest an edit on GitHub</a></div></aside>
  <article class="panel prose">
    <p class="crumbs"><a href="../index.html#guides">Guides</a> · <span class="tag t-{g["category"].lower()}">{html.escape(g["category"])}</span></p>
    <h1>{html.escape(g["title"])}</h1>
    <p class="lead">{html.escape(g["summary"])}</p>
    <p class="gmeta">{g["minutes"]} min read{tasks} · <span class="readstate" data-readstate>Not read yet</span></p>
    {path_nav(guides, g)}
    <figure class="diagram"><img src="../assets/diagrams/{g["diagram"]}.svg" alt="Diagram: {html.escape(g["title"])}" loading="lazy"></figure>
    {body_html}
    {widget}
    <div class="end-actions"><button type="button" class="btn" data-markread>Mark as read</button><a class="btn ghost" href="../sheets/{g["slug"]}.pdf">Download the one-page sheet (PDF)</a></div>
    {discussion(g)}
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


def path_card(guides, n, path):
    name, blurb, slugs = path
    steps = ''.join(
        f'<li><a href="guides/{s_}.html" data-slug="{s_}"><i></i>{html.escape(by_slug(guides, s_)["title"])}</a></li>'
        for s_ in slugs)
    mins = sum(by_slug(guides, s_)['minutes'] for s_ in slugs)
    return (f'<div class="card path" data-path="{n}"><h3>{html.escape(name)}</h3><p>{html.escape(blurb)}</p>'
            f'<ol class="steps">{steps}</ol>'
            f'<p class="path-foot"><span class="meta" data-pathcount>{len(slugs)} guides · {mins} min</span>'
            f'<a class="btn small" href="guides/{slugs[0]}.html" data-pathstart>Start the path</a></p></div>')


def build_index(guides):
    groups = ''
    for key, label in CATEGORIES:
        gs = [g for g in guides if g['category'] == key]
        if gs:
            groups += (f'<div class="gblock" data-group="{key.lower()}"><h3 class="group">{html.escape(label)}</h3><div class="grid">'
                       + ''.join(guide_card(g) for g in gs) + '</div></div>')
    chips = '<button type="button" class="chip on" data-filter="all">All</button>' + ''.join(
        f'<button type="button" class="chip" data-filter="{k.lower()}">{html.escape(l)}</button>' for k, l in CATEGORIES)
    paths = ''.join(path_card(guides, n, p_) for n, p_ in enumerate(PATHS))
    sheets = ''.join(f'<li><a href="sheets/{g["slug"]}.pdf"><span class="pdf">PDF</span>{html.escape(g["title"])}</a></li>' for g in guides)
    diagrams = ''.join(f'<a class="thumb" href="assets/diagrams/{g["diagram"]}.svg" target="_blank" rel="noopener"><img src="assets/diagrams/{g["diagram"]}.svg" alt="{html.escape(g["title"])}" loading="lazy"></a>' for g in guides)
    tools = ''.join(tool_card(t) for t in TOOLS[:3])
    latest = ''.join(f'<li><a href="guides/{g["slug"]}.html">{html.escape(g["title"])}</a></li>' for g in list(reversed(guides))[:4])
    body = f'''<main id="main">
<section class="hero">
  <div class="hero-in">
    <p class="eyebrow">An open forum for researchers</p>
    <h1>Research, written down and shared.</h1>
    <p class="lead">Practical guides on how to read papers, write them in clear English, choose a journal, answer referees, and find a PhD or a postdoc abroad. Free one-page sheets and diagrams, open-source tools, and a forum to ask the questions nobody teaches.</p>
    <button type="button" class="hero-search" data-search><svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.5" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M13 13l4.5 4.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg><span>Search the guides: cover letter, referee report, Q1, scholarships…</span><kbd>/</kbd></button>
    <div class="cta"><a class="btn" href="#paths">Find your path</a><a class="btn ghost" href="{FORUM}" target="_blank" rel="noopener">Join the forum</a></div>
    <ul class="facts"><li><b>{len(guides)}</b> guides</li><li><b>{len(PATHS)}</b> learning paths</li><li><b>{len(guides) + 1}</b> free PDFs</li><li><b>{len(TOOLS)}</b> open-source tools</li></ul>
  </div>
</section>

<section id="paths" class="band">
  <div class="band-in">
    <h2>Start where you are</h2>
    <p class="sub">Five paths through the guides, one for each stage of a research career. Read them in order, or jump to the step you need. Your progress is kept in this browser only.</p>
    <div class="grid paths">{paths}</div>
    <p class="all"><a class="btn ghost" href="resources.html">Portals, scholarships and reading list →</a></p>
  </div>
</section>

<section id="guides" class="band">
  <div class="band-in">
    <h2>All guides</h2>
    <p class="sub">From the first reading of a paper to the answer to the referees, and from finding a PhD abroad to the postdoc market. Most guides end with a checklist and all come with a one-page sheet. <span class="mine" data-mine></span></p>
    <div class="chips" role="toolbar" aria-label="Filter the guides">{chips}</div>
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
      <p class="sub">The forum runs on GitHub Discussions: posts and replies in Markdown with LaTeX formulas, reactions, and a free GitHub account is all you need. Every guide has its own thread.</p>
      <div class="cta"><a class="btn" href="{FORUM}" target="_blank" rel="noopener">Open the forum</a><a class="btn ghost" href="{FORUM}/new?category=q-a" target="_blank" rel="noopener">Ask a question</a></div>
      <h3 class="group">New guides</h3>
      <ul class="latest">{latest}</ul>
      <p class="follow">Follow new guides with the <a href="{SITE}feed.xml">Atom feed</a>, or watch the <a href="{REPO}" target="_blank" rel="noopener">repository</a> on GitHub.</p>
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

<section id="contribute" class="band">
  <div class="band-in">
    <h2>Write with us</h2>
    <p class="sub">VanoForum grows with the experience of its readers. Every guide is a Markdown file in the repository, and every contribution is credited.</p>
    <div class="grid three">
      <a class="card" href="{REPO}/blob/main/CONTRIBUTING.md#fix-a-guide" target="_blank" rel="noopener"><h3>Fix or improve a guide</h3><p>Every guide has a “Suggest an edit” link. Correct a mistake, add an example or update a link, and send it as a pull request.</p><span class="more"><span>How to edit →</span></span></a>
      <a class="card" href="{REPO}/blob/main/CONTRIBUTING.md#write-a-new-guide" target="_blank" rel="noopener"><h3>Write a new guide</h3><p>Know how admissions work in your country, or how your field publishes? Start from the guide template and propose it in the Ideas category.</p><span class="more"><span>The guide template →</span></span></a>
      <a class="card" href="{FORUM}/categories/ideas" target="_blank" rel="noopener"><h3>Suggest a resource or a tool</h3><p>A portal, a scholarship, an essay or a tool that helped you. Post it in Ideas and it can join the Resources page.</p><span class="more"><span>Open Ideas →</span></span></a>
    </div>
    <p class="sub small">The forum follows a short <a href="{REPO}/blob/main/CODE_OF_CONDUCT.md" target="_blank" rel="noopener">code of conduct</a>: be precise, be kind, credit others.</p>
  </div>
</section>
</main>'''
    (ROOT / 'index.html').write_text(page(SITE_TITLE + ' · Guides, sheets and tools for researchers', body, intensity='1', offset='2.6'), encoding='utf-8')


def build_search(guides):
    data = [{'t': g['title'], 's': g['slug'], 'c': g['category'], 'm': g['minutes'], 'd': g['summary'],
             'x': [[sec['id'], sec['name'], sec['text']] for sec in sections(g['body_md'], g['toc'])]} for g in guides]
    (ROOT / 'guides' / 'search.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')


def build_feed(guides, today):
    entries = ''.join(
        f'<entry><title>{html.escape(g["title"])}</title><link href="{SITE}guides/{g["slug"]}.html"/>'
        f'<id>{SITE}guides/{g["slug"]}.html</id><updated>{today}T00:00:00Z</updated>'
        f'<category term="{g["category"]}"/><summary>{html.escape(g["summary"])}</summary></entry>\n'
        for g in reversed(guides))
    feed = (f'<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom">\n'
            f'<title>VanoForum</title><subtitle>Guides, sheets and tools for researchers</subtitle>\n'
            f'<link href="{SITE}"/><link rel="self" href="{SITE}feed.xml"/><id>{SITE}</id><updated>{today}T00:00:00Z</updated>\n'
            f'<author><name>Yassine Ait Mohamed</name></author>\n{entries}</feed>\n')
    (ROOT / 'feed.xml').write_text(feed, encoding='utf-8')


def build_404():
    body = f'''<main id="main">
<section class="band first">
  <div class="band-in narrow">
    <h1 class="page-h">This page does not exist</h1>
    <p class="sub">The link may be old, or the guide may have moved. Search the guides, or start again from the home page.</p>
    <div class="cta"><button type="button" class="btn" data-search>Search the guides</button><a class="btn ghost" href="{SITE}">Home page</a></div>
  </div>
</section>
</main>'''
    (ROOT / '404.html').write_text(page('Page not found · ' + SITE_TITLE, body, rel=SITE, intensity='0.55', path='404.html'), encoding='utf-8')


def build_tools():
    cards = ''.join(tool_card(t) for t in TOOLS)
    body = f'''<main id="main">
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
    body = f'''<main id="main">
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
    build_search(gs)
    build_404()
    (ROOT / 'guides' / 'index.json').write_text(json.dumps([{k: g[k] for k in ('title', 'slug', 'category', 'summary', 'diagram', 'source')} for g in gs], indent=2), encoding='utf-8')
    import datetime
    today = datetime.date.today().isoformat()
    urls = [('', '1.0'), ('resources.html', '0.8'), ('tools.html', '0.8')] + [(f'guides/{g["slug"]}.html', '0.9') for g in gs] + [('sheets/vanoforum-research-handbook.pdf', '0.7')] + [(f'sheets/{g["slug"]}.pdf', '0.5') for g in gs]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += ''.join(f'  <url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod><priority>{p}</priority></url>\n' for u, p in urls)
    sm += '</urlset>\n'
    (ROOT / 'sitemap.xml').write_text(sm, encoding='utf-8')
    build_feed(gs, today)
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n', encoding='utf-8')
    print('built', len(gs), 'guides')
