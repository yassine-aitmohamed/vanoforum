# Contributing to VanoForum

VanoForum is written by researchers for researchers. Every guide is a Markdown file in [`guides/`](guides/), and the site is rebuilt from those files. Contributions of every size are welcome, from a fixed typo to a new guide.

## Fix a guide

1. Open the guide on the website and click **Suggest an edit on GitHub**, or open the file in `guides/` directly.
2. GitHub creates a fork for you. Make the change and describe it in one sentence.
3. Open a pull request. Small fixes are usually merged within a few days.

Good fixes: a broken link, an outdated deadline or portal, a missing example, an unclear sentence, a convention that differs in your field.

## Write a new guide

1. Propose the topic in the [Ideas](https://github.com/yassine-aitmohamed/vanoforum/discussions/categories/ideas) category, so that two people do not write the same guide.
2. Copy the template below into `guides/NN-short-slug.md`, where `NN` is the next free number.
3. Open a pull request. The guide is reviewed for accuracy and clarity, then published with its one-page sheet.

```markdown
---
title: Title in sentence case
slug: short-slug
category: Reading | Writing | Publishing | Method | Careers
summary: One or two sentences that say what the reader will be able to do.
diagram: short-slug
---

One paragraph that says why the topic matters and what the guide covers.

## First section

Short sentences. One idea per paragraph. Concrete examples.

## Checklist

- [ ] A step the reader can check.
- [ ] Another step.

## Summary

- The three to five points to remember.
```

### Style

- Write in plain English, in short and direct sentences.
- Give concrete examples. If an example is invented, say so.
- Every claim about a rule, a deadline or a programme links to its official source.
- End with a checklist the reader can tick and a short summary.

## Suggest a resource or a tool

Post it in [Ideas](https://github.com/yassine-aitmohamed/vanoforum/discussions/categories/ideas) with a link and one sentence on why it helped you.

## Build the site locally

```bash
pip install markdown
python3 scripts/build.py
```

Then open `index.html` in a browser.

## Licences

By contributing, you agree that guides and sheets are published under [CC BY 4.0](LICENSE-CONTENT) and code under the [MIT licence](LICENSE). Contributors are credited in the guide they improve.
