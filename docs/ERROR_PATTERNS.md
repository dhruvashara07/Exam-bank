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

## Round 23 (2005-2007): 11 of 36 wrong
23. Old column rules (straight thin vertical lines) taken as braces -> '{' at the start of answers. -> pre-2009 braces
    must be curves; straight vertical rules dropped.
24. '[total: 9]' in lower case left in the answer. -> any case.
25. 'B1 x 4' printed as three words -> '4' dropped as a part total, 'x' left in the answer. -> merged to 'B1×4' first.
26. '(ii)' printed twice in the MS -> second became (b)(ii). -> pre-2009: the next roman of the same letter.
27. Parts Cambridge did not label ('sound ticked' = 7(b)) or printed together ('(b) & (c)'): by eye -> ms.MS_SPLIT.
    MS letters for paper romans (2006 ON 06 q4 (b)(c)(d) = (b)(i)(ii)(iii)) -> ms.MS_RELABEL.
28. A label alone on its line ('(a)–(g)') left an empty band at the top of the row. -> answer starts at the top.
29. Captions 'Fig. 2.1a' / 'Fig. 2.1b' not read as captions -> figure missing. Ids now fig2-1a / fig2-1b.
30. Paper prints one [Total] for two questions (2007 MJ 03 q10+q11) -> extract.TOTAL_SLIPS (no flag).

## Batch 3 (2008-2010), found by Claude before the round
31. 2008-2009 downloads hold 0625/31 + /32 in one qp_3.pdf (also split into qp_31, qp_32) -> built 3 times.
    -> session_papers skips the combined original.
32. 2008 notes page names 'Question/Answer/Mark' -> the table parser was chosen and found nothing (no MS for paper 2).
    -> fall back to the column parser when the table parser finds no rows.
33. A tall figure beside a column of text (2008 MJ 02 Fig 4.1) was cut: crops may grow only 80 pt. -> pre-2009, all
    prose beside the figure: grow up to 400 pt.
34. Table 15 pt below its caption (2010 MJ 52) was not seen as a table -> tiny crop. -> window 18 pt.
35. A sentence ending with its mark '[2]' inside a graph's band was cut into the figure (2010 ON 32). -> prose.
36. Old printed MS layouts run to 2012, not 2008: rule 16 now for all years < 2013; codes printed '[B1]' (2008).
37. Stub questions (same as another variant) have no own table: the sweep skips them.
Known: 2010 MJ 13, 23, 53 have no mark scheme file at all. MCQ labels cut at the right in 2010 ON 11 q34 /
12 q31 / 13 q35 (same figure) and 2008 MJ 02 Fig 4.1 spotlight: in round 24.

## Round 24 (2008-2010): 25 of 50 wrong - most: MS rows not matching the paper's parts
38. Old mark schemes label rows their own way (whole question '1', '(a)–(e)', '1(b)' for (b)(i)-(iv), slips like
    5(c) for 5(b)(ii)) or put several parts in one row. -> rows assigned BY MEANING: read each paper part and each
    MS line and map them in pipeline/ms_map.json ([MS line start, label], optional split inside a line).
    Check before every round: `python3 pipeline/ms_align.py list <sessions>` must print nothing
    (it flags labels not in the paper, marked parts without a row, and rows on a parent part).
    A row labelled with the bare question number is a note for all parts (kept).
39. Codes and labels drawn stretched (a width stored for '[B1]', or a guessed width for 'f', 't', 'r'): the SVG
    draws text at its stored width -> 'different font'. -> real widths (codes 6.73/char, Arial widths for labels,
    pre-2013 only; 2013-2016 labels still use the old guess until their layout is rebuilt).
40. 'B1 + B1' on one line widened the Marks column -> codes stacked one under the other.
41. A question number in the corner of a tall figure crop -> crop starts below it.

