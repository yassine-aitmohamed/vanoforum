<p align="center"><img src="assets/img/favicon.svg" width="72" alt="VanoForum"></p>

<h1 align="center">VanoForum</h1>
<p align="center"><b>An open forum for researchers.</b><br>
Practical guides on reading papers, writing them in clear English, choosing a journal and answering referees.<br>
Free one-page sheets, diagrams, open-source tools, and a place to ask questions.</p>

<p align="center">
<a href="https://yassine-aitmohamed.github.io/vanoforum/"><b>Website</b></a> ·
<a href="https://github.com/yassine-aitmohamed/vanoforum/discussions"><b>Forum</b></a> ·
<a href="sheets/vanoforum-research-handbook.pdf"><b>The Research Handbook (PDF)</b></a> ·
<a href="https://yassine-aitmohamed.github.io/vanoforum/tools.html"><b>Tools</b></a>
</p>

---

## Guides

Each guide ends with a checklist and comes with a one-page sheet you can print.

| # | Guide | Topic | Sheet |
|---|---|---|---|
| 1 | [How to read a research paper](guides/01-reading-a-paper.md) | Reading | [PDF](sheets/reading-a-paper.pdf) |
| 2 | [Tools for finding, reading and managing papers](guides/02-tools-for-papers.md) | Reading | [PDF](sheets/tools-for-papers.pdf) |
| 3 | [Writing your first paper in English](guides/03-first-paper-in-english.md) | Writing | [PDF](sheets/first-paper-in-english.pdf) |
| 4 | [Writing the abstract](guides/04-writing-the-abstract.md) | Writing | [PDF](sheets/writing-the-abstract.pdf) |
| 5 | [Writing the introduction, the motivation and the contribution](guides/05-writing-the-introduction.md) | Writing | [PDF](sheets/writing-the-introduction.pdf) |
| 6 | [Presenting results and proofs](guides/06-presenting-results.md) | Writing | [PDF](sheets/presenting-results.pdf) |
| 7 | [Revising paragraphs, step by step](guides/07-revising-paragraphs.md) | Writing | [PDF](sheets/revising-paragraphs.pdf) |
| 8 | [Choosing a journal](guides/08-choosing-a-journal.md) | Publishing | [PDF](sheets/choosing-a-journal.pdf) |
| 9 | [Submission, cover letters and peer review](guides/09-submission-and-peer-review.md) | Publishing | [PDF](sheets/submission-and-peer-review.pdf) |
| 10 | [A research method, from the first idea to the preprint](guides/10-research-methodology.md) | Method | [PDF](sheets/research-methodology.pdf) |

All guides are also collected in **[The Research Handbook](sheets/vanoforum-research-handbook.pdf)**.

## The forum

The forum lives in **[Discussions](https://github.com/yassine-aitmohamed/vanoforum/discussions)**. Posts support Markdown, LaTeX formulas (`$x^2$`, `$$\int_M \omega$$`) and Mermaid diagrams. A free GitHub account is enough to take part.

- **Announcements**: new guides, sheets and tools.
- **General**: one thread per guide, and open discussion about research life.
- **Q&A**: questions about reading, writing, journals and referees.
- **Ideas**: suggest a guide, a sheet or a tool.
- **Show and tell**: share your own tools, templates and workflows.

## Open-source tools

| Tool | What it does |
|---|---|
| [VanoAtlas](https://github.com/yassine-aitmohamed/vanoatlas) | A local research workspace: projects, tasks, meetings, notes, papers and LaTeX in one private app. |
| [VanoLeaf](https://github.com/yassine-aitmohamed/VanoLeaf-LaTeX-Editor) | A LaTeX editor in the spirit of Overleaf that runs on your own computer, with no compile timeout. |
| [VanoLib Reader](https://github.com/yassine-aitmohamed/vanolib-extension) | A PDF reader for papers in the browser: citation cards, figure previews, annotations. |
| [VanoNote](https://github.com/yassine-aitmohamed/VanoNote) | A handwritten notebook and classroom whiteboard for pen tablets. |
| [VanoShelf](https://github.com/yassine-aitmohamed/vanoshelf-extension) | Fields, hidden projects and a discreet mode for the Overleaf projects page. |
| [VanoVeil](https://github.com/yassine-aitmohamed/vanoveil) | A private corner inside Chrome: protected link bar, hidden workspace, privacy veil. |

## Contributing

Corrections and suggestions are welcome. Open a discussion in **Ideas**, or a pull request that edits a file in `guides/`. Guides are plain Markdown with a short front matter.

To rebuild the site and the PDFs:

```bash
pip install markdown
python3 scripts/build.py        # HTML pages from guides/*.md
python3 scripts/build_pdf.py    # sheets/*.pdf (needs xelatex, pandoc, rsvg-convert)
```

## About the background

The animation on the website is an exact solution of the Schrödinger equation: a superposition of eigenstates of the two-dimensional harmonic oscillator with frequency ratio √2, so the motion never repeats. Hue shows the phase of ψ, brightness shows |ψ|², the faint curves are level sets of |ψ|², and the particles follow Bohmian trajectories dx/dt = Im(∇ψ/ψ). See [`assets/js/quantum.js`](assets/js/quantum.js).

## License

Guides, sheets and diagrams: [CC BY 4.0](LICENSE-CONTENT). Code: [MIT](LICENSE).
© 2026 Yassine Ait Mohamed.
