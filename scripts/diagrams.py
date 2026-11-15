"""Diagrams in quiver style: small colored vertices, labels in the vertex color,
descriptions in gray, curved arrows with the arrowhead in the middle."""
import math, os, sys
from xml.sax.saxutils import escape

OUT = sys.argv[1] if len(sys.argv) > 1 else 'assets/diagrams'
os.makedirs(OUT, exist_ok=True)

FONT = "IBM Plex Sans, Inter, Helvetica Neue, Arial, sans-serif"
INK = '#1f2937'
GRAY = '#6b7280'
EDGE = '#4b5563'
ROYAL, SKY, ORANGE = '#2b4fb3', '#3fa3dd', '#e07b24'
COLS = [ROYAL, SKY, ORANGE]


def col(i):
    return COLS[i % 3]


def wrap(text, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur); cur = w
        else:
            cur = (cur + ' ' + w).strip()
    if cur:
        lines.append(cur)
    return lines


def doc(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}" role="img" aria-label="{escape(title)}">'
            f'<title>{escape(title)}</title><rect width="100%" height="100%" fill="#ffffff"/>{body}</svg>')


def heading(title, subtitle=''):
    s = f'<text x="36" y="46" font-family="{FONT}" font-size="21" font-weight="600" fill="{INK}">{escape(title)}</text>'
    if subtitle:
        s += f'<text x="36" y="71" font-family="{FONT}" font-size="13.5" fill="{GRAY}">{escape(subtitle)}</text>'
    return s


def dot(x, y, c, r=6.5):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{c}"/>'


def label(x, y, head, sub, c, width=28, anchor='start', size=15):
    s = f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" font-weight="600" fill="{c}">{escape(head)}</text>'
    for k, ln in enumerate(wrap(sub, width) if sub else []):
        s += f'<text x="{x:.1f}" y="{y + 20 + 17 * k:.1f}" text-anchor="{anchor}" font-family="{FONT}" font-size="13" fill="{GRAY}">{escape(ln)}</text>'
    return s


def head_at(px, py, tx, ty, size=7.5, color=EDGE):
    n = math.hypot(tx, ty) or 1
    tx, ty = tx / n, ty / n
    nx, ny = -ty, tx
    a = (px + size * tx, py + size * ty)
    b = (px - size * tx + 0.62 * size * nx, py - size * ty + 0.62 * size * ny)
    c = (px - size * tx - 0.62 * size * nx, py - size * ty - 0.62 * size * ny)
    return f'<path d="M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}L{c[0]:.1f} {c[1]:.1f}Z" fill="{color}"/>'


