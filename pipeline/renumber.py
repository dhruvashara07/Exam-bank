"""One shared renumbering function (docs/V5_SPEC.md D): used by the PDF builder (store.sheet) and the page renderer
(store_view.py); the website ports the same rules.

    plan = make_plan(q, printed_parts, new_number, relabel_parts)    # what number every tagged word gets
    unit2 = apply_plan(unit, plan, doc='qp'|'ms')                   # a copy of the unit with the new words

Rules
  question bank view   question number N; Fig/Table n.k numbered 1..k in the order the question prints them; part labels as printed
  worksheet            question numbers 1..n; part labels relabelled in print order per level ((b)(ii) selected -> (a)(i) under
                       its stem); every figref / partref / mark-scheme label follows
  other question       a reference to another question's figure stays as printed (flag 'other-question')
  not printed          a reference to a figure/part that is not in the selection stays as printed (flag 'not-printed')
The original number/labels stay in the stored data; only the drawn words change.
"""
import copy, re
import pymupdf as fitz

FONT = {('sans', 0, 0): 'helv', ('sans', 1, 0): 'hebo', ('sans', 0, 1): 'heit', ('sans', 1, 1): 'hebi',
        ('serif', 0, 0): 'tiro', ('serif', 1, 0): 'tibo', ('serif', 0, 1): 'tiit', ('serif', 1, 1): 'tibi',
        ('mono', 0, 0): 'cour', ('mono', 1, 0): 'cobo', ('mono', 0, 1): 'coit', ('mono', 1, 1): 'cobi'}
_fonts = {}


def text_w(txt, w):
    key = FONT.get((w.get('f', 'sans'), 1 if w.get('b') else 0, 1 if w.get('i') else 0), 'helv')
    if key not in _fonts:
        _fonts[key] = fitz.Font(key)
    return _fonts[key].text_length(txt, fontsize=w['s'])


ROMAN = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii']


def _style(label):
    inner = label.strip('()')
    if re.fullmatch(r'\d+', inner):
        return 'digit'
    if inner in ROMAN and not (inner in ('i', 'v', 'x') and False):
        return 'roman'
    return 'letter'


def _label(style, k):
    if style == 'digit':
        return f'({k + 1})'
    if style == 'roman':
        return f'({ROMAN[k]})' if k < len(ROMAN) else f'({k + 1})'
    return f'({chr(ord("a") + k)})' if k < 26 else f'({k + 1})'


def comps(path):
    return re.findall(r'\([^()]*\)', path)


def make_plan(q, parts, new_number, relabel_parts=True):
    """parts: the printed parts of the question, in print order (each has 'layout' units with tagged words)."""
    plan = {'q': q['number'], 'new_q': new_number, 'fig': {}, 'label': {}, 'path': {}, 'flags': []}
    # figures and tables: numbered in the order their captions are printed
    cnt = {'fig': 0, 'table': 0}
    for p in parts:
        for u in p['layout']:
            for w in u['text']:
                if w.get('role') == 'caption':
                    k = (w['ref']['kind'], w['ref']['n'])
                    if k not in plan['fig']:
                        cnt[w['ref']['kind']] += 1
                        plan['fig'][k] = cnt[w['ref']['kind']]
    # part labels
    seen = {}                                       # parent path -> ordered original child labels
    paths = [p['path'] for p in parts]
    for path in paths:
        cs = comps(path)
        for i, c in enumerate(cs):
            parent = str(q['number']) + ''.join(cs[:i])
            kids = seen.setdefault(parent, [])
            if c not in kids:
                kids.append(c)
    for path in paths:
        cs = comps(path)
        new = []
        for i, c in enumerate(cs):
            parent = str(q['number']) + ''.join(cs[:i])
            kids = seen[parent]
            nl = _label(_style(c), kids.index(c)) if relabel_parts else c
            new.append(nl)
            plan['label'][str(q['number']) + ''.join(cs[:i + 1])] = nl
        plan['path'][path] = str(new_number) + ''.join(new)
    plan['path'][str(q['number'])] = str(new_number)
    # a parent label printed on the same line as its first child ('(d) (i) Calculate ...') belongs to the child's unit:
    # when only a later child is selected, that label is not printed at all -> draw it where the others stand
    printed = {w['path'] for p in parts for u in p['layout'] for w in u['text'] if w.get('role') == 'partlabel'}
    xs = {}
    for p in parts:
        for u in p['layout']:
            for w in u['text']:
                if w.get('role') == 'partlabel':
                    xs.setdefault(len(comps(w['path'])), w['x'])
    plan['synth'] = {}
    for p in parts:
        cs = comps(p['path'])
        miss = []
        for i in range(len(cs) - 1):
            anc = str(q['number']) + ''.join(cs[:i + 1])
            if anc not in printed:
                miss.append((i + 1, anc))
                printed.add(anc)
        if miss and p['layout']:
            plan['synth'][p['path']] = [(lv, anc, xs.get(lv, (42, 66, 90)[min(lv - 1, 2)])) for lv, anc in miss]
    return plan


