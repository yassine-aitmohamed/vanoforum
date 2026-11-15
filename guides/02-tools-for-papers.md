---
title: Tools for finding, reading and managing papers
slug: tools-for-papers
category: Reading
summary: Where to search, how to follow new work, how to read PDFs efficiently and how to keep a library you can still use in five years.
diagram: literature-loop
---

Good tools do not replace reading, but they remove most of the friction around it: finding the right paper, knowing when something new appears, jumping to a cited result, and finding your own notes again a year later. Below is a working set. Most of it is free.

## Searching the literature

- **arXiv** (arxiv.org). The preprint server for mathematics, physics, computer science, statistics and more. Most recent work appears there first. Learn the listing pages of your categories and the advanced search by author, title and abstract.
- **Google Scholar** (scholar.google.com). Broad coverage across all fields. Its most useful feature is *Cited by*: it lists the later papers that cite a given paper, which is how you follow an idea forward in time.
- **zbMATH Open** (zbmath.org). A free database of reviews for mathematics, with precise subject classification (MSC codes), author profiles and links between papers. A short review is often the best first pass on an older paper.
- **MathSciNet** (subscription, usually through your library). The other major reviewing database for mathematics, with the Mathematical Citation Quotient for journals.
- **Field databases.** PubMed for life sciences, Scopus and Web of Science for citation data across fields, DBLP for computer science, INSPIRE for high-energy physics.
- **Semantic Scholar** and **Connected Papers** show graphs of related work. They are useful to find the papers you did not know to search for.

A good habit: when you find a key paper, read its bibliography *and* its list of citing papers. The first tells you where the idea comes from, the second where it went.

## Following new work

You cannot search every week by hand. Let the new papers come to you.

- **arXiv email alerts.** Subscribe to the daily listing of one or two categories. Skim titles every morning. Five minutes a day is enough to know your field.
- **Google Scholar alerts.** Create an alert for the names of the people whose work you follow, and for a few precise keywords. Also follow the *citations* of your own papers.
- **Journal tables of contents.** Most journals offer email or RSS alerts for new issues.

Keep the bar low for opening a paper and high for reading it in full. The guide [How to read a research paper](reading-a-paper.html) explains the three passes.

## Reading PDFs

A PDF reader for research should do three things well: show you a citation without losing your place, let you annotate, and keep your annotations with the file.

- **[VanoLib Reader](https://github.com/yassine-aitmohamed/vanolib-extension)** is a free, open-source PDF reader for papers that works in Chrome, Edge and Brave. Clicking a citation shows the reference immediately, with a verified link. Clicking "Figure 3" or "Table 2" shows the figure in place. It supports highlights, notes, a night mode and export of all annotations, and it can copy a reference in BibTeX, AMS, APA, MLA or Chicago style.
- Other options include the Google Scholar PDF Reader extension, which also previews citations, and Skim on macOS, which previews internal links on hover.

Whatever you use, annotate with a purpose: one color for definitions, one for main results, one for things you do not understand yet.

## Managing your library

After a few years, a researcher has read thousands of papers. Without a system, you will reread papers without remembering that you have read them already.

- **Reference managers.** Zotero (free, open source) and JabRef keep your references, PDFs and BibTeX in one place. Zotero's browser connector saves a paper with one click. Export a `.bib` file per project.
- **One BibTeX file per paper you write.** Keep entries clean: correct capitalization in braces, DOI, journal name in full, and arXiv number for preprints. Check each entry against the publisher's page, not against an automatic import.
- **Reading sheets.** Keep your one-page sheets (see the reading guide) next to the PDFs, named by first author and year, for example `Weinstein1983-local-structure.md`.

## Writing and organizing projects

- **[VanoLeaf](https://github.com/yassine-aitmohamed/VanoLeaf-LaTeX-Editor)** is a LaTeX editor in the spirit of Overleaf that runs on your own computer: file tree, source on the left, PDF on the right, click-to-jump, no account and no compile timeout. Long theses compile to the end.
- **[VanoShelf](https://github.com/yassine-aitmohamed/vanoshelf-extension)** adds order to the Overleaf projects page: sort projects into fields, hide the ones you do not want on screen, and blur titles in a shared office.
- **[VanoAtlas](https://github.com/yassine-aitmohamed/vanoatlas)** is a local research workspace that keeps projects, tasks, meetings, notes, papers and LaTeX in one private app.
- **[VanoNote](https://github.com/yassine-aitmohamed/VanoNote)** is a handwritten notebook and classroom whiteboard for pen tablets, with PDF annotation and a live link for students.

All four are free and open source (MIT license). The [Tools page](../tools.html) lists them with installation links.

## A minimal setup to start today

1. Subscribe to the arXiv listing of your main category.
2. Create Google Scholar alerts for five researchers you follow.
3. Install a reference manager and a PDF reader with citation previews.
4. Create one folder per project with its PDFs, reading sheets and `.bib` file.
5. Spend ten minutes every morning on new titles, not more.
