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

42. Old practical schemes print parts out of order ('(c) units' or 'Table' first, '(e)' before '(b)–(d)') and we kept
    the printed order. -> rows sorted into the question paper's part order (pre-2013; a note row keeps its place).
43. A map that gives the same label to rows that are not next to each other ('evidence' after (d)) or labels like
    '4(c)(d)' / '4(c)–(e)' for a step with no marks -> label each line with the part where its marks are earned
    (the table/answer part, not the instruction step); general table lines go with the last part they cover.
44. Short bars ('±' printed as '+' over a bar, underlines) went into the row below (y split 12 pt above the next
    line) -> a short bar goes with the line it sits under.
45. Old schemes double-space some lines: a gap inside a row -> gaps over 15.5 pt closed when nothing is drawn there.
46. Notes printed far right ('(ecf NO)', '(too different, wtte)') wrapped onto their own line -> moved beside the
    line (gap 8 pt), with their underline. '[M2]' beside a brace -> '(max 2)' at the end of its line.
47. Stacked codes ('B1, B1') pushed the next line down -> they hang into the lines below when those have no marks.
48. 2008 '[1]' marks in the same column as '[M1]' codes were dropped as part totals -> kept (right edge = codes').
49. One line with one mark for two parts, split ('e1 ... and e2 ...'): the mark goes where Dhruv expects it
    (map option 'marks_first'); a mark that covers two parts and cannot be split keeps the combined label.

## Batch 4 (2011-2012), found by Claude before round 26
50. A fraction printed inside a line ('R = V/I', '1/u') draws its numerator and bar ABOVE the line's text
    top. The cut between two parts ran under them, so that ink was in no piece at all (coverage, blocking:
    2011 MJ 51 p8, 2012 ON 63 p13). -> `extract.lift_over_thin_ink`: the cut moves up to the first white
    row, so a line keeps the ink hanging over it (pre-2013). Also '(d) (i)' on one line: the two cuts are
    now always merged to the higher one, instead of leaving a 3 pt sliver that is dropped with its ink.
51. 2011 MJ 52 and 61 print the question number as '1.' (with a dot). The old-layout parser only accepted
    a bare number, so it found no rows and those two papers had NO mark scheme at all - and nothing failed,
    because marks come from the question paper. -> `ms.py` accepts '1.'. Check: a paper with no `ms_p` in
    any question is a bug, not a scan (`ms_sweep` 'no table').
52. ms_map prefixes are matched against the text OUR table shows, not against the printed line: marks read
    '[1]' not '1', mark codes (B1, M1) have moved to the Marks column, the rest of a printed label
    ('& (ii)', ', (b)') is stripped, and a line of only sub/superscripts ('3', '240 240') is dropped.
    -> `ms_layout._mnorm` ignores those differences; never take a prefix from a sub/superscript-only line,
    and never cut a prefix in the middle of a word or code. Check: `ms_align.py verify` - every mapped
    question's row labels must equal the labels in its map entry (ms_align list alone does not catch a
    prefix that matched the wrong line).
53. Mapped rows were sorted by the letter only, so a mark scheme printing '(ii)' before '(i)' kept the wrong
    order inside a part. -> `ms_layout` sorts by every part of the paper, sub-parts included (round 26).
    This also corrected two approved papers (2005 MJ 05 q4, 2005 ON 05 q3).
54. Rebuilding single papers with `store.build` and no `store.py dupes <session>` afterwards empties every
    `same_as` list (614 files changed in approved years). -> always run `dupes` for each session touched.

## Round 26 (2011-2012 + round-25 re-checks), Dhruv 2026-11-12: 37 ok, 13 wrong
55. Splitting a printed group by meaning when the lines do not each mark one part (trace marks, table marks over
    readings and repeats, 'Both sets of temperatures') = guessing; Dhruv: keep Cambridge's grouping, our layout
    (MS_TABLE_RULES 20). Sign: you need a label across letters ('2(b)(c)', '4(e)(h)') -> keep the group.
    (2011 ON 51 q4, 2012 ON 51 q2, 2011 MJ 52 q1, 2009 ON 05 q2, 2011 ON 52 q4, 2005 MJ 05 q4)
56. A figure crop warning was dismissed after looking at the stored figure alone: it showed a whole-looking
    picture (a woman, a basket, a cliff) but the man at the top of the cliff was gone (2012 MJ 22/23 q4). Cause:
    the questions printed BESIDE the figure counted as prose above it, so the crop started under them. The
    pre-2009 rule for text beside a figure now holds to 2012; a label whose line was read together with that text
    ('basket of') is taken whole. ALWAYS compare a flagged crop with the page.
57. An underline under several words ('neatly and correctly') went to the next row when a row started on the
    line below: it is now owned by the words it is under (2011 MJ 62 q4(b)(v) 'line').
58. A fraction's numerators ('1  1' of 1/u, 1/v) and a superscript ('3' of cm3) are a text line of their own just
    above their line; when a mapped row started at that line they stayed in the row above (2012 ON 63 q4: '1 1'
    left in (a)(iii), the fractions in (b) without numerators). They now join the line below them (pre-2013).
59. A stray '_' printed at the end of a mark scheme became a row line (2012 ON 21 q12(c)(ii)) -> dropped.
60. '≥' printed with a re-encoded '[' in a symbol subset (2011 ON 51 'distance [ 5.0cm'): the glyph check now
    covers brackets too (pre-2013).
61. 'all 3  B1' + brace: one mark for three parts - shown as one merged Marks cell (MS_TABLE_RULES 21).
62. The paper's '[3]' after (a)(iv) is the block total of (a): stored on (a) now (MS_TABLE_RULES 23).
63. Map prefixes and printed order: entries of an '@original' map are still matched in printed order; a heading
    line ('trace:', 'Table:') starts the row of the first marked line under it, so its entry is the heading.

## Maths 0607 pilot M0 (2014 MJ, 2019 ON, 2021 FM, 2025 MJ), found by Claude in pass 1
64. Equation-editor fonts re-encode symbols: MathType 'MM*' fonts (2014-2024) and 2025 'AllAndNone' print × as '#',
    ÷ as "'", ≠ as '!', ≤/≥ as 'G'/'H', π as 'r', ∪/∩ as ','/'+'. The store drew '#' in the PRINT layout too (2025 MJ 21 q5).
    -> `store_text.MATHS_GLYPHS` (read by eye from a glyph sheet of every code) and `MATHS_WIDE` (2025: the same code is a
    digit or a symbol, told apart by its width: '2' 0.83 em = '>'), maths only. Shape matching (glyph_remap) was tried and
    is NOT reliable for these (≠ read as √). Check: maths_tex character check + store verify. New font in a later batch:
    make the glyph sheet again (/tmp script in CONVERSATION_LOG M0 entry) and add the codes.
65. Page 2 'Formula List' / 'List of formulas' is no question (coverage error on every paper); 'Answer all the questions.'
    / 'Calculators must not be used in this paper.' on the first question page was ink outside every piece.
    -> `extract.is_formula_page` (skipped like a blank page, kept as paper.formula_list), `layout.page_bounds` (maths only).
66. Investigation / modelling papers (5, 6): the introduction before Q1 and the 'B MODELLING' / 'Section B' text before the
    first question of part B belong to no question (it was lost, or glued to the last part of part A).
    -> `extract.maths_paper_parts`: paper.json `intros` (section, before, segments); store paper.json has their layout +
    LaTeX; every question of a section has `intro` = its index. Coverage counts them.
67. 2014-2024 investigation papers print no [n] per part: marks found 0. -> marks from the mark scheme (`run.py`, maths
    investigation only). Their 'Communication: seen in ...' rows are paper marks: the rows printed under them name earlier
    parts (criteria) and were taken as extra rows of those parts (2019 ON 51: 3(c) got 2+1). -> `ms.fold_communication`
    (paper.json `communication`); numbers in the 'Partial Marks' column (fractions, tables) are not marks
    (`structured_rows_table` PX). Checks: marks + communication = cover total.
68. Maths diagrams have no 'Fig.' caption (a triangle 'NOT TO SCALE', axes, grids), so no figure was cut and the
    website text would read the diagram's labels as text. -> `extract.diagrams` (maths only): clusters of drawings/images
    with their short labels, ruled tables of text excluded (they stay text + rules), grown to all ink (light grey grids
    too: `_grow_light`). Ids `..._diagram<n>`. Check: checks.py crop warnings - compare each with the page (pattern 56).
69. Mark schemes 2018+ have a 4th column 'Partial Marks' (M1 for ..., B1 for ...): the header was not recognised and rows
    with a drawn symbol had no 4-column frame to fall back to (2025 MJ 21 q3: partial marks inside the Answer cell).
    -> header name 'Partial Marks', Answer and Partial Marks the same width (Dhruv, MS_TABLE_RULES 24), 4-column default
    from the printed rules when no row can be re-wrapped.
70. 2014 maths mark schemes are portrait tables ruled into 4 columns with no header row; labels '2', '(a)', '(i)' sit
    apart and only on a question's first row. -> `ms_layout._maths_ruled`: our full label per row, our header, re-laid out
    like the landscape era (FORCE_WRAP). NOT finished in M0: rows with fractions / column vectors / long notes (2014 MJ 41
    q10, 21 q2) still break; see PROGRESS.
71. Maths mark-scheme rows full of fractions / brackets / graphs broke in the physics re-wrap (fallbacks, old paths).
    -> `pipeline/ms_maths.py`: per printed cell, lines by vertical overlap, unbreakable chunks, rows grow (Dhruv).
72. 2019 ON 11-13 schemes: header words not found -> default column limits read answers as labels; numbers of answer
    tables counted as marks. -> maths: the table's own column rules decide Q / Marks / Partial Marks columns (ms.py).
73. 2014 paper 6: part B numbers its questions from 1 again (paper and mark scheme) -> part B was glued to the last
    question of part A. -> they continue our numbering (extract.boundaries, ms 'B' token).
74. Diagram crops: tick labels beside an axis, sideways axis titles and long labels of tree diagrams were cut off; bar
    charts were taken for tables of text. -> labels taken again after growing; tables need column rules top to bottom.

## Round 27 (maths M0), Dhruv 2026-11-13: 17 ok, 23 wrong - most were simple and should have been caught by Claude
75. Process: pass 2 looked at a sample of mark-scheme tables and never ran `store.py verify` or a MS content check.
    -> PLAYBOOK 2a-2f / 3a: automatic checks against the PDF on every paper + full contact sheets before any round.
76. Dot answer lines ('.......') missing in the rebuilt question (2014 MJ 11 q11, 21 q5, 33 q3, 42 q6): 2014 dots
    are hidden ('hide') like physics working space -> the print view must keep answer lines. Check 2a.
77. Mark-scheme fractions / vectors broken in ms_maths rows: stacked pieces split into different lines or chunks
    (2014 MJ 21 q5, 22 q4, 31 q3 '1/8' '7/25', 33 q3, 62 q2; 2019 ON 43 q6 vector arrows over OA/AB). Small (raised)
    pieces must join the chunk under/over them; drawn arrows join the letters under them.
78. Mark-scheme pictures (Venn diagrams, sketches) broken in ms_maths: a shaded region drawn as a black triangle,
    a picture scaled into a strip (2019 ON 42 q8, 2021 FM 32 q9, 2019 ON 52 q3). Pictures/drawings of a cell move as ONE
    block with their clip; never split by line bands.
79. Stray short lines in Marks / Partial Marks cells (2014 MJ 11 q11(b)(ii), q12(c)): pieces of printed row rules.
80. Fonts not consistent in our MS (serif answers, sans header and bold sans marks, small 2014 text). Dhruv: ONE font
    for question and mark scheme, same size, bold/italic only where printed (MS_TABLE_RULES 25).
81. Diagram labels left outside the picture (2014 MJ 11/13 q12) and two overlapping crops of one diagram (2021 FM 62 q9,
    2025 MJ 43 q16, 53 q3, 62 q6 '2 images', 'image 2 has a line'): crops must be merged / not cut through text.
82. 'NOT TO SCALE' (2025 MJ 23 q17, 43 q6): Dhruv's rule: it is part of the diagram -> always inside the picture.
83. A MS row missing: 2021 FM 42 q4(b)(iii) has a row in the printed scheme -> parse check per part (2b).
84. Digits of a number printed with thin spaces ('0.003 094 8') drawn with a gap too wide (2025 MJ 21 q2, q3).
85. Question tables (2019 ON 61 q3(b)) and 2019 ON 52 q3 render problems in the rebuilt question -> 2a.
Fixes made in the same chat (2026-11-13, before the re-check round):
- 76: 2014 dotted answer lines are rows of tiny pictures -> drawn as dots (store, maths); 2014 nameless 'TT..o00' fonts
  are Times -> serif by the font's serif flag (the rebuilt 2014 questions were in a sans font).
- 77: ms_maths bands: a drawing-only band (fraction bar, vector arrow) and a band of small raised text join their
  neighbours; MT Extra arrows ('JJG') are drawn glyphs; mark scheme scaled so its normal text is 11 pt.
- 78: ms_maths picture cells: curves/sketches/shaded areas (> 30 pt) and pages with a broken text layer are kept as the
  printed picture of the cell (axis labels with it); ruled inner tables stay text.
- 79: row-edge rule pieces and long lines in Marks / Partial Marks with nothing written over them dropped.
- 80: one font: the question paper's family for the whole table (header, labels, marks, Total), 11 pt.
- 81/82: diagram crops: 'NOT TO SCALE' always taken (up to 200 pt away), sentences on a crop's edge cut off, a line of a
  part label is question text, crops touching across a part boundary merged, light grids (< 253) grown.
- 83: '4(b)(iii)(a)' (a 4th level) read as a row of 4(b)(iii) with its full label (ms.SUB4, maths).
- 84: digits grouped by thin spaces -> '\,' in LaTeX.
- New tool `pipeline/maths_check.py` (ms_words, ms_overflow, ms_overlap, ms_font, fig_overlap, not_to_scale) - PLAYBOOK 2b-2d.
Known open: 2025 MJ 53 q3 (the part boundary cuts through the pyramid diagram); 2014 MJ 43 q3(b) inequality signs of
the 2014 symbol font not read in the mark scheme; 2014 MJ 62 p4 kept as pictures (broken text layer); 6 questions still on
the old MS paths (2014 MJ 22 q2, 43 q9, 2019 ON 11/12 q8, 23 q3, 62 q5).
86. 2014 maths fonts are nameless subsets ('TT1F0CAo00'): bold labels, marks and codes (M1, B1, FT) were drawn regular
    (store verify: 2-8 % ink missing in 2014 MS rows). -> `store_text.nameless_bold`: a font is bold when its printed
    letter widths match Times Bold better than Times Roman (cached per document). Found by PLAYBOOK 2a (store verify),
    not by Dhruv: the strict checks work.
87. Equation editors put the operators of one formula ('−', '×') in ONE text run, far apart: the run was drawn as a
    stretched word over the digits (maths_check ms_overlap '−×' / '2'). -> maths: a run is split at a gap > 1.5 pt.