def _row_shift(ws, i, dx):
    """Move the words after ws[i] on its row by dx (a replaced word got wider/narrower)."""
    y = ws[i]['y']
    for j, w in enumerate(ws):
        if j != i and abs(w['y'] - y) < 2.2 and w['x'] > ws[i]['x'] and not w.get('dir'):
            w['x'] = round(w['x'] + dx, 2)


def _set(w, txt):
    w['t'] = txt
    w['w'] = round(text_w(txt, w), 2) if len(txt) > 1 else w['w']
    w.pop('tl', None)


def apply_plan(u, plan, doc='qp', meta=None):
    """A copy of the unit with the renumbered words (the stored unit is not touched)."""
    u2 = copy.copy(u)
    ws = u2['text'] = [dict(w) for w in u['text']]
    if meta and meta.get('first') and meta.get('path') in plan.get('synth', {}):
        own = next((w for w in ws if w.get('role') == 'partlabel' and w['path'] == meta['path']), None)
        if own is not None:
            for lv, anc, x in plan['synth'][meta['path']]:
                ws.append({'t': plan['label'][anc], 'x': x, 'y': own['y'], 'w': 0, 's': own['s'], 'f': own['f'], 'b': 1,
                           'role': 'partlabel', 'path': anc})
                ws[-1]['w'] = round(text_w(ws[-1]['t'], ws[-1]), 2)
    for i, w in enumerate(ws):
        role = w.get('role')
        if role == 'qnum':
            new = str(plan['new_q'])
            if new != w['t']:
                right = w['x'] + w['w']                   # the number column is right-aligned
                _set(w, new)
                w['w'] = round(text_w(new, w), 2)
                w['x'] = round(right - w['w'], 2)
        elif role == 'mslabel':
            m = re.match(r'^(\d+)((?:\([^()]*\))*)(.*)$', w['t'])
            if m:
                orig = m.group(1) + m.group(2)
                new = plan['path'].get(orig) or (str(plan['new_q']) + m.group(2))
                _set(w, new + m.group(3))
        elif role == 'partlabel':
            new = plan['label'].get(w['path'])
            if new and new != w['t']:
                _set(w, new)
        elif role in ('caption', 'figref'):
            ref = w['ref']
            if ref.get('other'):
                plan['flags'].append(('other-question', w['t']))
                continue
            k = plan['fig'].get((ref['kind'], ref['n']))
            if k is None:
                plan['flags'].append(('not-printed', w['t']))
                continue
            tail = re.match(r'^.*?\d+\.\d+([.,;:)]*)$', w['t'])
            new = f"{plan['new_q']}.{k}" + (tail.group(1) if tail else '')
            if new == w['t']:
                continue
            old_w = w['w']
            _set(w, new)
            dx = round(w['w'] - old_w, 2)
            if role == 'caption':                          # captions are centred under the figure
                w['x'] = round(w['x'] - dx / 2, 2)
                for j in range(i - 1, -1, -1):             # its keyword 'Fig.' just before
                    if abs(ws[j]['y'] - w['y']) < 2.2 and ws[j]['x'] < w['x']:
                        ws[j]['x'] = round(ws[j]['x'] - dx / 2, 2)
                        break
                for j in range(i + 1, len(ws)):            # '(not to scale)' after it
                    if abs(ws[j]['y'] - w['y']) < 2.2 and 0 < ws[j]['x'] - (w['x'] + old_w) < 14:
                        ws[j]['x'] = round(ws[j]['x'] + dx / 2, 2)
            else:
                _row_shift(ws, i, dx)
        elif role == 'partref':
            tail = re.match(r'^(.*?)([.,;:]*)$', w['t'])
            new = plan['path'].get(w['path'])
            if new is None:
                plan['flags'].append(('not-printed', w['t']))
                continue
            bare = re.fullmatch(r'\((?:i{1,3}|iv|v|vi{1,3}|ix|x)\)[.,;:]*', w['t'])
            shown = (comps(new)[-1] if bare else re.sub(r'^\d+', '', new)) + tail.group(2)
            if shown != w['t']:
                old_w = w['w']
                _set(w, shown)
                _row_shift(ws, i, round(w['w'] - old_w, 2))
    return u2
