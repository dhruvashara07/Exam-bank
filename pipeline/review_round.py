"""Build a review round for Dhruv: flagged questions + a random sample, as files for the review page.

    python3 pipeline/review_round.py new <round no> <paper ids...> [--sample 3] [--title "..."] [--intro "..."]
    python3 pipeline/review_round.py close <round no> <answers.json>   # after reading the page's feedback

`new` writes
    out/review/round_<n>/round.json, items.json, <qid>/*.jpg     -> publish with the Artifact tool to the
                                                                  review page (review/portal.json review_url)
    review/rounds/<n>.json  {round, status: open, collection, items}   (the tracker's 'your review' stage)
Items: every question with a flag or an automatic-check problem in those papers, plus `--sample`
random questions per paper (seeded by the round number, so the choice is repeatable).
The page stores answers in its database, collection feedback_r<n>, doc id = question id:
    {verdict: ok|wrong, issues: [...], note, at}
`close` stores those answers in review/rounds/<n>.json (status closed) for the record.
"""
import datetime, json, os, random, sys

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
    figs = {}
    for i, f in enumerate(q.get('figures', [])):
        name = f'fig{i + 1}.jpg'
        im = ra.svg_img(f['svg']['file'])
        if im.width > 700:
            im = im.resize((700, round(im.height * 700 / im.width)), Image.LANCZOS)
        im.save(os.path.join(d, name), quality=75, optimize=True)
        figs[f['id']] = f'{qid}/{name}'
    out = []
    for n, depth in nodes(q):
        out.append({'label': n.get('label'), 'depth': depth, 'content': n.get('content', [])})
    return out, figs


def new(rnd, pids, sample=3, title=None, intro=None):
    byid = {os.path.basename(f)[:-5]: f for f in paths.question_files()}
    rng = random.Random(rnd)
    items, reasons = [], {}
    for pid in pids:
        qids = sorted(q for q in byid if q.startswith(pid + '_'))
        chk = json.load(open(os.path.join(paths.CHECKS, pid + '.json'))) if os.path.exists(os.path.join(paths.CHECKS, pid + '.json')) else {}
        for p in chk.get('problems', []) + chk.get('flags', []):
            qid = p['id'] if p['id'] in byid else None
            if qid:
                reasons.setdefault(qid, []).append(p['detail'] if p['kind'] == 'flag' else f"{p['kind']}: {p['detail']}")
        flagged = [q for q in qids if q in reasons]
        rest = [q for q in qids if q not in reasons]
        items += [(q, 'flagged') for q in flagged] + [(q, 'sample') for q in rng.sample(rest, min(sample, len(rest)))]
    out_dir = os.path.join(paths.ROOT, 'out', 'review', f'round_{rnd}')
    built = ra.render_items(out_dir, items, reasons, byid)
    for it in built:
        q = json.load(open(byid[it['id']]))
        it['editable'], it['figure_images'] = editable_payload(q, os.path.join(out_dir, it['id']), it['id'])
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
        new(int(a[1]), a[2:], sample, title, intro)
    elif a and a[0] == 'close':
        close(int(a[1]), a[2])
    else:
        print(__doc__)
