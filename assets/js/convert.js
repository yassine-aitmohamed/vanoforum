/*
 * VanoForum converters: Word (.docx) and LaTeX (.tex) to the Markdown of a guide.
 * Runs entirely in the browser. Needs JSZip, mammoth, TurndownService and turndownPluginGfm.
 *
 * Both converters return { md, title, summary, author, notes } where md uses
 * ## for sections, $...$ and $$...$$ for formulas, and "> **Theorem 1.**" blocks
 * for theorem-like environments, which is what scripts/build.py renders.
 */
(function (global) {
  'use strict';

  /* ---------------- shared helpers ---------------- */

  function shiftHeadings(md, top) {
    let fence = false, min = 7;
    const lines = md.split('\n');
    for (const l of lines) {
      if (/^```/.test(l)) fence = !fence;
      const m = !fence && /^(#{1,6})\s/.exec(l);
      if (m) min = Math.min(min, m[1].length);
    }
    if (min === 7) return md;
    fence = false;
    return lines.map(l => {
      if (/^```/.test(l)) fence = !fence;
      const m = !fence && /^(#{1,6})(\s.*)$/.exec(l);
      if (!m) return l;
      return '#'.repeat(Math.min(6, m[1].length - min + top)) + m[2];
    }).join('\n');
  }

  function tidy(md) {
    return md.replace(/[ \t]+$/gm, '').replace(/\n{3,}/g, '\n\n').trim() + '\n';
  }

  /* ---------------- Word equations (OMML) to LaTeX ---------------- */

  const SYM = {
    'α': '\\alpha', 'β': '\\beta', 'γ': '\\gamma', 'δ': '\\delta', 'ε': '\\varepsilon', 'ϵ': '\\epsilon', 'ζ': '\\zeta', 'η': '\\eta', 'θ': '\\theta', 'ϑ': '\\vartheta',
    'ι': '\\iota', 'κ': '\\kappa', 'λ': '\\lambda', 'μ': '\\mu', 'ν': '\\nu', 'ξ': '\\xi', 'π': '\\pi', 'ϖ': '\\varpi', 'ρ': '\\rho', 'ϱ': '\\varrho', 'σ': '\\sigma',
    'ς': '\\varsigma', 'τ': '\\tau', 'υ': '\\upsilon', 'φ': '\\varphi', 'ϕ': '\\phi', 'χ': '\\chi', 'ψ': '\\psi', 'ω': '\\omega',
    'Γ': '\\Gamma', 'Δ': '\\Delta', 'Θ': '\\Theta', 'Λ': '\\Lambda', 'Ξ': '\\Xi', 'Π': '\\Pi', 'Σ': '\\Sigma', 'Υ': '\\Upsilon', 'Φ': '\\Phi', 'Ψ': '\\Psi', 'Ω': '\\Omega',
    '∞': '\\infty', '∂': '\\partial', '∇': '\\nabla', '∈': '\\in', '∉': '\\notin', '∋': '\\ni', '⊂': '\\subset', '⊃': '\\supset', '⊆': '\\subseteq', '⊇': '\\supseteq',
    '∪': '\\cup', '∩': '\\cap', '∅': '\\emptyset', '∀': '\\forall', '∃': '\\exists', '¬': '\\neg', '∧': '\\wedge', '∨': '\\vee', '⊗': '\\otimes', '⊕': '\\oplus',
    '×': '\\times', '·': '\\cdot', '⋅': '\\cdot', '∘': '\\circ', '÷': '\\div', '±': '\\pm', '∓': '\\mp', '≤': '\\leq', '≥': '\\geq', '≠': '\\neq', '≈': '\\approx',
    '≡': '\\equiv', '≅': '\\cong', '∼': '\\sim', '≃': '\\simeq', '∝': '\\propto', '→': '\\to', '←': '\\leftarrow', '↦': '\\mapsto', '⇒': '\\Rightarrow', '⇔': '\\Leftrightarrow',
    '↔': '\\leftrightarrow', '⟶': '\\longrightarrow', '↪': '\\hookrightarrow', '↠': '\\twoheadrightarrow', '…': '\\ldots', '⋯': '\\cdots', '⋮': '\\vdots', '⋱': '\\ddots',
    'ℝ': '\\mathbb{R}', 'ℂ': '\\mathbb{C}', 'ℤ': '\\mathbb{Z}', 'ℕ': '\\mathbb{N}', 'ℚ': '\\mathbb{Q}', 'ℙ': '\\mathbb{P}', 'ℏ': '\\hbar', 'ℓ': '\\ell', '′': "'", '″': "''",
    '−': '-', '⟨': '\\langle', '⟩': '\\rangle', '‖': '\\|', '∖': '\\setminus', '⊥': '\\perp', '∥': '\\|', '⋉': '\\ltimes', '⋊': '\\rtimes', '♮': '\\natural',
    '∗': '\\ast', '⊢': '\\vdash', '⊤': '\\top', '∫': '\\int', '∑': '\\sum', '∏': '\\prod', '√': '\\surd', '°': '^\\circ', '□': '\\square', '∎': '\\blacksquare'
  };
  const NARY = { '∑': '\\sum', '∏': '\\prod', '∐': '\\coprod', '∫': '\\int', '∬': '\\iint', '∭': '\\iiint', '∮': '\\oint', '⋃': '\\bigcup', '⋂': '\\bigcap', '⨁': '\\bigoplus', '⨂': '\\bigotimes', '⋁': '\\bigvee', '⋀': '\\bigwedge' };
  const ACC = { '̂': '\\hat', '̃': '\\tilde', '̄': '\\bar', '̅': '\\bar', '⃗': '\\vec', '̇': '\\dot', '̈': '\\ddot', '̌': '\\check', '̆': '\\breve' };
  const FUNCS = new Set(['sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'sinh', 'cosh', 'tanh', 'log', 'ln', 'exp', 'lim', 'liminf', 'limsup', 'max', 'min', 'sup', 'inf', 'det', 'dim', 'ker', 'deg', 'gcd', 'arg', 'hom', 'Pr']);
  const DELIM = { '(': '(', ')': ')', '[': '[', ']': ']', '{': '\\{', '}': '\\}', '|': '|', '‖': '\\|', '⟨': '\\langle', '⟩': '\\rangle', '⌊': '\\lfloor', '⌋': '\\rfloor', '⌈': '\\lceil', '⌉': '\\rceil', '': '.' };

  function kids(el, name) { return Array.from(el.children).filter(c => c.localName === name); }
  function kid(el, name) { return kids(el, name)[0]; }
  function prop(el, prName, name) {
    const pr = kid(el, prName); if (!pr) return null;
    const p = kid(pr, name); if (!p) return null;
    for (const a of p.attributes) if (a.localName === 'val') return a.value;
    return '';
  }
  function grp(s) { return s.length === 1 ? s : '{' + s + '}'; }

  function run(r) {
    const text = kids(r, 't').map(t => t.textContent).join('').replace(/[\u200b-\u200d\u2061-\u2064\ufeff]/g, '');
    const scr = prop(r, 'rPr', 'scr'), sty = prop(r, 'rPr', 'sty'), nor = kid(r, 'rPr') && kid(kid(r, 'rPr'), 'nor');
    if (FUNCS.has(text.trim())) return '\\' + text.trim() + ' ';
    if (nor || (sty === 'p' && /^[A-Za-z]{2,}$/.test(text))) return '\\mathrm{' + text + '}';
    let out = '';
    for (const ch of text) out += SYM[ch] ? SYM[ch] + (/[a-z]$/.test(SYM[ch]) ? ' ' : '') : (ch === '{' || ch === '}' || ch === '%' || ch === '#' || ch === '&' ? '\\' + ch : ch);
    if (scr === 'double-struck') out = '\\mathbb{' + out + '}';
    else if (scr === 'fraktur') out = '\\mathfrak{' + out + '}';
    else if (scr === 'script') out = '\\mathcal{' + out + '}';
    if (sty === 'b' || sty === 'bi') out = '\\mathbf{' + out + '}';
    return out;
  }

  function omml(el) {
    if (!el) return '';
    const all = () => Array.from(el.children).map(omml).join('');
    switch (el.localName) {
      case 'r': return run(el);
      case 'f': {
        const n = omml(kid(el, 'num')), d = omml(kid(el, 'den')), t = prop(el, 'fPr', 'type');
        if (t === 'lin') return grp(n) + '/' + grp(d);
        if (t === 'noBar') return '\\genfrac{}{}{0pt}{}{' + n + '}{' + d + '}';
        return '\\frac{' + n + '}{' + d + '}';
      }
      case 'sSup': return grp(omml(kid(el, 'e'))) + '^{' + omml(kid(el, 'sup')) + '}';
      case 'sSub': return grp(omml(kid(el, 'e'))) + '_{' + omml(kid(el, 'sub')) + '}';
      case 'sSubSup': return grp(omml(kid(el, 'e'))) + '_{' + omml(kid(el, 'sub')) + '}^{' + omml(kid(el, 'sup')) + '}';
      case 'sPre': return '{}_{' + omml(kid(el, 'sub')) + '}^{' + omml(kid(el, 'sup')) + '}' + grp(omml(kid(el, 'e')));
      case 'rad': {
        const deg = omml(kid(el, 'deg')), e = omml(kid(el, 'e'));
        return deg ? '\\sqrt[' + deg + ']{' + e + '}' : '\\sqrt{' + e + '}';
      }
      case 'nary': {
        const c = prop(el, 'naryPr', 'chr'), op = NARY[c == null ? '∫' : c] || (SYM[c] || '\\int');
        const sub = omml(kid(el, 'sub')), sup = omml(kid(el, 'sup'));
        return op + (sub ? '_{' + sub + '}' : '') + (sup ? '^{' + sup + '}' : '') + ' ' + omml(kid(el, 'e'));
      }
      case 'd': {
        const b = prop(el, 'dPr', 'begChr'), e = prop(el, 'dPr', 'endChr'), s = prop(el, 'dPr', 'sepChr');
        const L = DELIM[b == null ? '(' : b] || b, R = DELIM[e == null ? ')' : e] || e, S = s == null ? '|' : s;
        const es = kids(el, 'e'), only = es.length === 1 && es[0].children.length === 1 ? es[0].children[0] : null;
        if (L === '(' && R === ')' && only && only.localName === 'f' && prop(only, 'fPr', 'type') === 'noBar') return '\\binom{' + omml(kid(only, 'num')) + '}{' + omml(kid(only, 'den')) + '}';
        const inner = kids(el, 'e').map(omml).join(S === '|' ? ' \\mid ' : (DELIM[S] || S));
        return '\\left' + L + inner + '\\right' + R;
      }
      case 'func': return omml(kid(el, 'fName')).replace(/\s+$/, '') + ' ' + grp(omml(kid(el, 'e')));
      case 'limLow': return omml(kid(el, 'e')).replace(/\s+$/, '') + '_{' + omml(kid(el, 'lim')) + '}';
      case 'limUpp': return omml(kid(el, 'e')).replace(/\s+$/, '') + '^{' + omml(kid(el, 'lim')) + '}';
      case 'acc': {
        const c = prop(el, 'accPr', 'chr');
        return (ACC[c == null ? '̂' : c] || '\\hat') + '{' + omml(kid(el, 'e')) + '}';
      }
      case 'bar': return (prop(el, 'barPr', 'pos') === 'top' ? '\\overline{' : '\\underline{') + omml(kid(el, 'e')) + '}';
      case 'groupChr': return (prop(el, 'groupChrPr', 'pos') === 'top' ? '\\overbrace{' : '\\underbrace{') + omml(kid(el, 'e')) + '}';
      case 'm': return '\\begin{matrix}' + kids(el, 'mr').map(r => kids(r, 'e').map(omml).join(' & ')).join(' \\\\ ') + '\\end{matrix}';
      case 'eqArr': return '\\begin{aligned}' + kids(el, 'e').map(omml).join(' \\\\ ') + '\\end{aligned}';
      case 'oMathPara': return kids(el, 'oMath').map(omml).join(' \\\\ ');
      case 'rPr': case 'ctrlPr': case 'fPr': case 'naryPr': case 'dPr': case 'radPr': case 'accPr': case 'barPr': case 'sSupPr': case 'sSubPr': case 'sSubSupPr':
      case 'funcPr': case 'limLowPr': case 'limUppPr': case 'mPr': case 'eqArrPr': case 'groupChrPr': case 'oMathParaPr': case 'boxPr': case 'borderBoxPr': case 'sPrePr': case 'phantPr':
        return '';
      default: return all();
    }
  }

  async function fromDocx(buf) {
    const notes = [];
    const zip = await global.JSZip.loadAsync(buf);
    const f = zip.file('word/document.xml');
    if (!f) throw new Error('This file does not look like a Word document (.docx).');
    const doc = new DOMParser().parseFromString(await f.async('string'), 'application/xml');
    const W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main';
    const maths = [];
    const token = (tex, display) => {
      maths.push({ tex: tex.replace(/\s+/g, ' ').trim(), display });
      const r = doc.createElementNS(W, 'w:r'), t = doc.createElementNS(W, 'w:t');
      t.setAttributeNS('http://www.w3.org/XML/1998/namespace', 'xml:space', 'preserve');
      t.textContent = 'VFMATH' + (maths.length - 1) + 'X';
      r.appendChild(t);
      return r;
    };
    const byName = n => Array.from(doc.getElementsByTagNameNS('*', n));
    for (const p of byName('oMathPara')) p.parentNode.replaceChild(token(omml(p), true), p);
    for (const m of byName('oMath')) {
      // An equation alone in its paragraph is a displayed equation.
      const para = m.parentNode, alone = para.localName === 'p' && !Array.from(para.children).some(c => c !== m && c.localName === 'r' && c.textContent.trim());
      para.replaceChild(token(omml(m), alone), m);
    }
    zip.file('word/document.xml', new XMLSerializer().serializeToString(doc));
    const out = await global.mammoth.convertToHtml({ arrayBuffer: await zip.generateAsync({ type: 'arraybuffer' }) }, {
      styleMap: ["p[style-name='Title'] => p.vf-title:fresh", "p[style-name='Subtitle'] => p.vf-subtitle:fresh", "p[style-name='Abstract'] => p.vf-abstract:fresh",
        "p[style-name='Author'] => p.vf-author:fresh", "p[style-name='Abstract Title'] => !", "p[style-name='Date'] => !", "p[style-name='Quote'] => blockquote > p:fresh", "p[style-name='Intense Quote'] => blockquote > p:fresh"]
    });
    const td = new global.TurndownService({ headingStyle: 'atx', bulletListMarker: '-', codeBlockStyle: 'fenced', emDelimiter: '*' });
    if (global.turndownPluginGfm) td.use(global.turndownPluginGfm.gfm);
    for (const k of ['title', 'subtitle', 'abstract', 'author']) {
      td.addRule(k, { filter: n => n.classList && n.classList.contains('vf-' + k), replacement: c => '\n\nVF' + k.toUpperCase() + ':' + c.replace(/\n+/g, ' ') + '\n\n' });
    }
    const box = document.createElement('div');
    box.innerHTML = out.value;
    box.querySelectorAll('td, th').forEach(c => { const ps = Array.from(c.querySelectorAll('p')); if (ps.length) c.innerHTML = ps.map(p => p.innerHTML).join('<br>'); });
    let md = td.turndown(box);
    const meta = {};
    md = md.replace(/^VF(TITLE|SUBTITLE|ABSTRACT|AUTHOR):(.*)$/gm, (_, k, v) => { if (!meta[k]) meta[k] = v.trim(); return ''; });
    md = md.replace(/VFMATH(\d+)X/g, (_, i) => {
      const m = maths[+i];
      return m.display ? '\n\n$$' + m.tex + '$$\n\n' : '$' + m.tex + '$';
    });
    md = md.replace(/(\n(?:\d+\.|-)\s+[^\n]*\n)\n+(\$\$[^\n]*\$\$)\n\n+(?=(?:\d+\.|-)\s)/g, '$1\n    $2\n\n');
    if (/!\[[^\]]*\]\(data:/.test(md)) notes.push('Images were found. They are kept in the preview; on the site they become files next to the guide.');
    if (maths.length) notes.push(maths.length + ' Word equation' + (maths.length > 1 ? 's were' : ' was') + ' converted to LaTeX.');
    const bad = out.messages.filter(m => m.type === 'warning' && !/Unrecognised paragraph style/.test(m.message));
    if (bad.length) notes.push('Some Word formatting was simplified (' + bad.length + ' item' + (bad.length > 1 ? 's' : '') + ').');
    return { md: tidy(shiftHeadings(md, 2)), title: meta.TITLE || '', summary: meta.ABSTRACT || meta.SUBTITLE || '', author: meta.AUTHOR || '', notes, maths: maths.length };
  }

  /* ---------------- LaTeX to Markdown ---------------- */

  // Read a balanced {...} group starting at s[i] === '{'. Returns [content, indexAfter].
  function group(s, i) {
    if (s[i] !== '{') return null;
    let d = 0;
    for (let j = i; j < s.length; j++) {
      const c = s[j];
      if (c === '\\') { j++; continue; }
      if (c === '{') d++;
      else if (c === '}' && --d === 0) return [s.slice(i + 1, j), j + 1];
    }
    return null;
  }
  function skipWs(s, i) { while (i < s.length && /[ \t]/.test(s[i])) i++; return i; }
  function optArg(s, i) {
    i = skipWs(s, i);
    if (s[i] !== '[') return [null, i];
    let d = 0;
    for (let j = i; j < s.length; j++) {
      if (s[j] === '{') d++; else if (s[j] === '}') d--;
      else if (s[j] === ']' && d === 0) return [s.slice(i + 1, j), j + 1];
    }
    return [null, i];
  }

  // Replace \name[opt]{a1}...{an} using fn(args, opt). Repeats until stable so nesting works.
  function cmd(s, name, n, fn) {
    const re = new RegExp('\\\\' + name + '(?![A-Za-z@])\\*?', 'g');
    for (let guard = 0; guard < 50; guard++) {
      let changed = false, out = '', last = 0, m;
      re.lastIndex = 0;
      while ((m = re.exec(s))) {
        let i = m.index + m[0].length, opt = null;
        [opt, i] = optArg(s, i);
        const args = [];
        let ok = true;
        for (let k = 0; k < n; k++) {
          i = skipWs(s, i);
          if (s[i] === '\n') i = skipWs(s, i + 1);
          const g = group(s, i);
          if (!g) { ok = false; break; }
          args.push(g[0]); i = g[1];
        }
        if (!ok) continue;
        out += s.slice(last, m.index) + fn(args, opt, m[0].endsWith('*'));
        last = i; changed = true;
        re.lastIndex = i;
      }
      if (!changed) return s;
      s = out + s.slice(last);
    }
    return s;
  }

  const THM_DEFAULT = {
    theorem: 'Theorem', thm: 'Theorem', lemma: 'Lemma', lem: 'Lemma', proposition: 'Proposition', prop: 'Proposition', corollary: 'Corollary', cor: 'Corollary',
    definition: 'Definition', defn: 'Definition', def: 'Definition', remark: 'Remark', rem: 'Remark', rmk: 'Remark', example: 'Example', ex: 'Example', exa: 'Example',
    conjecture: 'Conjecture', conj: 'Conjecture', exercise: 'Exercise', question: 'Question', problem: 'Problem', claim: 'Claim', notation: 'Notation', note: 'Note',
    observation: 'Observation', fact: 'Fact', assumption: 'Assumption', hypothesis: 'Hypothesis'
  };

  function typo(x) {
    return x.replace(/---/g, '—').replace(/--/g, '–').replace(/``/g, '“').replace(/''/g, '”').replace(/(^|[\s(])`/g, '$1‘');
  }

  function fromTex(src) {
    const notes = [], ignored = new Set();
    const keep = [];                        // protected chunks
    const protect = (s, kind) => { keep.push({ s, kind }); return 'VFKEEP' + (keep.length - 1) + 'X'; };
    let s = src.replace(/\r\n?/g, '\n');

    // verbatim blocks first, before comments are stripped
    s = s.replace(/\\begin\{(verbatim|lstlisting|minted)\}(?:\[[^\]]*\])?(?:\{[^}]*\})?\n?([\s\S]*?)\\end\{\1\}/g, (_, e, c) => protect('\n\n```\n' + c.replace(/\n$/, '') + '\n```\n\n', 'code'));
    s = s.replace(/\\verb([^a-zA-Z\s])(.*?)\1/g, (_, d, c) => protect('`' + c + '`', 'code'));
    s = s.replace(/(^|[^\\])%.*$/gm, '$1');   // comments
    const PCT = protect('%', 'pct'), DOL = protect('\\$', 'dol');
    s = s.replace(/\\%/g, PCT).replace(/\\\$/g, DOL);
    const inMath = b => b.split(PCT).join('\\%').split(DOL).join('\\$');

    // preamble: title, author, macros, theorem names
    const meta = {};
    const thm = Object.assign({}, THM_DEFAULT);
    const macros = [];
    s.replace(/\\newtheorem\*?\{([^}]+)\}(?:\[[^\]]*\])?\{([^}]+)\}/g, (_, env, label) => { thm[env] = label; });
    {
      const re = /\\(?:newcommand|renewcommand|providecommand|def)\*?\s*\{?\\([A-Za-z@]+)\}?\s*(?:\[(\d)\])?(?:\[[^\]]*\])?\s*/g;
      let m;
      while ((m = re.exec(s))) {
        const g = group(s, re.lastIndex);
        if (g) { macros.push({ name: m[1], n: +(m[2] || 0), body: g[0] }); re.lastIndex = g[1]; }
      }
      const re2 = /\\DeclareMathOperator(\*?)\s*\{\\([A-Za-z]+)\}\s*\{([^}]*)\}/g;
      while ((m = re2.exec(s))) macros.push({ name: m[2], n: 0, body: '\\operatorname' + m[1] + '{' + m[3] + '}' });
    }
    const t = /\\title(?:\[[^\]]*\])?\s*/.exec(s);
    if (t) { const g = group(s, t.index + t[0].length); if (g) meta.title = g[0]; }
    const a = /\\author(?:\[[^\]]*\])?\s*/.exec(s);
    if (a) { const g = group(s, a.index + a[0].length); if (g) meta.author = g[0].split(/\\and|\\\\/)[0]; }

    const bd = /\\begin\{document\}/.exec(s);
    if (bd) s = s.slice(bd.index + bd[0].length);
    s = s.replace(/\\end\{document\}[\s\S]*$/, '');

    // expand user macros (in text and formulas)
    if (macros.length) {
      for (let pass = 0; pass < 6; pass++) {
        const before = s;
        for (const mc of macros) {
          if (mc.n === 0) s = s.replace(new RegExp('\\\\' + mc.name + '(?![A-Za-z@])\\s?', 'g'), () => '{' + mc.body + '}');
          else s = cmd(s, mc.name, mc.n, args => '{' + mc.body.replace(/#(\d)/g, (_, k) => args[k - 1] || '') + '}');
        }
        if (s === before) break;
      }
      notes.push(macros.length + ' macro' + (macros.length > 1 ? 's' : '') + ' from your preamble ' + (macros.length > 1 ? 'were' : 'was') + ' expanded.');
    }

    // abstract becomes the summary
    s = s.replace(/\\begin\{abstract\}([\s\S]*?)\\end\{abstract\}/, (_, c) => { meta.abstract = c.trim(); return ''; });

    // labels and numbering
    const labels = {};
    let eqn = 0, sec = [0, 0, 0], thmN = 0;

    // displayed formulas
    const disp = (body, numbered, envName) => {
      let lab = null;
      body = body.replace(/\\label\{([^}]*)\}/g, (_, l) => { lab = lab || l; return ''; });
      const noNum = /\\nonumber|\\notag/.test(body);
      body = body.replace(/\\nonumber|\\notag/g, '').trim();
      if (envName && /^(align|alignat|eqnarray|flalign)/.test(envName)) body = '\\begin{aligned}' + body.replace(/&\s*=\s*&/g, '&=') + '\\end{aligned}';
      else if (envName && /^(gather)/.test(envName)) body = '\\begin{gathered}' + body + '\\end{gathered}';
      else if (envName && /^multline/.test(envName)) body = '\\begin{gathered}' + body + '\\end{gathered}';
      else if (envName === 'split') body = '\\begin{aligned}' + body + '\\end{aligned}';
      let tag = '';
      if (numbered && !noNum) { eqn++; tag = '\\tag{' + eqn + '}'; if (lab) labels[lab] = { n: String(eqn), kind: 'eq' }; }
      eqCount++;
      body = inMath(body).replace(/\s*\n\s*/g, ' ');
      return protect('\n\n$$' + body.replace(/\n\s*\n/g, '\n') + (tag ? ' ' + tag : '') + '$$\n\n', 'math');
    };
    let eqCount = 0;
    s = s.replace(/\\begin\{(equation|align|gather|multline|alignat|eqnarray|flalign|displaymath)(\*?)\}(?:\{\d+\})?([\s\S]*?)\\end\{\1\2\}/g,
      (_, e, star, body) => disp(body, !star && e !== 'displaymath', e));
    s = s.replace(/\\\[([\s\S]*?)\\\]/g, (_, b) => disp(b, false));
    s = s.replace(/\$\$([\s\S]+?)\$\$/g, (_, b) => disp(b, false));
    s = s.replace(/\\\(([\s\S]*?)\\\)/g, (_, b) => { eqCount++; return protect('$' + inMath(b).trim() + '$', 'math'); });
    s = s.replace(/\$((?:\\.|[^$\\])+?)\$/g, (_, b) => { eqCount++; return protect('$' + inMath(b).replace(/\s+/g, ' ').trim() + '$', 'math'); });

    // bibliography
    const cites = {};
    s = s.replace(/\\begin\{thebibliography\}\{[^}]*\}([\s\S]*?)\\end\{thebibliography\}/, (_, body) => {
      const items = body.split(/\\bibitem/).slice(1);
      const out = items.map((it, k) => {
        let i = 0, opt; [opt, i] = optArg(it, 0);
        const g = group(it, skipWs(it, i));
        if (g) { cites[g[0]] = String(k + 1); it = it.slice(g[1]); }
        return (k + 1) + '. ' + it.replace(/\s+/g, ' ').trim();
      });
      return '\n\n## References\n\n' + out.join('\n') + '\n\n';
    });
    if (/\\bibliography\{/.test(s)) notes.push('A BibTeX file is referenced. Paste the references into a "References" section, or use \\begin{thebibliography}.');
    s = s.replace(/\\bibliography\{[^}]*\}|\\bibliographystyle\{[^}]*\}|\\printbibliography(\[[^\]]*\])?/g, '');

    // sections
    const secCmd = (lvl) => (args, opt, star) => {
      if (!star && lvl <= 3) { sec[lvl - 1]++; for (let k = lvl; k < 3; k++) sec[k] = 0; }
      return '\n\nVFSEC' + lvl + (star ? 's' : 'n') + sec.slice(0, lvl).join('.') + 'VF' + args[0].replace(/\n/g, ' ') + '\n\n';
    };
    s = cmd(s, 'section', 1, secCmd(1));
    s = cmd(s, 'subsection', 1, secCmd(2));
    s = cmd(s, 'subsubsection', 1, secCmd(3));
    s = cmd(s, 'paragraph', 1, a => '\n\n**' + a[0] + '** ');
    s = s.replace(/VFSEC(\d)([sn])([\d.]*)VF([^\n]*)\n\n\s*\\label\{([^}]*)\}/g, (m, l, k, n, title, lab) => { labels[lab] = { n, kind: 'sec' }; return 'VFSEC' + l + k + n + 'VF' + title + '\n\n'; });
    s = s.replace(/VFSEC(\d)[sn][\d.]*VF/g, (_, l) => '#'.repeat(+l + 1) + ' ');

    // tables (tabular inside table/center)
    s = s.replace(/\\begin\{(tabular|tabularx|longtable)\}(?:\{[^}]*\})?\{[^{}]*(?:\{[^}]*\}[^{}]*)*\}([\s\S]*?)\\end\{\1\}/g, (_, e, body) => {
      const rows = body.replace(/\\(hline|toprule|midrule|bottomrule|cline\{[^}]*\})/g, '').split(/\\\\/).map(r => r.trim()).filter(Boolean)
        .map(r => r.split(/(?<!\\)&/).map(c => typo(c.trim().replace(/\n/g, ' ').replace(/\|/g, '\\|'))));
      if (!rows.length) return '';
      const w = Math.max(...rows.map(r => r.length));
      const line = r => '| ' + Array.from({ length: w }, (_, k) => r[k] || '').join(' | ') + ' |';
      return protect('\n\n' + [line(rows[0]), '|' + ' --- |'.repeat(w), ...rows.slice(1).map(line)].join('\n') + '\n\n', 'table');
    });
    s = s.replace(/\\begin\{(table|figure)\*?\}(?:\[[^\]]*\])?/g, '\n\n').replace(/\\end\{(table|figure)\*?\}/g, '\n\n');
    s = cmd(s, 'caption', 1, a => '\n\n*' + a[0] + '*\n\n');
    if (/\\includegraphics/.test(s)) notes.push('Figures (\\includegraphics) are not included in the demo; on the site, images are uploaded next to the guide.');
    s = cmd(s, 'includegraphics', 1, () => '');

    // lists, line by line, with nesting
    {
      const lines = s.split('\n').map(l => l.replace(/^\s+/, ''));
      const out = [], stack = [];
      for (let line of lines) {
        let rest = line;
        // a line may hold several list commands
        while (rest.length) {
          const m = /\\(begin|end)\{(itemize|enumerate|description|compactitem|compactenum)\}(\[[^\]]*\])?|\\item(\[[^\]]*\])?/.exec(rest);
          if (!m) { pushText(rest); break; }
          pushText(rest.slice(0, m.index));
          if (m[1] === 'begin') { if (!stack.length) out.push(''); stack.push(/enum/.test(m[2]) ? '1.' : '-'); }
          else if (m[1] === 'end') { stack.pop(); if (!stack.length) out.push(''); }
          else {
            const depth = Math.max(0, stack.length - 1);
            const marker = stack[stack.length - 1] || '-';
            const lab = m[4] ? '**' + m[4].slice(1, -1) + '** ' : '';
            out.push('    '.repeat(depth) + marker + ' ' + lab);
          }
          rest = rest.slice(m.index + m[0].length).replace(/^\s+/, '');
        }
        if (!line.length) out.push(stack.length ? '' : '');
      }
      function pushText(t) {
        if (!t.trim()) return;
        if (stack.length && out.length && out[out.length - 1].trim()) out[out.length - 1] += (/ $/.test(out[out.length - 1]) ? '' : ' ') + t.trim();
        else if (stack.length) out.push('    '.repeat(stack.length) + t.trim());
        else out.push(t);
      }
      s = out.join('\n');
    }

    // theorem-like environments, proofs, quotes
    const thmNames = Object.keys(thm).map(k => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
    const reThm = new RegExp('\\\\begin\\{(' + thmNames + ')(\\*?)\\}(?:\\s*\\[([^\\]]*)\\])?([\\s\\S]*?)\\\\end\\{\\1\\2\\}', 'g');
    const quoteBlock = (head, body) => {
      // displayed formulas stay inside the block: make their token a single line
      body = body.replace(/VFKEEP(\d+)X/g, (m, i) => {
        const k = keep[+i];
        if (k.kind !== 'math' || k.s.indexOf('$$') < 0) return m;
        k.s = k.s.trim();
        return '\n\n' + m + '\n\n';
      }).replace(/\n{3,}/g, '\n\n');
      const lines = (head + (/^\s*\n\s*(-|1\.)\s/.test(body) ? '\n\n' : (head ? ' ' : '')) + body.trim()).split('\n');
      return '\n\n' + lines.map(l => l.trim() ? '> ' + l : '>').join('\n') + '\n\n';
    };
    s = s.replace(reThm, (_, env, star, name, body) => {
      let lab = null;
      body = body.replace(/\\label\{([^}]*)\}/g, (_, l) => { lab = lab || l; return ''; });
      let num = '';
      if (!star) { thmN++; num = ' ' + thmN; if (lab) labels[lab] = { n: String(thmN), kind: thm[env] }; }
      return quoteBlock('**' + thm[env] + num + '**' + (name ? ' (' + name.trim() + ')' : '') + '.', body);
    });
    s = s.replace(/\\begin\{proof\}(?:\s*\[([^\]]*)\])?([\s\S]*?)\\end\{proof\}/g, (_, name, body) => '\n\n*' + (name ? name.trim() : 'Proof') + '.* ' + body.trim().replace(/\s*\\qedhere/, '') + ' ∎\n\n');
    s = s.replace(/\\begin\{(quote|quotation)\}([\s\S]*?)\\end\{\1\}/g, (_, e, body) => quoteBlock('', body));
    s = s.replace(/\\begin\{(center|flushleft|flushright|minipage)\}(\{[^}]*\})?/g, '').replace(/\\end\{(center|flushleft|flushright|minipage)\}/g, '');

    // references and citations
    const refText = (l, paren) => { const x = labels[l]; if (!x) return '??'; return paren ? '(' + x.n + ')' : x.n; };
    s = cmd(s, 'eqref', 1, a => refText(a[0], true));
    s = cmd(s, '(?:cref|Cref|autoref)', 1, a => a[0].split(',').map(l => { const x = labels[l.trim()]; if (!x) return '??'; const k = x.kind === 'eq' ? 'Equation' : x.kind === 'sec' ? 'Section' : x.kind; return k + ' ' + (x.kind === 'eq' ? '(' + x.n + ')' : x.n); }).join(', '));
    s = cmd(s, '(?:ref|pageref)', 1, a => refText(a[0]));
    s = cmd(s, '(?:cite|citep|citet|parencite|textcite)', 1, (a, opt) => '[' + a[0].split(',').map(k => cites[k.trim()] || k.trim()).join(', ') + (opt ? ', ' + opt : '') + ']');
    s = s.replace(/\\label\{[^}]*\}/g, '');

    // footnotes
    const foot = [];
    s = cmd(s, 'footnote', 1, a => { foot.push(a[0].trim()); return '<sup>' + foot.length + '</sup>'; });

    // inline formatting
    s = cmd(s, '(?:textbf|mathbf)', 1, a => '**' + a[0].trim() + '**');
    s = cmd(s, '(?:emph|textit|textsl)', 1, a => '*' + a[0].trim() + '*');
    s = cmd(s, 'texttt', 1, a => '`' + a[0] + '`');
    s = cmd(s, '(?:underline|textsc|textrm|textsf|textup|textnormal|mbox|hbox|text)', 1, a => a[0]);
    s = cmd(s, 'href', 2, a => '[' + a[1] + '](' + protect(a[0], 'text') + ')');
    s = cmd(s, 'url', 1, a => protect('<' + a[0] + '>', 'text'));
    s = s.replace(/\{\\(bf|bfseries)\s+([^{}]*)\}/g, '**$2**').replace(/\{\\(it|em|itshape)\s+([^{}]*)\}/g, '*$2*');

    // spacing and layout commands
    s = s.replace(/\\(maketitle|tableofcontents|newpage|clearpage|cleardoublepage|noindent|indent|centering|raggedright|medskip|bigskip|smallskip|par|hfill|vfill|qed|appendix|frontmatter|mainmatter|backmatter)(?![A-Za-z])/g, '\n');
    s = cmd(s, '(?:vspace|hspace|setlength|addtolength|setcounter|thispagestyle|pagestyle|keywords|subjclass|date|address|email|thanks|dedicatory|markboth)', 1, () => '');
    s = s.replace(/\\\\(\[[^\]]*\])?/g, '  \n');

    // typography
    s = s.replace(/---/g, '—').replace(/--/g, '–').replace(/``/g, '“').replace(/''/g, '”').replace(/(^|[\s(])`/g, '$1‘').replace(/~/g, ' ')
      .replace(/\\(ldots|dots)(?![A-Za-z])/g, '…').replace(/\\LaTeX(?![A-Za-z])\s?/g, 'LaTeX').replace(/\\TeX(?![A-Za-z])\s?/g, 'TeX').replace(/\\S(?![A-Za-z])\s?/g, '§')
      .replace(/\\&/g, '&').replace(/\\_/g, '\\_').replace(/\\#/g, '#').replace(/\\(,|;|:| |!)/g, ' ').replace(/\\@/g, '')
      .replace(/\\'\{?([aeiouAEIOU])\}?/g, (_, c) => c.normalize('NFD') + '́').replace(/\\`\{?([aeiouAEIOU])\}?/g, (_, c) => c + '̀')
      .replace(/\\\^\{?([aeiouAEIOU])\}?/g, (_, c) => c + '̂').replace(/\\"\{?([aeiouAEIOU])\}?/g, (_, c) => c + '̈').replace(/\\c\{?c\}?/g, 'ç');
    s = s.normalize('NFC');

    // anything left: drop unknown environments and commands, keep their text
    s = s.replace(/\\(begin|end)\{([^}]*)\}(\[[^\]]*\])?/g, (_, be, e) => { ignored.add('\\begin{' + e + '}'); return ''; });
    s = s.replace(/\\([A-Za-z]+)\*?(\[[^\]]*\])?/g, (m, c) => { ignored.add('\\' + c); return ''; });
    for (let k = 0; k < 6; k++) s = s.replace(/(^|[^\\])[{}]/g, '$1');

    if (foot.length) s += '\n\n## Notes\n\n' + foot.map((f, k) => (k + 1) + '. ' + f).join('\n') + '\n';

    // restore protected chunks
    for (let k = 0; k < 3; k++) s = s.replace(/VFKEEP(\d+)X/g, (_, i) => keep[+i].s);

    // paragraphs: LaTeX wraps lines, Markdown keeps them; join soft breaks inside paragraphs
    s = s.split(/\n{2,}/).map(p => {
      if (/^\s*(#|>|\||```|\$\$|-\s|\d+\.\s|\s{4})/m.test(p)) return p.replace(/^\n+|\s+$/g, '');
      return p.replace(/\s*\n\s*/g, ' ').trim();
    }).join('\n\n');

    if (ignored.size) notes.push('Ignored LaTeX commands: ' + Array.from(ignored).slice(0, 8).join(', ') + (ignored.size > 8 ? '…' : '') + '.');
    if (eqCount) notes.push(eqCount + ' formula' + (eqCount > 1 ? 's' : '') + ' kept for KaTeX.');
    if (thmN) notes.push(thmN + ' theorem-like block' + (thmN > 1 ? 's' : '') + ' (theorem, lemma, definition…) numbered.');
    const clean = x => x ? fromTexInline(x) : '';
    return { md: tidy(shiftHeadings(s, 2)), title: clean(meta.title), summary: meta.abstract ? fromTex(meta.abstract).md.replace(/\n+/g, ' ').trim() : '', author: clean(meta.author), notes, maths: eqCount };
  }

  function fromTexInline(x) {
    return x.replace(/\\\\/g, ' ').replace(/\\(thanks|footnote)\{[^}]*\}/g, '').replace(/\\[A-Za-z]+\*?/g, '').replace(/[{}]/g, '').replace(/\s+/g, ' ').trim();
  }

  global.VanoConvert = { fromDocx, fromTex, shiftHeadings };
})(window);
