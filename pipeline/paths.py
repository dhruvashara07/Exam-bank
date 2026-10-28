"""Where everything lives. Every script finds files through here.

bank/
  index.json                                   one line per question (id, path, type, marks, topic...)
  cambridge-igcse/                             board-exam
    0625-physics/                              syllabus-subject
      2025-MJ/                                 year-session (FM = Feb/Mar, MJ = May/Jun, ON = Oct/Nov)
        p41/                                   paper + variant
          paper.json
          q01/
            0625_2025MJ_41_q01.json            the question: structure, text, marks, layout, links
            question/0625_2025MJ_41_q01_a-ii_s1.svg     exact printed pieces (with answer space)
            figures/0625_2025MJ_41_q01_fig1-1.svg       diagrams/tables on their own
            markscheme/0625_2025MJ_41_q01_a-ii_ms1.svg  mark-scheme rows
raw/<syllabus>/<year>-<session>/{qp,ms}_<pv>.pdf          the original PDFs

Cloudinary public id = question_bank/ + the path inside bank/ without '.svg', so the cloud folders
mirror the repo:  question_bank/cambridge-igcse/0625-physics/2025-MJ/p41/q01/question/0625_2025MJ_41_q01_a-ii_s1
review/approvals.json  papers Claude has checked; only these go to MongoDB (see docs/DAILY_CHECK.md)
"""
import glob, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BANK = os.path.join(ROOT, 'bank')
BOARD = {'CAIE': 'cambridge', 'IB': 'ib'}
KINDS = ('question', 'figures', 'markscheme')
CLOUD_ROOT = 'question_bank'                 # top Cloudinary folder
APPROVALS = os.path.join(ROOT, 'review', 'approvals.json')


def paper_dir(meta):
    group = f"{BOARD.get(meta['board'], meta['board'].lower())}-{meta['exam'].lower()}"
    subject = f"{meta['syllabus']}-{meta['subject'].lower().replace(' ', '-')}"
    return os.path.join(BANK, group, subject, f"{meta['year']}-{meta['session']}", f"p{meta['paper']}{meta['variant']}")


def split_id(qid):
    """'0625_2025MJ_41_q01' -> ('0625', '2025', 'MJ', '41', 'q01')"""
    syl, ses, pv, q = qid.split('_')[:4]
    return syl, ses[:4], ses[4:], pv, q


def question_dir(qid):
    syl, year, session, pv, q = split_id(qid)
    hits = glob.glob(os.path.join(BANK, '*', f'{syl}-*', f'{year}-{session}', f'p{pv}', q))
    if not hits:
        raise FileNotFoundError(qid)
    return hits[0]


def question_file(qid):
    qid = '_'.join(qid.split('_')[:4])
    return os.path.join(question_dir(qid), f'{qid}.json')


def question_files():
    return sorted(glob.glob(os.path.join(BANK, '*', '*', '*', 'p*', 'q*', '*.json')))


def paper_files():
    return sorted(glob.glob(os.path.join(BANK, '*', '*', '*', 'p*', 'paper.json')))


def svg_files():
    return sorted(glob.glob(os.path.join(BANK, '**', '*.svg'), recursive=True))


def raw_pdfs(qid):
    syl, year, session, pv, _ = split_id(qid)
    d = os.path.join(ROOT, 'raw', syl, f'{year}-{session}')
    return os.path.join(d, f'qp_{pv}.pdf'), os.path.join(d, f'ms_{pv}.pdf')


def public_id(path):
    return CLOUD_ROOT + '/' + os.path.relpath(path, BANK).replace('\\', '/')[:-4]


def paper_id(meta):
    return f"{meta['syllabus']}_{meta['year']}{meta['session']}_{meta['paper']}{meta['variant']}"


def approvals():
    import json
    return json.load(open(APPROVALS)) if os.path.exists(APPROVALS) else {}


def save_approvals(a):
    import json
    os.makedirs(os.path.dirname(APPROVALS), exist_ok=True)
    with open(APPROVALS, 'w') as f:
        json.dump(dict(sorted(a.items())), f, indent=1)
