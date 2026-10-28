"""Build a test paper PDF from chosen questions or parts, in the original layout.

Each selection is a question id, optionally with a part:
    0625_2025MJ_41_q01          whole question
    0625_2025MJ_41_q01:b-ii     part (b)(ii), with the stems of Q1 and (b) above it
Segments are placed at their original size and horizontal position (vector, from the
cleaned source PDF), stacked down A4 pages. A segment never splits across pages.

Usage: python3 pipeline/build_test.py out.pdf SEL [SEL ...] [--title "Test 1"] [--ms] [--space original|compact]
"""
import json, os, sys, argparse
import pymupdf as fitz

sys.path.insert(0, os.path.dirname(__file__))
from run import cleaned, ROOT
import paths

A4 = fitz.paper_rect('a4')
TOP, BOTTOM, GAP = 50.0, A4.height - 45.0, 6.0


def load(qid):
    return (json.load(open(paths.question_file(qid))),) + paths.raw_pdfs(qid)


def pieces(q, part):
    """Segments to print, in order: stems on the way down to the part, then the whole part."""
    want = part.split('-') if part else []
    out = list(q.get('segments', []))
    node = q
    for i, label in enumerate(want):
        node = next(k for k in node.get('parts', []) if k['label'] == label)
        if i < len(want) - 1:
            out += node.get('segments', [])
    def walk(n):
        res = list(n.get('segments', []))
        for k in n.get('parts', []):
            res += walk(k)
        return res
    if want:
        out += walk(node)
    else:
        out = walk(q)
    # labels that would otherwise be missing (they sit on the line of a part we skipped)
    stamps = []
    if want:
        if not q.get('segments'):
            stamps.append((49.6, str(q['number'])))
        n = q
        for depth, label in enumerate(want[:-1]):
            n = next(k for k in n.get('parts', []) if k['label'] == label)
            if not n.get('segments'):
                stamps.append((72.3 if depth == 0 else 92.0, f'({label})'))
    return out, node, stamps


def ms_pieces(node):
    res = []
    for m in node.get('mark_scheme', []):
        res += m['segments']
    for k in node.get('parts', []):
        res += ms_pieces(k)
    return res


def compact(seg):
    """Optional: shrink very large blank working areas to 60% (keeps at least 40 pt)."""
    h = seg['bbox'][3] - seg['bbox'][1]
    gap = seg.get('answer_space', {}).get('working_gap_pt', 0)
    return max(h - 0.4 * max(gap - 40, 0), 20)


class Doc:
    def __init__(self, title):
        self.out = fitz.open(); self.page = None; self.y = BOTTOM; self.title = title; self.n = 0

    def new_page(self):
        self.page = self.out.new_page(width=A4.width, height=A4.height)
        self.n += 1
        if self.title:
            self.page.insert_text((41, 32), self.title, fontsize=9, fontname='helv', color=(0.35, 0.35, 0.35))
        self.page.insert_text((A4.width / 2 - 3, 32), str(self.n), fontsize=9, fontname='helv')
        self.y = TOP

    def place(self, src, page_no, bbox, height=None):
        clip = fitz.Rect(bbox)
        h = height or clip.height
        if self.page is None or self.y + min(h, clip.height) > BOTTOM:
            self.new_page()
        if h < clip.height:      # compact: keep the top (prompt) and bottom (answer line) of the strip
            top_part = fitz.Rect(clip.x0, clip.y0, clip.x1, clip.y0 + h * 0.55)
            bot_part = fitz.Rect(clip.x0, clip.y1 - h * 0.45, clip.x1, clip.y1)
            for part in (top_part, bot_part):
                self.page.show_pdf_page(fitz.Rect(part.x0, self.y, part.x1, self.y + part.height), src, page_no - 1, clip=part)
                self.y += part.height
        else:
            self.page.show_pdf_page(fitz.Rect(clip.x0, self.y, clip.x1, self.y + clip.height), src, page_no - 1, clip=clip)
            self.y += clip.height
        self.y += GAP


def build(out_path, selections, title='', with_ms=False, space='original'):
    d = Doc(title)
    ms_queue = []
    for sel in selections:
        qid, _, part = sel.partition(':')
        q, qp_raw, ms_raw = load(qid)
        src = fitz.open(cleaned(qp_raw))
        segs, node, stamps = pieces(q, part)
        for i, s in enumerate(segs):
            d.place(src, s['page'], s['bbox'], compact(s) if space == 'compact' else None)
            if i == 0:
                y = d.y - GAP - (fitz.Rect(s['bbox']).height if space == 'original' else 0)
                for x, text in stamps:
                    d.page.insert_text((x, y + 4 + 9.3), text, fontsize=11, fontname='hebo')
        d.y += 10
        if with_ms:
            ms_queue.append((q, node if part else q, ms_raw))
    if with_ms and ms_queue:
        d.page = None
        for q, node, ms_raw in ms_queue:
            if q['type'] == 'mcq':
                continue
            msrc = fitz.open(cleaned(ms_raw))
            for s in ms_pieces(node):
                clip = fitz.Rect(s['bbox']); scale = (A4.width - 60) / clip.width
                if d.page is None or d.y + clip.height * scale > BOTTOM:
                    d.new_page()
                d.page.show_pdf_page(fitz.Rect(30, d.y, A4.width - 30, d.y + clip.height * scale), msrc, s['page'] - 1, clip=clip)
                d.y += clip.height * scale + 4
        keys = [(q['id'], q.get('answer')) for q, _, _ in ms_queue if q['type'] == 'mcq']
        if keys:
            if d.page is None or d.y > BOTTOM - 40:
                d.new_page()
            for qid, ans in keys:
                d.page.insert_text((41, d.y + 12), f'{qid}: {ans}', fontsize=10, fontname='helv'); d.y += 15
    d.out.save(out_path, garbage=3, deflate=True)
    return d.n


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('out'); ap.add_argument('sel', nargs='+')
    ap.add_argument('--title', default=''); ap.add_argument('--ms', action='store_true')
    ap.add_argument('--space', default='original', choices=['original', 'compact'])
    a = ap.parse_args()
    print(build(a.out, a.sel, a.title, a.ms, a.space), 'pages')
