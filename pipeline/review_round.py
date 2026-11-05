"""Build a review round for Dhruv: flagged questions + a random sample, as files for the review page.

    python3 pipeline/review_round.py new <round no> <paper ids...> [--sample 3] [--max 100] [--title "..."] [--intro "..."]
    python3 pipeline/review_round.py close <round no> <answers.json>   # after reading the page's feedback

`new` writes
    out/review/round_<n>/round.json, items.json, <qid>/*.jpg     -> publish with the Artifact tool to the
                                                                  review page (review/portal.json review_url)
    review/rounds/<n>.json  {round, status: open, collection, items}   (the tracker's 'your review' stage)
Items: every question with a flag, an automatic-check problem or a stored piece that differs from the page
(review/store/<paper>.json, pipeline/store.py verify) in those papers, plus `--sample`
random questions per paper (seeded by the round number, so the choice is repeatable).
The page stores answers in its database, collection feedback_r<n>, doc id = question id:
    {verdict: ok|wrong, issues: [...], note, at}
`close` stores those answers in review/rounds/<n>.json (status closed) for the record.
"""
import datetime, json, os, random, re, sys

sys.path.insert(0, os.path.dirname(__file__))
import paths
import review_assets as ra
from PIL import Image


def nodes(n, depth=0):
    yield n, depth
    for k in n.get('parts', []):
        yield from nodes(k, depth + 1)


def editable_payload(q, d, qid):
    """Content blocks for the page's 'Editable' tab, with each figure saved as its own image."""
    import store
    sq, sdir = store.load(qid)
    if sq.get('stub'):
        sq, sdir = store.load(sq['same_as'][0])
    figs = {}
    for i, f in enumerate(sq.get('figures', [])):
        name = f'fig{i + 1}.jpg'
        im = ra.fig_img(os.path.join(sdir, 'figures', f['file']))
        if im.width > 700:
            im = im.resize((700, round(im.height * 700 / im.width)), Image.LANCZOS)
        im.save(os.path.join(d, name), quality=75, optimize=True)
        figs[f['id']] = f'{qid}/{name}'
    out = []
    for n, depth in nodes(q):
        out.append({'label': n.get('label'), 'depth': depth, 'content': n.get('content', [])})
    return out, figs


def risk_reasons(qid):
    """Why a question needs Dhruv's eyes even when every automatic check passed. Built from what his
    rounds 5-7 found wrong: option pictures and mark-scheme layout, never plain text questions."""
    import store as S
    try:
        q, st = S.load(qid)
        if q.get('stub'):
            return []
    except Exception:
        return []
    out = []
    mp = q.get('ms_p')
    if mp:
        if mp.get('modes', {}).get('scale'):
            out.append('mark scheme: a row could not be re-wrapped and is shrunk to fit')
        last = mp['rows'][-1]['text']
        if not (len(last) == 2 and last[0]['t'] == 'Total'):
            out.append('mark scheme: no Total row of our own')
        elif last[1]['t'] != str(q.get('marks')):
            out.append(f"mark scheme: Total {last[1]['t']} but the question has {q.get('marks')} marks")
        if mp.get('printed_total'):
            out.append(f"mark scheme prints Total {mp['printed_total']}, the question has {q.get('marks')} marks: we show {q.get('marks')}")
        if mp.get('problems'):
            out.append('mark scheme: a word check failed')
        if [t['t'] for t in mp['rows'][0]['text']][:1] != ['Q']:
            out.append('mark scheme: header row is not Q | Answer | Marks')
    labs = {r['label'].split('(')[0] for p in q.get('parts', []) for r in p.get('ms', [])}
    if labs - {str(q.get('number'))}:
        out.append(f"mark scheme rows of another question attached ({', '.join(sorted(labs))})")
    if mp and sum(1 for v in mp['rows'] if len(v['text']) == 2 and v['text'][0]['t'] == 'Total') > 1:
        out.append('mark scheme: more than one Total row')
    if q.get('options') and any('figure' in o for o in q['options']):
        out.append('options split into separate pictures')
    for f in q.get('figures', []):
        if f.get('table_as_picture'):
            out.append(f"table kept as a picture ({f['table_as_picture']})")
            break
    return out