def curved(x1, y1, x2, y2, bend=0.22, gap=14, color=EDGE, dash=False):
    """Quadratic arc from (x1,y1) to (x2,y2), bent to the left of the direction, arrowhead in the middle."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    sx, sy = x1 + gap * ux, y1 + gap * uy
    ex, ey = x2 - gap * ux, y2 - gap * uy
    mx, my = (sx + ex) / 2, (sy + ey) / 2
    nx, ny = uy, -ux
    cx, cy = mx + bend * L * nx, my + bend * L * ny
    px, py = 0.25 * sx + 0.5 * cx + 0.25 * ex, 0.25 * sy + 0.5 * cy + 0.25 * ey
    tx, ty = ex - sx, ey - sy
    d = ' stroke-dasharray="5 5"' if dash else ''
    return (f'<path d="M{sx:.1f} {sy:.1f}Q{cx:.1f} {cy:.1f} {ex:.1f} {ey:.1f}" fill="none" stroke="{color}" stroke-width="1.5"{d}/>'
            + head_at(px, py, tx, ty, color=color))


def lens(x1, y1, x2, y2, bend=0.2):
    return curved(x1, y1, x2, y2, bend) + curved(x2, y2, x1, y1, bend)


def flow_h(name, title, subtitle, steps, step_w=250, lenses=()):
    n = len(steps)
    W = 72 + step_w * n
    y = 128
    body = heading(title, subtitle)
    xs = [56 + step_w * i + 8 for i in range(n)]
    maxl = 0
    ww = int((step_w - 30) / 7.1)
    for i, (h, sub) in enumerate(steps):
        c = col(i)
        body += dot(xs[i], y, c)
        body += label(xs[i] - 6, y + 38, h, sub, c, width=ww)
        maxl = max(maxl, len(wrap(sub, ww)))
    for i in range(n - 1):
        if (i, i + 1) in lenses:
            body += lens(xs[i], y, xs[i + 1], y, 0.16)
        else:
            body += curved(xs[i], y, xs[i + 1], y, 0.16)
    H = y + 70 + 17 * maxl + 20
    open(f'{OUT}/{name}.svg', 'w').write(doc(W, H, body, title))


def flow_v(name, title, subtitle, steps, gap=96, width=60, side=None, W=None):
    n = len(steps)
    x = 64
    y0 = 118
    body = heading(title, subtitle)
    ys = [y0 + gap * i for i in range(n)]
    for i, (h, sub) in enumerate(steps):
        c = col(i)
        body += dot(x, ys[i], c)
        body += label(x + 30, ys[i] + 5, h, sub, c, width=width)
        if side and side[i]:
            sx = x + 30 + width * 7.1 + 40
            body += curved(x + 30 + width * 7.1 - 10, ys[i] + 5, sx - 4, ys[i] + 5, 0.0, gap=0, color='#9ca3af', dash=True)
            body += f'<text x="{sx + 6:.1f}" y="{ys[i] - 8:.1f}" font-family="{FONT}" font-size="12" font-style="italic" fill="{ORANGE}">if not</text>'
            for k, ln in enumerate(wrap(side[i], 30)):
                body += f'<text x="{sx + 6:.1f}" y="{ys[i] + 10 + 17 * k:.1f}" font-family="{FONT}" font-size="13" fill="{GRAY}">{escape(ln)}</text>'
    for i in range(n - 1):
        body += curved(x, ys[i], x, ys[i + 1], -0.2)
    W = W or (x + 30 + width * 7.1 + (330 if side else 40))
    H = ys[-1] + 60 + 17 * len(wrap(steps[-1][1], width))
    open(f'{OUT}/{name}.svg', 'w').write(doc(W, H, body, title))


def cycle(name, title, subtitle, steps, rx=330, ry=210, lenses=()):
    n = len(steps)
    cx, cy = 60 + rx + 150, 160 + ry + 30
    body = heading(title, subtitle)
    pts = []
    for i in range(n):
        a = -math.pi / 2 + 2 * math.pi * i / n
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a), a))
    for i in range(n):
        j = (i + 1) % n
        x1, y1, _ = pts[i]; x2, y2, _ = pts[j]
        if (i, j) in lenses:
            body += lens(x1, y1, x2, y2, 0.18)
        else:
            body += curved(x1, y1, x2, y2, 0.2)
    for i, ((h, sub), (px, py, a)) in enumerate(zip(steps, pts)):
        c = col(i)
        body += dot(px, py, c)
        ca, sa = math.cos(a), math.sin(a)
        if abs(ca) < 0.3:
            anchor, lx = 'middle', px
            ly = py - 46 - 17 * (len(wrap(sub, 26)) - 1) if sa < 0 else py + 30
        else:
            anchor = 'start' if ca > 0 else 'end'
            lx = px + (22 if ca > 0 else -22)
            ly = py + 5
        body += label(lx, ly, h, sub, c, width=26, anchor=anchor)
    W = 2 * cx
    H = cy + ry + 90
    open(f'{OUT}/{name}.svg', 'w').write(doc(W, H, body, title))


def results_quiver(name, title, subtitle):
    body = heading(title, subtitle)
    L1 = (130, 200); L2 = (130, 330); P = (380, 265); T = (630, 200); C = (870, 200); R = (630, 360)
    body += curved(*L1, *P, 0.12) + curved(*L2, *P, -0.12) + curved(*P, *T, 0.12) + curved(*T, *C, 0.16)
    body += curved(*L1, *T, 0.18)
    body += curved(*T, *R, 0.0, color='#9ca3af', dash=True)
    body += dot(*L1, SKY) + dot(*L2, SKY) + dot(*P, ROYAL, 8) + dot(*T, ORANGE, 10) + dot(*C, ROYAL) + dot(*R, SKY)
    body += label(L1[0] - 18, L1[1] + 5, 'Lemma', '', SKY, anchor='end')
    body += label(L2[0] - 18, L2[1] + 5, 'Lemma', 'technical steps', SKY, width=16, anchor='end')
    body += label(P[0], P[1] + 34, 'Proposition', 'important, not main', ROYAL, width=22, anchor='middle')
    body += label(T[0], T[1] - 60, 'Theorem A', 'main result, stated in the introduction', ORANGE, width=44, anchor='middle')
    body += label(C[0], C[1] + 34, 'Corollary', 'direct consequence', ROYAL, width=20, anchor='middle')
    body += label(R[0] + 22, R[1] + 5, 'Remark, Example', 'not used in proofs', SKY, width=22)
    body += f'<text x="36" y="440" font-family="{FONT}" font-size="13" fill="{GRAY}">Arrows point from a result to the results whose proofs use it. Known results are cited with exact numbers, never restated.</text>'
    open(f'{OUT}/{name}.svg', 'w').write(doc(1000, 470, body, title))


flow_h('three-pass', 'Reading a paper in three passes', 'Adapted from S. Keshav, How to Read a Paper (2007). Most papers only need the first pass.', [
    ('Shape · 10 min', 'Title, abstract, introduction, section titles, main statements, bibliography. Keep or drop.'),
    ('Content · 1 hour', 'Definitions, statements, examples, figures. Skip long proofs. Mark references.'),
    ('Proofs · hours', 'Reconstruct the arguments. Prove before reading. Test every hypothesis.'),
    ('Reading sheet', 'One page: problem, results, method, dependencies, novelty, open questions.')])

cycle('literature-loop', 'Keeping up with the literature', 'A loop that costs ten minutes a day.', [
    ('Alerts', 'arXiv listings, Scholar alerts, journal tables of contents.'),
    ('Screen', 'Titles and abstracts. Keep few.'),
    ('Read', 'Three passes, with a PDF reader that previews citations.'),
    ('File', 'Reference manager, BibTeX, reading sheet.'),
    ('Follow', 'Bibliography backward, citing papers forward.')], rx=300, ry=180)

flow_v('anatomy', 'Anatomy of a research paper', 'Each part answers one question. Most readers stop early, so each part must stand on its own.', [
    ('Title', 'What is this paper about? Name the objects and the type of result.'),
    ('Abstract', 'What does it prove or find? All main contributions, strong verbs, no symbols.'),
    ('Introduction', 'Why it matters, what was missing, what is new. Main results stated early.'),
    ('Preliminaries', 'Only the definitions and known results the paper uses, with one notation.'),
    ('Main sections', 'How the results are obtained. Each section opens with its goal.'),
    ('Examples and applications', 'What the results give in concrete cases.'),
    ('References', 'Complete, consistent, cited with exact numbers in the text.')], gap=78, width=74)

flow_h('abstract', 'A strong abstract in three moves', 'One paragraph, four to six sentences, no symbols, no citations.', [
    ('Main result', '"We prove that …", "We classify …". The first words state what the paper does.'),
    ('Other contributions', '"We also construct …", "As an application, we determine …". All of them.'),
    ('Method, if new', 'One sentence, only when the approach is itself a contribution.')], step_w=300)

flow_v('introduction-arc', 'The arc of an introduction', 'Continuous prose. The main result appears early, and every object is defined before it.', [
    ('Context and history', 'Where the problem comes from and what was known. A few sentences, not a survey.'),
    ('Motivation', 'Why it matters: an open problem, a bridge between areas, a phenomenon to explain.'),
    ('The gap', 'What was missing before this paper, stated fairly.'),
    ('Main contribution', 'Theorem A, stated after its objects are defined, with its meaning in prose after it.'),
    ('Other results', 'The contribution of each part, in general terms. No proof details.'),
    ('Organization, acknowledgments', 'One sentence per section, then thanks.')], gap=84, width=74)

results_quiver('results-hierarchy', 'A hierarchy of results', 'If everything is a Theorem, nothing stands out.')

flow_h('revision-passes', 'Revising a paragraph in four passes', 'From the largest scale to the smallest. Keep the notation and the structure.', [
    ('Correct?', 'Every claim true, every step justified by a proof or an exact reference.'),
    ('One job', 'Each paragraph does one thing, announced in its first sentence.'),
    ('Sentences', 'One idea each. Periods, not semicolons. Active voice.'),
    ('Words', 'Cut empty phrases and vague words. Read aloud.')], step_w=240)

flow_v('journal-choice', 'Choosing a journal', 'Scope first, then level, then the editor. Decide a ladder of three journals before the first submission.', [
    ('Scope', 'Does it publish papers like mine in the last two years?'),
    ('Level', 'Does the significance of the result match the journal?'),
    ('Editor', 'Does at least one board member work in my area?'),
    ('Trust', 'Indexed in the right databases, transparent fees, real peer review?'),
    ('Submit', 'One journal at a time. Preprint on arXiv if the policy allows it.')], gap=88, width=48,
    side=['Look at where your references were published.', 'Ask a senior colleague. Aim one notch higher, not three.', 'The journal is probably not right for this paper.', 'Do not submit. Check thinkchecksubmit.org and DOAJ.', None])

flow_h('review-pipeline', 'From submission to decision', 'Typical stages. In mathematics, a full review often takes several months. Revisions go back and forth.', [
    ('Submission', 'PDF, source, a one-page cover letter, suggested referees.'),
    ('Screening', 'The editor checks scope and level. Desk rejections are common and fast.'),
    ('Referees', 'The handling editor invites experts. This alone can take weeks.'),
    ('Reports', 'Accept, minor or major revision, or reject.'),
    ('Revision', 'Point-by-point answers, exact changes, polite disagreement.')], step_w=215, lenses={(3, 4)})

cycle('research-cycle', 'A research cycle', 'Most ideas fail. A method makes them fail early and cheaply. Examples and strategy go back and forth.', [
    ('Problem', 'One precise sentence, from an open question or a gap.'),
    ('Examples', 'Smallest cases by hand. Look for counterexamples.'),
    ('Strategy', 'Half a page, discussed before any formal proof.'),
    ('Originality', 'Does a statement of this form exist? Keep it separate from difficulty.'),
    ('Write', 'Results first, introduction and abstract last.'),
    ('Preprint', 'Post, submit, start the next project.')], rx=320, ry=200, lenses={(1, 2)})
print('ok')
