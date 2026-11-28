# Contributing to VanoForum

VanoForum is written by researchers for researchers. Every guide is a Markdown file in [`guides/`](guides/), and the site is rebuilt from those files. Contributions of every size are welcome, from a fixed typo to a new guide.

## Before you write

- **Check what already exists.** Search the guides on the site first. If your topic is already covered, add a section to that guide instead of writing a new one, so that readers find everything in one place. The contribution page warns you when your title is close to an existing guide.
- **Bring something new:** the rules of your country or your field, a worked example, a mistake you made and how you fixed it.
- **Write what you know first-hand,** in plain English and short sentences. Link every rule, deadline or programme to its official source.
- **Do not copy** text from other websites, books or guides, even with small changes.

## Contribute from the website (Word or LaTeX)

The easiest way: open the [contribution page](https://yassine-aitmohamed.github.io/vanoforum/contribute.html).

1. Choose **a new guide** or **a section in an existing guide**.
2. Write your name (it is printed on the page), and optionally your affiliation and a link.
3. Upload a Word (`.docx`) or LaTeX (`.tex`) file, or type your text. Headings, lists, tables, theorems and formulas are kept. PDF and old `.doc` files are not accepted.
4. Click **Generate the page** to see your page in the style of the site.
5. Click **Send for review**. GitHub opens with your file ready: click **Propose new file**, then **Create pull request**. You need a free GitHub account, the same as for the forum.

The editors review every pull request. Once it is merged, the site rebuilds itself: the page, its one-page PDF sheet and the search index.

If no category fits your guide, choose **Create a new category** in the menu. A new category appears on the site once the guide is accepted.

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
category: Reading | Writing | Publishing | Method | Careers | Philosophy | Wellbeing | a new one
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

Optional fields: `author`, `affiliation` and `author_url` print your name under the title and in the contributors box. A category that is not in the list above creates a new category; add `category_description:` with one sentence for the home page. `diagram:` is optional for new guides: the editors draw one after review.

## Add a section to an existing guide

A section is a file of its own in [`guides/sections/`](guides/sections/), named `guide-slug--section-slug.md`. The site inserts it into the guide with your name on it.

```markdown
---
guide: choosing-a-journal
title: How mathematicians in Morocco choose a journal
after: Rules you must follow
author: Your name
affiliation: Your university (optional)
author_url: https://your-page (optional)
---

Your text, with ### for sub-headings, lists and $formulas$.
```

`after` is the title of the section yours follows. Leave it out to place your section before the checklist.

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
python3 scripts/check_contribution.py   # checks the front matter of guides and sections
python3 scripts/build.py
```

Then open `index.html` in a browser.

## Licences

By contributing, you agree that guides and sheets are published under [CC BY 4.0](LICENSE-CONTENT) and code under the [MIT licence](LICENSE). Contributors are credited in the guide they improve.
