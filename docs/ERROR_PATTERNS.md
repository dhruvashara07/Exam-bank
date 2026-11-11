# Error patterns (do not repeat these)
Every mistake Dhruv found, or Claude found itself, as a pattern + the check that now catches it. Read before every batch.
Add a line whenever a review round or a check finds something new. Format: what went wrong -> fix -> how it is checked now.

## Build / GitHub
1. GitHub `bank.yml` checks step passed ids without `0625/` -> checked nothing. -> Always run `checks.py 0625/<ses>/<p>`
   locally after a GitHub build.
2. Old PDFs exist under two names (qp_3 and qp_03) -> every paper built twice. -> `session_papers.py` keeps the 2-digit one.
3. The golden check compares what is on disk: without the golden PDFs fetched, `run.py` silently does nothing.
   -> `raw_store.py fetch <golden ids>` first, then rebuild them, then `golden.py check` (0 changed cuts).

## Question papers (pre-2009)
4. Paper numbers mean other things before 2009 (1 MCQ, 2 core, 3 extended, 5 practical, 6 ATP): read as MCQ.
   -> `extract.OLD_PAPER_TYPES`. Check: every paper's marks = its total.
5. No total printed on old covers -> take 'MAXIMUM MARK' from the mark scheme (pre-2009 only, to leave approved years alone).
6. 2002 ON practical: answer booklet pages inside the PDF; 'Question 1' headings. -> dropped / read.
7. 'For Examiner's Use' column drawn as a thin line in the page picture (no vector) -> slivers in every piece.
   -> `clean.strip_examiner_rule_drawn`.
8. Invisible text (OCR layer) read as a figure caption -> bogus figure. -> captions need ink under them.
9. CMYK pictures show black in browsers -> `render.fix_cmyk_images`.
10. Figure crop stopped at a text line printed BESIDE the figure -> cut-off figure. -> band top ignores beside-text.

## Mark schemes (round 22: 20 of 33 items wrong, all mark-scheme layout)
11. Part totals shown twice (sub-totals + our Total row). -> rule 16; sweep: no bare number / [n] / M2 in Marks of a
    question with codes.
12. Mark codes left in the Answer column (fixed 0.82 threshold). -> codes column found per question. Sweep: no code
    token left of the Marks column.
13. 'TOTAL n' / '1.' left in practical answers. -> dropped.
14. F/C removal by redaction moved the next word ('8 F B1' -> 'B1' beside 8). -> never use apply_redactions on text;
    paint + hide list. Check: after any cleaning of text, compare word positions before/after.
15. My contact sheets drew the raw pieces, not our table (`ms_p`) -> I checked the wrong picture. -> check mark
    schemes with `store.review_svgs` (what the review page and students get), e.g. pipeline/ms_grid.py.
16. A new layout era (old MS) went to review before being put in our table -> Dhruv reviewed known problems.
    -> before a round: the MS sweep (PLAYBOOK step 5) must be clean, and look at one MS of each paper type.

## Batch 2 (2005-2007), found by Claude before the round
17. Practical marks only in the mark scheme as '[1]' per point + '[Total: 10]' -> marks 0. -> per-question
    '[Total: n]' (run.py ms_qtotals), else the summed '[1]'s.
18. A scale line ('-10 0 10 ... 110 C') or padded labels ('C       D') counted as the sentence above a figure ->
    crop cut at the top. -> not prose (extract.find_figures); pre-2009 figures may reach into the prose line's descent.
19. F/C column at x 482 (2006) outside the 380-480 window -> F/C shown. -> window 380-500; sweep shows no lone F/C.
20. Repeated column heads at a page top ('QU. SCHEME MARK') inside a row; '[TOTAL: 10]' in caps -> dropped (pre09).
21. Letters printed in the roman column (2005 ON 03 q11 at x 133) -> the question had no mark-scheme rows.
    -> pre-2009 letters a-h accepted up to the roman column. Sweep: 'no table' hit = look.
22. Run labels '(a)–(e)' (practical) -> one row labelled 1(a)–(e).
Known small leftover: in-text codes at the far right of an answer line ('120 gets C1 C1 A0') can land in Marks.

