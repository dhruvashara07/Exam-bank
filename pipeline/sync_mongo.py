"""Upsert question JSON into the learnerspoint MongoDB as QuestionV2 documents.

Needs secrets MONGODB_URI (same as learnerspoint's .env) and CLOUDINARY_URL (for image URLs).
Matching key: `source` = question id, so re-running updates instead of duplicating.

    python3 pipeline/sync_mongo.py            # all questions
    python3 pipeline/sync_mongo.py --dry-run  # print one mapped document, write nothing

Mapping (QuestionV2 fields used by the website):
  mcqContent / structuredContent  image blocks of the exact question pieces (SVG on Cloudinary)
  solutionData                    image blocks of the mark-scheme rows
  pastPaper                       the full pipeline JSON (layout, answer space, text) for the
                                  exact test-paper builder and search
"""
import glob, json, os, sys
from urllib.parse import urlparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
COLLECTION = 'questionv2s'          # mongoose model 'QuestionV2'


def cloud_name():
    u = os.environ.get('CLOUDINARY_URL')
    return urlparse(u).hostname if u else 'CLOUD_NAME'


def url(svg, cloud):
    return f"https://res.cloudinary.com/{cloud}/image/upload/{svg['public_id']}.svg"


def img_blocks(segments, cloud, alt, prefix):
    return [{'id': f'{prefix}-s{i}', 'type': 'image', 'imageUrl': url(s['svg'], cloud), 'altText': alt}
            for i, s in enumerate(segments, 1)]


def ms_blocks(node, cloud, prefix):
    out = []
    for m in node.get('mark_scheme', []):
        out += [{'id': f'{prefix}-ms{i}', 'type': 'image', 'imageUrl': url(s['svg'], cloud),
                 'altText': f"Mark scheme {m['label']}"} for i, s in enumerate(m['segments'], 1)]
    return out


def to_doc(q, cloud):
    qid = q['id']
    doc = {
        'source': qid, 'board': 'CAIE', 'exam': 'IGCSE', 'paper_code': q['paper_code'], 'subject': q['subject'],
        'paper': str(q['paper']), 'chapter': q.get('topic') or '', 'topic': q.get('topic') or '',
        'subtopic': q.get('subtopic') or '', 'is_calc_allowed': True, 'total_marks': q['total_marks'],
        'question_type': 'mcq' if q['type'] == 'mcq' else 'structured',
        'isPastPaperQuestion': True, 'season': q['season'], 'year': q['year'], 'variant': q['variant'],
        'keywords': q.get('keywords', []),
        'images': [url(f['svg'], cloud) for f in q['figures']],
        'diagrams': [], 'requiresLatex': False,
        'pastPaper': {**q, 'cloudinary_cloud': cloud},
    }
    if q.get('difficulty'):
        doc['level_of_difficulty'] = q['difficulty']
    alt = f"{q['paper_code']} {q['season']} {q['year']} question {q['number']}"
    if q['type'] == 'mcq':
        doc['mcqContent'] = {
            'question': img_blocks(q['segments'], cloud, alt, qid),
            'options': [{'id': f"{qid}-{o['label']}", 'label': o['label'],
                         'blocks': [{'id': f"{qid}-{o['label']}-t", 'type': 'text', 'content': o['text']}]} for o in q['options']],
            'correctOption': (q.get('answer') or '').lower() or None,
        }
    else:
        subparts, sol = [], []
        for i, p in enumerate(q.get('parts', []), 1):
            sp = {'id': f"{qid}-{p['label']}", 'number': i, 'title': f"({p['label']})", 'marks': p.get('marks', 0),
                  'blocks': img_blocks(p['segments'], cloud, f"{alt} part ({p['label']})", f"{qid}-{p['label']}"), 'subsubparts': []}
            sol.append({'id': sp['id'], 'blocks': ms_blocks(p, cloud, sp['id'])})
            for j, k in enumerate(p.get('parts', []), 1):
                ssp_id = f"{qid}-{p['label']}-{k['label']}"
                sp['subsubparts'].append({'id': ssp_id, 'number': j, 'title': f"({k['label']})", 'marks': k.get('marks', 0),
                                          'blocks': img_blocks(k['segments'], cloud, f"{alt} part {k.get('path', '')}", ssp_id)})
                sol.append({'id': ssp_id, 'blocks': ms_blocks(k, cloud, ssp_id)})
            subparts.append(sp)
        doc['structuredContent'] = {'questionIntro': img_blocks(q['segments'], cloud, alt, qid), 'questionSubparts': subparts}
        doc['solutionData'] = {'subparts': [s for s in sol if s['blocks']]}
    return doc


def all_questions():
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', '*', '*', '*', 'q*.json'))):
        yield json.load(open(f))


if __name__ == '__main__':
    cloud = cloud_name()
    if '--dry-run' in sys.argv:
        q = next(q for q in all_questions() if q['type'] != 'mcq')
        print(json.dumps({k: v for k, v in to_doc(q, cloud).items() if k != 'pastPaper'}, indent=1)[:4000])
        sys.exit(0)
    from pymongo import MongoClient, UpdateOne
    from datetime import datetime, timezone
    client = MongoClient(os.environ['MONGODB_URI'])
    db = client.get_default_database()
    col = db[COLLECTION]
    now = datetime.now(timezone.utc)
    ops = []
    for q in all_questions():
        d = to_doc(q, cloud)
        d['updatedAt'] = now
        ops.append(UpdateOne({'source': d['source']}, {'$set': d, '$setOnInsert': {'createdAt': now}}, upsert=True))
    res = col.bulk_write(ops, ordered=False)
    col.create_index('source')
    print(f'{len(ops)} questions: {res.upserted_count} new, {res.modified_count} updated (database {db.name}, collection {COLLECTION})')
