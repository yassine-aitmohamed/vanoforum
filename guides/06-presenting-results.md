---
title: Presenting results and proofs
slug: presenting-results
category: Writing
summary: How to organize sections, choose between Theorem, Proposition and Lemma, write proofs that read as prose, display equations, and keep the LaTeX source clean.
diagram: results-hierarchy
---

A paper can contain excellent results and still be hard to read because of how they are presented. Structure is not decoration. It tells the reader what matters, where to find it and what can be skipped.

## Sections

- **Few sections, each with one job.** A typical research paper has an introduction, a section of preliminaries, two to four sections of results, and sometimes a section of examples. Short papers can do with three sections in total.
- **Name sections after objects or tools**: "Graded modules and their duals", "The blow-up groupoid", "A spectral sequence". Do not title a section "Proof of Theorem A". The title should tell the reader what the section is about.
- **Open each section with its goal.** One or two sentences: "In this section, we construct… The main result is Proposition 3.5, which is the key input in the proof of Theorem B." The reader knows immediately why the section is there.

## Theorem, Proposition, Lemma, Corollary

Use the environments as a hierarchy, not as decoration.

- **Theorem** for the main results of the paper, the ones announced in the introduction. Usually two to four in a paper.
- **Proposition** for important results of the paper that are not main results.
- **Lemma** for technical steps used in proofs.
- **Corollary** for direct consequences of a theorem or a proposition.
- **Remark** and **Example** for comments and illustrations that are not used in proofs.

If every result is a Theorem, nothing stands out. A standard or easy fact does not need an environment at all: state it in a sentence in the text, with a short justification.

**Results from the literature are cited, not restated.** If you use a known result, write "by [8, Theorem 2.1], the map is an isomorphism". Do not restate it as "Proposition 2.3 ([8])" and do not reprove it. Keep the paper focused on what is new.

## Writing proofs

- **Continuous prose.** Write proofs as connected paragraphs, not as "Step 1, Step 2, Step 3". If a proof is long, split it into lemmas with clear statements, then the proof of the theorem becomes short and readable.
- **Announce the strategy.** For a long proof, the first sentence says how it goes: "We argue by induction on the length", "The proof reduces to the case of a point, which we treat with a local model".
- **Make the main proofs easy to find.** When the proof of a main theorem comes much later than its statement, give it a visible heading: **Proof of Theorem B.** in bold. A reader looking for it should find it in seconds.
- **Be exact about what is used.** Each step should be justified by a precise reference: an earlier equation, a numbered lemma, or an exact citation.

## Displayed equations

- **Display the important equations.** Center the key formulas on their own lines. Inline formulas should be short.
- **Number only what you refer to.** An equation needs a number only if the text cites it later. Unnumbered displays are cleaner.
- **Punctuate equations.** A displayed equation is part of a sentence. End it with a comma or a period when the sentence requires it.
- **Align multi-line computations** on the relation symbol, so the reader follows the chain of equalities.

## Notation

- Introduce all notation in one place when possible, usually the preliminaries.
- Use standard symbols for standard objects. Use simple letters ($U$, $V$, $W$ for open sets, $f$, $g$ for maps) and keep fancy alphabets for genuinely different types of objects.
- Never use the same symbol for two different things, and never change the symbol of an object halfway through the paper.

## Figures

Figures are often the fastest way to explain a construction. Keep captions short, one line if possible, and put the explanation in the text that cites the figure. Use the same colors and conventions in all figures of the paper.

## Length

Clarity is worth a few pages. A 20-page paper that a referee reads in one afternoon is better than a 12-page paper that takes a week to decode. Do not condense to the point of losing the reader.

## LaTeX habits that editors notice

- **Use a standard class** (for example `amsart` in mathematics) and the journal's class only at the end, when the paper is accepted.
- **Write references with their name**: `Lemma~\ref{...}` or `Lemma \ref{...}`. Avoid packages that cause trouble on arXiv. Check that the source compiles on arXiv before submitting.
- **Use meaningful or stable labels** and never reuse a label.
- **One bibliography style** for the whole paper, with complete entries: authors, title, journal, volume, year, pages, DOI or arXiv number.
- **Clean the source before posting.** Remove commented-out paragraphs, private notes and unused packages. arXiv makes the source public.
- **Do not fight the class.** Avoid manual spacing such as `\vspace` and `\\` to adjust the layout. Let LaTeX do the typesetting.

## Checklist

- [ ] Sections are named after objects, and each opens with its goal.
- [ ] Theorem is reserved for the main results.
- [ ] Known results are cited with exact numbers, not reproved.
- [ ] Proofs are in prose, and main proofs have bold headings.
- [ ] Only referenced equations are numbered.
- [ ] Notation is introduced once and never changes.
- [ ] The source is clean and compiles on arXiv.
