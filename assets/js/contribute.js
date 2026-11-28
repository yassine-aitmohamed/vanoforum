/* VanoForum: "Contribute" page (demo). Builds a guide page, in the site's style, from Word, LaTeX or typed text. */
(function () {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  // On the site, build.py sets window.VF_CONFIG; without it the page runs as a self-contained demo.
  const CFG = window.VF_CONFIG || {};
  const LIVE = !!CFG.repo;

  let DATA = { categories: [], guides: [] };
  const state = { mode: 'new', source: 'file', file: null, fileMd: '', fileName: '' };

  /* ---------- data ---------- */
  fetch(CFG.data || 'guides.json').then(r => r.json()).then(d => {
    DATA = d;
    $('#f-category').innerHTML = '<option value="">Choose a category</option>' + d.categories.map(([k, l]) => `<option value="${k}">${esc(l)}</option>`).join('')
      + '<option value="__new">＋ Create a new category…</option>';
    $('#f-guide').innerHTML = '<option value="">Choose a guide</option>' + d.categories.map(([k, l]) =>
      `<optgroup label="${esc(l)}">` + d.guides.filter(g => g.category === k).map(g => `<option value="${g.slug}">${esc(g.title)}</option>`).join('') + '</optgroup>').join('');
  }).catch(() => showErrors(['The list of guides could not be loaded.']));

  /* ---------- views ---------- */
  function show(view) {
    $$('.view').forEach(v => { v.hidden = v.id !== 'view-' + view; });
    window.scrollTo({ top: 0 });
  }
  $$('[data-go]').forEach(b => b.addEventListener('click', () => {
    setMode(b.dataset.go);
    show('form');
  }));
  if ($('#back-home')) $('#back-home').addEventListener('click', e => { e.preventDefault(); show('home'); });

  function setMode(m) {
    state.mode = m;
    $$('input[name=mode]').forEach(r => { r.checked = r.value === m; });
    $('#fields-new').hidden = m !== 'new';
    $('#fields-section').hidden = m !== 'section';
    $('#step3-h').textContent = m === 'new' ? 'About the guide' : 'Where your section goes';
    $('#step3-hint').textContent = m === 'new'
      ? 'This appears on the guide card and at the top of the page.'
      : 'Choose the guide and the place of your section. Your name appears on the section you add.';
  }
  $$('input[name=mode]').forEach(r => r.addEventListener('change', () => setMode(r.value)));

  $('#f-guide').addEventListener('change', () => {
    const g = DATA.guides.find(x => x.slug === $('#f-guide').value);
    const sel = $('#f-after');
    if (!g) { sel.innerHTML = '<option value="">Choose a guide first</option>'; return; }
    const heads = sections(g.body).slice(1).map(p => p.title);
    let def = heads.findIndex(h => /^(checklist|summary)/i.test(h)) - 1;
    if (def < 0) def = heads.length - 1;
    sel.innerHTML = heads.map((h, k) => `<option value="${k}"${k === def ? ' selected' : ''}>After “${esc(h)}”</option>`).join('');
  });

  /* ---------- new category ---------- */
  $('#f-category').addEventListener('change', () => {
    const isNew = $('#f-category').value === '__new';
    $('#newcat-name').hidden = !isNew; $('#newcat-desc').hidden = !isNew;
    if (isNew) $('#f-newcat').focus();
  });

  /* ---------- similar guides: avoid duplicates ---------- */
  const STOP = new Set('a an the of to in on for and or with your you my how what why when is are be at by from into about guide guides research researchers paper papers'.split(' '));
  const words = t => t.toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').match(/[a-z0-9]+/g) || [];
  const stem = w => w.replace(/(ings?|ies|es|s)$/, '').replace(/(ed)$/, '');
  const keys = t => Array.from(new Set(words(t).filter(w => w.length > 2 && !STOP.has(w)).map(stem)));
  const GUIDE_BASE = CFG.guideBase || '';
  function similarGuides(text) {
    const q = keys(text);
    if (q.length < 2 && !(q.length === 1 && text.trim().length > 6)) return [];
    return DATA.guides.map(g => {
      const t = new Set(keys(g.title)), s = new Set(keys(g.summary));
      const score = q.reduce((n, w) => n + (t.has(w) ? 1 : s.has(w) ? 0.5 : 0), 0) / q.length;
      return { g, score };
    }).filter(x => x.score >= 0.5).sort((a, b) => b.score - a.score).slice(0, 3).map(x => x.g);
  }
  let simTimer;
  $('#f-title').addEventListener('input', () => {
    clearTimeout(simTimer);
    simTimer = setTimeout(() => {
      const list = similarGuides($('#f-title').value), box = $('#similar');
      if (!list.length) { box.hidden = true; return; }
      box.innerHTML = '<p>These guides already exist on VanoForum. If your text covers the same topic, add a section to one of them instead:</p><ul>'
        + list.map(g => `<li><b>${esc(g.title)}</b>${GUIDE_BASE ? `<a href="${GUIDE_BASE}${g.slug}.html" target="_blank" rel="noopener">Read it</a>` : ''}<button type="button" data-addto="${g.slug}">Add a section to it →</button></li>`).join('') + '</ul>';
      box.hidden = false;
      $$('[data-addto]', box).forEach(b => b.addEventListener('click', () => {
        const title = $('#f-title').value;
        setMode('section');
        $('#f-guide').value = b.dataset.addto;
        $('#f-guide').dispatchEvent(new Event('change'));
        if (!$('#f-sectitle').value) $('#f-sectitle').value = title;
        $('#fields-section').scrollIntoView({ behavior: 'smooth', block: 'center' });
      }));
    }, 250);
  });
  function checkSection() {
    const g = DATA.guides.find(x => x.slug === $('#f-guide').value), box = $('#similar-sec');
    const q = keys($('#f-sectitle').value);
    if (!g || !q.length) { box.hidden = true; return; }
    const hit = sections(g.body).slice(1).map(p => p.title).find(h => { const k = new Set(keys(h)); return q.filter(w => k.has(w)).length / q.length >= 0.6; });
    box.hidden = !hit;
    if (hit) box.innerHTML = `<p>This guide already has a section “${esc(hit)}”. Make sure your section adds something new, or give it a more precise title.</p>`;
  }
  $('#f-sectitle').addEventListener('input', () => { clearTimeout(simTimer); simTimer = setTimeout(checkSection, 250); });
  $('#f-guide').addEventListener('change', checkSection);

  /* ---------- counters ---------- */
  $('#f-summary').addEventListener('input', () => { $('#sum-count').textContent = $('#f-summary').value.length + ' / 280'; });

  /* ---------- tabs ---------- */
  $$('.tabs button').forEach(b => b.addEventListener('click', () => {
    state.source = b.dataset.tab;
    $$('.tabs button').forEach(x => x.setAttribute('aria-selected', String(x === b)));
    $('#pane-file').hidden = state.source !== 'file';
    $('#pane-write').hidden = state.source !== 'write';
  }));

  /* ---------- files ---------- */
  const drop = $('#drop'), input = $('#file');
  drop.addEventListener('click', () => input.click());
  drop.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); input.click(); } });
  input.addEventListener('change', () => input.files[0] && readFile(input.files[0]));
  ['dragenter', 'dragover'].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.add('over'); }));
  ['dragleave', 'drop'].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.remove('over'); }));
  drop.addEventListener('drop', e => e.dataTransfer.files[0] && readFile(e.dataTransfer.files[0]));
  $$('[data-sample]').forEach(b => b.addEventListener('click', async () => {
    const name = b.dataset.sample;
    try {
      const raw = window.VF_SAMPLES[name];
      const data = name.endsWith('.docx') ? Uint8Array.from(atob(raw), c => c.charCodeAt(0)) : raw;
      readFile(new File([data], name));
    } catch (e) { showErrors(['The sample file could not be loaded.']); }
  }));
  $('#file-x').addEventListener('click', () => { state.fileMd = ''; state.fileName = ''; input.value = ''; $('#fileinfo').hidden = true; });

  async function readFile(f) {
    hideErrors();
    const ext = (f.name.split('.').pop() || '').toLowerCase();
    if (ext === 'doc') return showErrors(['This is an old Word file (.doc). In Word, use File → Save As → Word Document (.docx), then upload it again.']);
    if (ext === 'pdf') return showErrors(['PDF files are not accepted. Please upload the Word (.docx) or LaTeX (.tex) source of your text.']);
    if (ext !== 'docx' && ext !== 'tex') return showErrors(['Only Word (.docx) and LaTeX (.tex) files are accepted.']);
    if (f.size > 15 * 1024 * 1024) return showErrors(['The file is larger than 15 MB.']);
    const info = $('#fileinfo');
    info.hidden = false;
    $('#file-name').textContent = f.name;
    $('#file-notes').innerHTML = '<li>Reading the file…</li>';
    try {
      const r = ext === 'docx' ? await VanoConvert.fromDocx(await f.arrayBuffer()) : VanoConvert.fromTex(await f.text());
      state.fileMd = r.md; state.fileName = f.name;
      prefill(r);
      const nsec = (r.md.match(/^## /gm) || []).length;
      const words = plainText(r.md).split(/\s+/).filter(Boolean).length;
      const notes = [`${words} words, ${nsec} section${nsec === 1 ? '' : 's'}.`].concat(r.notes);
      $('#file-notes').innerHTML = notes.map(n => `<li${/Ignored|not included|BibTeX|simplified/.test(n) ? ' class="warn"' : ''}>${esc(n)}</li>`).join('');
    } catch (e) {
      state.fileMd = '';
      $('#file-notes').innerHTML = `<li class="warn">${esc(e.message || 'The file could not be read.')}</li>`;
    }
  }

  function prefill(r) {
    const setIf = (id, v) => { const el = $(id); if (v && !el.value.trim()) { el.value = v; el.dispatchEvent(new Event('input')); } };
    if (state.mode === 'new') { setIf('#f-title', r.title); setIf('#f-summary', r.summary.slice(0, 280)); }
    else setIf('#f-sectitle', r.title);
    setIf('#f-name', r.author);
  }

  /* ---------- markdown helpers (same rules as scripts/build.py) ---------- */
  const MATH_RE = /(```[\s\S]*?```|`[^`\n]+`)|(\$\$[\s\S]+?\$\$|(?<!\\)\$(?!\s)(?:\\.|[^$\\\n])+?(?<!\s)\$)/g;
  function mdToHtml(md) {
    const maths = [];
    const src = md.replace(MATH_RE, (m, code) => code ? m : (maths.push(m), `MATHTOKEN${maths.length - 1}X`));
    let out = marked.parse(src, { gfm: true, breaks: false });
    out = out.replace(/MATHTOKEN(\d+)X/g, (_, i) => esc(maths[+i]).replace(/&quot;/g, '"'));
    out = out.replace(/<li>\s*<input (checked="" )?disabled="" type="checkbox">\s*/g, (_, c) => c ? '<li class="task done">' : '<li class="task">');
    out = out.replace(/<li>\[ \] /g, '<li class="task">').replace(/<li>\[x\] /g, '<li class="task done">');
    out = out.replace(/<a href="(https?:\/\/[^"]+)"/g, '<a href="$1" target="_blank" rel="noopener"');
    return out;
  }
  function plainText(md) {
    return md.replace(/```[\s\S]*?```/g, ' ').replace(/!?\[([^\]]*)\]\([^)]*\)/g, '$1').replace(/^\s*(>|\d+\.|[-*]\s(\[[ x]\]\s)?)\s*/gm, '')
      .replace(/[*_`#|]/g, '').replace(/\s+/g, ' ').trim();
  }
  function slugify(s) {
    return s.normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[^\w\s-]/g, '').trim().toLowerCase().replace(/[-\s]+/g, '-');
  }
  function sections(md) {
    const parts = md.split(/^(?=## )/m);
    return parts.map((p, k) => ({ title: k === 0 ? '' : p.split('\n')[0].replace(/^##\s+/, '').trim(), text: p }));
  }
  function initials(n) { return n.trim().split(/\s+/).filter(Boolean).slice(0, 2).map(w => w[0].toUpperCase()).join('') || '?'; }

  /* ---------- gather and check ---------- */
  function hideErrors() { $('#errors').hidden = true; }
  function showErrors(list) {
    const e = $('#errors');
    e.innerHTML = '<ul style="margin:0;padding:0">' + list.map(x => `<li>${esc(x)}</li>`).join('') + '</ul>';
    e.hidden = false;
    e.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
  function gather() {
    $$('.field.bad, .agree.bad').forEach(x => x.classList.remove('bad'));
    const errs = [];
    const need = (id, msg) => { const el = $(id); if (!el.value.trim()) { errs.push(msg); el.closest('.field').classList.add('bad'); } return el.value.trim(); };
    const d = { mode: state.mode };
    d.name = need('#f-name', 'Write your name: it is shown on the page.');
    d.aff = $('#f-aff').value.trim();
    d.url = $('#f-url').value.trim();
    if (state.mode === 'new') {
      d.title = need('#f-title', 'Give the guide a title.');
      d.category = need('#f-category', 'Choose a category, or create a new one.');
      d.newcat = false;
      if (d.category === '__new') {
        const n = $('#f-newcat').value.trim().replace(/\s+/g, ' ');
        const known = DATA.categories.find(([k, l]) => k.toLowerCase() === n.toLowerCase() || l.toLowerCase() === n.toLowerCase());
        if (!n) { errs.push('Give your new category a name.'); $('#f-newcat').closest('.field').classList.add('bad'); }
        else if (known) d.category = known[0];
        else { d.category = n.charAt(0).toUpperCase() + n.slice(1); d.newcat = true; d.newcatDesc = $('#f-newcat-desc').value.trim(); }
      }
      d.summary = need('#f-summary', 'Write a one or two sentence summary.');
    } else {
      d.slug = need('#f-guide', 'Choose the guide your section goes into.');
      d.sectitle = need('#f-sectitle', 'Give your section a title.');
      d.after = +$('#f-after').value || 0;
    }
    let md = state.source === 'file' ? state.fileMd : $('#write-text').value;
    if (state.source === 'write' && /\\(section|begin|textbf|emph)\b/.test(md)) md = VanoConvert.fromTex(md).md;
    if (!md.trim()) errs.push(state.source === 'file' ? 'Upload a Word (.docx) or LaTeX (.tex) file, or switch to “Write here”.' : 'Write your text in the box.');
    d.md = VanoConvert.shiftHeadings(md, state.mode === 'new' ? 2 : 3);
    if (!$('#f-agree').checked) { errs.push('Accept the licence so that your text can be published with your name.'); $('#f-agree').closest('.agree').classList.add('bad'); }
    return { d, errs };
  }

  /* ---------- build the markdown file that would be committed ---------- */
  function guideFile(d) {
    const g = DATA.guides;
    const nn = String(g.length + 1).padStart(2, '0');
    const slug = slugify(d.title);
    const fm = ['---', 'title: ' + d.title, 'slug: ' + slug, 'category: ' + d.category].concat(d.newcat ? ['category_new: yes'].concat(d.newcatDesc ? ['category_description: ' + d.newcatDesc] : []) : []).concat(['summary: ' + d.summary.replace(/\s+/g, ' '),
      'author: ' + d.name]).concat(d.aff ? ['affiliation: ' + d.aff] : []).concat(d.url ? ['author_url: ' + d.url] : []).concat(['---', '']).join('\n');
    return { path: `guides/${nn}-${slug}.md`, text: fm + '\n' + d.md.trim() + '\n', body: d.md, slug };
  }
  function sectionFile(d) {
    const g = DATA.guides.find(x => x.slug === d.slug);
    const parts = sections(g.body);
    const k = Math.min(d.after + 1, parts.length - 1);
    const credit = `<!-- contributed-by: ${[d.name, d.aff, d.url].map(x => x.replace(/\|/g, '/')).join(' | ')} -->`;
    const snippet = `## ${d.sectitle}\n${credit}\n\n${d.md.trim()}\n\n`;
    const body = parts.slice(0, k + 1).map(p => p.text).join('').replace(/\s*$/, '\n\n') + snippet + parts.slice(k + 1).map(p => p.text).join('');
    // The section is a file of its own: build.py inserts it into the guide, with the name of its author.
    const fm = ['---', 'guide: ' + g.slug, 'title: ' + d.sectitle, 'after: ' + parts[k].title, 'author: ' + d.name]
      .concat(d.aff ? ['affiliation: ' + d.aff] : []).concat(d.url ? ['author_url: ' + d.url] : []).concat(['---', '']).join('\n');
    return { path: `guides/sections/${g.slug}--${slugify(d.sectitle)}.md`, text: fm + '\n' + d.md.trim() + '\n', body, guide: g };
  }

  /* ---------- preview ---------- */
  $('#generate').addEventListener('click', () => {
    hideErrors();
    const { d, errs } = gather();
    if (errs.length) return showErrors(errs);
    state.last = d;
    state.out = d.mode === 'new' ? guideFile(d) : sectionFile(d);
    renderPreview(d, state.out);
    show('preview');
    if (d.mode === 'section') setTimeout(() => { const s = $('.contrib-section'); if (s) s.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 350);
  });

  function byline(d, role) {
    const who = d.url ? `<a href="${esc(d.url)}" target="_blank" rel="noopener"><b>${esc(d.name)}</b></a>` : `<b>${esc(d.name)}</b>`;
    return `<div class="byline"><span class="avatar">${esc(initials(d.name))}</span><span class="who">${role} ${who}${d.aff ? `<small>${esc(d.aff)}</small>` : ''}</span><span class="role">Contributor</span></div>`;
  }

  function renderPreview(d, out) {
    const isNew = d.mode === 'new';
    const g = isNew ? { title: d.title, summary: d.summary, category: d.category } : out.guide;
    const body = isNew ? out.body : out.body;
    const minutes = Math.max(1, Math.round(plainText(body).split(/\s+/).length / 220));
    const tasks = (body.match(/^- \[[ x]\] /gm) || []).length;
    const known = DATA.categories.some(([k]) => k === g.category);
    const cat = known ? g.category.toLowerCase() : 'custom';
    const catNote = known ? '' : '<span class="newcat-note">new category</span>';
    const diagram = isNew ? '<div class="nodiagram">The diagram of the guide is drawn by the editors after review</div>'
      : `<figure class="diagram"><img src="assets/diagrams/${g.diagram}.svg" alt="Diagram: ${esc(g.title)}"></figure>`;
    const credit = isNew
      ? `<section class="credits"><h2>Contributors</h2><p>This guide was written by <b>${esc(d.name)}</b>${d.aff ? ', ' + esc(d.aff) : ''}, and is published under CC BY 4.0. Corrections by other readers are credited here too.</p></section>`
      : `<section class="credits"><h2>Contributors</h2><p>Guide by Yassine Ait Mohamed. Section “${esc(d.sectitle)}” by <b>${esc(d.name)}</b>${d.aff ? ', ' + esc(d.aff) : ''}.</p></section>`;
    const html = `<main class="guide">
  <aside class="toc"><div class="toc-in"><p class="toc-h">On this page</p><ol id="p-toc"></ol>
    <p class="toc-h">${isNew ? 'Written by' : 'Contributors'}</p><p class="by">${esc(d.name)}${d.aff ? `<small>${esc(d.aff)}</small>` : ''}</p>
    <span class="btn small" aria-disabled="true">One-page sheet (PDF)</span>
    <span class="btn small ghost" aria-disabled="true">Discuss this guide</span></div></aside>
  <article class="panel prose">
    <p class="crumbs"><span>Guides</span> · <span class="tag t-${cat}">${esc(g.category)}</span>${catNote}</p>
    <h1>${esc(g.title)}</h1>
    <p class="lead">${esc(g.summary)}</p>
    <p class="gmeta">${minutes} min read${tasks ? ` · ${tasks}-item checklist` : ''} · ${isNew ? 'by ' + esc(d.name) : 'with a section by ' + esc(d.name)}</p>
    ${isNew ? byline(d, 'Written by') : ''}
    ${diagram}
    <div class="gbody">${mdToHtml(body)}</div>
    ${credit}
    <div class="end-actions"><span class="btn" aria-disabled="true">Mark as read</span><span class="btn ghost" aria-disabled="true">Download the one-page sheet (PDF)</span></div>
  </article>
</main>`;
    const host = $('#preview-host');
    host.innerHTML = html;
    decorate(host, d);
    if (window.renderMathInElement) {
      renderMathInElement(host, {
        delimiters: [{ left: '$$', right: '$$', display: true }, { left: '$', right: '$', display: false }],
        ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'], throwOnError: false
      });
    }
  }

  function decorate(host, d) {
    const art = $('.gbody', host);
    // headings: ids and anchors, as the toc extension of Python-Markdown does
    const used = {};
    $$('h2, h3', art).forEach(h => {
      let id = slugify(h.textContent) || 'section';
      if (used[id]) id += '_' + used[id]++; else used[id] = 1;
      h.id = id;
      h.insertAdjacentHTML('beforeend', `<a class="anchor" href="#${id}" title="Link to this section">#</a>`);
    });
    // contributed sections
    const walker = document.createTreeWalker(art, NodeFilter.SHOW_COMMENT);
    const marks = [];
    while (walker.nextNode()) if (/^\s*contributed-by:/.test(walker.currentNode.nodeValue)) marks.push(walker.currentNode);
    for (const c of marks) {
      const [name, aff] = c.nodeValue.replace(/^\s*contributed-by:\s*/, '').split('|').map(x => x.trim());
      let h = c.previousSibling;
      while (h && h.nodeType !== 1) h = h.previousSibling;
      const box = document.createElement('div');
      box.className = 'contrib-section';
      const badge = document.createElement('p');
      badge.className = 'contrib-badge';
      badge.innerHTML = `<span class="avatar">${esc(initials(name))}</span><span>Section contributed by <b>${esc(name)}</b>${aff ? ' · ' + esc(aff) : ''}</span>`;
      if (h && h.tagName === 'H2') {
        h.parentNode.insertBefore(box, h);
        let n = h;
        while (n && !(n !== h && n.nodeType === 1 && n.tagName === 'H2')) { const nx = n.nextSibling; box.appendChild(n); n = nx; }
        h.after(badge);
        h.dataset.contrib = '1';
      }
      c.remove();
    }
    // theorem-like blocks
    $$('blockquote', art).forEach(b => {
      const s = b.querySelector('p > strong:first-child');
      if (s && /^(Theorem|Lemma|Proposition|Corollary|Definition|Remark|Example|Conjecture|Claim|Notation|Exercise|Question|Problem)\b/.test(s.textContent)) b.classList.add('thm');
    });
    // table of contents
    $('#p-toc', host).innerHTML = $$('h2', art).map(h => `<li><a href="#${h.id}">${esc(h.textContent.replace(/#$/, ''))}${h.dataset.contrib ? '<span class="dot" title="New section"></span>' : ''}</a></li>`).join('');
    $$('#p-toc a, .anchor', host).forEach(a => a.addEventListener('click', e => {
      e.preventDefault();
      const t = document.getElementById(a.getAttribute('href').slice(1));
      if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }));
    $$('li.task', art).forEach(li => li.addEventListener('click', () => li.classList.toggle('done')));
  }

  /* ---------- preview actions ---------- */
  $('#edit').addEventListener('click', () => show('form'));
  $('#show-md').addEventListener('click', () => {
    const o = state.out;
    $('#md-path').textContent = 'New file: ' + o.path;
    $('#md-code').textContent = o.text;
    $('#copied').textContent = '';
    $('#dlg-md').hidden = false;
  });
  $('#copy-md').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(state.out.text); $('#copied').textContent = 'Copied'; }
    catch (e) {
      const r = document.createRange(); r.selectNodeContents($('#md-code'));
      const s = getSelection(); s.removeAllRanges(); s.addRange(r);
      $('#copied').textContent = 'Selected: press Ctrl+C (⌘C)';
    }
  });
  function forGitHub(text) {
    // images pasted in Word arrive as data URIs: too large for a pull request made in the browser
    return text.replace(/!\[[^\]]*\]\(data:[^)]*\)/g, '*[Image: send it to the editors in the pull request]*');
  }
  async function copyText(t) {
    try { await navigator.clipboard.writeText(t); return true; } catch (e) { return false; }
  }
  $('#send').addEventListener('click', async () => {
    const d = state.last, o = state.out;
    if (LIVE) {
      const text = forGitHub(o.text);
      const enc = encodeURIComponent(text);
      const pre = enc.length < 7000;
      const url = `${CFG.repo}/new/main?filename=${encodeURIComponent(o.path)}` + (pre ? '&value=' + enc : '');
      const copied = await copyText(text);
      $('#send-body').innerHTML = `<p>Your page is ready. The last step happens on GitHub, with a free account (the same one as for the forum):</p>
        <ol class="flow">
          <li>Click <b>Open GitHub</b>. The file <span class="path">${esc(o.path)}</span> ${pre ? 'is already filled in.' : copied ? 'is copied: click in the large empty box and paste it (Ctrl+V or ⌘V).' : 'must be pasted in the large empty box: click <b>Copy the file</b> first.'}</li>
          <li>At the bottom of the GitHub page, click <b>Propose new file</b> (or <b>Commit changes</b>), then <b>Create pull request</b>.</li>
          <li>The editors read it and may ask for changes in the pull request. Once it is accepted, the page goes online with your name on it.</li>
        </ol>
        <div class="go"><a class="btn" href="${url}" target="_blank" rel="noopener">Open GitHub</a><button type="button" class="btn ghost" id="send-copy">Copy the file</button><button type="button" class="btn ghost" id="send-dl">Download the file</button><span class="copied" id="send-ok">${copied ? 'Copied' : ''}</span></div>`;
      $('#send-copy').addEventListener('click', async () => { $('#send-ok').textContent = (await copyText(text)) ? 'Copied' : 'Copy failed: use Download'; });
      $('#send-dl').addEventListener('click', () => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(new Blob([text], { type: 'text/markdown' }));
        a.download = o.path.split('/').pop();
        document.body.appendChild(a); a.click(); a.remove();
      });
      $('#dlg-send').hidden = false;
      return;
    }
    const what = d.mode === 'new' ? `New guide: ${d.title}` : `New section in “${o.guide.title}”: ${d.sectitle}`;
    const catStep = d.mode === 'new' && d.newcat ? `<li>It proposes the new category <b>${esc(d.category)}</b>. Once accepted, the category gets its own block on the home page, its own filter, and appears in this menu for the next contributors.</li>` : '';
    $('#send-body').innerHTML = `<p>On the real site, this button sends your text to the editors. Here is what happens next:</p>
      <ol class="flow">
        <li>A pull request is opened on GitHub: <b>${esc(what)}</b>, by ${esc(d.name)}. It contains <span class="path">${esc(o.path)}</span>.</li>
        ${catStep}<li>The site is rebuilt automatically for the review: the page, its one-page PDF sheet and the search index.</li>
        <li>Yassine reads it, and may ask for changes in the comments of the pull request.</li>
        <li>Once it is accepted, the page goes online with your name on it.</li>
      </ol>
      <p><b>This is a demo: nothing was sent.</b></p>`;
    $('#dlg-send').hidden = false;
  });
  $$('[data-close]').forEach(b => b.addEventListener('click', () => { b.closest('.dlg').hidden = true; }));
  $$('.dlg').forEach(dl => dl.addEventListener('click', e => { if (e.target === dl) dl.hidden = true; }));
  document.addEventListener('keydown', e => { if (e.key === 'Escape') $$('.dlg').forEach(x => { x.hidden = true; }); });

  // mobile menu (on the site, site.js already handles it)
  const mb = LIVE ? null : $('.menu-btn');
  if (mb) mb.addEventListener('click', () => { const n = $('#site-nav'); const o = n.classList.toggle('open'); mb.setAttribute('aria-expanded', String(o)); });

  setMode(location.hash === '#section' ? 'section' : 'new');
})();