88. A long mark-scheme answer printed over several lines (the printed Answer column is wider than ours) was wrapped
    line by line: ragged lines ('previous / numerator.'). -> `ms_maths._cell` joins text-only lines with the same indent,
    a normal gap and a full previous line into one paragraph and re-flows it in our column (MS_TABLE_RULES 26).
89. Nested / continued fractions (n/(1 + n/(1 + n))) were turned into flat LaTeX that passed KaTeX AND the character
    check: both checks test form, not meaning. -> `maths_tex`: a shorter fraction bar inside an outer one with text over
    both = 'nested fraction' -> the part is shown as the printed picture. Found only because Dhruv asked how the sequence
    was treated: PLAYBOOK 2c now asks to compare the LaTeX of every part with a stacked layout against the page.
90. Ruled tables inside question text were read as one jumbled LaTeX line. -> `maths_tex`: >= 3 column rules and >= 3 row
    rules in a unit = 'table' -> printed picture (105 parts in M0). Printed layout (store units) was never affected.

### Round 28 (25 of 34 wrong) - why the strict checks missed them: they tested CONTENT (every word present, nothing
### overlapping), never APPEARANCE (font, width, spacing, cut pictures). maths_check.py now has appearance checks.
91. Q labels, header and Total of the maths MS were given GUESSED widths (0.5-0.55 x size x letters) and the renderer
    stretches text to its width: '5(a)' 22.6 pt for 17.7 pt -> a 'wider font'. -> `ms_maths.text_width` (real Times /
    Helvetica metrics) for every word we make; labels normal weight, header and Total bold (Dhruv). Check: ms_stretch.
92. Rows were cut at the top of their first text line and no space was added above tall maths: fractions touched the
    row's top rule or the line above. -> `ms_maths._pushes`: 4 pt above a row's highest ink, 3 pt above and below a line
    with stacked maths, applied across all columns at that height (labels and marks stay level with the fraction's
    middle, as printed). Check: ms_edge (ink closer than 2 pt to a row rule).
93. A MS row ended 6 pt under its last text line or image: vector drawings (Venn diagram, sketch) were not counted, the
    bottom of the drawing was cut (2019 ON 42 q8). -> ms.py (maths): drawings in the row (not table rules / shading) count.
94. 'Graph = 15 straight lines' (round 27) also counted root signs and brackets: a long answer full of square roots
    became a half picture with loose words in the Marks column (2025 MJ 61 q4). -> a grid needs >= 3 long vertical and
    >= 3 long horizontal rules; text on the same line as a drawing goes into the picture with it.
95. A printed picture lying over its own heading ('Correct diagram', 2021 FM 32 q9) was copied with the half-hidden text
    and a light grey band. -> the picture starts under the heading (heading = our text); near-white (> 232) = paper.
96. Straight lines have EMPTY boxes in PyMuPDF and `Rect |= empty` does nothing: grids and axes never widened a diagram
    crop (2014 MJ 11 q12: dots without their grid and 'Diagram 1-4'). -> line boxes get 0.3 pt each side. Check: fig_cut.
97. A diagram crop took the part's question line ('(ii) Sketch the model ...', '(b) Shade P∩Q′', 'So N(6, 4) = ...'):
    pieces of the line were each < 22 characters. -> whole printed lines are judged; a line starting with a part label,
    or a line above / below the drawing and off to its side, is question text. Check: fig_text.
98. A box of words (arc / circumference / ... 2014 MJ 11 q4) was cut as a picture. -> a cluster made only of the box's
    edges with words inside stays text + rules.
99. 2025 'AllAndNone' (one font holding regular, bold and italic Times) was read as SANS, and the one-font rule then put
    the whole 2025 mark scheme in sans too; bold labels '(a)' came out regular (glyph_styles was tuned on physics sans).
    -> maths: AllAndNone = serif; `store_text.maths_styles` reads bold / italic from Times letter widths + slant.
    Check: q_font (any sans word in a maths question).
100. 2014 nameless fonts: italic x, y, their drawn upright. -> `store_text.nameless_style` (regular / bold / italic /
    bold italic by letter widths against the four Times fonts).
101. Recurring-decimal dots are letters of equation fonts (MMEtc 'o', MT Extra code 5 and 'i'): written as the letter
    'o' squeezed to 1.8 pt they drew a blob over the digit (2019 ON 61 q3). -> kept as drawn glyphs (exact shape and
    place); EuclidMathTwo '-' = '≤'. Symbol sweep of all M0 equation fonts: no other unmapped letter left.
102. Graphs in MS cells drawn from many short straight pieces with dashed grids were not seen as drawings (no curve
    over 30 pt, no long grid lines): laid out as faint loose lines, axis numbers lost (2014 MJ 42 q2, 2019 ON 41 q11).
    -> `_picture_cell`: axes (a long vertical line crossing a long horizontal one) = a graph = picture.
