(function () {
  'use strict';
  var ROOT = document.body.getAttribute('data-root') || '';
  var store = {
    get: function (k, d) { try { var v = localStorage.getItem('vf:' + k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem('vf:' + k, JSON.stringify(v)); } catch (e) {} }
  };
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function math() {
    if (window.renderMathInElement) {
      window.renderMathInElement(document.body, {
        delimiters: [{ left: '$$', right: '$$', display: true }, { left: '$', right: '$', display: false }],
        ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'],
        throwOnError: false
      });
    }
  }

  function toc() {
    var links = $$('.toc li a');
    if (!links.length || !('IntersectionObserver' in window)) return;
    var map = {};
    links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          links.forEach(function (a) { a.classList.remove('on'); });
          var a = map[e.target.id]; if (a) a.classList.add('on');
        }
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    Object.keys(map).forEach(function (id) { var h = document.getElementById(id); if (h) obs.observe(h); });
  }

  /* menu on small screens */
  function menu() {
    var b = $('.menu-btn'), nav = $('#site-nav');
    if (!b || !nav) return;
    b.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      b.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    $$('a', nav).forEach(function (a) { a.addEventListener('click', function () { nav.classList.remove('open'); b.setAttribute('aria-expanded', 'false'); }); });
  }

  /* reading state */
  var read = store.get('read', {});
  function markDots() {
    $$('[data-slug]').forEach(function (el) { el.classList.toggle('is-read', !!read[el.getAttribute('data-slug')]); });
    $$('[data-path]').forEach(function (card) {
      var items = $$('.steps a', card), done = items.filter(function (a) { return read[a.getAttribute('data-slug')]; }).length;
      var c = $('[data-pathcount]', card), start = $('[data-pathstart]', card);
      if (done) {
        c.textContent = done + ' of ' + items.length + ' read';
        var next = items.filter(function (a) { return !read[a.getAttribute('data-slug')]; })[0];
        if (next) { start.href = next.href; start.textContent = 'Continue'; } else { start.textContent = 'Read again'; }
      }
    });
    var mine = $('[data-mine]'), n = Object.keys(read).length;
    if (mine && n) mine.textContent = 'You have read ' + n + ' of ' + $$('#guides .card').length + '.';
  }
  function guidePage() {
    var main = $('[data-guide]');
    if (!main) return;
    var slug = main.getAttribute('data-guide');
    var state = $('[data-readstate]'), btn = $('[data-markread]');
    function show() {
      var r = !!read[slug];
      if (state) state.textContent = r ? 'Read' : 'Not read yet';
      if (state) state.classList.toggle('yes', r);
      if (btn) btn.textContent = r ? 'Read ✓ (mark as unread)' : 'Mark as read';
      markDots();
    }
    if (btn) btn.addEventListener('click', function () {
      if (read[slug]) delete read[slug]; else read[slug] = 1;
      store.set('read', read); show();
    });
    show();

    /* checklist */
    var tasks = $$('.prose li.task'), saved = store.get('check:' + slug, []);
    var counter = $('[data-checkcount]');
    function count() {
      var d = tasks.filter(function (t) { return t.classList.contains('done'); }).length;
      if (counter) counter.textContent = 'checklist ' + d + '/' + tasks.length;
    }
    tasks.forEach(function (t, i) {
      t.setAttribute('role', 'checkbox'); t.tabIndex = 0;
      if (saved.indexOf(i) > -1) t.classList.add('done');
      t.setAttribute('aria-checked', t.classList.contains('done'));
      function flip() {
        t.classList.toggle('done'); t.setAttribute('aria-checked', t.classList.contains('done'));
        store.set('check:' + slug, tasks.map(function (x, j) { return x.classList.contains('done') ? j : -1; }).filter(function (j) { return j > -1; }));
        count();
      }
      t.addEventListener('click', flip);
      t.addEventListener('keydown', function (e) { if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); flip(); } });
    });
    if (tasks.length) count();

    /* progress bar */
    var bar = $('.progress span'), art = $('.prose');
    if (bar && art) {
      var tick = function () {
        var r = art.getBoundingClientRect(), h = r.height - window.innerHeight;
        var p = h > 0 ? Math.min(1, Math.max(0, -r.top / h)) : 1;
        bar.style.transform = 'scaleX(' + p + ')';
      };
      window.addEventListener('scroll', tick, { passive: true }); window.addEventListener('resize', tick); tick();
    }
  }

  /* filter chips */
  function chips() {
    var cs = $$('.chip');
    cs.forEach(function (c) {
      c.addEventListener('click', function () {
        var f = c.getAttribute('data-filter');
        cs.forEach(function (x) { x.classList.toggle('on', x === c); });
        $$('.gblock').forEach(function (g) { g.hidden = !(f === 'all' || g.getAttribute('data-group') === f); });
      });
    });
  }

  /* search */
  var index = null, loading = null;
  function load() {
    if (index) return Promise.resolve(index);
    if (!loading) loading = fetch(ROOT + 'guides/search.json').then(function (r) { return r.json(); }).then(function (d) { index = d; return d; });
    return loading;
  }
  function norm(s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function search(q) {
    var terms = norm(q).split(/\s+/).filter(function (t) { return t.length > 1; });
    if (!terms.length) return [];
    var out = [];
    index.forEach(function (g) {
      var title = norm(g.t), desc = norm(g.d);
      g.x.forEach(function (sec) {
        var name = norm(sec[1]), text = norm(sec[2]), score = 0, ok = true;
        terms.forEach(function (t) {
          var s = 0;
          if (title.indexOf(t) > -1) s += 6;
          if (name.indexOf(t) > -1) s += 4;
          if (!sec[0] && desc.indexOf(t) > -1) s += 3;
          var m = text.split(t).length - 1; s += Math.min(m, 4);
          if (!s) ok = false; score += s;
        });
        if (ok) out.push({ g: g, sec: sec, score: score + (sec[0] ? 0 : 0.5) });
      });
    });
    out.sort(function (a, b) { return b.score - a.score; });
    var seen = {}, res = [];
    out.forEach(function (r) { var n = seen[r.g.s] = (seen[r.g.s] || 0) + 1; if (n <= 2 && res.length < 12) res.push(r); });
    return res.map(function (r) { return { r: r, terms: terms }; });
  }
  function snippet(text, terms) {
    var t = norm(text), at = -1;
    terms.forEach(function (x) { var i = t.indexOf(x); if (i > -1 && (at < 0 || i < at)) at = i; });
    var start = Math.max(0, at - 60), s = (start ? '…' : '') + text.slice(start, start + 170) + (start + 170 < text.length ? '…' : '');
    var h = esc(s);
    terms.forEach(function (x) {
      h = h.replace(new RegExp('(' + x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'), '<mark>$1</mark>');
    });
    return h;
  }
  function searchUI() {
    var openers = $$('[data-search]');
    if (!openers.length) return;
    var box = document.createElement('div');
    box.className = 'sbox'; box.hidden = true;
    box.innerHTML = '<div class="sbox-in" role="dialog" aria-modal="true" aria-label="Search the guides">' +
      '<div class="sbox-head"><input type="search" id="sq" placeholder="Search 25 guides…" autocomplete="off" spellcheck="false" aria-label="Search">' +
      '<button type="button" class="sbox-x" aria-label="Close">Esc</button></div>' +
      '<ul class="sres" id="sres" role="listbox"></ul>' +
      '<p class="shint">Try <button type="button" data-q="cover letter">cover letter</button> <button type="button" data-q="referee">referee</button> <button type="button" data-q="Q1 journal">Q1 journal</button> <button type="button" data-q="scholarship">scholarship</button> <button type="button" data-q="endorsement">endorsement</button></p></div>';
    document.body.appendChild(box);
    var input = $('#sq', box), list = $('#sres', box), sel = 0, last = document.activeElement;
    function render() {
      var q = input.value.trim();
      if (!q) { list.innerHTML = ''; return; }
      load().then(function () {
        var rs = search(q);
        if (!rs.length) { list.innerHTML = '<li class="none">No guide mentions “' + esc(q) + '”. Ask it in the <a href="https://github.com/yassine-aitmohamed/vanoforum/discussions/new?category=q-a" target="_blank" rel="noopener">forum</a>.</li>'; return; }
        sel = 0;
        list.innerHTML = rs.map(function (x, i) {
          var r = x.r, href = ROOT + 'guides/' + r.g.s + '.html' + (r.sec[0] ? '#' + r.sec[0] : '');
          return '<li role="option"' + (i === 0 ? ' aria-selected="true"' : '') + '><a href="' + href + '">' +
            '<span class="tag t-' + r.g.c.toLowerCase() + '">' + esc(r.g.c) + '</span>' +
            '<b>' + esc(r.g.t) + (r.sec[1] ? ' <small>› ' + esc(r.sec[1]) + '</small>' : '') + '</b>' +
            '<span class="snip">' + snippet(r.sec[0] ? r.sec[2] : r.g.d + ' ' + r.sec[2], x.terms) + '</span></a></li>';
        }).join('');
      }).catch(function () { list.innerHTML = '<li class="none">The search index could not be loaded.</li>'; });
    }
    function move(d) {
      var items = $$('li[role=option]', list); if (!items.length) return;
      items[sel].removeAttribute('aria-selected');
      sel = (sel + d + items.length) % items.length;
      items[sel].setAttribute('aria-selected', 'true'); items[sel].scrollIntoView({ block: 'nearest' });
    }
    function open() { last = document.activeElement; box.hidden = false; document.documentElement.classList.add('locked'); input.focus(); input.select(); load(); }
    function close() { box.hidden = true; document.documentElement.classList.remove('locked'); if (last && last.focus) last.focus(); }
    openers.forEach(function (o) { o.addEventListener('click', open); });
    input.addEventListener('input', render);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
      else if (e.key === 'Enter') { var a = $('li[aria-selected] a', list); if (a) { e.preventDefault(); close(); location.href = a.href; } }
    });
    box.addEventListener('click', function (e) {
      if (e.target === box || e.target.classList.contains('sbox-x')) close();
      var q = e.target.getAttribute && e.target.getAttribute('data-q');
      if (q) { input.value = q; render(); input.focus(); }
      if (e.target.closest && e.target.closest('.sres a')) close();
    });
    document.addEventListener('keydown', function (e) {
      var typing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) || document.activeElement.isContentEditable;
      if (e.key === 'Escape' && !box.hidden) close();
      else if ((e.key === '/' && !typing) || ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k')) { e.preventDefault(); open(); }
    });
  }

  /* abstract checker (guide: Writing the abstract) */
  function abstractChecker() {
    var ta = $('#ac-in');
    if (!ta) return;
    var out = $('#ac-out'), cnt = $('#ac-count');
    var BEFORE = 'In this paper, we study certain properties of interacting particle systems. These systems are important in probability and statistical physics. We consider their long-time behavior and we give some conditions under which they converge. As a key step, we compute a spectral gap in a special case. We also discuss some examples.';
    var WEAK = ['compute', 'computes', 'computed', 'deduce', 'deduces', 'give', 'gives', 'study', 'studies', 'studied', 'discuss', 'discusses', 'consider', 'considers', 'investigate', 'investigates', 'present', 'presents', 'describe', 'describes'];
    var HYPE = ['novel', 'powerful', 'elegant', 'groundbreaking', 'remarkable', 'for the first time', 'first time'];
    var UNDER = ['a tool', 'a key step', 'key step', 'technical lemma', 'a special case of', 'special case of'];
    function run() {
      var t = ta.value.trim(), items = [];
      var words = t ? t.split(/\s+/).length : 0;
      cnt.textContent = words + (words === 1 ? ' word' : ' words');
      if (!t) { out.innerHTML = ''; return; }
      var low = t.toLowerCase(), first = low.split(/(?<=[.!?])\s+/)[0] || '';
      function add(ok, msg) { items.push('<li class="' + (ok ? 'ok' : 'warn') + '">' + msg + '</li>'); }
      if (/^(in this (paper|article|note|work)|this (paper|article|note))/.test(low)) add(false, 'Opens with “' + esc(t.split(/[,.]/)[0]) + '”. Start with the result instead: “We prove that…”.');
      else if (/^we (study|consider|investigate|discuss|look at)/.test(low)) add(false, 'Opens with “' + esc(t.split(/\s+/).slice(0, 2).join(' ')) + '”. Say what you prove, construct or determine.');
      else if (/^we (prove|show|construct|classify|characteri[sz]e|determine|establish|introduce|extend|obtain)/.test(low)) add(true, 'The first sentence starts with a result.');
      else add(false, 'The first sentence does not start with “We + a result verb”. Check that it states the main result.');
      var weak = WEAK.filter(function (w) { return new RegExp('\\b' + w + '\\b', 'i').test(t); });
      if (weak.length) add(false, 'Weak verbs: <b>' + weak.map(esc).join(', ') + '</b>. Prefer prove, construct, classify, characterize, determine, establish.');
      else add(true, 'No weak verbs from the guide’s list.');
      if (/[$\\^_=<>∈⊂→∫∑]/.test(t)) add(false, 'Symbols or formulas found. Describe the objects in words.');
      else add(true, 'No symbols or formulas.');
      if (/\[\d+|\(\d{4}\)|et al\./i.test(t)) add(false, 'Looks like a citation. An abstract usually has none.');
      var under = UNDER.filter(function (w) { return low.indexOf(w) > -1; });
      if (under.length) add(false, 'Undersells a result: “' + esc(under[0]) + '”. If it is new, say what it is.');
      var hype = HYPE.filter(function (w) { return low.indexOf(w) > -1; });
      if (hype.length) add(false, 'Oversells: “' + esc(hype[0]) + '”. Let the result speak.');
      if (/\bsome (properties|conditions|results|examples)\b|\bcertain\b/i.test(t)) add(false, '“Some …” or “certain …” hides the result. Name it.');
      if (/\n\s*\n|^\s*[-•*]\s/m.test(ta.value)) add(false, 'Several paragraphs or a list. An abstract is one paragraph of prose.');
      if (words < 50) add(false, 'Short (' + words + ' words). Make sure every main contribution appears.');
      else if (words > 200) add(false, 'Long (' + words + ' words). Most abstracts run 80 to 150 words. Check the journal limit.');
      else add(true, 'Length ' + words + ' words, within the usual range.');
      out.innerHTML = items.join('');
    }
    ta.addEventListener('input', run);
    $('#ac-demo').addEventListener('click', function () { ta.value = BEFORE; run(); ta.focus(); });
  }

  document.addEventListener('DOMContentLoaded', function () {
    math(); toc(); menu(); markDots(); guidePage(); chips(); searchUI(); abstractChecker();
  });
  window.addEventListener('load', math);
})();
