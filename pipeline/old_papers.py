"""Give the 2002-2009 PDFs the names the pipeline uses (one-off, 2026-11; the originals stay in Releases).

Before 2009 Cambridge printed one paper per component (0625/03) and some downloads hold several papers:
    qp_3.pdf / ms_5.pdf                 -> qp_03.pdf / ms_05.pdf            (component, no variant)
    qp_3.pdf with pages of 0625/31 and /32 -> qp_31.pdf + qp_32.pdf       (2008, May/June 2009)
    ms_all.pdf (every component)        -> ms_01.pdf, ms_02.pdf, ...       (2003, June 2004)
Writes the new files next to the originals in raw/ (git-ignored); push them to the branch incoming-raw to
store them in Releases. Prints what it did. Never deletes or changes an original.

    python3 pipeline/old_papers.py [--dry]
"""
import glob, os, re, sys
import pymupdf as fitz

sys.path.insert(0, os.path.dirname(__file__))
from paths import ROOT


def codes(page):
    """Component codes printed on a page: '31', '03', ..."""
    t = page.get_text()
    out = re.findall(r'0625\s*/\s*(\d{1,2})\b', t)
    return [c if len(c) == 2 else '0' + c for c in out]


def split_by_code(doc):
    """{code: [page numbers]}; a page without a code goes with the page before it."""
    groups, cur = {}, None
    for i, pg in enumerate(doc):
        c = codes(pg)
        if len(set(c)) == 1:          # a contents page lists every component: it starts no paper
            cur = c[0]
        if cur is None:
            cur = '?'
        groups.setdefault(cur, []).append(i)
    return groups


def write_pages(doc, pages, dst, dry):
    if os.path.exists(dst):
        return f'exists {os.path.relpath(dst, ROOT)}'
    if not dry:
        out = fitz.open()
        for p in pages:
            out.insert_pdf(doc, from_page=p, to_page=p)
        out.save(dst, garbage=3, deflate=True)
    return f'{os.path.relpath(dst, ROOT)} <- pages {pages[0] + 1}-{pages[-1] + 1} ({len(pages)})'


def main(dry=False):
    for path in sorted(glob.glob(os.path.join(ROOT, 'raw', '0625', '200[0-9]-*', '*.pdf'))):
        d, name = os.path.split(path)
        m = re.fullmatch(r'(qp|ms)_(\d|all)\.pdf', name)
        if not m:
            continue
        kind = m.group(1)
        doc = fitz.open(path)
        groups = split_by_code(doc)
        real = {c: p for c, p in groups.items() if c != '?' and len(c) == 2}
        if m.group(2) == 'all' or len(real) > 1:            # several papers in one file
            # a mark-scheme page naming another paper only in passing must not open a new group
            for c, pages in sorted(real.items()):
                print(write_pages(doc, pages, os.path.join(d, f'{kind}_{c}.pdf'), dry))
            if '?' in groups:
                print(f'  {os.path.relpath(path, ROOT)}: pages {groups["?"]} without a paper code (before the first one)')
        else:
            c = next(iter(real), None) or '0' + m.group(2)
            print(write_pages(doc, list(range(len(doc))), os.path.join(d, f'{kind}_{c}.pdf'), dry))


if __name__ == '__main__':
    main('--dry' in sys.argv)
