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

Cloudinary public id = the same path without '.svg', so the cloud folders mirror the repo.
"""
import glob, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BANK = os.path.join(ROOT, 'bank')
BOARD = {'CAIE': 'cambridge', 'IB': 'ib'}
KINDS = ('question', 'figures', 'markscheme')


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
    return os.path.relpath(path, ROOT).replace('\\', '/')[:-4]
