#!/usr/bin/env python3
"""Check the guides and the contributed sections before they are merged.

Usage: python3 scripts/check_contribution.py
Exits with an error if a file cannot be built; prints warnings for the reviewer.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from build import CATEGORIES, front_matter  # noqa: E402

errors, notes = [], []


def read(f):
    text = f.read_text(encoding='utf-8')
    if not re.match(r'^---\n.*?\n---\n', text, re.S):
        errors.append(f'{f.relative_to(ROOT)}: the file must start with a front matter block between two "---" lines.')
        return None, None
    return front_matter(text)


guides, slugs = {}, {}
for f in sorted((ROOT / 'guides').glob('*.md')):
    meta, body = read(f)
    if meta is None:
        continue
    name = f.relative_to(ROOT)
    for k in ('title', 'slug', 'category', 'summary'):
        if not meta.get(k):
            errors.append(f'{name}: missing "{k}".')
    slug = meta.get('slug', '')
    if slug and not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', slug):
        errors.append(f'{name}: the slug "{slug}" must use lowercase letters, digits and hyphens only.')
    if slug in slugs:
        errors.append(f'{name}: the slug "{slug}" is already used by {slugs[slug]}.')
    slugs[slug] = name
    guides[slug] = body
    if meta.get('category') and meta['category'] not in dict(CATEGORIES):
        notes.append(f'{name}: proposes the new category "{meta["category"]}".')
    if meta.get('author'):
        notes.append(f'{name}: written by {meta["author"]}.')
    if not re.search(r'^## ', body, re.M):
        notes.append(f'{name}: has no section heading (## ...).')

for f in sorted(p for p in (ROOT / 'guides' / 'sections').glob('*.md') if p.name != 'README.md') if (ROOT / 'guides' / 'sections').is_dir() else []:
    meta, body = read(f)
    if meta is None:
        continue
    name = f.relative_to(ROOT)
    for k in ('guide', 'title', 'author'):
        if not meta.get(k):
            errors.append(f'{name}: missing "{k}".')
    g = meta.get('guide', '')
    if g and g not in guides:
        errors.append(f'{name}: there is no guide with the slug "{g}".')
    elif g:
        heads = re.findall(r'^## +(.+)$', guides[g], re.M)
        if meta.get('after') and meta['after'] not in heads:
            notes.append(f'{name}: the section "{meta["after"]}" was not found in {g}; the new section goes before the checklist.')
        if meta.get('title') in heads:
            notes.append(f'{name}: {g} already has a section called "{meta["title"]}".')
        notes.append(f'{name}: section "{meta.get("title")}" by {meta.get("author")} for {g}.')

for n in notes:
    print('note:', n)
for e in errors:
    print('error:', e)
if errors:
    sys.exit(1)
print(f'ok: {len(guides)} guides checked')