def new(rnd, pids, sample=3, title=None, intro=None, max_items=None, recheck=None, risk=False, spot=0):
    """max_items caps the round (one page version holds ~100 items): flagged items first (Cambridge
    flags, then figure crops, then editable text) up to four fifths, then random spot checks spread over
    the papers. Flags that did not fit go into the next round (the paper waits for them)."""
    byid = {os.path.basename(f)[:-5]: f for f in paths.question_files()}
    rng = random.Random(rnd)
    reasons, prio, samples = {}, {}, []
    rank = {'flag': 0, 'figure': 1, 'text': 2}
    for pid in pids:
        qids = sorted(q for q in byid if q.startswith(pid + '_'))
        chk = json.load(open(os.path.join(paths.CHECKS, pid + '.json'))) if os.path.exists(os.path.join(paths.CHECKS, pid + '.json')) else {}
        for p in chk.get('problems', []) + chk.get('flags', []):
            qid = p['id'] if p['id'] in byid else None
            if p['kind'] == 'text':      # the old editable layer: replaced by the store check below
                continue
            if qid:
                reasons.setdefault(qid, []).append(p['detail'] if p['kind'] == 'flag' else f"{p['kind']}: {p['detail']}")
                prio[qid] = min(prio.get(qid, 9), rank.get(p['kind'], 3))
        sv = os.path.join(paths.STORE_CHECKS, pid + '.json')
        for d in (json.load(open(sv)).get('differ', []) if os.path.exists(sv) else []):
            if d['q'] in byid:            # a stored piece that does not redraw like the paper
                reasons.setdefault(d['q'], []).append(f"stored copy differs from the paper in {d['unit']}: "
                                                      f"{d['missing']}% missing, {d['extra']}% extra")
                prio[d['q']] = min(prio.get(d['q'], 9), 1)
        rest = [q for q in qids if q not in reasons]
        samples.append(rng.sample(rest, min(sample, len(rest))))
    if risk:                                   # strict mode (Dhruv 2026-11-05): only what can go wrong, see risk_reasons()
        for pid in pids:
            for qid in sorted(q for q in byid if q.startswith(pid + '_')):
                for why in risk_reasons(qid):
                    reasons.setdefault(qid, []).append(why); prio[qid] = min(prio.get(qid, 9), 1)
        rest = [q for pid in pids for q in sorted(byid) if q.startswith(pid + '_') and q not in reasons]
        samples = [rng.sample(rest, min(spot, len(rest)))]
        sample = 1 if spot else 0
        samples = [[q] for q in samples[0]]
    for qid, why in (recheck or {}).items():    # items fixed after an earlier round: shown again first
        if qid in byid:
            reasons.setdefault(qid, []).insert(0, why); prio[qid] = -1
    flagged = sorted(prio, key=lambda q: (prio[q], q))
    sampled = [q for k in range(sample) for lst in rng.sample(samples, len(samples)) for q in lst[k:k + 1]]
    if max_items is not None:            # keep a fifth of the round for spot checks; left-over flags wait for the next round
        flagged = flagged[:max_items - min(len(sampled), max_items // 5)]
        sampled = sampled[:max(0, max_items - len(flagged))]
    items = [(q, 'flagged') for q in flagged] + [(q, 'sample') for q in sampled]
    out_dir = os.path.join(paths.ROOT, 'out', 'review', f'round_{rnd}')
    built = ra.render_items(out_dir, items, reasons, byid)
    for it in built:
        q = json.load(open(byid[it['id']]))
        it['editable'], it['figure_images'] = editable_payload(q, os.path.join(out_dir, it['id']), it['id'])
        for fn in os.listdir(os.path.join(out_dir, it['id'])):     # one page version holds max 511 files: keep figs.jpg only
            if re.fullmatch(r'fig\d+\.jpg', fn):
                os.remove(os.path.join(out_dir, it['id'], fn))
        it['figure_images'] = {}
    json.dump(built, open(os.path.join(out_dir, 'items.json'), 'w'), ensure_ascii=False)
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
    meta = {'round': rnd, 'collection': f'feedback_r{rnd}', 'created': now,
            'title': title or f'Review round {rnd}',
            'intro': intro or 'Questions the checks flagged, plus a few random ones from each paper. '
                              'Look at the rebuilt question against the original page; tap "Looks right" or say what is wrong.',
            'papers': pids}
    json.dump(meta, open(os.path.join(out_dir, 'round.json'), 'w'), ensure_ascii=False)
    os.makedirs(paths.ROUNDS, exist_ok=True)
    rec = {**meta, 'status': 'open', 'items': [{'id': i['id'], 'group': i['group'], 'reasons': i['reasons']} for i in built]}
    json.dump(rec, open(os.path.join(paths.ROUNDS, f'{rnd}.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'round {rnd}: {len(built)} items ({sum(i["group"] == "flagged" for i in built)} flagged) -> {out_dir}')
    return out_dir


def close(rnd, answers_file):
    f = os.path.join(paths.ROUNDS, f'{rnd}.json')
    rec = json.load(open(f))
    ans = json.load(open(answers_file))
    rec['answers'] = ans
    rec['status'] = 'closed'
    rec['closed'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
    json.dump(rec, open(f, 'w'), ensure_ascii=False, indent=1)
    wrong = [k for k, v in ans.items() if v.get('verdict') == 'wrong']
    print(f'round {rnd} closed: {len(ans)} answers, {len(wrong)} wrong: {" ".join(wrong)}')


if __name__ == '__main__':
    a = sys.argv[1:]
    def opt(name, default=None):
        if name in a:
            i = a.index(name); v = a[i + 1]; del a[i:i + 2]; return v
        return default
    if a and a[0] == 'new':
        sample = int(opt('--sample', 3)); title = opt('--title'); intro = opt('--intro')
        mx = opt('--max'); mx = int(mx) if mx else None
        rc = opt('--recheck')                      # "qid=why;qid=why"
        rc = dict(x.split('=', 1) for x in rc.split(';') if '=' in x) if rc else None
        risk = '--risk' in a
        if risk:
            a.remove('--risk')
        spot = int(opt('--spot', 0))
        new(int(a[1]), a[2:], sample, title, intro, mx, rc, risk, spot)
    elif a and a[0] == 'close':
        close(int(a[1]), a[2])
    else:
        print(__doc__)
