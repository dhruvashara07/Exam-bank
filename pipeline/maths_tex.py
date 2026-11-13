"""Maths text as LaTeX (KaTeX on the site) - docs/MATHS_PLAN.md section 6. Maths subjects only (0607).

Input: the store layout units of one part (words with x, baseline y, width, size, font; rules; drawn glyphs; figure
boxes). Output: content blocks for the website, e.g.
    [{'type': 'text', 'tex': 'Work out $1\\frac{3}{7} \\div 4\\frac{2}{3}$.'}, {'type': 'figure', 'id': ...},
     {'type': 'answer', 'tex': '$x =$ … or $x =$ …'}]
The exact SVG layout (print) is not touched.

What is understood: words and spaces, stacked fractions (numerator / bar / denominator), raised and lowered small text
(powers, indices), symbols (× ÷ ≤ ≥ ≠ ± π ° ...), column vectors / big brackets drawn as glyph pieces with stacked numbers.
Anything else drawn inside the text (a root sign, an unknown glyph, a diagonal stroke) is NOT guessed: the part gets
{'tex_check': 'picture: <why>'} and the site shows the print picture of that part instead (never wrong maths).

Check (every part): (1) every printed character of the part's text is in the LaTeX (in order of lines), (2) KaTeX parses
every formula (node + katex, out/katex). Parts failing either check fall back to the picture.

    python3 pipeline/maths_tex.py 0607_2025MJ_21          # print the LaTeX of every part of a paper (store must exist)
"""
import glob, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

SYM = {'×': r'\times', '÷': r'\div', '≤': r'\leqslant', '≥': r'\geqslant', '≠': r'\neq', '±': r'\pm', 'π': r'\pi',
       '°': r'^{\circ}', '−': '-', '–': '-', '∩': r'\cap', '∪': r'\cup', '∉': r'\notin', '∈': r'\in', '…': r'\ldots',
       '′': "'", '√': r'\surd', '∞': r'\infty', '≈': r'\approx', 'θ': r'\theta', 'α': r'\alpha', 'β': r'\beta',
       '∠': r'\angle', '%': r'\%', '$': r'\$', '<': '<', '>': '>', '{': r'\{', '}': r'\}', '#': r'\#', '&': r'\&',
       '£': r'\pounds', '€': r'\text{€}', '¥': r'\text{¥}', '·': r'\cdot', '•': r'\bullet', 'µ': r'\mu', 'σ': r'\sigma',
       'Σ': r'\Sigma', 'λ': r'\lambda', 'φ': r'\varphi', 'ξ': r'\xi', '∅': r'\varnothing', '⊂': r'\subset', '⊆': r'\subseteq',
       '∝': r'\propto', '→': r'\to', '△': r'\triangle', '∴': r'\therefore', '\u2032': "'"}
NUM = re.compile(r'-?\d+(?:\.\d+)?')
MATHCH = set('0123456789=+-−–×÷≤≥≠±π<>()[]^_/.,°′∩∪∉∈|:;') | set(SYM)
WORD = re.compile(r"^[A-Za-z][a-z]+[.,:;?!)]*$|^[A-Z][A-Za-z'’]+[.,:;?!)]*$")


