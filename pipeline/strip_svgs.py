"""One-off (2026-11): the exact SVG pieces are replaced by the question store (store/, docs/STORE_DESIGN.md).
Removes question/, figures/, markscheme/ SVG folders from bank/ and the 'svg' links from the question JSON.
Cuts (pages and boxes), marks, mark-scheme links and approvals are unchanged."""
import glob, json, os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
import paths


def strip(n):
    n.pop('svg', None)
    for s in n.get('segments', []):
        s.pop('svg', None)
    for f in n.get('figures', []):
        f.pop('svg', None)
    for r in n.get('mark_scheme', []):
        for s in r.get('segments', []):
            s.pop('svg', None)
    for k in n.get('parts', []):
        strip(k)


if __name__ == '__main__':
    nq = nd = 0
    for f in paths.question_files():
        q = json.load(open(f))
        strip(q)
        json.dump(q, open(f, 'w'), ensure_ascii=False, indent=1)
        nq += 1
        for kind in paths.KINDS:
            d = os.path.join(os.path.dirname(f), kind)
            if os.path.isdir(d):
                shutil.rmtree(d); nd += 1
    print(f'{nq} questions without svg links, {nd} SVG folders removed')
