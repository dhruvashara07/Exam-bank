"""Copy the bank into MongoDB, in our own format (not tied to any website model).

Needs secrets MONGODB_URI (or MONGO_URI) and CLOUDINARY_URL (only the cloud name is used, for image URLs).
Only papers approved in review/approvals.json are synced (Claude checks each paper first).

    python3 pipeline/sync_mongo.py            # everything (upsert: re-running updates, never duplicates)
    python3 pipeline/sync_mongo.py --dry-run  # print one document, write nothing

Database MONGO_DB (default 'question_bank'), collections:
  papers     _id '0625_2025MJ_41'      paper.json as is
  questions  _id '0625_2025MJ_41_q01'  the question JSON as is, with every svg.url filled in,
                                        plus 'paper_id', 'search' (plain text) and 'leaf_paths'
Every document carries origin='exam-bank'; clean-up only ever deletes documents with that mark.
The git repo stays the master copy; MongoDB is the fast copy the website reads.
"""
import json, os, sys
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(__file__))
import paths


def cloud_name():
    u = os.environ.get('CLOUDINARY_URL')
    return urlparse(u).hostname if u else 'CLOUD_NAME'


def fill_urls(node, cloud):
    if isinstance(node, dict):
        if 'public_id' in node and 'file' in node:
            node['url'] = f"https://res.cloudinary.com/{cloud}/image/upload/{node['public_id']}.svg"
        for v in node.values():
            fill_urls(v, cloud)
    elif isinstance(node, list):
        for v in node:
            fill_urls(v, cloud)


def leaf_paths(node):
    kids = node.get('parts', [])
    if not kids:
        return [node['path']] if 'path' in node else []
    return [p for k in kids for p in leaf_paths(k)]


def all_text(node):
    out = [node.get('text') or '']
    for k in node.get('parts', []):
        out.append(all_text(k))
    return '\n'.join(t for t in out if t)


def question_doc(q, cloud):
    d = json.loads(json.dumps(q))
    fill_urls(d, cloud)
    d['_id'] = q['id']
    d['paper_id'] = '_'.join(q['id'].split('_')[:3])
    d['leaf_paths'] = leaf_paths(q)
    d['search'] = all_text(q)
    return d


DB_NAME = os.environ.get('MONGO_DB', 'question_bank')
ORIGIN = 'exam-bank'


def approved_files():
    appr = paths.approvals()
    return [f for f in paths.question_files() if '_'.join(os.path.basename(f).split('_')[:3]) in appr], appr


if __name__ == '__main__':
    cloud = cloud_name()
    files, appr = approved_files()
    print(f'{len(appr)} approved papers, {len(files)} questions')
    if '--dry-run' in sys.argv:
        q = json.load(open(next(f for f in files if json.load(open(f))['type'] != 'mcq')))
        print(json.dumps(question_doc(q, cloud), ensure_ascii=False, indent=1)[:3000])
        sys.exit(0)
    from pymongo import MongoClient, ReplaceOne, ASCENDING, TEXT
    from datetime import datetime, timezone
    uri = (os.environ.get('MONGODB_URI') or os.environ.get('MONGO_URI') or '').strip()
    if not uri.startswith('mongodb'):
        sys.exit('MONGODB_URI secret is missing or not a mongodb:// / mongodb+srv:// address (see docs/SETUP.md)')
    db = MongoClient(uri)[DB_NAME]
    now = datetime.now(timezone.utc)

    papers = []
    for f in paths.paper_files():
        p = json.load(open(f))
        p['_id'] = paths.paper_id(p)
        if p['_id'] not in appr:
            continue
        p.update({'origin': ORIGIN, 'approval': appr[p['_id']], 'synced_at': now})
        papers.append(ReplaceOne({'_id': p['_id']}, p, upsert=True))
    if papers:
        db.papers.bulk_write(papers, ordered=False)

    ops, n = [], 0
    for f in files:
        d = question_doc(json.load(open(f)), cloud)
        d.update({'origin': ORIGIN, 'synced_at': now})
        ops.append(ReplaceOne({'_id': d['_id']}, d, upsert=True))
        if len(ops) == 200:
            db.questions.bulk_write(ops, ordered=False); n += len(ops); ops = []
    if ops:
        db.questions.bulk_write(ops, ordered=False); n += len(ops)
    # ours but no longer in the repo / no longer approved (e.g. re-cut, waiting for a new check)
    gone = db.questions.delete_many({'origin': ORIGIN, 'synced_at': {'$lt': now}}).deleted_count
    db.papers.delete_many({'origin': ORIGIN, 'synced_at': {'$lt': now}})

    qc = db.questions
    qc.create_index([('syllabus', ASCENDING), ('year', ASCENDING), ('session', ASCENDING),
                     ('paper', ASCENDING), ('variant', ASCENDING), ('number', ASCENDING)])
    qc.create_index('paper_id'); qc.create_index('type'); qc.create_index('topic'); qc.create_index('keywords')
    qc.create_index([('search', TEXT)])
    print(f'{len(papers)} papers, {n} questions synced, {gone} removed (database {db.name})')