def _bbox(d):
    v = [float(x) for x in NUM.findall(d)]
    if len(v) < 4:
        return None
    xs, ys = [], []
    toks = re.findall(r'[MLHVCZ]|-?\d+(?:\.\d+)?', d)
    cx = cy = 0.0
    i, cmd = 0, None
    while i < len(toks):
        t = toks[i]
        if t in 'MLHVCZ':
            cmd = t; i += 1
            if t == 'Z':
                continue
            continue
        if cmd in ('M', 'L'):
            cx, cy = float(toks[i]), float(toks[i + 1]); i += 2
        elif cmd == 'H':
            cx = float(toks[i]); i += 1
        elif cmd == 'V':
            cy = float(toks[i]); i += 1
        elif cmd == 'C':
            cx, cy = float(toks[i + 4]), float(toks[i + 5]); xs += [float(toks[i]), float(toks[i + 2])]
            ys += [float(toks[i + 1]), float(toks[i + 3])]; i += 6
        else:
            i += 1
        xs.append(cx); ys.append(cy)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def _diagonal(d):
    """True when a path has a slanted straight segment or a curve (a root sign, a drawn symbol), not only rules."""
    if 'C' in d:
        return True
    pts, cur, cmd = [], None, None
    toks = re.findall(r'[MLHVZ]|-?\d+(?:\.\d+)?', d)
    i = 0
    while i < len(toks):
        t = toks[i]
        if t in 'MLHVZ':
            cmd = t; i += 1; continue
        if cmd in ('M', 'L'):
            p = (float(toks[i]), float(toks[i + 1])); i += 2
            if cmd == 'L' and cur and abs(p[0] - cur[0]) > 0.6 and abs(p[1] - cur[1]) > 0.6:
                return True
            cur = p
        elif cmd == 'H':
            cur = (float(toks[i]), cur[1] if cur else 0); i += 1
        elif cmd == 'V':
            cur = (cur[0] if cur else 0, float(toks[i])); i += 1
        else:
            i += 1
    return False


def esc_text(t):
    return re.sub(r'([%$&#_{}])', r'\\\1', t)


def tex_token(t):
    """One printed word as LaTeX math."""
    m = FUNC.match(t)
    if m:
        return m.group(1) + '\\' + m.group(2) + (' ' + tex_token(m.group(3)) if m.group(3) else ' ')
    out = []
    for ch in t:
        out.append(SYM.get(ch, ch) + (' ' if ch in SYM and SYM[ch].startswith('\\') and SYM[ch][-1].isalpha() else ''))
    return ''.join(out).replace('  ', ' ')


SMALL_WORDS = {'of', 'to', 'in', 'is', 'on', 'at', 'by', 'the', 'and', 'or', 'an', 'as', 'be', 'it', 'if', 'for', 'are', 'its'}
FUNC = re.compile(r'^(\d*)(sin|cos|tan|log|ln)(\^?-1|[xyθABC]|\d+|\(.*)?$')


def is_mathy(w):
    t = w['t']
    if FUNC.match(t):
        return True
    if w.get('frac') or w.get('vec') or w.get('sup') or w.get('sub'):
        return True
    if WORD.match(t) and not (w.get('i') and len(t) <= 2):
        return False
    if re.match(r'^Answer\b', t):
        return False
    if len(t) == 1 and t.isalpha():
        return (bool(w.get('i')) and t not in ('a', 'A', 'I')) or (t.islower() and t != 'a')     # 'a' alone is the article unless italic
    return all(ch in MATHCH or ch.isdigit() or (ch.isalpha() and w.get('i')) for ch in t) and any(
        ch.isdigit() or ch in SYM or ch in '=+-<>()/^' for ch in t) or (bool(w.get('i')) and len(t) <= 3 and t.isalpha()
                                                             and t.lower() not in SMALL_WORDS)


class Unsure(Exception):
    pass


