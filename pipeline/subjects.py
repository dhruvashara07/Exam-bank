"""One entry per syllabus. Everything that differs between subjects lives here, so the rest of the
pipeline never hard-codes a syllabus number.

    0625  Physics                         papers 1/2 multiple choice, 3/4 theory, 5 practical, 6 ATP
    0607  Cambridge International Maths   no multiple choice: 1/2 short answer or non-calculator,
                                          3/4 long answer or calculator, 5/6 investigation (and modelling)
    0620  Chemistry                       same paper numbering as physics; takes the PHYSICS path everywhere
                                          except code gated with is_chem (docs/CHEM_PLAN.md)

Maths-only code asks is_maths() / maths_path(), never 'not physics' (a third subject must not fall into it).

Physics is frozen (all years approved): never change a physics value here; golden.py guards it.
"""
import re

SUBJECTS = {
    '0625': {'subject': 'Physics', 'slug': '0625-physics', 'mcq_papers': (1, 2), 'maths_text': False},
    '0607': {'subject': 'International Mathematics', 'slug': '0607-international-mathematics',
             'mcq_papers': (), 'maths_text': True},
    '0620': {'subject': 'Chemistry', 'slug': '0620-chemistry', 'mcq_papers': (1, 2), 'maths_text': False, 'chem': True},
}

# 0607 paper kinds by paper number when the cover title does not say (tier comes from '(Core)'/'(Extended)').
MATHS_KIND = {1: 'short_answer', 2: 'short_answer', 3: 'long_answer', 4: 'long_answer',
              5: 'investigation', 6: 'investigation_modelling'}


def subject(syl):
    return SUBJECTS[syl]


def is_physics(syl_or_id):
    return str(syl_or_id)[:4] == '0625'


def is_maths(syl_or_id):
    """Maths text subject (0607): '0607', '0607_2021MJ_41', '0607/2021-MJ/41'."""
    return SUBJECTS.get(str(syl_or_id)[:4], {}).get('maths_text', False)


def is_chem(syl_or_id):
    return SUBJECTS.get(str(syl_or_id)[:4], {}).get('chem', False)


def path_syl(name):
    """Syllabus of a (cleaned / raw) PDF path holding /<syllabus>/<year>-<session>/, else None."""
    m = re.search(r'/(\d{4})/\d{4}-[A-Z]{2}/', (name or '').replace('\\', '/'))
    return m.group(1) if m else None


def maths_path(name):
    """A maths paper's path: /<maths syllabus>/ anywhere in it (was '/0607/' in name)."""
    n = (name or '').replace('\\', '/')
    return any(f'/{k}/' in n for k, v in SUBJECTS.items() if v['maths_text'])


def maths_paper_type(cover, paper):
    """'Paper 4 (Extended)' -> extended_long_answer;  'Paper 2 Non-calculator (Extended)' (2025 syllabus)
    -> extended_non_calculator;  'Paper 6 Investigation and Modelling (Extended)' -> extended_investigation_modelling."""
    m = re.search(r'Paper\s+\d\s+([^\n]+)', cover)
    title = (m.group(1) if m else '').lower()
    tier = 'extended' if 'extended' in title else ('core' if 'core' in title else
                                                      ('extended' if paper % 2 == 0 else 'core'))
    if 'non-calculator' in title or 'non calculator' in title:
        kind = 'non_calculator'
    elif 'calculator' in title:
        kind = 'calculator'
    elif 'modelling' in title:
        kind = 'investigation_modelling'
    elif 'investigation' in title:
        kind = 'investigation'
    else:
        kind = MATHS_KIND.get(paper, 'paper')
    return f'{tier}_{kind}'


def total_from_cover(cover, syl):
    """Total marks printed on the cover. Physics keeps its original (narrow) pattern."""
    if is_physics(syl):
        m = re.search(r'total mark for this paper is (\d+)', cover)
    else:
        m = re.search(r'total (?:number )?(?:of (?:the )?)?marks? for this paper is (\d+)', cover, re.I)
    return int(m.group(1)) if m else None


def current():
    """Syllabus for session-based tools (ms_align, ms_sweep, year_audit, audit): SYL=0607 env, default physics."""
    import os
    return os.environ.get('SYL', '0625')


def mcq_dir(path_or_syl, pv):
    """True when paper <pv> of this syllabus is multiple choice (no mark-scheme table)."""
    syl = str(path_or_syl)[:4]
    pv = str(pv)
    paper = int(pv[1]) if pv[0] == '0' else int(pv[0])
    return paper in SUBJECTS[syl]['mcq_papers']