103. A MS row starts 4 pt above its label, but maths prints things higher: a numerator ('144' over '233', 2014 MJ 52
    q1(b)(ii)), a rotated table label ('All pos', 2021 FM 52 q3), a table's top band (2014 MJ 62 q1) went into the row
    above. -> ms.py `_lift` (maths, both row finders): while a word or drawing crosses a row's top cut, the cut moves
    up above it (not above the previous label's line).
104. The round-27 re-flow joined separate answer lines ('... -1.241' + '[x =] 1.13 ...', 2019 ON 42 q12). -> only a line
    that goes on with a sentence (starts with a lower-case word, not 'or' / 'and') is joined.
105. The 'heading under a pasted picture' rule (pattern 95) cut the top edge of a DRAWN Venn box (2021 FM 42 q9). -> only
    for pasted pictures (images); and the whole heading line is our text (only its first word was kept).
106. Cell shading printed as many thin grey strips counted piece by piece (< 400 pt2 each): the table was laid out as
    items and the strips landed in the wrong cells (2019 ON 51 q1(b)(ii)). -> shading area is added up.
107. A long answer that wraps in our narrower column moved only its own column: the Marks / Partial Marks lines stayed
    beside the wrong answer line (2025 MJ 61 q4). -> two passes: each column's growth by printed height, then every
    column is laid out with the largest growth at each height.
108. 2014 nameless SYMBOL subsets re-use letter codes: '<' printed as <=, '.' as >, 'Y' as <=, 'I' as >= (2014 MJ 43 q6,
    q3(b)). Glyph names lie (the <= glyph is named 'less'). -> `store_text.symbol_subset`: a nameless font with a
    character far off every Times width (a '.' as wide as a '>') is a symbol font; its one-letter spans are kept drawn.
109. fit_crop (store) took a part's question line into a diagram crop again: maths part lines are indented under their
    label, so they never counted as sentences ('(ii) Sketch ...', 2021 FM 62 q9). -> fit_crop(maths=True): a line
    starting with a part label, or a full sentence, or a line above/below the drawing and off to its side, stays out.
110. A diagram crop grew down through a ruled table under it (2019 ON 62 q3). -> crops stop at tables / boxes of words.
111. A rounded box of text (curved corners, 2021 FM 62 q6) was cut as a picture. -> straight sides + small corner arcs
    = a box (pattern 98).
112. The next section's title ('MODELLING ...' 2021, 'Modelling: ...' 2025) went into the last MS row. -> it ends the
    table like a 'Question' header.
113. A printed line hanging right ('+ 8[corners]') kept its indent and crossed our column rule; two printed lines joined
    by a tall root sign were wrapped piece by piece and drawn on top of each other (2025 MJ 21 q15). -> the line moves
    left to end at our edge; joined lines are one block (scaled if wider than the column).
114. Long text lines just under a drawing went into its cell picture (2025 MJ 61 q1: a table and its notes shrank into
    one small picture). -> words longer than 6 letters join a picture only inside the drawing's own height.
115. Symbols (x, <=, ÷, °, π) were drawn in sans in maths papers. -> maths: Liberation Serif when it has the symbol.
116. Check false alarms fixed: ms_stretch only for words WE make (printed words keep printed widths); ms_piccut and
    fig_cut ignore a straight table rule beside the edge.
117. A ruled table 15 pt under a diagram joined the diagram's cluster (drawings within 20 pt), so the table test never saw
    it alone and the crop took the table (2019 ON 62 q3). -> ruled tables (>= 3 rules with the same ends, vertical rules,
    text in most rows - not a grid) are found BEFORE clustering and kept as text + rules.
118. An empty answer box beside a formula was cut as a diagram (2025 MJ 61 q5). -> an empty box < 40 pt tall is no diagram.
119. An equation line under a graph ('f(x) = (3x + 2)/...', 2019 ON 43 q12) was half inside the crop. -> a line with '='
    fully above / below the drawing is question text (extract and fit_crop).
120. Broken text layer (2014 MJ 62 p4): words outside the drawing's height were laid out as text OVER the cell picture,
    and the picture's top was clamped to the graph (the formula above it was lost). -> broken page: the whole cell is
    the picture, from its first ink.
121. Graphs traced in short pieces with no long axis line (2014 MJ 42 q2, 43 q6). -> 20+ pieces touching no text, or 5+
    slanted pieces longer than 8 pt, spread over 60 x 30 pt = a drawing (root-sign ticks are 2.7 x 5 pt, beside text).
122. A row lifted over the table header ended at the header (it counted as 'a new table below'): the first row of a page
    lost all its content (2025 MJ 61 q1(a)). -> a header above the row's label never ends the row; the first row's lift
    stops at the table top.
123. Main column rules drawn in 6 pt pieces: the lift climbed up them into the row above (2021 FM 52 q4(c)(ii) took
    4(c)(i)'s lines). -> verticals at an x where the page's verticals add up to > 30 % of the page height are main
    column rules and never lift a cut; an inner table's border does (2021 FM 52 q3(b): its top row came back).
124. Pasted pictures (images) were not seen by the lift. -> images count.
125. Notes under a table went into its picture because a root sign in them counted as part of the drawing. -> a cell
    picture takes the main clusters of drawings (>= 30 % of the largest); small marks standing apart stay text.
126. A rotated label ('All' left of 'pos', no text item) was cut at the picture's left edge. -> cell pictures grow
    sideways while ink is cut, inside the cell.
127. The header's grey shading pokes 2 pt into the first row of a page: its area made the cell a 'shaded' picture with
    the text drawn twice (2019 ON 63 q6(b)(i)). -> anything lying wholly in a row's top / bottom 3 pt is the neighbour's.
128. 2025 'AllAndNone' also re-uses letter codes for symbols ('+' printed as the cap sign, 'l' as a prime: 'P + Ql' for
    P∩Q′, 2025 MJ 43 q16). -> a glyph that is not its character's usual glyph AND matches no Times width (> 0.02 em off)
    is a symbol: kept drawn (digits and . , excluded).
129. A drawn glyph's cut (its character box) holds the ink under it too, and one cut was reused for every same glyph
    of the paper: a recurring dot cut over '0' drew '0' over '3' -> theta (2019 ON 61 q3 MS). -> maths: one cut per place.

### Round 29 (21 of 39 wrong; fractions now right)
130. 2014 prints a full-width rule between questions: kept at the end of every question. -> store (maths): a rule
    > 85 % of the width in the last 10 pt of a block is dropped.
131. A short underline in the Marks column (printed total line) drawn as a stray line. -> the Marks column holds no
    drawing (MS_TABLE_RULES 28).
132. The question number '12' went into a diagram crop through the sideways-label passes (they skip _label_like). ->
    a 1-2 digit line at the left margin (x < 62) is never a label (extract and fit_crop).
133. 2014 MJ 22 q2: grids drawn in the answer have tall lines too, the column finder found 5 'rules' and gave up -> old
    layout with stray '}' and no grids. -> when not 2-3, keep only the full-height rules.
134. Tables in MS cells were pictures (Dhruv: 'lines and box and text, as in physics'); laid out line by line they fell
    apart (shading strips, dotted rows). -> `_has_table` (>= 2 row rules running most of the width): every item inside
    the table's rules is one rigid block (`_emit_block`); boxes around numbers are no table.
135. A pasted graph covering its own heading ('Correct sketch' drawn twice, 2021 FM 62 q9(d)(ii)). -> a text line in the
    top 30 % of a pasted picture is the heading: our text, the picture starts under it.
136. A light grey band of a pasted screenshot and the cell's row rule were kept in the picture (2021 FM 32 q9). ->
    pasted pictures: lighter than 230 = paper; the picture region stops at the row / cell rule (never pixel-stripping:
    that took the Venn box too).
137. Review page: stored figures under the question were drawn at 96 dpi beside a 192 dpi question ('shrunk'). ->
    review_assets.fig_img at the question's scale.
138. (process) Two Claude passes doubled the time without catching appearance faults. -> ONE round: rules on all papers
    (claude_check.py checklist) + side by side only for doubtful items, each passed with a reason or fixed as a class.

### Round 30 - found in Claude's ONE check round (before Dhruv's round)
139. Pasted screenshots: the global 'lighter than 229 = paper' cut (136) erased graph grids and pale curves (2014 MJ 31
    q15, 33 q15). -> pasted pictures keep everything darker than 252; a light tone is paper only when it is a BAND
    (>= 10 rows/cols of one tone), a SMOOTH area (5x5 window spread <= 4) or the background tone that reaches the
    picture's edges (`ms_maths._erase_bands`). Shading inside a Venn box never reaches the edges (2025 MJ 11 q16).
140. Table lines in a cell: the rule 'thin vertical taller than half the row = a column rule' removed every vertical of a
    tall table row (2014 MJ 62 q3). -> >= 3 thin verticals with the same span inside the Answer column are the table's
    own (`grid_v`); rules are drawn over the shading.
141. A heading above a DRAWN graph ('Correct sketch') went half into the picture and half into our text -> drawn twice
    (2019 ON 41 q11, 43 q3, 43 q12, 2025 MJ 31 q18). -> a text line (> 8 chars) ending above the drawing's top, or our
    text over the top 30 % of it, is the heading: our text, the picture starts under it.
142. Column finder summed the lengths of a graph's grid line drawn 3 times over itself: it out-measured the table rules
    and the whole mark scheme fell back to the general layout (2014 MJ 43 q9) - no check looked, as every maths check
    needed the maths layout. -> covered height = UNION of the pieces; new check `ms_mode` (any fallback is a hit).
143. A tall nested root sign (sqrt of a fraction, 33 pt) counted as a 'sketch' -> Partial Marks cell became a cut
    picture (2025 MJ 21 q15). -> `_root_sign`: a bar along the top of the path is a root, never a sketch.
144. Rotated row labels ('1 neg') boxed as level text: split from their table, '3 neg' under it (2021 FM 52 q3). ->
    rotated text gets its real (vertical) box; rotated labels beside a table and whole unruled table rows right
    against it go into the table's rigid block.
145. The y-axis of a sketch standing near the column rule taken for a column rule (2025 MJ 61 q5(a)(v)). -> a vertical
    in the Answer column met by a horizontal axis inside its height is an axis.
146. A rule printed as 12 pt dashes (2014 MJ 62 p4): each dash too short for the row-rule tests -> stray lines and
    partial-marks pictures. -> pieces on one line are judged by the whole run.
147. (check) ms_words counted text printed twice on top of itself twice (tick labels of 2014 graphs): false 'missing'.
    -> the check dedups by position, like the layout.
148. (open) 2014 MJ 62: marks found 39 of 40 - q6(f)(ii) [1] is not read (QP pages 9-10 have no text for the mark
    brackets). Paper not approved until fixed.

### Round 30 (14 of 40 wrong) + round-31 Claude check
149. Stray verticals in Partial Marks (2014 MJ 11/12/13/42): the sketch-axis rule (145) took column-rule pieces for axes.
    -> axis rule only inside the Answer column (already fixed before the round-30 images were cut; verified 0 across all papers).
150. Shrunk text (2014 MJ 12 q9(c), 42 q1(e)): printed lines joined by a tall sign / a superscript were scaled as one
    block. -> (Dhruv: 'take the extra space, a whole step may start on a new line') bands split unless a fraction bar /
    stack / root joins them; a piece wider than the column wraps between parts that do not overlap in x; several
    fraction bars drawn as ONE path are split into bars; a line ending mid-step ('÷ their', '=') joins the next.
151. Boxed formula / small answer boxes as pictures (2014 MJ 62 q3, 2019 ON 53 q1) -> extract: a box around a short
    formula = text + box lines; only small empty boxes on equation lines = no diagram.
152. Two drawings side by side at one height = ONE picture (2014 MJ 43 q13).
153. Word 'double' table border drew two top edges (2021 FM 52 q4) -> corner pieces dropped, column rules reach the rule.
154. 2014 MJ 62 marks 39/40 (148): the broken text layer prints words as overlapping pieces ('(i'+'ii)', '1F'+'FT') ->
    pieces that overlap are joined; paper now 40/40.
155. Faint mark-scheme graphs (Dhruv: redraw + darken): graphs drawn as lines are redrawn by us (curves of tiny strokes
    joined into one polyline, curves darker / thicker, grey grids stay light); pasted screenshots: thin ink x 2.4
    contrast, shading keeps its tone; shaded-area sketches stay the printed picture.
156. (found in the check) a graph's grid + numbers looked like a table (coloured curve / polyline / tiny strokes =
    graph); table-rule search used fraction bars far above the grid -> grid = its verticals; rows against a table join
    it only if their cells line up with its columns and hold no words.

### Round 31 (36 of 40 ok) - M0 approved
157. A table placed at its printed height ran into OUR re-flowed text above it (2025 MJ 62 q4(b)) -> the table starts
    under our text as placed.
158. A chart's thin black frame darkened like a curve: a black box 2 pt from the y-axis (2019 ON 41 q11) -> a frame
    on the outer edges of a gridded graph is drawn light grey like the grid.
159. A Word double border's short corner pieces were outside the table-rule search (2021 FM 52 q4, 2025 MJ 62 q4(a))
    -> all rule pieces inside the grid's box (+10 pt) belong to the table.
160. (limit, not a bug) Pasted screenshot graphs (2014 MJ 31 q15 ...) are pixels only: contrast raised, never redrawn.

### M1 Claude check (2024 FM - 2026 MJ, 90 papers)
161. New equation-font codes in 2024-2026 papers: MMBinary j/k (∪ ∩), MMEtc c/g (° ⋯), EuclidMathTwo and Calibri
    F084/F085 (≤ ≥) -> MATHS_GLYPHS; maths_tex knows ⋯ ⩽ ⩾. New font: make a glyph sheet (crop each unknown code).
162. Paper-6 notice without 'task' ('The modelling starts on the next page.', 2024 MJ 61) -> layout regex.
163. MS label typo '9a)(ii)' (2024 MJ 43) -> label_text reads it as 9(a)(ii).
164. ms_align list read labels only at y == 14.0 (maths labels sit at 13.97 or lower) -> every maths question was
    listed; maths: the top Q-column word; a 4th-level label belongs to its part. (Was open since M0.)
165. 2026 MJ mark schemes: 5th column Guidance -> 5 columns, Answer : Partial : Guidance = 40 : 30 : 30 (Dhruv);
    gated by 'Guidance' in the stored MS header.
166. A fraction bar took only the numerator band; the denominator stayed its own line and another column's growth
    pushed it away -> a band ending in a bar takes the band under it (inside the bar's width).
167. Lines of one cell overlapped or ran past the row bottom when other columns' growth and the cell's own wrap met
    -> each line starts under the line placed above it (+ its printed gap); bottom = last placed ink.
168. Two fraction bars 0.06 pt apart in height (Answer and Partial Marks) joined into one rule over the Marks column
    and were dropped -> a rule run never takes a piece left of it. Also in approved M0 (2014 MJ 41 q11, 52/53 q4,
    2019 ON 42 q10, 2025 MJ 13 q7, 21 q22, 43 q17): re-shown.
169. Diagram label pieces ('Q', 'S', '65') over pasted pictures taken as a heading -> empty picture crop, crash;
    a heading line needs 4+ letters; empty crops are skipped.
170. Diagram crops: a sentence BESIDE the drawing moved the top through it (2025 ON 51 q4, half a grid lost) -> cut
    at the side (pixel test); vector pieces above (rider over scooter) chain in; axis titles up to 7 words and labels
    touching the edge are taken in (7 approved M0 crops gained their axis title / last label: re-shown).
171. A note across the table (a merged row 'For all parts accept ...', or a band inside a row 'In parts (a)(ii)(b)
    and (a)(ii)(c) ...') was cut into our columns or lost -> one full-width cell; column rules stop at a band; the
    next section's title row is never a note.
172. 4th-level labels printed without the number '(a)(ii)(b)' (2024 MJ 41 q2) -> ms.NONUM4.
173. A picture cell that fell back to text laid its heading out twice (2026 MJ 21 q7/q10, 23 q7: every word twice)
    -> the heading placement is undone when no picture is made.
174. Section-wide note 'Throughout the modelling allow ...' (2026 MJ paper 6) was glued to one question's end and
    the next's top -> ms.section_notes cuts it out and puts it on top of EVERY later question (Dhruv), one cell.
175. 2024-2025 section titles 'Modelling DELIVERIES BY SCOOTER', 'Modelling Waste Plastic', a bare 'Modelling' were
    not titles -> shown as the last row of the question before; header regex takes title words.
176. Dotted table rules printed as runs of 1 pt wide pictures were lost (2024 MJ 53 q4(a); also approved 2021 FM
    52/62: re-shown) -> 2+ thin pictures in a run = one dotted line of ours (mark schemes only).
177. A picture cell under a heading started at the drawing's top: a numerator / labels printed above the pasted piece
    were cut (2024 ON 41 q5(a)) -> the picture starts at its own first ink under the heading; a heading needs 4+
    letters (a numerator line is never a heading).
178. Every row of a table inside a cell got the fraction margin: a big gap under long tables (2024 ON 62 q1(b); also
    approved 2025 MJ 61 q1/q2: re-shown) -> table rows (2+ cell rules) are not 'tall' lines.
179. Items under a sub-row rule inside a picture cell were outside the crop and lost (2024 ON 61 q2(d) formula,
    2025 FM 62 q12 pasted '≤'); a power on the heading line was cut ('k²') -> items the crop leaves out are laid
    out as text / pictures; small raised text joins the heading line.
180. A text line under a sketch went half into the picture (short words) and half to our text: drawn twice (2025 ON
    63 q1 'Correct sketch passing through', 2025 FM 42 q9) -> the whole line goes to our text.
    Open: a small pasted symbol ('≠' image) inside a text line still makes the cell a picture and doubles the line
    (2025 FM 62 q5(b)(ii)) - sent to Dhruv's round as a recheck.

### Round 32 (M1: 12 of 30 ok; 14 of the 18 wrong should have been caught by me - START_HERE 2c)
181. Unit pictures were rendered WITH the page text: words under a clipped image's box were drawn twice and looked
    bold (2025 ON 61 q4 first line, 51 q4) -> pictures are rendered from a text-free copy of the page (maths).
182. Merged-font (AllAndNone) bold read from the page render mixed neighbouring ink: bold '(c)' missed, regular glyphs
    bold -> stroke weight from the font program's outline; a character's most used shape is regular (maths).
183. 'Question 11 is printed on the next page.' stayed in the question (38 questions, M0 too) -> page_bounds + checks.
184. Mark-scheme label slip '15(d)' for the paper's 15(c) -> one orphan row goes to the one free leaf at its level.
185. (repeat of 171, my own fix) a note band at the row's top got our rule over the row border: double edge.
186. Tables in MS cells: Dhruv 'make similar but proper' - rule pieces snap to one grid and join (no step at a shaded
    cell), a missing outer edge is drawn, stubs above the table dropped (2025 MJ 61 q2, 2014 MJ 31 q5). MS_TABLE_RULES 32.
187. Sub-row rules inside a row were dropped: answer lines no longer lined up with their marks (2025 ON 23 q15 'line
    between A1 and M1', 2026 MJ 62 q6) -> redrawn between the placed lines when every column is aligned there.
188. Steps with fractions never re-flowed; wrapped rows took the fraction's height ('7.5 oe' alone, 'of x' far below)
    -> re-flow allows bars / roots; rows aligned on baselines, each row as tall as its own pieces.
189. Calibri F084 (invisible, opacity 0, glyph 0) was mapped to '≤' (pattern 161): a second ≤ drawn -> dropped.
190. (repeat, left OPEN in round 32 - never again) a small pasted symbol in a text line made the cell a picture and
    the line was drawn twice (2025 FM 62 q5) -> a picture <= 24 x 90 pt inside a text line is a piece of the line.
191. A labelled rectangle beside a diagram (same band as NOT TO SCALE) was left out of the crop and redrawn as lines
    (2025 ON 23 q15) -> short-label / empty boxes on a NOT TO SCALE band join the diagram.
192. MS graphs printed as calculator screenshots (colour, blurry) -> drawn again from the function the question gives
    (pipeline/ms_graphs.py SPECS: function, window, ticks as on the question's axes; black curves, light grid, function
    in a box top right, 2nd curve dashed). New screenshot graph: add a SPECS line (the check sheet shows it).
193. MathType minus (MMTimesRoman '-') read as a hyphen left a gap ('5- 1/2x') -> mapped to '−' (store_text).
194. Re-flow joined lines across a printed sub-row rule ('... or better' + next sub-row '32.8 km/h' in one cell,
    2024 FM 62 q9(c); 25 questions) -> never join across a rule (ms_maths re-flow, CTX subrules).
195. A column that wraps more than printed (5-column Guidance) left no room for the sub-row rule: the rule was dropped
    -> the row under the rule moves down so the rule fits (2026 MJ 63 q6(b)).
198. A rule that would run through a line (a mark '1' beside the table above its '18', 2026 MJ 62 q6 - Dhruv round 32
    'all lines align with their answer'): the columns under the rule move down to their printed offsets (not to the
    same top: a centred cell stays lower), only where the rule would otherwise be dropped (everywhere broke good rows).
    Text around a table and the table itself now count for rules (placed_all).
199. Text under a table in a cell did not move down with the table (2024 ON 63 q6: a rule ran through 'or') -> it
    starts under the table as placed.
200. Maths notices 'Question 4(b) / 10(c)(i) and (ii) is/are printed on the next page' (6 papers, found by checks).
196. A task heading with no section letter ('Modelling   Helix', 2026 MJ 63) was not found: no intro, no task record
    -> extract.TASK_HEAD + 'You are advised' on the next lines; letter by order.
197. Paper 5/6 tasks as ONE record (Dhruv round 32): pipeline/tasks.py writes task_<S>.json (id ..._t<S>): intro as
    stem, every printed question as a part (printed numbers kept: renumber skips qnum/mslabel for type 'task'), one
    MS (header, section note once, one Total). Per-question records stay for the checks and point to it ('task').

## Round 33 (Dhruv, 2026-11-17: 9 of 23 wrong)
201. Graph labels in drawn MS graphs: small (7 pt), fractions as fractions, placed where no curve, axis or tick number
    is (ms_graphs); a label only where the printed graph has one.
202. 'y2 - y1' printed as one subscript chain (sign and second letter at subscript size): back to normal size, digits stay
    subscripts (ms_maths._sub_chain).
203. Signs in the 'symbol' face were drawn in DejaVu Sans, far wider than printed ('>' ran into '9'): signs use the
    paper's font, centred in their printed width (ms_maths OPS_SERIF).
204. A part label whose bold was not read ('(c)', 2025 ON 32 q15): bold + partlabel when it leads its part's first line.
205. An intro picture running on beside the first question (the scooter, 2024 FM 62 B) was cut at the question's top:
    its lower part joins the intro (store.paper_record).
206. Figure SVGs lost the width of every space (MuPDF redaction rewrites text runs: 'Reflectioninleftdiagonal'): each
    glyph goes back to its printed x (render._respace, maths only).
207. A formula with a root sign ('H1 = piD sqrt(1 + (h/t)^2)') was cut as a diagram: text + root sign (extract, maths).
208. An MS picture took the top of the text line under it, and tall-bracket pieces went into the picture: the picture
    stops above our text, bracket pieces and their line stay text (2026 MJ 63 q9).
Passed with reason: 2024 FM 62 task A empty magic squares are vector drawings (lines), already crisp - Dhruv: 'your call'.

## M2 (2026-11-19) - found while building the two-pass flow
209. fontTools was not in requirements.txt: on GitHub every `from fontTools ...` failed and was swallowed - ms_maths fell
    back to the physics layout ('wrap'/'scale'/'cell': Partial Marks inside Answer, codes in the Answer column) for 1682
    questions in the LAST M1 Action run, and bold / symbol-font reading (patterns 182, 108) never ran on GitHub. The M1
    approval committed that Action output: ~880 approved maths questions (M0 + M1) were in the fallback layout. This was
    also the real cause of 'local store.build differs from the Action (font family)'. -> fonttools pinned in
    requirements; run.py imports it; ImportError is never caught (ms_layout, store_units, store_text). Check: reasons.py
    ms_mode class must be 0 after every GitHub build; any 'No module named' in the Action log = stop.
210. (checks) ms_sweep tested 'code left of x 470' (physics columns): in maths every 'M1 for ...' of Partial Marks was a
    hit -> maths uses the table's own Answer / Marks edges. ms_align globbed the whole bank per question (20+ min for 11
    sessions) -> direct path (1 s).
211. (tool) Local ms_rebuild without the session's printed PDFs: every picture cell silently fell back, so the local result
    differed from the Action (164 'changes' of 253 were this, not my fixes). -> ms_rebuild.py exits unless the PDFs are
    fetched. Measure blast radius only with the PDFs on disk.
212. 2023 MJ 33: 'Answer all the questions.' with Question 1 printed 13 pt under it - the notice cut (y1 + 3) took Q1's label:
    0 questions; checks.py then crashed and left 10 papers unchecked. -> page_bounds stops above a question number;
    checks.py reports an empty paper as blocking instead of crashing.
213. A formula wider than the Partial Marks column (one fraction with a long numerator, a long root) was clipped at the
    column edge in the re-flow paths. -> the unbreakable piece is scaled to fit (>= 60 %, MS_TABLE_RULES 30).
214. A 2x2 px image stretched under a formula line (invisible mask) made the cell a 'picture': the formula was half picture,
    half text (2022 ON 43 q5(c)). -> images of <= 16 pixels are no pictures (store, maths). Open: the '[...]' dots there.
215. Re-flow joined a new marking point ('B1 for ...', 'FT ...', 'If ...') to the line above: open_end() looked at the widest
    line of a joined paragraph (ending 'or') instead of its last line. -> last printed line; code-led lines never join.
216. A question whose MS is mostly a small printed table (8 pt) got a small median size and the whole scheme was scaled to
    ~15 pt (2023 MJ 53 q6, 2023 FM 52 q1/q2). -> the paper's most used MS size decides when the question's is < 90 % of it.
217. MS labels: '12(a)(i)' printed twice (the second = 12(a)(ii)) -> rows past the first leaf's marks go to the one free
    leaf when the marks match (run.py); '5(a)(iv)' wrapped over '(b)' in the Q column -> one label 5(a)(iv)(b) (ms.py).
218. A sub-row rule was redrawn through text laid out under a cell picture ('[on third roll] ...' struck through, 2021 MJ 51
    q7). -> a rule is never drawn through a word (no rule rather than one through content).
219. Tables in MS cells fell apart: rules starting at the cell's left edge were taken for sub-row rules, and a table whose
    rows are cell fills (no row rules) was taken for a shaded picture (2023 FM 62 q1/q2). -> one-ended rules crossed by
    >= 2 column rules are table rules; fills count as row lines; >= 4 column rules over the grid = a table.
220. A line running on past a table ('x = 2 and y = 3 or x = 3 and y = 2' under the bins table) was half pulled into the
    table block: its tail drawn at the cell's left ('x = 22', 2022 MJ 61 q3). -> a printed line that does not fit the
    table's width is a sentence, never a table row.
221. One 16 pt equation-font letter ('m' of m²) made every 11 pt line of the cell 'small raised text' that joined the line
    above: words moved paragraphs and a big gap opened (2021 ON 63 q1(c)). -> 'small' is measured against the cell's
    normal size (most used), not its largest letter.
222. Labels inside a Venn frame ('Sandwich', 'Fruit') were taken as a heading: moved out as text, the frame's top cut
    (2023 ON 12 q20). -> text inside a drawn frame is never a heading.
223. A table printed at the very top of its row lost its top edge (dropped as the row's rule) and kept rule stubs (2022 FM 52
    q4). -> an inner rule with the table's own column rules hanging under it is the table's edge.
224. 2026 MJ (5 columns): no Total row at all (_own_total accepted 3-4 columns) - in the M1 approval too. -> 5 columns:
    Total in the Marks column (MS_TABLE_RULES 8). 256 approved questions gain their Total row.
225. Diagram crops kept question text above / below the drawing: the tail of 'shade A∪B.', part lines '(a) A′∪B′',
    '11 (a) On the Venn diagram ...', the question number, 'f(x) = ... for ...' under a graph, '... shape is 7√3/4.'
    (9 crops). -> fit_crop (maths): a line above / below all drawing ink that is a part line, a question number at the
    margin, a 'f(x) = ... for' line or a sentence running past the crop is cut off; strokes on a text line (|..|, roots,
    bars) are text, not drawing.
226. New equation-font codes: MathematicalPi-Six N Z Q R (ℕ ℤ ℚ ℝ), MMRelation 1 ; (⊂ ⩽), MMEtc k (…), MMaEtc g (⋯) were
    drawn as plain sans letters (q_font). -> MATHS_GLYPHS + maths_tex.
227. Page furniture at a page top / bottom: 'The modelling task starts on the next page.' at y 61 (rule needed y > 100) and
    an answer line '..... [3]' printed 0.2 pt into the box of 'Question 12 is printed on the next page.' was cut off with
    it (2021 ON 61 marks 57/60). -> notice at any height; the line above it stays.
Known open (M2, written down after 2-3 tries): a tree diagram cut into two crops (2023 MJ 32 q11), a box of words taken into
the circle's crop (2023 MJ 11 q3), a rounded formula box kept as a picture (2022 ON 61 q6), the dotted '[...]' of 2022 ON
43 q5(c) lost. Status 'known' in M2_reasons.json - fixed first in the next chat, never sent to Dhruv as items.
228. (pass 2) Pattern 225's cut stopped at the f(x) line's text box: its own fraction bar / numerator ('1' over
    '(2x-3)(2x+1)') stayed in the graph crop (2023 ON 41 q2, 2024 ON 41 q9 - approved, re-shown). -> the cut passes the
    line's own strokes and the stacked pieces just above / below it.
229. (pass 2) Pattern 219's 'grid of >= 4 columns = table' also took boxes around numbers ('2 x 5 x [2] x [5]', 2019 ON
    51/52 q1) for a table; a fill-only table lost its row lines and its row-name column fell over it (2022 FM 62 q1).
    -> the grid rule needs cell fills; fill edges become row lines; text left of the first column rule joins the table.
Lesson (M2): the pass-2 diff caught my own collateral (229) BEFORE Dhruv's round - the flow works; my one-off visual check
of a fix must include one 'look-alike that must NOT change' (boxes, grids) next to the target.
230. (pass 3) Pattern 225's 'sentence running past the crop' joined every word on the row: an axis title plus the mark
    '[2]' (2022 MJ 32 q10 lost its x axis) and two tree labels ('0.80' + 'on time') counted as one sentence. -> only the
    line's own words, chained by word gaps < 12 pt; marks '[n]' never count.
231. Figure grouping (maths): a tree printed as two clusters (2023 MJ 32 q11) -> stacked crops with only short labels
    between are one picture; two grids each with their own 'Step' text beside them in one 10 pt cluster (2023 MJ 53 q3 /
    63 q3) -> split at the empty band, never re-merged; a drawn box of words under a circle (2023 MJ 11 q3) -> its words
    are no labels and the box is text + rules; a formula in a ROUNDED box (2022 ON 61 q6) -> text + box, no picture.
(tool) reasons.py pass 2 re-judged 'verified' picture / table reasons against the newest fingerprints: 19 false 'not
fixed' in pass 3 -> verified stays verified.
232. (pass 4) My first versions of the 231 rules were too wide - the pass-4 diff showed 34 + 20 collateral questions:
    the 'rounded box = text' rule dropped real diagrams (a number line, a triangle, cubes with NOT TO SCALE), the tree
    merge joined grid rows / diagram pairs, the word-box rule cut 'x cm' labels of a shape beside another shape, and the
    stacked split broke a circle from its label. -> rounded box: ONE line >= 15 chars between full-width top and bottom
    edges; word box: one drawn rectangle with only text in it; tree merge: a branch of one crop ends at a label and a
    branch of the other leaves just right of it (a NODE); split: side text >= 15 chars and both halves >= 40 pt.
    Re-tested on all 28 affected questions: targets right, every other crop back to its pre-M2 (approved) box.
    Lesson: a grouping rule is tested on its target AND on the 20+ look-alikes the diff names, before any push.
233. (round 34 prep) After the 231 split, the lower 'Step 2' grid's stored crop grew up into the upper grid's x axis
    (fit_crop grows over ink crossing its edge). -> maths: a stored crop never grows into a sibling figure of the same
    page. Blast radius measured on all 423 figures with a sibling: 3 change (the target + 2 circles, all right).

## Round 34 (Dhruv: 6 wrong of 13; my 4 fixes: 2 wrong, 4 changed approved: 2 wrong, 5 calibration: 2 wrong)
234. MS 'boxes around numbers' (2019 ON 51 q1(a)(ii), approved before, changed by M2) got a rule drawn under the x signs
    between the boxes: _has_table added the lengths of SEPARATE rule pieces (four boxes 11-16 pt apart) and called the sum
    a row rule; _clean_table then 'added the missing outer edge' because the boxes' outer verticals reached it.
    -> a row rule is only pieces that TOUCH (<= 1.5 pt); the missing outer top/bottom edge is added only when the grid has a
    real row rule across (>= 60 % of its width). Same blast measured on all 20 maths sessions: 4 questions changed.
235. MS table 2023 FM 62 q1(a) (cells shaded in strips: top / middle / bottom strip + the whole cell on top): every strip
    edge became a row line (double / triple rules), the 5.6 pt stubs of the column rules were left outside the table block
    as loose ticks above the header, and the right outer edge (printed against the column rule) was lost.
    -> fill-only row lines come from the WHOLE cell's edges only (strips inside a larger fill are ignored); a column rule
    printed in pieces is one rule (stubs <= 8 pt that touch it go with the block); the right outer edge is drawn like the
    left one, over the header row too.
236. A column vector's brackets (2021 FM 22 q2 answer cell): the printed pieces (top, extender, bottom) are 13 pt apart
    but our piece glyphs are 8.7 pt tall -> a visible gap each side of the extender. -> ms_layout._close_brackets adds
    extenders between pieces more than 1.2 glyph heights apart (touching brackets stay as they are).
237. Question side (maths): fit_crop's 'ink crosses the edge' test is a pixel test and misses a SLANTED stroke (ink above
    and below the edge sit at other x): 2022 FM 42 q10(c) tree lost its top branch. -> maths: a stroked drawing > 12 pt
    each way that crosses the crop's top / bottom edge counts as cut and is taken in (store.FIT_SLANT).
238. Question side (maths): the two COLUMN HEADINGS above a tree ('Wears a sweatshirt', 'Goes for a walk') were left out
    of the stored figure (2022 FM 42 q10). -> two short non-sentence lines on one baseline, >= 40 pt apart, nothing else
    between them and the crop, within 34 pt above it, are part of the picture (store.FIT_HEAD).
239. MS pictures that are blurred RASTER screenshots: a handwriting-style tree (2023 MJ 32 q11(a)) and a calculator graph
    (2023 MJ 63 q12(c)(iii)) look poor next to our text. -> ms_graphs.SPECS: new 'tree' spec (two stages, probabilities
    on the branches, drawn as lines + text like the question's tree) and options 'xlab' / 'xlow' for graphs. Only the two
    flagged ones are redrawn; ALL other raster screenshots of M2 (about 60 graphs / Venn pictures) are an open decision
    for Dhruv (a batch of its own, every redraw needs the function read by eye).
Lesson (round 34): the 6 wrong items were 3 classes I had passed as 'matches print' - (a) MS pictures that match the print
but look blurred (239), (b) a stray edge inside a few-cell group (234), (c) crop rules blind to slanted strokes (237).
The 'look-alike that must NOT change' list for 234/235: every MS table with only strips or boxes (blast run = 0 more).
Tool note: `ms_rebuild.py` WITHOUT --write still rewrites msimg_*.png (byte noise, ~300 files): `git restore` them before
the commit (never commit msimg PNGs from a local run).
240. Stacked column vectors torn apart when a mark-scheme line wraps ('B1 for translation of (-5 / y) or (x / -3)': the
    second vector's top on line 1, its bottom on line 2; 2025 ON 22 q10, 2026 MJ 22 q4) and, found in the round-34 pass
    check of my own bracket fix (236): an extender run drawn between the bottom piece of one bracket and the top of another
    at the same x (a line down the whole cell, 2023 ON 41 q1 1(d)(ii)). -> ms_layout._close_brackets bridges ONLY a
    top/extender piece to the bottom/extender piece right below it (<= 3 glyph heights); ms_maths._cell merges the bands a
    bracket column spans (BRK_). maths_check ignores the extender glyphs it adds. FIXED 2026-11-24 (2023 MJ 32 q8(c), 2026 MJ 11 q18(b),
    2026 MJ 22 q6): (a) ms_maths._lines_of joins the line of a bracket's top piece with the line of its lower pieces (the
    glyph boxes do not overlap); (b) _brk_join: a wrap piece never ends on an opening bracket or starts with a closing one
    (gap up to 2 x GAP). Blast: 60 questions in 2020-2026, all vectors now one block, all looked at side by side (fine).
Lesson (round 34 pass 2): a new layout rule needs the SCAN for its look-alikes before the push (here: stored rows whose
bracket tops have no matching bottom, rows with >= 5 extenders): that scan found the stray line and 6 more questions in 2 min.

## M3 (2018 MJ/ON, 2020 MJ/ON - 2026-11-23), GitHub pass 1: 182 reasons in 115 questions
241. 2018 ON 31: WHITE '[2]' / '[3]' text on the first line of a two-line answer ('Perimeter = ... cm' / 'Area = ... cm2 [2]')
    prints nothing but was read as a mark: marks 105 of 96. -> layout.visible_lines (maths) drops white mark brackets.
    Scan of all 0607 QPs: only this paper.
242. 2018 MJ 63 / 2018 ON 61: a 'Communication' row printed 6.5 pt under its full-width rule: the cut 4 pt above its text
    crossed the rule's column stubs and the lift climbed the sub-row column rules of the merged cell above - 'Justification',
    9(b) A1, 7(c)(iii) went into the communication row (marks 35/40, 38/40). -> ms.py (maths): a Communication cut never
    lifts above the rule it sits under. Also corrected approved 2019 ON 61 q5(c)(ii) (27 pt of it was in the C row).
243. 2020 ON 41 q2: labels printed without the number ('(a)(ii)') were accepted only after a page with rows; Q1 and Q2 share
    the first table page -> 7 rows lost. -> maths: accepted when a numbered label is above them on the same page.
244. MS label typos '(12b)' (2018 ON 22) and '1(ii)' after 1(b)(i) (2018 ON 42) -> label_text / the current letter (maths).
    Typos '6a)(i)', '3(b(ii)', '6b(ii)', '7c(ii)' were already read right (ms_words only: passed).
245. 2018 MJ 32 q14 / 33 q5: a whole answer line 'B ( ...... , ...... ) [2]' printed level with the next part's label: its
    mark went to the part below (part marks wrong, paper total right - only checks.piece saw it). -> the 'lone mark' cut
    rule (extract.raw_segments) takes answer lines ending in a mark (maths). Blast: 4 approved papers had the same
    defect and are corrected (2019 ON 43 q11, 2021 ON 42 q2, 2022 MJ 31 q3, 2022 MJ 42 q10).
246. fit_crop (maths) 'sentence BESIDE the drawing': a part's question line overlapping the crop top ('(iv) On the Venn
    diagram below, shade the region G'∩B') counted as beside because its own symbols / its '[1]' at the right looked like
    drawing ink: the crop lost its left half (2020 MJ 31 q11 Venn, 2018 MJ 63 q8 axes, 2020 ON 11 q8 chart). -> a line
    led by a part label is never beside; words are blanked before the beside pixel test.
247. A mapping diagram's 5 arrows are 20.7 pt apart; the 10 pt cluster rule joined only two (2018 ON 11 q15 lost rows).
    -> extract.diagrams (maths): a column of the same thin shape (same x, < 30 pt apart) is one cluster.
248. Hatched bars: hatch lines are long diagonals clipped by the bar; their whole boxes reached 80 pt into the next part
    (2020 ON 11 q8: the chart crop took q7's last line and the stem; part (a) got a text-only 'diagram'). -> extract.
    clipped_drawings (boxes cut to their clip path) in extract.diagrams and fit_crop (maths); a chart's small legend
    cluster beside it joins it.
249. Question text under a drawing not cut: 'f ( )x = x3 - ...' (italic pieces broke the f(x) regex, 2020 MJ 43 q4) and a
    full sentence with no part label ('On the grid, translate the triangle by the vector (4, -2).', 2020 ON 12 q15).
    -> fit_crop q_ test: 'f ( )x =' and a sentence of >= 6 lower-case words ending in '.'.
250. New equation-font codes: MMGreekItalic i a (θ α), MMEtc h (⋮), MMNegate 'Y' (the slash over a separate '=': kept as a
    drawn glyph) - drawn as sans letters before (q_font). Arial 'U' (universal set), Helvetica answer dots and the 96 pt
    Arial 'VRIEND' (a symmetry question) match the print: passed.
251. KNOWN OPEN (M3, 5 questions, written after the ~30 min budget): MS cell pictures broken in ms_maths - (a) a Venn picture
    with a light frame split into a frame strip + circles (2018 MJ 33 q8(b)(i), 2020 MJ 31 q11(a)(i)); (b) Venn letters that
    are tiny pasted images lost and the drawing drawn twice (2020 ON 33 q8(b)); (c) a partial-marks sketch lost (2020 ON 43
    q8(a)(iii)); (d) plotted crosses (4 strokes of 1.5 pt each) lost from a redrawn graph (2020 ON 62 q6(a)) - not dropped by
    _chain; look at the store's MS row lines first (store.py drawings for docname 'ms'). Status 'known' in M3_reasons.json.
252. KNOWN OPEN (M3): 2018 ON 61 MS - root-sign bars drawn through the text (7(a), 7(b)(i)) and bold bleeding into the next
    letters ('C op|portunity', 'Co|rrect': ms_overlap); 2018 ON 63 q6(d)(i) - four formula lines re-flowed into one
    paragraph (lines starting 'sin', 'cos' counted as a sentence going on).
Lesson (M3): a figure rule that looks fine on its target can change ~100 approved crops (an 'arrowhead = graph, not table'
rule turned every numbered coordinate grid into a picture): the full-batch figure blast (old vs new crop of every 0607
figure, pipeline/fig_blast.py) caught it before any push - run it for every extract/fit_crop change.

## Round 35 (Dhruv, 2026-11-24): 7 ok, 3 wrong (2 of them my calibration passes)
253. MS brace '}' drawn as one filled outline with ZERO-LENGTH lines and flat curve pieces inside: each one restarted the
    sub-path, so the fill fell apart into wedges (2019 ON 61 5(a)(i)). -> store_units.drawing_d (maths): such pieces keep
    the current sub-path. 27 pages of 0607 have such outlines; approved ones change only path joins (draw the same as print).
254. MS screenshot graph 2019 ON 61 5(a)(ii) redrawn from the question's model y = 12 - 1.8 cos t (ms_graphs.SPECS, grid as
    the screenshot: t every 20, y every 2 to 14).
255. Diagrams side by side / one above the other with no text between them are ONE picture, captions under them inside
    whole (never a '[2]' mark or answer dots); a one-square diagram joins its row (2020 ON 51 q1, q2). Dhruv's rule,
    round 35. Blast: 57 questions merge (all 0607); applied to M3 now, approved papers only on a later rebuild.
256. Dotty paper (>= 40 round dots on a grid) is drawn with the shapes on it - no crop of a part of it (2020 ON 51 q2(a)).
    A first version counted any 12 small dots and dropped real graph pictures (plotted points): the blast caught it.
Calibration lesson: I had passed 2020 ON 51 q2 as 'matches print' - a row of 3 separate crops matched the print but is
not what Dhruv wants (one picture). 2018 MJ 33 q5: the graph is drawn exactly (lines + text); Dhruv: drawn is fine.

## Round 37 work (2026-11-24): the 7 pending M3 papers fixed (Dhruv: 'show me what is wrong, redraw faint ones')
257. MS rows cut too high over a Venn of 1-pt image tiles: the Communication row-line floor now holds for every maths label
    (only when the cut was lifted more than 6 pt) - 2018 MJ 33 q8(b)(i), 2020 MJ 31 q11(a)(i), 2020 ON 33 q8(b), 2020 ON 43 q8
    and 14 other mark schemes (2018 MJ 42, 2019 ON 23, 2021 MJ 32, 2022 MJ 53/61, 2022 ON 63, 2023 MJ 63, 2023 ON 11, 2025 ON
    51/53/61 ...). Closes 251 (a)/(b) and 252's Venn part.
258. Venn letters pasted as narrow images (< 8 pt wide) were dropped: maths keeps images >= 4 pt wide when >= 20 pt tall (store.py).
259. Faint / screenshot MS graphs redrawn (ms_graphs.SPECS, no function label): 2020 ON 43 8(a)(iii) (column 3, vector),
    2020 ON 62 6(a) (12 plotted crosses, drawn over the line), 2018 ON 61 5(b)(i) and 6(c) (blurry screenshots with broken
    grid). A spec now also works for a vector picture ('vector': True) and for the partial-marks column ('col': 3).
260. A cell whose PDF text is unusable (root sign with no drawing of its bar, doubled bold letters) is kept as its printed
    picture by name: ms_maths.PRINTED_CELLS (2018 ON 61 7(a), 7(b)(i)).
261. A list of formulas is not re-flowed into one paragraph: a line ending with ':' or with 'oe' followed by a line with '='
    starts a new line (2018 ON 63 q6(d)(i)).
262. A white background box wider than our column made the text 'too wide' and shrank marks / partial marks to 70-88 %
    (2020 MJ 31 q11(a)(i) '2'): wide white boxes are not ink in a text cell (6 questions had it).
263. A blank line under a re-flowed sentence (the next line kept its printed place: 2018 ON 63 6(c), 6(d)(i), Dhruv round
    37): space a re-flow saves now moves the next lines up, unless the line lines up with another column (a line there at
    the same height) or a sub-row rule lies between; a wrap in the Partial Marks column beside it does not hold it down.
    Sample rebuild (2014 MJ 41, 2022 FM 62, 2024 FM 62, 2026 MJ 12, 2023 ON 11, 2025 ON 53): 13 questions tighter, no overlap.

## Screenshot-redraw batch (2026-11-24, decided 2026-11-22): every blurry MS picture of M2 + M3 drawn again
264. 110 blurry pictures in 84 questions (83 graphs, 12 data plots, 12 Venns, 3 trees; 95 other screenshots - tables, shape
    grids, dot patterns, pie charts - out of scope). 96 redrawn with ms_graphs.SPECS (each read from the question by eye,
    the question's own axes and ticks, no label unless the screenshot prints one). New spec kinds: 'venn' (2 or 3 circles,
    'shade' = a set expression, 'nums' per region, 'names' words go in the box corners, a list = several Venns, 'stack'
    = one above the other, 'cap' caption), 'bars' (bar chart), 'band' (region between two curves shaded), 'tags' (text
    on the drawing: 'a = 2.5'), 'vlines' (x = 95), 'h': 1.0 (the picture keeps its own height: text under it in the
    cell), tree probabilities 'a/b' drawn as fractions. Text under a redrawn graph now grows the row (it ran into the
    next row: 2021 MJ 62 q3(b)). A spec whose line breaks Python makes the whole MS fall back to the old layout (KeyError
    'x' after a comment pasted mid-line): always run ms_rebuild.py without --write and grep 'failed' after editing SPECS.
    KEPT as printed (no axes in the question / the function is the candidate's own / hand-drawn data plot with a fitted
    curve): 2021 MJ 41 q6(c), 2021 MJ 41 q11(b), 2022 ON 62 q6(b), 2023 ON 61 q10, 2020 ON 41 q3(b), 2022 MJ 41 q9(b)(i)
    (already clear), data plots 2021 MJ 62 q8(c)(i), 2022 MJ 62 q8(b), 2022 MJ 63 q10(f), 2022 ON 32 q7(c), 2020 MJ 63
    q6(a)(i); 2020 MJ 31 q11 Venns (Dhruv ok, round 37).
    Approval hashes cover the cut and marks, not the MS drawing: the 83 rebuilt papers stayed approved (all 227 changed
    questions looked at side by side: 96 redraws, 81 MS spacing/row moves from patterns 257/263, 41 round-35 figure
    merges - all match print).

## Round 38 (Dhruv, 2026-11-24): 13 ok, 7 wrong - all fixed
265. Text in a redrawn picture looked like another font: the drawing guessed widths (0.5 em per letter) and the SVG
    stretches each text to its width (textLength) - Venn numbers '1 5', 'a = 2.5' tags, function labels. Now the real
    width (ms_graphs._w; characters outside Latin-1 such as '–' measured 0.55 em: the font table measured '–3' as 1/4 em).
266. The y-axis letter sat on the window's top edge, on a curve that starts at the top (2021 MJ 62 q9 'p', 2023 MJ 41 q3):
    now beside the arrow tip above the window (top padding 12 pt). Curve tags ('a = 2.5') placed in clear space next to
    their own curve.
267. A redrawn graph taller than the printed picture ran over the next sub-row (2021 MJ 63 q7(d)): everything under it in
    the row now moves down by the extra height (CTX pic_grow; the drawing's own pieces carry _g and stay).
268. Tree probabilities as fractions sat on their branch (2021 ON 31 q7): each fraction's corner is placed clear of the
    line at its right edge (above the upper branch, below the lower one), layout like the question's tree.
269. Function label only where Dhruv wants it: 2022 ON 42 q11 none (the printed corner label is not needed there).
270. RULE (Dhruv round 38): every faint or blurry picture is redrawn; what cannot be redrawn reliably is FLAGGED for his
    decision. pipeline/maths_check.py picture_checks -> reasons 'ms_screenshot' (a raster image in a mark-scheme cell,
    >= 50 x 35 pt, no ms_graphs spec), 'ms_faint' (ink mostly light grey, not shading), 'fig_faint' (question picture
    with curves / slanted lines whose ink is light; empty answer grids and tables are never flagged). ms_graphs.KEPT holds
    the pictures he decided to keep as printed. Found at once: 3 faint graphs (2018 ON 41 q3(a), 2018 ON 61 q7(b)(ii),
    2023 MJ 62 q6(b)(iii)) - redrawn. Open: 47 screenshots in M2/M3 (tables, grid shapes, dot patterns, pie charts,
    hand sketches, data plots) and 131 in the other 0607 batches - his decision.

## Picture batch RD2 (2026-11-24): every flagged blurry MS picture of all 0607 batches (M0-M3) drawn again
271. 181 flagged pictures in 149 questions (maths_check picture_checks: 179 ms_screenshot + 2 ms_faint, no fig_faint): 107 graphs,
    19 shapes on grids, 14 Venns, 11 data plots / bar charts, 10 tables, 9 dot patterns, 3 trees, 2 pie charts, 2 mapping
    diagrams, 4 sketches. 180 redrawn with ms_graphs.SPECS, 1 kept (ms_graphs.KEPT: 2025 FM 62 10(a), a student's own
    triangle sketch - Dhruv decides in round 39). New drawers: 'table' (rows, '*' bold answer, '~' grey given value, '_'
    italic, 'span' merged header, 'nohl' no rule under a merged cell, 'noframe'/'hlines'/'vlines' for stem-and-leaf,
    numbers split by 3 spaces drawn as separate texts), 'plane' / 'panels' (squared paper, dotty paper 'dots', triangle
    lattice 'iso' and turned 'isov', axes, polygons with fill/dash, unit cells, circles, angle arcs, crosses, text; panels side
    by side with 'seps' or 'stack' one above the other with OR), 'pie', 'map', 'graphs' (two graphs stacked in one cell),
    'alts' (several screenshots under one label: the k-th picture of the label takes alts[k], per column), 'smooth' (a
    monotone curve through data points: cumulative frequency) and 'dots' (points as dots, not crosses). maths_check reads some
    labels as a number in the cell ('48', '0', '3', '10'): those specs are copied under that key too.
    Fitted curves where the question gives a sketch and no formula (2022 MJ 41 9(b)(i) j(x), 2024 MJ 31 7(d) f(x)): round 39
    calibration items.
272. The redraw replaced the WHOLE picture cluster: a quadratic-formula line printed under a screenshot whose fraction bar and
    root sign joined the cluster vanished (2024 ON 61 2(d)). -> ms_maths: the drawing replaces the pasted image's box only;
    text, lines and glyphs outside it are laid out under the drawing. Look-alike scan: rows changed outside the spec'd labels
    = 3 (all the redraw rows themselves).
273. Graph drawer details found side by side: y numbers wider than 22 pt ('146000', '1.2585') spilled out of the cell (left
    room now from the widest number); curves ran through tick numbers (white ground under each); '–1' printed twice at the
    origin of x0 = y0 = -1 windows (the y one dropped); function labels placed over an axis (axes sampled as points to keep
    clear); dense x ticks over a curve -> 'xlow'. Text in tables / Venns as separate tokens: an SVG text with several spaces
    collapses them and stretches to its width (pattern 265 again).
Repeat check: pattern 264's rule 'grep failed after every SPECS edit' caught one broken spec (a comment pasted into a line).
274. Graph look not matched to the printed screenshot (Dhruv round 39: 'don't change grid from original'). A grid, a square
    versus wide aspect and small tick numbers were chosen by eye. Now measured on the printed screenshot (grid line spacing,
    major lines, aspect) and stored per graph in ms_graphs.RD2_LOOK (ar, grid, gmaj, ts); no grid when the original has none.
    Where the printed grid is too faint to count, the graph is listed in RD2_GRID_UNSURE and shown to Dhruv for a yes/no.
275. Dot paper cut as half a picture (Dhruv round 39, 2025 FM 52 q2): extract.diagrams() only knew square dot paper
    (>= 40 round dots on a grid). Triangle paper (every other row moved half a step, 4.8 pt dots, 12-90 dots) was not a lattice,
    so the shaded shape was cut as a picture while the dots around it stayed dots. A TRIANGLE lattice rule now exists (one dot
    size, same step along every row, rows moved half a step, 3+ rows) - shapes on it stay drawn with the dots. Blast radius
    (fig_blast, 336 papers): only 2022 ON 51, 2024 ON 51 and 2024 ON 61 (house of cards / trapezium dot paper, ~20 figures) would
    change on a later re-extract; they are approved and NOT rebuilt now - look at them side by side before they are.
276. Row growth counted twice under a taller drawing (2022 MJ 33 q3, 'empty space below the cell'): the cell height now
    shrinks to the drawing's real bottom and the later rows are shifted once (ms_maths pic_bots).

## Chemistry 0620 - analysis and pilot C0 set-up (2026-11-25)
277. A third subject would have taken the MATHS path: 12 places decided 'maths' as 'syllabus != 0625' / 'not is_physics' /
    '/0607/' in the path (layout, ms, store_text, store_units, render, checks, ms_layout, review_round, ms_align, ms_sweep,
    extract.paper_meta). -> all ask `subjects.is_maths()` / `maths_path()`; chemistry-only code asks `subjects.is_chem()`.
    Never write 'not physics' for maths again. Proof: golden 0 changed cuts, nothing tracked under 0625 changed, ms_rebuild
    over all 23 maths sessions = 0 changed questions.
278. Chemistry 2002-2009 is stored only as one-digit names (qp_1, ms_5); the pipeline needs qp_01 (old = pv starts with 0).
    -> session_papers prints 0620/2005-MJ/01 (non-physics only); raw_store.fetch fetches the one-digit original for it and
    writes the qp_01 copy with old_papers.main(syl) (now syllabus-aware). Combined files (ms_1-2-3-5-6, 2003-2004) are NOT
    split yet - batch C8.
279. Periodic Table (last page of MCQ / theory papers) and 'Notes for use in qualitative analysis' (practical papers, 1-2
    pages) are no questions. -> extract.data_page_kind (chemistry only: >= 60 element names / the notes headings): skipped like
    a blank page, meta.data_sheet; store writes each DIFFERENT sheet once to store/.../0620-chemistry/data_sheets/ (keyed by its
    text, ~1 MB SVG) and paper.json points to it (Dhruv D3). Coverage counts it.

## Chemistry C0 pass 1 (2026-11-25, GitHub run 45545804757: 56 papers, 2242 reasons, 50 papers exact totals at once)
280. (tool) ms_align read chemistry labels only at y == 14.0; they sit at 13.96-13.98 (as maths, pattern 164): 151 false
    hits. -> chemistry uses the top Q-column word like maths. 23 questions left (Cambridge label slips / practical rows).
281. MS label slip at another LEVEL: '8(c)(iii)' printed for the paper's 8(d) (2024 MJ 33). -> run.py (chemistry): the one
    orphan row goes to the one free part when it follows the rows of the part just before it.
282. Guidance tables (2015, 2026 MJ): a row whose Guidance cell is empty was cut at the Marks|Guidance rule (_tighten took the
    FIRST rule right of the text) and kept 'as printed' with 3 columns: frames of different widths, marks drifting. ->
    chemistry: the OUTER border (ms_layout._tighten, MP.CHEM). Physics 2026 may have the same: PHYSICS_LATER.
283. 2015 covers print only 'Paper 2' (no 'Core'): paper 2 read as MCQ (marks 7/40, 'answer key not found'); 2015 ATP total
    60 (MS 'maximum raw mark 60') taken as the standard 40. -> chemistry < 2016 uses the old numbering; chemistry reads
    'MAXIMUM (RAW) MARK' from the MS in any year when the cover has no total.
284. 2024 MJ 41: Q1's table starts under a notes paragraph on MS page 5 -> no mark scheme for Q1/Q2. -> the maths rule
    'a table can start lower on a page' now also for chemistry (ms._table_area).
285. Displayed formulae in MCQ / theory figures lost their END atom ('H—' / '—H'): the letter overlaps the crop by <= 15 %, so
    it was neither 'half inside' nor 'near' (needs 0 overlap). -> fit_crop(chem=True): the maths 'just touching' clause.
    Blast: 12 of 459 C0 figures grow ~6 pt (one atom), all the target class.
286. Displayed formulae INSIDE mark-scheme cells (2015 / 2024 / 2026: ~41 questions in C0): atom letters are filled glyph
    outlines and bonds thin lines (or straight lines with EMPTY boxes - pattern 96 again), laid out piece by piece: letters
    squeezed, words over the drawing, whole formulae lost. -> store._chem_structures (chemistry MS): a cluster of >= 4
    letter shapes (or >= 2 + bonds, 5+ pieces, <= 17 pt apart) = ONE vector picture (figures/msfml_*.svg, an 'image' the
    layout moves whole). Open: a cell with a structure + a long line beside it falls to the 'cell' layout and is shrunk
    (2026 MJ 41 7(c)(iii) Answer) - counted in pass 2.
    2024 MS draws the atom letters as tiny pasted IMAGES (like maths 258): they count as letter shapes too.
287. 2015 MS page 9 continues the table with NO header row: the page was skipped (2015 MJ 21: 6(b) and all of Q7 had no mark
    scheme; found in pass 2 once paper 2 was read as theory). -> chemistry: a page with labels and no header row starts its
    table under the page header box ('Page 9 | Mark Scheme | Syllabus | Paper'). Blast over all C0 MS: only 2015 21 (+ 284).
288. A band holding pictures was never re-wrapped (`pure = not PP`) and was SHRUNK to fit (25 rows / 23 C0 questions with a
    displayed formula + a long line, e.g. 2026 MJ 41 7(c)(iii)): Dhruv's rule is normal size always. -> chemistry: pictures
    on lines of their own let the text re-wrap; each picture moves down with the lines above it (ms_layout pic_own).
289. Practical MS (2026 MJ 51/52) numbers marking points 1(a)(i)-(iv) under a part the paper does not split: rows matched no
    part. -> chemistry: a row one level below an existing LEAF part belongs to that part (run.py).
Known (C0, all <= 3 questions, written down under the budget rule): MCQ question line / statements inside the options-table
picture (2026 MJ 12 q3, 2015 MJ 11 q1); extra marking points (iii)/(iv) under a split part stay on the parent (2026 MJ 51 q2,
52 q1, 52 q2); Cambridge label slips '2(b)' twice / '1(f)' twice / extra '6(f)' (2024 MJ 33 q2, 52 q1, 32 q6); editable text
93-97 % where labels sit inside pictures (5 questions).

## Chemistry C0 round 41 fixes (2026-11-26; Dhruv: 2 ok, 5 wrong + his notes)
290. (round 41, 2024 MJ 61 Table 2.1) Thermometer scales drawn inside table cells were loose lines in the layout. Dhruv:
    'table and images individual inside respective cell'. -> chemistry questions: a drawing closed in by table rules on all
    four sides (>= 6 strokes, >= 8 x 20 pt) + its scale numbers = ONE picture in its cell (store._chem_cell_pictures); the
    table text stays text.
291. (round 41, 2005 MJ 03 q4 'dots are missing') 2005 answer dots are rows of 3 x 1 pt pictures; only maths turned them
    into dots. -> the maths rule now also for chemistry.
292. (round 41, 2015 MJ 21 7(a) 'empty space') a re-wrapped row = printed height + extra lines, so the print's empty band
    under the content stayed. -> chemistry: ms_portrait._trim_bottom (content + 7 pt).
293. (Dhruv: 'no standard proportion in column') column widths followed each print (Q 40-47, Answer/Guidance 259-325).
    -> chemistry: ONE standard: 3 columns Q 47 | Answer 436 | Marks 40; 4 columns Q 47 | Answer 218 | Marks 40 | Guidance 218
    (equal text columns: Guidance at 37 % made 2026 cells very tall); slivers at the table edge stay slivers (a sliver
    widened to 40 pt became a phantom 5th column and sent every row to the cell fallback - caught by eye at once).
294. (found while checking) old MS: a subscript at a line end ('V2O5', 2005 4(c)(i)) went into the Marks column. -> a
    small token touching the word before it is never a mark (chemistry).
295. (found by a NEW check: Marks column total vs question marks) 2005 MJ 03: every '[1]' dropped as a 'part total' (a rule
    for papers that print codes) -> empty Marks column. -> chemistry: part totals only when codes exist. The mark-sum
    check (/tmp/msum.py idea) belongs in reasons pass 1 for chemistry - add it.
296. old MS notes 'N.B. a total of [3] not [2]' lost 'total' and the numbers; a stray '=' of 'TOTAL = 16' stayed. ->
    chemistry: 'total of' is text; the '=' goes with the printed total.
297. (round 41 decision 2015 MJ 33 7(b)(i): 'yes but properly like that') faint pasted structure pictures are redrawn by
    hand as vector SVG: pipeline/chem_redraw/<paper>_<picture>.svg replaces the picture of that name at build.
298. text just under a picture (0.5 pt overlap) counted as 'beside it' -> the row shrank (cell fallback). -> chemistry: 2 pt.
299. (open item) 2026 MJ 23 q36 MCQ option pictures each held two rows: fit_crop growth (my 285 end-atom rule and the
    half-inside rule) pulled the next option's atoms in. -> chemistry option pictures keep diagram_options' exact cut.
300. (open item) MCQ question line / statements inside the options-table picture (2026 MJ 12 q3, 2015 MJ 11 q1). ->
    chemistry: sentences at the top of a figure box above its first drawn ink are text (store._chem_trim_prose); 12 q3's
    options are now read as text options.
301. (open item) MS label slips with one row per part ('2(b)' twice for 2(b)/2(f); '6(e)(ii)' '6(f)' for 6(d)(ii) 6(e);
    '1(f)' twice): chemistry maps rows to parts in order when the counts match and every good label is in place.
302. (open item) 2026 practical MS: one row per marking point, numbered (i), (ii), (iii) while the part's points run M1 M2
    M3. -> chemistry: group rows by M-number (a new part at M1 or no M; '+ M2' after a charge counts), map groups to parts
    in order when the count and every part's marks match.
303. (round 42, 2026 MJ 12 q3: 'no need for image, simple table and text and atom notation') a table whose header and
    atom notation are drawn letter outlines (no text layer) was cut as cell pictures. -> chemistry: filled letter-sized
    outlines are never drawing pieces (store._chem_cell_pictures, store_options CHEM_LETTERS); prose is trimmed before the
    option grid; drawn text is typed once in pipeline/chem_drawn_text.json (paper, page, box, tokens).
304. (round 42, 2026 MJ 61 q2: 'number beside thermometer should be part of image') thermometer tube walls are 82 pt thin
    lines, so they were taken as table rules and that cell's picture fell apart. -> thin lines up to 90 pt also count as
    drawing pieces (they stay rules too); all thermometer/syringe/cylinder cells of C0 are pictures with their scale numbers.
305. (round 42, 2026 MJ 52 q1: 'check by yourself') the MS rows were mapped right (301/302) but the Q column still showed
    the print's slips ('1(a)(i)'... for an unsplit (a), '1b(i)', '1(e)' for (e)(i)). -> chemistry: a remapped row shows the
    question paper's label (run.py sets the label; ms_layout rewrites the Q cell, centred, shrunk to fit).
306. MS tree not the question's shape (Dhruv round 40: 'whenever a tree comes, the MS matches the question's structure'). Five trees
    were drawn with fixed proportions; two had hand-typed geometry. Now EVERY tree spec carries the question's geometry, measured
    with pipeline/tree_geom.py (branch ends, rises, and how far each second tree sits further out than its first branch end -
    2023 MJ 32 11(a): 38 pt); ms_graphs asserts no tree without it. Decimals placed clear of the branch like fractions.
307. Row did not grow under a moved text (Dhruv round 40, 2024 ON 61 5(c) 'last cell overflowing - why?'): a graph drawn taller
    than the printed one moves the text under it down; the row's bottom for that text had the same value as the graph's own
    bottom, which the round-39 rule never moves twice - so the row ended above the text. Now the row ends under its lowest text
    when that text runs past it. Also fixed 8 approved rows where text was cut by the line under it (2024 FM 62 8(f), 2025 ON 63
    4(d), 2026 MJ 41 17, ...).
308. Sub-row rules dropped in a row with a cell across all columns (2025 ON 62 2(e), 'layout messed up'): the extra column entry
    of the merged cell paired the printed right border with x 44, so every full-width rule was thrown away; where kept it was
    drawn twice beside the note band's own rule. Edges now pair with the real columns only; a sub-row rule next to a rule the row
    draws itself is dropped. Rules came back in 2021 MJ 62 q5 / q9, 2023 FM 52 q4, 2025 ON 63 q4. Small sketches drawn 110 pt
    tall grew the row (2025 ON 62 2(d)): drawn at their printed height. Open: the small table in 2(d) Partial Marks has no right
    border (lost when the row is read; a 10 pt edge rule changed 60+ papers, so not done).
309. Dot paper cut as a partial picture (Dhruv round 40: 'it should be whole as a image, partial image is very bad idea in que and
    ms'; replaces pattern 275's 'keep as dots'). Each connected PATCH of triangle dot paper (dots at most 1.25 diagonal steps apart;
    text between patches splits them) is ONE picture with the shapes on it, empty answer grids too. Unless whole pictures already
    cover >= 80 % of the dots (house-of-cards patterns 2024 ON 51/61 unchanged). Dots printed twice counted once. fig_blast: 2025 FM
    52 q2, 2021 MJ 52 q5, 2022 ON 51 q1/q2/q4/q5/q6, 2022 ON 61 q2/q3/q4 - all looked at, all whole now; rebuilt with run.py.
    Open: 2022 ON 51 5(a)'s empty grid is not shown (was missing before too).
310. Tree placed against the top of its cell / decimals not at the branch middle (Dhruv round 43, 2019 ON 31, 2023 MJ 32/33):
    every geometry tree is centred in its cell (same space above as the cell keeps below, centred left-right), and a decimal
    sits over the MIDDLE of an upper branch / under the middle of a lower one, clear of the line - like 0.8 in the question.
    A picture cell is now always as tall as its drawing (a tree's last label ran out of its cell; 5 tables gained ~1 pt).
311. Native MS table too crowded (Dhruv round 43, 2021 MJ 62 5(a)(i) coordinates): a 'vector' table spec in ms_graphs now
    redraws a plain table too (the table branch of layout_row; before, only picture cells looked at specs); the row is as tall
    as the drawn table. 2025 ON 62 2(d): a table that lost its right border when read is closed for that row only
    (ms_graphs.CLOSE_TABLES) - the general fix changed 60+ papers. 2023 MJ 63 q4: the top '2' moved off the line QP.
312. Fractions on a tree not at the branch middle (Dhruv round 44: 'above the middle of the edge, like I said'): pattern 310 moved
    only decimals. Every probability on a geometry tree - fraction or decimal - is now centred over the middle of an upper branch
    / under the middle of a lower one, clear of the line at both ends. A tree cell keeps 5 pt under the tree (it touched the
    bottom edge, 2023 MJ 33). 2023 MJ 63 q4: the bottom-right '3' centred in its rectangle. Lesson: when Dhruv names a rule for one
    kind of label, apply it to every label of that drawing.

## Chemistry C1 pass 1 (2026-11-27, GitHub run 45959753924: 70 papers, 83 reasons - the C0 classes held)
313. MS page that continues the table with NO header row and has a new question's 'Question | Answer | Marks' header LOWER on
    the page (2025 ON 33 p9 / p12): the table was read from that lower header only - 4(e)(ii)-4(h) and 7(f) had no mark
    scheme. -> chemistry (ms._table_area): labels above the lower header -> the table starts under the page header text.
    Blast over C0 + C1 MS: only these 2 pages.
314. Label '(a)(ii)' printed without its question number on the SAME page as '2(a)(i)' (2025 MJ 33 q2) was dropped (the
    rule needed rows from an earlier page). -> the maths rule (pattern 243) now also for chemistry.
315. (repeat of 285, too narrow) the end atom 'H' of a displayed formula lying 10-17 pt OUTSIDE the crop became question text
    and drifted away from its bond in the layout (2025 ON 23 q37 'H  -C', 2025 FM 12 q10 'O.   H'). -> chemistry fit_crop: a
    lone atom symbol level with the drawing, <= 22 pt from the crop, is taken in when ink (a bond) runs from it towards the
    crop (pixel test: some bonds are not reported by get_drawings). An option letter 'C' beside a chain has a gap and stays
    out (2024 ON 23 q37 caught by the blast). Blast (all C0 + C1 figures, 1216): exactly the 2 targets.
    NOTE: fig_blast.py does not see MCQ figures (extract gives them none) - use a bank/ json harness for MCQ crops.
316. A picture under a line that the re-wrap breaks into two did not move down (2025 ON 63 1(e): 2nd line under the
    tube picture). The beside test lets a line 2 pt above the picture through, cum_above wanted 2.5 pt. -> chemistry 0.5.
317. MS row cut at the last TEXT line: a displayed formula drawn under it (vector strokes) was cut off (2025 ON 43 6(d)(iv),
    2026 FM 42 6(c) - structure missing entirely, 2025 MJ 31 4(c)). -> chemistry: small strokes inside the Answer cell (no
    rules: <= 80 pt, not both sides > 40) count for the row bottom, as maths drawings do. First try (all drawings) moved
    3600 rows - narrowed to strokes: 13 rows, all checked.
318. A 6 pt stub of the Answer column's rule (the rule is drawn in two pieces) was read as a bond and pulled into the
    structure picture: a stray vertical line left of the formula (2025 ON 43 6(e)(i)). -> rule pieces in line with a long rule
    they touch are no bonds (_chem_structures). Blast: 1 picture.
319. A long Answer line kept by the cell / table fallback (or a line the re-wrap could not break) ran over the Marks /
    Guidance column: words over the mark, words lost past the page edge (2025 MJ 53 1(a), 2025 MJ 63 2(a); C0 approved:
    2015 MJ 32 3(b)(i), 2015 MJ 21 q6). Found by a new text-overlap check (/home/claude/tools idea: pairs of words of one row
    overlapping). -> chemistry ms_layout._wrap_overrun: an Answer line = a run of words in reading order (other columns'
    words on the same line skipped); its words past the column go to a new line, the Answer column below moves down.
    Known (C0, 2 questions, 4 attempts - budget rule): 2026 MJ 41 4(c)(i) (bulleted lines in a table fallback row still
    overlap the Guidance column) and 2026 MJ 63 2(a) ('temperature / °C' over two narrowed table columns overlaps itself).
Known (C1, budget rule, no text lost): polymer chains' open left bond shows as a short stub (2024 ON 21 q38, 22 q36, 22 q37);
2025 ON 23 q36 options 'A 1 and 3 ...' inside the structures picture (pattern 300 class).
Hint check (pattern 295, now in pass 1 as ms_marksum): 9 hits in C1, 2 real (313), 7 Cambridge slips / Guidance rows.

## M4 (2014 ON - 2017 ON, 124 papers - 2026-11-27), GitHub pass 1: 623 reasons
320. 2015-2016 maths MS print the labels apart in the Q column ('1' | '(a) (i)' on one row, '(ii)' alone below): the table
    parser lost every lone roman (its rows went into the row above: ~200 rows, 44 hits in 2016 MJ alone), read '(i)' / '(v)'
    as LETTERS ('3(i)', '6(v)'), missed the number when '(a) (i)' sat 0.3 pt above it, read 'Part Marks' (2015-2017 header) as
    no header (numbers of fractions in that column counted as marks: 2017 MJ 61 marks 118/40), and paper 6 part B numbering
    from 1 again went into part A's questions. -> ms.structured_rows_table (maths): ROMAN1 labels join the current letter;
    labels on one row merge; 'Part Marks' = Partial Marks column; part B after its 'B MODELLING' heading continues our
    numbering (never after the 'Communication' criteria lines that name earlier parts). Blast: all 460 approved maths MS
    unchanged (labels + segments); only 2020 ON 11 q20/q21 lose 2 Part-Marks numbers from their stored codes (not used).
321. A maths table that runs on to pages with NO header row (2015 MJ 31 p3-5): 10 questions had no mark scheme. -> _table_area
    (maths): such a page starts under its page-header box when a question number sits in the Q column (chemistry 287 too).
322. Old column-format MS (2014 ON, 2015 MJ): romans are printed RIGHT-aligned - '(iii)' 6 pt left of '(i)' - so (ii)/(iii)
    fell outside the roman column (2014 ON 42, 2015 MJ 42: rows lost); a page whose column rules are hidden by drawn grids
    had no marks column (2014 ON 51-53: marks 10/24). -> _label_columns: the roman column starts at the leftmost (ii)/(iii);
    _maths_rules falls back to the scheme's most common rule set.
323. Question side, paper 6 2015-2017: the 'B MODELLING' heading on a page of its own before part B's '1': part B was not
    found at all (2016 ON 61: 7 of 11 questions; 2015 MJ 62, 2016 ON 63, 2017 ON 62). -> extract.boundaries carries the
    heading to the next page. Blast: only those 4 M4 papers change.
324. fit_crop (maths): (a) a tree's answer slot '.........' under its LAST branch was left out (the other slots were in):
    2015 ON 31-33 q10, 2015 ON 43 q10 (2 trees), 2016 ON 31 q8; (b) number labels of a drawing ('1' over a circle of points,
    '4' beside a box, the top '6' of a tree) were dropped as 'question numbers'. -> a dots-only line next to a crop that holds
    other dot slots, and a 1-2 digit line inside the drawing's span away from the margin (not in a ruled cell), are taken in.
    store.FIT_M4 toggles them. fig_blast (460 papers): 43 crops grow, all looked at - all gain a missing label / heading /
    slot. 6 are APPROVED (2014 MJ 21 q8, 2014 MJ 32 q9, 2018 MJ 31 q8, 2022 ON 51 q2, 2023 ON 62 q2 clock numerals, 2025 MJ
    61 q2): not rebuilt now - they improve at their next rebuild (re-show then).
325. New equation-font codes: MMEtc 'Q' = ∅ (2015 MJ 23), MMaFermat-Regular 'Q' = ℚ (2017 MJ 32) -> MATHS_GLYPHS.
326. KNOWN (1 question each): α of a nameless subset (2014 ON 22 q5) and π (2015 MJ 12 q12) drawn in sans.
327. KNOWN (crop fragments, 1 question each): formula sentence under the triangle (2014 ON 63 q2), captions twice + 'r.'
    (2015 ON 62 q2), a vector bracket piece over a grid (2016 MJ 33 q7), the 2nd camera diagram cut beside its text
    (2015 ON 63 q5). Pre-existing, found by the blast: approved 2021 FM 42 q4(b)(i) 'Table 1' crop starts at its 2nd row.

## Chemistry C1 round 45 (Dhruv, 2026-11-27: 10 items, 3 wrong)
320. (Dhruv, wrong calibration) a part whose mark scheme prints NO mark number (2025 FM 42 5(d)(iii) M1-M3) - I passed it
    'as printed'; Dhruv: take the question paper's [n]. -> chemistry ms_layout: a row with no mark code, whose label (and
    sub-parts) have no mark anywhere, gets the QP part's marks in the Marks column. Blast C0 + C1: 7 rows (6 in 2026 MJ).
    Rule for passing: an EMPTY Marks cell is never 'as printed' - the QP has the marks.
321. (Dhruv) a Guidance paragraph was not level with the Answer line it was printed beside once the Answer re-wrapped
    (2015 MJ 32 3(a): 'A if electron configuration ...' beside M3 sat a line higher). Each column counted only its own
    added lines. -> chemistry ms_portrait: Guidance paragraphs take the Answer column's added lines (the Answer column, the
    first flexible one, leads; a paragraph only ever moves down). 56 approved C0 questions (2015 MJ, 2026 MJ: the Guidance
    papers) changed - sampled 12 + 3 targets, all level; no new overlaps.
319 (repeat, 2 faults in my own fix). (a) The row grew by a full line though the cell had room under its text (2015 MJ 21
    6(a)(iv), Dhruv). -> grow only by what the text needs. (b) Paths written with H/V commands: V (a y value) was not moved,
    so the stop-clock answer boxes of 2025 MJ 63 2(a) became black bars - pushed in pass 2 and NOT seen in my check (I looked
    at the 53 twin only). -> V moves like L, a thin rule moves as one piece; new check: filled black shapes > 4x4 pt in a
    mark scheme (/home/claude/tools idea, 2 hits = bond strokes) - look at EVERY question a layout fix changes, not one twin.

(Numbers 320 and 321 are used twice: maths M4 320-327 above were pushed first, chemistry C1 320/321 here - read each with its subject.)

328. Blurry / faint MS pictures of M4 redrawn in the batch (ms_graphs.SPECS, 27): 14 graphs from the questions' functions and
    axes ('ar' = printed shape; gridded ones listed in RD2_GRID_UNSURE), a cumulative-frequency curve, a bar chart, 4 Venns, 4
    tables (answers bold, given values grey), 3 stars on numbered dot circles (new helper ms_graphs._ring), a crosses grid.
    KEPT for Dhruv: 2015 ON 42 15(a)/(b) (candidate's own graphs, no window in the question), 2015 ON 61 5(a) (3 fitted
    model curves told apart by colour).
329. Papers 5/6 marks from the MS (2015-2017): pass 2 still had 11 wrong totals - marks printed '1FT' / 'FT1' / '1dep' /
    'M1FT' / 'DM1' were not codes; an 'Alternative method' block counted its marks twice (2017 MJ 61 7(b)); the Partial
    Marks column was not found on pages whose header sits under a title or that have no header (fraction numbers counted);
    'Communication in 2 from ...' printed in the Answer column (or across the Q column) was no communication row; the C mark
    printed beside a criteria line was lost (2015 MJ 61). -> ms.py (maths) code regexes, Answer-column 'Alternative method'
    cut-off, PX from the 'Mark' heading's rule and kept across pages, COMMX labels, fold_communication takes the C mark.
    All 142 papers of 2014-2017 exact. Lesson: check papers-5/6 totals LOCALLY before the GitHub pass (cost ~25 min).
330. (my own, caught by the final blast) Pattern 321's 'table on a page without header' also fired on the 2018+ 'Maths-Specific
    Marking Principles' page (numbered notes 1-6 inside a frame): every 2018-2026 maths MS got rows 1..6 and lost its codes. It
    was in the pushed pass-1 code; approved papers were NOT rebuilt with it (stored data intact), M4 rebuilt locally after the
    fix. -> needs >= 4 column rules (a ruled table). Blast after the fix: all 460 approved maths MS have identical labels and
    cuts; only stored codes change ('(C1)' of Partial Marks dropped, '1FT'/'1dep' read) - none feeds an approved paper's marks.
    Lesson: run the full MS blast after EVERY ms.py change before a push, not only after the first one.
331. MS labels printed on ONE text line with the answer ('(a) (i) Correct graph', 2015 ON 42 - q7/q13 rows were '7', '13(iii)'),
    letter + roman pairs on one row in either x/y order ('(c)' and '(i)' 0.3 pt apart), and Cambridge's 'number going back' slip
    ('10(b)', '10(c)(i)', '10(c)(ii)' printed after 11(a) for 11(b), 11(c)(i), 11(c)(ii): 2017 ON 43). -> ms.py (maths): the label
    part of such a line is the words left of the Q column edge; one-row pairs merge left to right; a label one question back
    inside the next question (not after a Communication row) takes the current number. MS_RELABEL may hold syllabus-keyed
    entries ('0607_...', looked up first). A table running on with '(b) (i)' and no number on a header-less page (2016 ON 31)
    starts under the page header (321 extended; still only on a ruled table page). Blast: approved maths MS labels/cuts identical.
332. Question side: romans printed further right under a diagram (x 112-119, 2015 MJ 43 9(a)(i)-(iii)) were no labels ->
    layout.label_tokens accepts romans up to x 122 on maths pages. Boundary blast over all 460 maths QPs: only that paper changes.
333. 2017 MJ Venns (22 q9(a), 32 3(g), 33 10(c), 43 9(g)) are thousands of 1-pt image tiles painted OVER a hidden '.....' text
    layer: redrawing them from a spec replaced only the tiles and showed the hidden dots as a dark band. -> specs removed, kept as
    the printed picture (clear enough) in ms_graphs.KEPT for Dhruv's decision; a spec redraw now drops dots-only text inside its
    drawing area.
334. 2014 ON 51-53 (paper 5): the ruled table is narrower than our unit, so its outer borders counted as inner rules (5, not 3)
    and _maths_ruled gave up (old layout with stray braces). -> outer pair dropped when there are 5. q1, q5, q6 right now; KNOWN:
    q2 (3 columns, 'wrap'), q3 (3(b)(i) misaligned), q4 (cube-drawing table, old layout) - paper 5 of 2014 ON kept PENDING.
    FIXED 2026-11-28 by 347 (all 6 questions now take the maths layout).
335. KNOWN small leftovers (budget rule): 2017 MJ 42 q7/q8 Partial Marks shrunk (scale fallback); 2015 MJ 43 5(b)/11(d) the
    wrapped last Partial-Marks line pushed under a redrawn graph (pic_grow moves other columns' text below the printed picture's
    bottom - needs a 'continuation of a paragraph' test); 2016 MJ 41 13(b)'s answer printed with no label (under 13(a)(iii));
    picture edges (ms_piccut) 2014 ON 42 q4, 2014 ON 62 q3, 2015 ON 42 q15.

## Round 46 (Dhruv, M4 review: 8 wrong) + M4 final check
336. MS rows cut short by image tiles: hair-thin image strips (min side < 5 pt, the 2015 ON 31-33 q10 tree, 8(a) Venn) counted
    as 'ink' for the row edge, so 10(a) ended at its first line and the tree fell into 10(b). -> ms._lift ignores tiles < 5 pt.
    Blast over 460 maths MS: 8 MS change; approved 2018 MJ 33 8(b) and 2020 MJ 31 11(a) move 2 pt onto the row rule (better).
    Rows that are now whole showed tile pictures badly: redrawn from specs (2015 ON 31-33 8(a) Venn and q10 tree).
337. Paper 5/6 task MS: the Q column width came from each question's own labels, so one task's rows had different widths
    (2016 MJ 62 B). -> ms_maths: papers 5/6 take the widest label of the whole paper.
338. Intro pictures of paper 5/6 tasks (the chequered flag of 2017 ON 63 A, stars, clocks, graphs ... ~105 intros) were drawn
    in the print layout only, never figures: the task had 2 figures where 3 are printed and the app content had no picture
    (Dhruv: 'there should be 3 images'). -> extract.maths_paper_parts finds intro diagrams (extract.diagrams), pieces side by
    side joined (the 2024 MJ 52/62 tree), pieces inside a sentence dropped (circled 'Corner (1)', one row of a step table);
    store.paper_record saves them as figures `<paper>_t<S>_diagramN` and lays the intro out around them (its LaTeX check now
    passes where the drawing was read as a 'table'); tasks.py puts them first in the task's figures. KNOWN: 2018 ON 62 A's
    spiral grid (dashed zero-width lines) is still not found - it stays in the print layout only.
339. Duplicate paper 5/6 tasks (2016 ON 53 = 52): built before store.dupes made the questions stubs, so they pointed at figures
    that were then removed (19 broken links; HEAD had a 1-part empty shell instead). -> a task whose questions are all stubs of
    one paper is a stub `same_as` that paper's task; store.dupes rebuilds tasks after it.
340. Store build failed for 5 maths papers (2014 MJ 31/33, 2015 ON 23, 2016 MJ 42, 2017 ON 21: in HEAD, store stopped at the
    question before): MuPDF 'Cannot create unique resource name' redacting text on a page of ~30 000 image tiles. ->
    store._notext falls back to cutting the BT..ET text objects out of the page content. Lesson: 'store build failed' in
    review/queue.json must stop an approval - check it every batch.
341. MS pictures built from 1-3 pt image tiles lost their letters / arrow (2016 MJ 21 7(a) Venn F, M, E, U; 2016 ON 31 10(b)
    number line): redrawn from specs (venn; plane with an open circle + arrow). Marker size: spec 'cross' / 'cross_sw' (2016 MJ
    31 12(d): crosses on the axis or under the curve read as lines, Dhruv 'make marking consistent').

## Chemistry C2a pass 1 (2026-11-28, GitHub run 46141426546: 58 papers, 51 reasons in 45 questions - 8 min build)
342. Cambridge MS label TYPOS '7(c)iii)' (2022 ON 33), '4(f)(iii)i' (2023 MJ 42), '4biv' (2023 ON 42) were no labels: the row
    merged into the row above it, the part had 'no mark scheme'. -> ms.label_text (chemistry only, `_CHEM_LABELS` set by
    structured_rows_table): add the missing '(', bracket an unbracketed letter + roman, drop a doubled last roman letter.
343. A label printed TWICE where the FIRST copy is the slip ('2(e)(iii)' for 2(e)(ii) and again for 2(e)(iii), 2023 ON 63): rule
    301 needed every other row in place. -> run.py (chemistry): a row whose label is printed twice may be remapped by order when
    its marks equal the part's marks.
344. 'Cl2' / 'PCl5' / 'Cl-' in mark-scheme rows shown 'C 2l', 'PC 5l', 'C -l' (42 questions, approved C0/C1 included - missed
    in C0/C1 because sheets are read at a size where 'Cl2' and 'C2l' look alike): Cambridge prints the l of Cl in Bookman italic,
    3 pt wide; ms_portrait._groups gave the subscript to the FIRST word whose span (+4 pt) reached it ('C'), and the re-wrap
    pushed the 'l' behind the C2 group. -> chemistry: the NEAREST word before it. 41 stored questions re-laid out (ms_rebuild
    --write, every change carries the 'l'; 3 + 3 targets looked at); scan tool /home/claude/tools/cl_scan.py = 0 left.
    Lesson: zoom chemical formulae (2x) on every sheet - a letter order slip does not show at sheet size.
345. End atoms 'H' / 'OH' of displayed formulae and key words ('paracetamo|l') cut IN HALF by the figure crop's left/right edge
    (15 C2a figures; the 'text line half inside' check found them): the atom row is one long text line, so the line rules of
    fit_crop never took the single letter in. -> store.fit_crop (chemistry, toggle FIT_EDGE_WORDS): a word crossing the left
    or right edge with >= 1 pt inside and its centre level with the crop is taken in (sideways only - never up/down, 299).
    Blast (all 0620 figures in bank/, MCQ included): 68 crops grow, ~1.3 pt each (4 by 12-16 pt: a cut 'OH'); a word only
    touching the edge ('as', 2024 FM 22 q4) is not taken. Approved C0/C1 figures (53) improve at their next rebuild.
346. Editable text 'BaCl 2(s)', 'KCl (s)', 'Cl -(aq)' (~200 spots in all chemistry): Cambridge prints a 1.5 pt kerning space
    (a 5.5-7.8 pt space glyph) after the Bookman 'l'; the editable joiner made it a word space. -> editable (chemistry, CHEM set
    by build): no space after the Bookman / italic 'l' when the gap is < 2.5 pt (line joiner and tok_html); a THIN SPACE
    (U+2009) glued to the next letter right after the l ('Al\u2009F3', 'KCl\u2009(aq)') is dropped in spans_in. (A first
    try that stripped any leading space ate real ones: 'C2H5Cl+ HCl', 'H-Clbond' - caught by reading every hit.) Approved
    papers improve at their next rebuild.
297 (repeat). 2023 ON 43 6(e)(ii): hand-drawn scan structures (grey paper, a black bar) - redrawn as vector in chem_redraw.
Checked and passed: ms_marksum hits (rows add up; several M-rows per part), checks.text 87-97 % (tokenisation of isotope
numbers / scripts), every MS table and picture cell. 2023 ON paper 51 is NOT in Releases: C2a = 58 papers, 51 not done.
348. BEL control character (\x07) printed before every paragraph in chemistry 2015+ PDFs leaked into stored question
    text / html / answer prefixes (278 files; physics / maths 0). -> editable.build (chemistry): removed from the stored text
    fields only. A first try in layout.norm CHANGED 5 practical-paper graph crops: the BEL glyph's box set the line's left
    edge, so 'Draw a line of best fit ...' no longer counted as a margin sentence and went into the graph picture - reverted
    (lesson: a text-normalising change is a layout change; diff store/ after every local rebuild). Approved 2015-MJ, 2024-FM,
    2024-MJ (70 files) keep the BEL until their next rebuild - rebuild before the MongoDB push.
Tool lessons (C2a): a contact sheet of several SVGs INLINE in one HTML page shares clip-path / glyph ids between them and draws
broken figures - use one <img> per SVG (/home/claude/tools/figsheet.py). Maths freeze hash: /home/claude/tools/ms_hash.py.

## M4 finish (2014 ON paper 5, 2026-11-28)
347. (fixes 334) 2014 ON 51-53 (paper 5): the ruled MS table is narrower than the cut, so ms_maths.columns saw 5 'inner' rules
    (its outer borders too) and every question fell to the old wrap/fallback path: q2 lost its empty Partial Marks column (_tighten
    cut at the last ink), q3 3(b)(i)/(ii) were boxed (our label placed left of the table border), q4's cube table was re-flowed
    and its partial-mark words 'row 1 column 5' read as marks. -> ms_maths.columns drops the outer pair when 5 rules span less than
    the cut (as 334 did in _maths_ruled); ms_maths._drop_outer_borders removes those borders from the cells (their stub under the
    last row's rule showed as a tick). The same paper's 'Communication in two of 3(a), ...' row has no label (printed in the Answer
    column): the column-layout reader (2014-2016 MS) only knew 'Communication:' / 'Communication seen' -> COMMX there too (329's
    class, missed in the column path). It also moved APPROVED 2014 ON 63's 'Communication in 2(c)' out of 7(b) into the paper's
    communication marks (Dhruv: yes; re-approved after a look). Blasts: ms.py rows old vs new on all 461 0607 MS - only 2014 ON
    51/52/53/63 change; ms_maths columns / borders on every stored 0607 unit - only 2014 ON 51. 2014 ON 51/52/53 APPROVED.
    Lesson: a fix in one reader (table path) must be searched for in the other (column path) at once.

## Chemistry C2a fixes after round 47 (2026-11-28)
349. (Dhruv r47, 2023 ON 12 q34 'All options separate images') MCQ options drawn as displayed formulae stayed ONE picture and
    their cut end atoms leaked as text lines ('H H', 'OH', 'H Cl') in the editable layer: diagram_options' final test (every
    piece WHOLE in one option) failed on an end atom sticking out of the box - same root as 345, which fit_crop fixed only
    AFTER the option split. -> store: edge_words() widens the box before diagram_options (chemistry); run.py widens the bank
    MCQ figure box over ATOM-SYMBOL words only (a '?' or question number at the edge stays text: 2024 MJ 12 q05 / 2026 MJ 12 q03).
    15 figures now split (7 in approved C1: 2024 MJ 23 q32, 2024 ON 12 q34, 2024 ON 22 q29, 2025 MJ 22 q33, 2025 ON 11 q27,
    2025 ON 12 q36, 2025 ON 21 q33); stray atom text gone from 54 questions. Every split and every changed figure looked at.
    KNOWN (pre-existing): 2024 MJ 12 q05 and 2026 MJ 12 q03 lose their stem in the editable layer (the bank figure box takes
    the stem line because of its nuclide notation; the print layout is right).
350. SVG transform matrices cut to 3 decimals by render.minify: a path drawn at scale .04398 on coordinates ~16000 became .043
    and moved ~16 pt. Bonds / electron shells / graph curves / chromatogram spots / label ends out of place in 68 APPROVED
    2024-2026 chemistry figures (2024 MJ 11 q24 shells, q38 spots, 2024 MJ 22 q34 bonds, 2024 FM 22 q01 curve, ...) - missed
    in C0/C1 because the sheets looked plausible. Both rsvg and Chromium agree: the SVG itself was wrong.
    -> render.region_svg (chemistry only): matrices keep 6 significant digits. 15 approved papers rebuilt; every visibly
    changed figure compared old | new with rsvg (68, all now right). Physics has 30 and maths 2 figures with the same risk
    (frozen - NOT changed; listed by /home/claude/tools/matrix_scan.py for Dhruv to decide).
Tool lesson: never run pipeline/run.py with a computed list without checking it is non-empty - an empty list rebuilds
EVERYTHING (it reached maths 2014-2015 before it was stopped; all non-chemistry output restored with git, 22 stray chemistry
rebuilds restored too). Guard: `[ $(echo $P | wc -w) -gt 0 ]`.

## Chemistry C2b (2021-FM .. 2022-MJ, 2026-11-28)
351. MS label slips Cambridge printed: '7(c)(Ii)' (capital I, 2021 ON 31); '1(v)(i)'-(iii) for the three marks of 1(a)(vi) (2021 FM
    42); 'pH 4 circled' printed with NO label (= 2(d), 2021 MJ 31) - parsed into the 2(c) row. -> ms.label_text lowercases roman
    numerals in brackets (chemistry); run.py (chemistry): when exactly ONE paper part has no rows it takes (a) the contiguous rows
    whose printed label is no part, if their marks add up to its marks, or (b) the surplus last row of the part before it - a row
    merged with it is split at its single printed rule; ms_layout: such a MARKED row shows the paper's label in its empty Q cell,
    and _tighten keeps the table's outer left border (it cut the whole Q column off). Unmarked heading rows ('Tests on solid O')
    keep no label (first try labelled them '1(j)' - caught by the blast over all chemistry).
352. Atom letters printed as tiny IMAGES taller than the letter (6 x 42-51 pt, the glyph at one end) vanished from MS structure
    pictures: render._isolated_page redacts with PDF_REDACT_IMAGE_REMOVE, which deletes every image reaching outside the cut; and
    an image whose centre lay below the row was not counted, so the end atoms fell outside the picture box. -> chemistry:
    PDF_REDACT_IMAGE_PIXELS (only pixels outside are blanked); store._chem_structures sizes letter images by their INK and takes
    them up to 60 pt tall (51 pt ones were laid out one by one and the narrow 'C' / 'H' dropped).
353. A text line just under a structure picture came out squeezed or half cut ('nvoneerepeatunit(1)', '1 anyonerepeatunitwithexte',
    'propan-2-ol'): the picture box (tall letter images) reached into it. -> a word line the picture only partly covers stays text;
    the picture stops above / starts below it.
354. The H under a carbon cut off at a figure's bottom edge (2022 MJ 21-23 q35; 2021 ON 21-23 q11 lost both bottom H rows): the bond
    STARTS at the edge, so 'ink crossing the edge' never fired, and the drawing's rect did not even cover its lower line. ->
    fit_crop (chemistry, FIT_BOND_ENDS): vertical bond line ITEMS starting within 3 pt of the top / bottom edge are followed to
    their end, plus the atom letter there. Blast: 6 crops, all wanted.
355. SYSTEMIC: chemistry papers before 2023 print no 'Fig.' captions - every theory / practical paper of 2005 MJ, 2015 MJ and
    2021-2022 had ZERO figures (approved C0 2005/2015 and C2a 2022 ON included): diagrams were loose lines + text in the print
    layout (rotated labels drawn as blobs: 2021 ON 32 q6 'Br') and missing from the editable layer. Missed in C0-C2a because the
    print layout looked complete on the sheets. -> extract: a chemistry paper with no caption anywhere uses the maths
    uncaptioned-diagram finder (diagrams()); mark lines '[2]' / '[Total: n]' trimmed off the crop; region_svg respaces words for
    chemistry ('leastreactive' -> 'least reactive'). 2005 MJ, 2015 MJ, 2022 ON rebuilt in C2b's pass 2 and re-checked.
    Check for every batch: count figures per theory paper (0 = this class).

356. Uncaptioned-diagram crops (355) after the first look at all 210 new diagrams (C2b): (a) ruled TABLES became pictures
    ('tests | observations' of 2005 / 2015 practicals, the burette / gas-syringe / thermometer tables) - the rules are drawn cell by
    cell or as one drawing's frame + lines -> extract merges horizontal / vertical segments per line and skips a box with 1-8
    full-height column rules + 2 full-width rules or both side rules (or 4+ rules with 1-12 columns at 70 %); a framed chromatogram
    (no column rule) and graph grids (many) stay pictures. (b) question text inside the crop: 'Name ester X.' under a structure
    (extract trim + store fit_crop FIT_SENT_DOT for '_diagram' crops only - captioned figures lost their top line when it was
    global, 27 of 28 blast hits), '[5]' / '[Total: n]' (store FIT_MARK_LINE, blast 1 = wanted). (c) labels of two drawings side by
    side ('at the start' | 'after 20 minutes') were not pulled in (6 words): the pull-in counts words per group. (d) one row of
    small drawings (atoms A-E) lost the smallest one ('B', 2022 FM 32 q1a): drawings of one row in one part are ONE picture.
    Check for every batch: a contact sheet of every new diagram, compare a doubtful one with the page.