def part_tex(units, figs_by_id=None, skip_label=True):
    """content blocks for one part, or raise Unsure(why)."""
    blocks = []
    for u in units:
        ws = [dict(w) for w in u['text'] if w.get('t', '').strip()]
        ws = [w for w in ws if w.get('role') not in ('qnum', 'label', 'mark', 'caption') and not w.get('hide')]
        ws = [w for w in ws if not re.fullmatch(r'\[\d{1,2}\]', w['t'])]                 # marks
        ws = [w for w in ws if not (skip_label and re.fullmatch(r'\([a-z]{1,4}\)', w['t']) and w['x'] < 75)]   # part labels
        figs = [dict(f) for f in u.get('figs', [])]
        if any(g for g in u.get('glyphs', []) if not _bracket_piece(g)):
            raise Unsure('drawn symbol in the text')
        S = sorted(w['s'] for w in ws)[len(ws) // 2] if ws else 11.0
        # rules: fraction bars (short thin horizontal under/over words); slanted strokes = drawn maths we do not read
        bars = []
        for l in u.get('lines', []):
            bb = _bbox(l['d'])
            if not bb:
                continue
            if _diagonal(l['d']) and bb[2] - bb[0] < 60 and bb[3] - bb[1] < 25 and \
                    any(abs(w['y'] - bb[3]) < 14 and w['x'] - 20 < bb[0] < w['x'] + w['w'] + 20 for w in ws):
                raise Unsure('drawn sign or letters in the text (root sign, vector arrow?)')
            if bb[2] - bb[0] > 380 or (bb[3] - bb[1] > 1.6 and bb[2] - bb[0] > 1.6) or bb[3] - bb[1] > 30:
                continue                                   # page-wide rules, boxes, table rules: not inline maths
            if bb[3] - bb[1] <= 1.6 and 2.5 <= bb[2] - bb[0] <= 160:
                bars.append(bb)
        used = set()
        toks = []
        for bb in sorted(bars, key=lambda b: (b[1], b[0])):
            yb = (bb[1] + bb[3]) / 2
            num = [w for w in ws if id(w) not in used and bb[0] - 2 <= w['x'] and w['x'] + w['w'] <= bb[2] + 2 and 0 < yb - w['y'] < 0.55 * S + 2]
            den = [w for w in ws if id(w) not in used and bb[0] - 2 <= w['x'] and w['x'] + w['w'] <= bb[2] + 2 and 0.5 * S < w['y'] - yb < 1.25 * S]
            if not num or not den:
                if num and not den:
                    continue                               # an underline
                if den and not num:
                    continue                               # an overline
                continue
            for w in num + den:
                used.add(id(w))
            toks.append({'t': '', 'x': bb[0], 'w': bb[2] - bb[0], 'y': yb + 0.33 * S, 's': S,
                         'frac': (_line_tex(num, S), _line_tex(den, S))})
        brackets = _vectors(u, ws, used, S)
        toks += brackets
        toks += [w for w in ws if id(w) not in used]
        for f in figs:
            toks.append({'t': '', 'x': f.get('x', 0), 'y': f.get('y', 0) + 1, 'w': 0, 's': S, 'fig': f.get('id')})
        blocks += _blocks(toks, S)
    return blocks


def _bracket_piece(g):
    return g.get('h', 0) > 6 and g.get('w', 0) < 9


def _vectors(u, ws, used, S):
    """Column vectors / matrices: tall bracket pieces (glyphs) left and right, numbers stacked between."""
    gl = sorted([g for g in u.get('glyphs', []) if _bracket_piece(g)], key=lambda g: (g['x'], g['y']))
    cols = []
    for g in gl:
        for c in cols:
            if abs(c['x'] - g['x']) < 3 and g['y'] <= c['y1'] + 3:
                c['y1'] = max(c['y1'], g['y'] + g['h']); break
        else:
            cols.append({'x': g['x'], 'y0': g['y'], 'y1': g['y'] + g['h'], 'w': g['w']})
    cols.sort(key=lambda c: c['x'])
    out = []
    used_cols = set()
    for i, a in enumerate(cols):
        if i in used_cols:
            continue
        for j in range(i + 1, len(cols)):
            b = cols[j]
            if j in used_cols or abs(a['y0'] - b['y0']) > 4 or abs(a['y1'] - b['y1']) > 4:
                continue
            inside = [w for w in ws if id(w) not in used and a['x'] < w['x'] < b['x'] and a['y0'] - 2 < w['y'] < a['y1'] + 4]
            if not inside:                             # empty brackets: a column vector to fill in (answer space)
                out.append({'t': '', 'x': a['x'], 'w': b['x'] + b['w'] - a['x'], 'y': (a['y0'] + a['y1']) / 2 + 0.33 * S, 's': S,
                            'vec': r'\begin{pmatrix} \quad \\ \quad \end{pmatrix}'})
                used_cols |= {i, j}
                break
            rows = []
            for w in sorted(inside, key=lambda w: w['y']):
                if rows and abs(rows[-1][0]['y'] - w['y']) < 0.5 * S:
                    rows[-1].append(w)
                else:
                    rows.append([w])
            for w in inside:
                used.add(id(w))
            body = r' \\ '.join(' & '.join(tex_token(x['t']) for x in sorted(r, key=lambda x: x['x'])) for r in rows)
            out.append({'t': '', 'x': a['x'], 'w': b['x'] + b['w'] - a['x'], 'y': (a['y0'] + a['y1']) / 2 + 0.33 * S, 's': S,
                        'vec': r'\begin{pmatrix}' + body + r'\end{pmatrix}'})
            used_cols |= {i, j}
            break
    if len(used_cols) != len(cols):
        raise Unsure('bracket pieces not understood')
    return out


def _line_tex(ws, S):
    """Words of a numerator / denominator (one or two levels: powers inside) as LaTeX."""
    ws = sorted(ws, key=lambda w: w['x'])
    base = max(ws, key=lambda w: w['s'])['y'] if ws else 0
    out, prev = [], None
    for w in ws:
        t = tex_token(w['t']) if not w.get('frac') else r'\frac{%s}{%s}' % w['frac']
        if w['s'] < 0.85 * max(x['s'] for x in ws) and w['y'] < base - 1.5:
            out.append('^{' + t + '}')
        elif w['s'] < 0.85 * max(x['s'] for x in ws) and w['y'] > base + 1:
            out.append('_{' + t + '}')
        else:
            if prev is not None and w['x'] - (prev['x'] + prev['w']) > 0.2 * w['s']:
                out.append(' ')
            out.append(t)
        prev = w
    return ''.join(out).strip()


def _blocks(toks, S):
    """Tokens -> lines (by baseline) -> paragraphs; inline maths wrapped in $...$."""
    toks = [t for t in toks if t.get('t') is not None]
    # small raised / lowered text joins the token before it on the line
    big = [t for t in toks if t['s'] >= 0.85 * S or t.get('frac') or t.get('vec') or t.get('fig')]
    small = [t for t in toks if t not in big]
    for sm in sorted(small, key=lambda t: t['x']):
        host = [b for b in big if b['x'] + b['w'] <= sm['x'] + 1.5 and sm['x'] - (b['x'] + b['w']) < 4 and
                -0.2 * S < (b['y'] - sm['y']) < 0.75 * S]
        down = [b for b in big if b['x'] + b['w'] <= sm['x'] + 1.5 and sm['x'] - (b['x'] + b['w']) < 4 and
                0 < (sm['y'] - b['y']) < 0.5 * S]
        if host and host[-1]['y'] - sm['y'] > 1.2:
            h = max(host, key=lambda b: b['x'])
            h.setdefault('sup', []).append(sm)
        elif down:
            h = max(down, key=lambda b: b['x'])
            h.setdefault('sub', []).append(sm)
        else:
            big.append(dict(sm, s=S))                     # small text on its own line (a note): normal text
    lines = []
    for t in sorted(big, key=lambda t: t['y']):
        if lines and abs(lines[-1]['y'] - t['y']) < 0.45 * S:
            lines[-1]['ws'].append(t)
        else:
            lines.append({'y': t['y'], 'ws': [t]})
    blocks, para, last_y = [], [], None
    for ln in lines:
        ws = sorted(ln['ws'], key=lambda t: t['x'])
        figs = [w for w in ws if w.get('fig')]
        ws = [w for w in ws if not w.get('fig')]
        if figs:
            if para:
                blocks.append({'type': 'text', 'tex': ' '.join(para)}); para = []
            blocks += [{'type': 'figure', 'id': f['fig']} for f in figs]
        if not ws:
            continue
        txt = _line(ws, S)
        answer = any(re.search(r'\.{6,}|…{3,}|_{5,}', w['t']) for w in ws) or any(re.match(r'Answer\b', w['t']) for w in ws)
        if answer:
            if para:
                blocks.append({'type': 'text', 'tex': ' '.join(para)}); para = []
            blocks.append({'type': 'answer', 'tex': txt or ''})
            last_y = ln['y']; continue
        if last_y is not None and ln['y'] - last_y > 1.75 * S and para:
            blocks.append({'type': 'text', 'tex': ' '.join(para)}); para = []
        para.append(txt)
        last_y = ln['y']
    if para:
        blocks.append({'type': 'text', 'tex': ' '.join(para)})
    return blocks


def _tok_tex(w):
    if w.get('frac'):
        t = r'\frac{%s}{%s}' % w['frac']
    elif w.get('vec'):
        t = w['vec']
    else:
        t = tex_token(w['t'])
    if w.get('sub'):
        t += '_{' + ''.join(tex_token(s['t']) for s in sorted(w['sub'], key=lambda s: s['x'])) + '}'
    if w.get('sup'):
        sup = ''.join(tex_token(s['t']) for s in sorted(w['sup'], key=lambda s: s['x']))
        t = (t + ('^{' + sup + '}' if sup != r'^{\circ}' else sup)).replace('^{^{\\circ}}', '^{\\circ}')
    return t


def _line(ws, S):
    """One printed line: runs of maths tokens in $...$, words as text."""
    out, mrun, prev = [], [], None
    def flush():
        if mrun:
            s_ = ''.join(mrun).strip()
            if re.fullmatch(r'[(\[]?\d[\d.,]*[)\]]?[.,:;]?|[(\[]?\d[\d.,]*(?: \d{3})+[)\]]?', s_):
                out.append(s_)                         # a plain number in a sentence stays text ('120 plants', '(20 marks)')
            else:
                out.append('\\(' + s_ + '\\)')
            mrun.clear()
    for k, w in enumerate(ws):
        gap = prev is not None and w['x'] - (prev['x'] + prev['w']) > 0.18 * S
        nxt = ws[k + 1] if k + 1 < len(ws) else None
        glued = (mrun and not gap and re.fullmatch(r'[.,:]', w['t']) and nxt is not None and is_mathy(nxt)
                 and nxt['x'] - (w['x'] + w['w']) < 0.18 * S)          # '3.2' printed as '3' '.' '2'
        if is_mathy(w) or glued:
            if gap and mrun:
                mrun.append(r'\quad ' if w['x'] - (prev['x'] + prev['w']) > 2.2 * S else ' ')
            elif gap and out and not mrun:
                out.append(' ')
            mrun.append(_tok_tex(w))
        else:
            flush()
            if gap or (out and out[-1].endswith('\\)') and prev is not None):
                if out and not out[-1].endswith(' '):
                    out.append(' ')
            t = re.sub(r'\.{6,}|…{2,}', '…', w['t'])
            if re.fullmatch(r'Answer\s*(\([a-z]{1,4}\))*', t):
                prev = w
                continue                                   # 2014 'Answer(a)' before the answer line: the label, not content
            out.append(esc_text(t))
        prev = w
    flush()
    s = ''.join(out)
    s = re.sub(r'\\\(\s*\\\)', ' ', s)
    s = re.sub(r' {2,}', ' ', s).strip()
    return s


# ---------------------------------------------------------------- checks
KATEX_DIR = os.path.join(paths.ROOT, 'out', 'katex')
KATEX_JS = r"""
const katex = require(process.argv[process.argv.length - 1] + '/node_modules/katex');
const items = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = items.map(t => { try { katex.renderToString(t, {throwOnError: true, strict: 'ignore'}); return ''; } catch (e) { return String(e.message).slice(0, 120); } });
process.stdout.write(JSON.stringify(out));
"""


def katex_ok(formulas):
    """[error or ''] per formula; None when KaTeX cannot run here (then the check says 'unchecked')."""
    if not formulas:
        return []
    if not os.path.exists(os.path.join(KATEX_DIR, 'node_modules', 'katex')):
        try:
            os.makedirs(KATEX_DIR, exist_ok=True)
            subprocess.run(['npm', 'install', '--prefix', KATEX_DIR, 'katex@0.16'], capture_output=True, timeout=300)
        except Exception:
            return None
    try:
        r = subprocess.run(['node', '-e', KATEX_JS, KATEX_DIR], input=json.dumps(formulas), capture_output=True, text=True, timeout=300)
        return json.loads(r.stdout)
    except Exception:
        return None


def formulas_of(blocks):
    return [m for b in blocks if b.get('tex') for m in re.findall(r'\\\((.+?)\\\)', b['tex'])]


def printed_chars(units, skip_label=True):
    """The characters a reader sees in the part's text (no labels, marks, dot leaders, figure text)."""
    s = ''
    for u in units:
        for w in u['text']:
            t = w.get('t', '')
            if w.get('role') in ('qnum', 'label', 'mark', 'caption') or w.get('hide') or re.fullmatch(r'\[\d{1,2}\]', t):
                continue
            if skip_label and re.fullmatch(r'\([a-z]{1,4}\)', t) and w['x'] < 75:
                continue
            if re.fullmatch(r'Answer\s*(\([a-z]{1,4}\))*', t):
                continue
            s += re.sub(r'\.{4,}|…', '', t)
    return s


def chars_in(blocks):
    s = ' '.join(b.get('tex', '') for b in blocks)
    s = re.sub(r'\\[()]|\\quad', ' ', s)
    s = re.sub(r'\\(begin|end)\{pmatrix\}', '', s)
    rev = {v.strip(): k for k, v in SYM.items() if v.startswith('\\')}
    s = re.sub(r'\\(sin|cos|tan|log|ln)\b', r'\1', s)
    s = re.sub(r'\\[A-Za-z]+', lambda m: rev.get(m.group(0), ''), s)
    return re.sub(r'[\s{}^_\\&…]', '', s)


def check_chars(units, blocks):
    want = re.sub(r'[\s{}^_\\&…−–-]', '', printed_chars(units))
    got = chars_in(blocks).replace('-', '')
    import collections
    a, b = collections.Counter(want), collections.Counter(got)
    miss = a - b
    miss.pop('$', None); miss.pop('%', None); miss.pop('#', None); miss.pop('°', None)
    return ''.join(sorted(miss.elements()))


def build_record(rec):
    """Adds 'content' (or 'tex_check') to every part of a store question record; returns (ok parts, picture parts)."""
    ok = bad = 0
    pending = []
    for p in rec['parts']:
        p.pop('content', None); p.pop('tex_check', None)
        try:
            blocks = part_tex(p['layout'])
        except Unsure as e:
            p['tex_check'] = 'picture: ' + str(e); bad += 1
            continue
        except Exception as e:
            p['tex_check'] = 'picture: error ' + type(e).__name__; bad += 1
            continue
        miss = check_chars(p['layout'], blocks)
        if miss:
            p['tex_check'] = 'picture: characters missing ' + miss[:20]; bad += 1
            continue
        p['content'] = blocks
        pending.append(p)
    forms = [f for p in pending for f in formulas_of(p['content'])]
    res = katex_ok(forms)
    i = 0
    for p in pending:
        n = len(formulas_of(p['content']))
        errs = [e for e in (res[i:i + n] if res is not None else []) if e]
        i += n
        if res is None:
            p['tex_check'] = 'unchecked (no KaTeX)'; ok += 1
        elif errs:
            p['tex_check'] = 'picture: KaTeX ' + errs[0]
            p.pop('content'); bad += 1
        else:
            p['tex_check'] = 'ok'; ok += 1
    return ok, bad


if __name__ == '__main__':
    for pid in sys.argv[1:]:
        for f in sorted(glob.glob(os.path.join(paths.store_dir(pid), 'q*.json'))):
            rec = json.load(open(f))
            if rec.get('stub'):
                continue
            build_record(rec)
            for p in rec['parts']:
                print(rec['id'][-3:], p['path'], p.get('tex_check'))
                for b in p.get('content', []):
                    print('     ', b['type'], b.get('tex') or b.get('id'))


# ---------------------------------------------------------------- formula list (paper page 2)
FORMULAS = [   # (printed description, LaTeX) - the same lists on every 0607 paper 1-4, 2014-2025 (checked in M0)
    ('Area, A, of triangle, base b, height h.', r'A = \frac{1}{2}bh'),
    ('Area, A, of circle', r'A = \pi r^{2}'),
    ('Circumference, C, of circle', r'C = 2\pi r'),
    ('Curved surface area, A, of cylinder of radius r, height h.', r'A = 2\pi rh'),
    ('Curved surface area, A, of cone of radius r, sloping edge l.', r'A = \pi rl'),
    ('urface area, A, of sphere of radius r.', r'A = 4\pi r^{2}'),
    ('Volume, V, of prism, cross-sectional area A, length l.', r'V = Al'),
    ('Volume, V, of pyramid, base area A, height h.', r'V = \frac{1}{3}Ah'),
    ('Volume, V, of cylinder of radius r, height h.', r'V = \pi r^{2}h'),
    ('Volume, V, of cone of radius r, height h.', r'V = \frac{1}{3}\pi r^{2}h'),
    ('Volume, V, of sphere of radius r.', r'V = \frac{4}{3}\pi r^{3}'),
]


def formula_list(page_text):
    """[{'text': description, 'tex': LaTeX}] for a formula page, in printed order; None if a line is not known."""
    t = ' '.join(page_text.split())
    out = []
    for desc, tex in FORMULAS:
        i = t.find(desc)
        if i >= 0:
            full = re.search(r'[A-Z][^.]*' + re.escape(desc[-12:]), t[max(0, i - 20):i + len(desc)])
            out.append((i, {'text': (full.group(0) if full else desc).strip(), 'tex': tex}))
    i = t.find('For the equation')
    if i >= 0:
        out.append((i, {'text': 'For the equation ax² + bx + c = 0' + (', where a ≠ 0,' if 'where a' in t else ''),
                        'tex': r'x = \frac{-b \pm \sqrt{b^{2} - 4ac}}{2a}'}))
    j = t.find(' sin ')
    if j >= 0 or 'sin\n' in page_text:
        j = j if j >= 0 else len(t)
        out.append((j, {'text': 'For the triangle shown,' if 'For the triangle shown' in t else 'In any triangle ABC',
                        'tex': r'\frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C}'}))
        out.append((j + 1, {'text': '', 'tex': r'a^{2} = b^{2} + c^{2} - 2bc\cos A'}))
        out.append((j + 2, {'text': '', 'tex': r'\text{Area} = \frac{1}{2}bc\sin A' if 'bc sin A' in t else r'\text{Area} = \frac{1}{2}ab\sin C'}))
    known = sum(1 for d, _ in FORMULAS if d[:20] in t) + ('For the equation' in t)
    descs = len(re.findall(r'(?:Area|Circumference|Curved surface area|Surface area|Volume), [A-Z], of', t))
    if descs != sum(1 for d, _ in FORMULAS if d in t):
        return None
    return [x for _, x in sorted(out, key=lambda a: a[0])]
