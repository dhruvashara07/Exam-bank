"""ONE review page for Dhruv with a button per open round (Dhruv 2026-11-05).

    python3 pipeline/review_page.py add <round no> <title>     # copy out/review/round_<n> into the page folder as r<n>/
    python3 pipeline/review_page.py drop <round no>            # take a finished round off the page
    python3 pipeline/review_page.py files [r<n>...]            # JSON list of files to publish (all, or some rounds)

The page folder is out/review/page/ (index.html = site/review/index.html, rounds.json, r<n>/...). Publish it with the Artifact
tool to review/portal.json review_url: file_path = out/review/page/index.html, root = out/review/page, files = the list
(at most 255 per publish; a version holds 511 files, so drop finished rounds: their paths go as null).
Figures are merged under the "Rebuilt" picture (one file less per question).
"""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
from PIL import Image, ImageDraw

PAGE = os.path.join(paths.ROOT, 'out', 'review', 'page')


def _rounds():
    p = os.path.join(PAGE, 'rounds.json')
    return json.load(open(p)) if os.path.exists(p) else []


def _save(rs):
    json.dump(rs, open(os.path.join(PAGE, 'rounds.json'), 'w'))
    shutil.copy(os.path.join(paths.ROOT, 'site', 'review', 'index.html'), os.path.join(PAGE, 'index.html'))


def add(n, title):
    os.makedirs(PAGE, exist_ok=True)
    src, dst = os.path.join(paths.ROOT, 'out', 'review', f'round_{n}'), os.path.join(PAGE, f'r{n}')
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst)
    items = json.load(open(os.path.join(dst, 'items.json')))
    for it in items:
        d = os.path.join(dst, it['id'])
        q, f = os.path.join(d, 'q.jpg'), os.path.join(d, 'figs.jpg')
        if os.path.exists(q) and os.path.exists(f):
            a, b = Image.open(q).convert('RGB'), Image.open(f).convert('RGB')
            w = max(a.width, b.width)
            out = Image.new('RGB', (w, a.height + 24 + b.height), 'white')
            out.paste(a, (0, 0))
            dr = ImageDraw.Draw(out)
            dr.rectangle([0, a.height + 8, w, a.height + 10], fill=(200, 120, 0))
            dr.text((4, a.height + 12), 'stored figures:', fill=(150, 80, 0))
            out.paste(b, (0, a.height + 24))
            out.save(q, quality=72, optimize=True)
            os.remove(f)
            it['images'].pop('figs', None)
    json.dump(items, open(os.path.join(dst, 'items.json'), 'w'), ensure_ascii=False)
    rs = [r for r in _rounds() if r['round'] != n] + [{'round': n, 'path': f'r{n}', 'title': title}]
    _save(sorted(rs, key=lambda r: r['round']))


def drop(n):
    gone = files([f'r{n}'])
    _save([r for r in _rounds() if r['round'] != n])
    shutil.rmtree(os.path.join(PAGE, f'r{n}'), ignore_errors=True)
    return gone


def files(only=None):
    out = []
    for root, _, fs in os.walk(PAGE):
        for f in fs:
            rel = os.path.relpath(os.path.join(root, f), PAGE)
            if rel == 'index.html':
                continue
            if only and not any(rel.startswith(o + '/') for o in only) and rel != 'rounds.json':
                continue
            out.append(rel)
    return sorted(out)


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'add':
        add(int(a[1]), ' '.join(a[2:]))
    elif a[0] == 'drop':
        print(json.dumps({p: None for p in drop(int(a[1])) if p != 'rounds.json'}, separators=(',', ':')))
    elif a[0] == 'files':
        print(json.dumps(files(a[1:] or None), separators=(',', ':')))
