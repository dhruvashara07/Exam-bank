# Progress

Read this first in every session. Update it before ending a session.

## Chemistry 0620 (started 2026-11-25) - plan: docs/CHEM_PLAN.md, entry: docs/START_HERE.md, steps: docs/PLAYBOOK.md
- 2026-11-25: analysis + CHEM_PLAN.md (Dhruv's decisions D1-D4: Unicode like physics + LaTeX only where needed; MS columns
  follow print; Periodic Table once per paper; pilot 2005-MJ 2015-MJ 2024-MJ 2026-MJ). Shared code: the 12 'not 0625 = maths'
  gates now ask subjects.is_maths (chemistry runs the physics path); chemistry-only code asks subjects.is_chem.
- 2026-11-25: pilot C0 (56 papers) built: GitHub pass 1 (run 45545804757) + pass 2 (45548516463), then the last fixes rebuilt
  LOCALLY (= Action; both GitHub passes of the budget used). 56/56 papers exact mark totals, 0 blocking. Patterns 277-289.
  Reasons: 2040 passed, 189 verified, 3 fixed, 29 known, 0 open. Freeze proven before each push: golden 0 changed cuts,
  nothing tracked under 0625/0607 changed, maths ms_layout byte-identical on 192 questions, ms_rebuild list = untouched baseline.
- Round 41 (chemistry pilot, 7 items: 3 new rules, 3 calibration, 1 decision - faint MS structure pictures redraw yes/no) on
  Dhruv's OWN-account review page https://claude.ai/artifact/PCdP6oibAkjQvGz8mKm73e (this chat runs in his own account; round 34
  dropped from it). Maths rounds all closed (round 44 closed 2026-11-27); the shared-account page is empty.
- Known C0 items (not in the round, ERROR_PATTERNS 'Known (C0...)'): 2026 MJ 23 q36 MCQ option pictures cut over two rows
  (paper NOT to approve until fixed); options-table pictures holding question text (2026 MJ 12 q3, 2015 MJ 11 q1); practical
  marking points (iii)/(iv) under a split part (2026 MJ 51 q2, 52 q1, 52 q2); Cambridge label slips (2024 MJ 33 q2, 52 q1, 32 q6);
  2015 MJ 33 q7 7(b)(i) small text beside a faint picture.
- 2026-11-26: round 41 closed (7 answers: 2 ok, 5 wrong). Fixed as classes (patterns 290-302): table cell drawings as one
  picture each, 2005 answer dots, empty bands, ONE standard MS column proportion, 2005 MS Marks column (was empty) and notes,
  faint structure redrawn by hand (chem_redraw/), and ALL items left open in C0 (MCQ option crops, question text in option
  tables, label slips, practical marking points). 2015 paper numbering confirmed online (to 2015: 2 = Core Theory). C0
  rebuilt locally: 56/56 exact, 0 flags, 0 blocking. Freeze: golden 0, nothing under 0625/0607, maths layout identical.
  Round 42 (recheck, 9 items) on the own-account page https://claude.ai/artifact/PCdP6oibAkjQvGz8mKm73e.
- 2026-11-26: round 42 closed (9 answers: 6 ok, 3 wrong), all 3 fixed as classes (patterns 303-305): drawn-letter tables are
  text, thermometer tube walls join their cell picture, MS Q column shows the paper's labels after remapping. C0 rebuilt: 56/56
  exact, 0 flags. Freeze: golden 0, nothing under 0625/0607, maths layout identical (192/192), ms_rebuild list = baseline.
  C0 APPROVED (56 papers). Pilot done.
- 2026-11-27: C1 (2024-FM 2024-ON 2025-FM 2025-MJ 2025-ON 2026-FM, 70 papers) built: GitHub pass 1 (run 45959753924, 83 reasons -
  the C0 classes held; new pass-1 hint ms_marksum = Marks-column sum, ERROR_PATTERNS 295) + pass 2 (45969884881: 12 verified, 0 open).
  Fixed as classes (patterns 313-319, all gated to chemistry): MS rows lost on a page continuing without header / '(a)(ii)'
  without number; end atoms of displayed formulae as drifting text; picture under a re-wrapped line; structures under the last
  text line cut off (2026 FM 42 6(c) missing); column-rule stub in a structure picture; long Answer lines over the Marks/Guidance
  column (also 2 approved C0 questions: 2015 MJ 32 q3, 2015 MJ 21 q6 - in the round). Freeze: golden 0, nothing under 0625/0607,
  maths ms_layout hash identical on all 4014 maths questions (so the ms_rebuild list = baseline).
  Known (budget rule): C0 2026 MJ 41 4(c)(i) and 2026 MJ 63 2(a) text still overlapping (4 tries, 2 questions, approved papers,
  NOT rebuilt - stored as approved); polymer open bonds as short stubs (3 Qs); 2025 ON 23 q36 options inside the picture.
  2026 FM 32: Cambridge removed 3(d)(iv): marks 79/80 is a blocking check - approve with --force-note if approve.py refuses.
  Round 45 (10 items: 5 calibration, 3 fixes, 2 changed pilot questions) on https://claude.ai/artifact/PCdP6oibAkjQvGz8mKm73e.
- NEXT: (1) C1: Dhruv answers round 45 -> read feedback_r45 (db_list, slug b3c8a710-c92b-4a33-95b2-f7eba1bc0031), fix wrong
  items as classes (gated 0620), freeze checks, review_round close 45, approve.py the 70 C1 papers, docs, push. Then C2 (CHEM_PLAN 6)
  in a new chat.
  (2) Maths: RD2 done; next maths batch M4 - see the maths NEXT below.

## Maths 0607 (started 2026-11-12) - plan: docs/MATHS_PLAN.md, entry: docs/START_HERE.md, steps: docs/PLAYBOOK.md
- 2026-11-18: CHEM stored: 1599 of 1600 PDFs in Releases (only chemistry_0652_to_0620_mapping.pdf, not a Cambridge name,
  stays on branch store-chem). inbox.py now keeps gt/ci/ir/in/eq/one-digit/combined files (302 had been skipped).
  Branches store-chem and store-chem-rest: Dhruv deletes them (this session cannot delete branches).
- 2026-11-24 (round 37 work, Dhruv asked 'what is wrong in the 7 pending papers - show me'): all 7 fixed (ERROR_PATTERNS
  257-262), plus 14 other mark schemes whose rows were cut too high (approved ones included) - rebuilt locally, photos sent
  to Dhruv in chat.
- 2026-11-24: Dhruv ok on round-37 photos -> M3 DONE: all M3 papers approved (16 approved today incl. 9 re-shown MS
  row fixes). Only 0607_2023MJ_32 stays pending (M2 item below).
- 2026-11-24 (own account): pattern 240 fixed, 0607_2023MJ_32 approved -> ALL maths papers approved (0 pending). The fix
  moved 60 approved questions (vectors kept whole; checked side by side, fine): list in review/claude/R240_changed.txt, re-show
  a sample of 5 in the next round.
- 2026-11-24: screenshot-redraw batch DONE locally (ERROR_PATTERNS 264): 96 blurry MS pictures redrawn (ms_graphs.SPECS),
  11 kept as printed; same rebuild applied the round-35 rules to 35 approved papers (83 papers rebuilt, 227 questions checked
  side by side, all approved still). Round 38 published (10 redraws + 5 calibration + 5 vector-bracket items).
- 2026-11-24: round 38 closed (13 ok, 7 wrong - fixed, patterns 265-269). New rule + check: faint / blurry pictures are
  redrawn or flagged (pattern 270, maths_check picture_checks); 3 faint graphs redrawn.
- 2026-11-24: picture batch RD2 DONE locally (ERROR_PATTERNS 271-273): 181 flagged MS pictures in all 0607 batches (149
  questions): 180 redrawn (107 graphs, 19 grid shapes, 14 Venns, 11 data plots / bar charts, 10 tables, 9 dot patterns, 3 trees,
  2 pies, 2 mappings, 3 sketches), 1 kept (2025 FM 62 10(a), Dhruv decides). maths_check picture_checks: 0 left. One local
  rebuild (ms_rebuild, 105 questions written after the groups; all redraws looked at side by side); golden 0, nothing under
  0625; approvals unchanged (hash = cut + marks). Round 39 published (10 redraws + 5 calibration + 1 decision).
- MATHS NEXT: (1) Batch M4 (MATHS_PLAN 5: 2014-ON 2015-MJ 2015-ON 2016-MJ 2016-ON 2017-MJ 2017-ON, ~115 papers, PDFs in
  Releases) in a NEW chat - prompt in docs/NEXT_CHAT.md ('Maths M4'). Put the 5 round-44 fixes in M4's first review round as
  recheck items (2019 ON 31 q12, 2021 ON 31 q7, 2026 MJ 11 q14: fractions over the branch middle; 2023 MJ 33 q6: space under the
  tree; 2023 MJ 63 q4: '3' centred). (2) Open: 2022 ON 51 5(a) empty grid not shown; 2024 ON 23 q7 partial marks a bit small.
- 2026-11-27: RD2 DONE (rounds 39, 40, 43, 44 closed). 180 MS pictures redrawn; graphs match the printed grid; every MS tree
  has the question's geometry; dot paper = whole pictures; no 0607 paper pending approval (cuts unchanged).
- 2026-11-24: ROUND 36 closed (7 ok, 1 wrong: no function label on the redrawn 2019 ON 61 graph - removed). M3 APPROVED:
  62 of 69 papers + re-approved 2019 ON 43, 2021 ON 42, 2022 MJ 31, 2022 MJ 42 (their part marks were corrected); 7 M3
  papers kept pending for the known open MS pictures. Rounds 35-36 removed from the review page.
- 2026-11-24: ROUND 35 answered (7 ok, 3 wrong). Fixed: 2019 ON 61 q5 brace + graph redrawn from the model; 2020 ON 51
  q1/q2 rows of diagrams = one picture with captions, dotty paper drawn. Dhruv's decisions -> MATHS_PLAN section 12
  (plain words in rounds; drawn grids need no image; row rule; dotty paper). GitHub dispatch was refused this time:
  M3 rebuilt locally (same as the Action).
- 2026-11-23: M3 BUILT + pass 1/pass 2 (2018 MJ/ON, 2020 MJ/ON = 69 papers; 2020-MJ has no 13/33/53 at all). Pass 1: 182 reasons
  in 115 questions -> 30 fixed (patterns 241-250: white marks, Communication rows, number-less labels, label typos, answer line
  beside the next label, crop side-cut / arrow column / hatch clipping / question text in crops, new equation-font glyphs),
  125 passed, 30 known (251-252). Blast measured before push (fig_blast.py, ms old/new): 4 approved papers had wrong part
  marks (245) and 2019 ON 61 q5(c)(ii) a lost MS piece (242) - corrected. Pass 2 (run 45231218239): 27 verified, 0 new,
  30 collateral all looked at (corrections or 2 pt rule shifts); approved-session extras = bracket extenders only.
  Golden 0 changed cuts, nothing under 0625. Round 35 published on a NEW review page (shared account).
- 2026-11-22: ROUND 34 CLOSED (13 items, 6 wrong -> patterns 234-239, all fixed and checked side by side), M2 APPROVED: 116 of
  117 papers (2023 MJ 32 waits for pattern 240). Pass 2 on GitHub (run 45052380975): 2 not fixed passed (231 grids), 17 NEW
  = bracket-extender words (check now ignores them) + the two redraws; 52 collateral questions all looked at: one real
  regression of my own (stray extender line, fixed) and 3 old vector-wrap defects (pattern 240, 2 fixed, 3 open).
- 2026-11-20: M2 passes 3-5 on GitHub; known items fixed (patterns 230-233: tree in one picture, Step grids split, word box
  as text, rounded formula box as text, crops never grow into a sibling); pass 4 caught my own collateral (54 questions),
  narrowed and re-tested - all approved crops back to their approved boxes. Reasons file: 0 open, 0 ask.
- 2026-11-19: two-pass flow BUILT (pipeline/reasons.py, bank.yml 'reasons'); pattern 209: fontTools missing on GitHub ->
  ~880 approved maths questions had been stored in the fallback layout; all 11 approved sessions rebuilt (R209: ms_mode
  0). M2 built (117 papers), pass 1 resolved (62 fixed / 263 passed / 4 known, patterns 211-227). Approved papers whose
  rebuild changed must be re-approved after the pass-2 look (approve.py).
- 2026-11-17 (night): round 33 (9 of 23 wrong) fixed - patterns 201-208; GitHub run 44134367484; M1 APPROVED (111 papers:
  100 of 2024-2026 + 11 earlier papers whose approval the re-cut removed). MongoDB unchanged (Dhruv: approve in git only).
  Bridge upload of zips timed out (only <=40 MB files pass): Dhruv uploads PDFs himself.
- 2026-11-17 (evening): round 32 fixed (patterns 181-200): ms_graphs.py, tasks.py (75 task records), re-flow stops at
  sub-row rules, columns align under a rule only where it would be dropped, text under tables, notice regex; 3 GitHub
  runs (44085611730, 44119747495, 44125482795); golden 0; round 33 published.
- 2026-11-17: M1 built on GitHub (90 papers, 11 min, run 43893190451), checks 0 blocking; ONE Claude check round found
  20 classes (ERROR_PATTERNS 161-180) incl. the 2026 MJ Guidance column (5 columns, Dhruv: 40:30:30), the paper-6
  section note (Dhruv: top of every modelling question), fraction bars dropped / denominators split (also re-shown from
  approved M0), dotted rules from pictures, diagram crops beside sentences. ms_align adapted to maths (was listing every
  question since M0). New tool pipeline/ms_rebuild.py (layout-only rebuild). Golden 0, nothing under 0625.
- 2026-11-16 (night): M0 PILOT DONE - 60 papers approved (rounds 27-31; round 31 36/40 ok, 3 fixed: patterns 157-159).
  Known limit: mark-scheme graphs that are pasted SCREENSHOTS (most of 2014) have no line data - only contrast is raised,
  they cannot be redrawn as lines (graphs the PDF draws as lines ARE redrawn).
- 2026-11-16 (evening): round 30 (14/40 wrong) fixed - ERROR_PATTERNS 149-156; faint graphs redrawn + darkened (Dhruv);
  'similar not exact' layout rule (MS_TABLE_RULES 30); checks 60/60; golden 0.
- 2026-11-16: round 29 fixed (ERROR_PATTERNS 130-138) and Claude's ONE check round introduced (Dhruv: one round, rules +
  checkboxes, side by side only in doubt; `pipeline/claude_check.py`, checklist review/claude/M0_check.md, zoom sheets
  `ms_compare.py --zoom`, new checks ms_mode and q_rule). That round found 8 more classes (139-147) and fixed them before
  Dhruv's round. Answer column now 60 % / Partial Marks 40 % of the free width (Dhruv; MS_TABLE_RULES 28). Review page:
  stored figures at the question's scale. checks 59/60 (2014 MJ 62 marks 39/40, pattern 148). Golden 0.
- 2026-11-14 (evening): round 28 (25 of 34 wrong) fixed as ERROR_PATTERNS 91-121; new appearance checks (maths_check)
  and pipeline/ms_compare.py; PLAYBOOK 2b+/2b++. Open: 2014 MJ 62 p4 (broken text layer: (g)(i)/(ii) one row, stray
  rule pieces in its cell pictures), a wrap inside a long bracket (2014 MJ 62 q6(g)(v)), wide inner tables shrink to 60 %.
- 2026-11-14: round 27 fixed (ERROR_PATTERNS 75-90): one font 11 pt with bold, run split, paragraph re-flow, picture
  cells, dot lines, diagram crops, 4th-level labels, nested fractions and question tables kept as the printed picture
  (LaTeX: 2118 parts ok, 228 picture). maths_check: 9 hits left (2014 62 broken page, 2 overflows, 1 missing word).
  Open (MATHS_PLAN 10): 2025 MJ 53 q3 pyramid cut by a part boundary; 2014 43 q3(b) inequality signs; 2019 ON 52 3(b)
  inner-table shading; 6 MS questions on old paths.
- 2026-11-13 (later): mark schemes fixed before the round (Dhruv): new `pipeline/ms_maths.py` - every maths MS row laid
  out cell by cell (fractions / vectors / graphs kept whole, rows grow, Answer = Partial Marks width): 645 questions in
  our 4-column layout, 13 still on old paths (2019 ON 11 q8 etc., see MATHS_PLAN 10). Also: 2019 ON 11-13 MS parsing
  (rules decide the columns), tables lower on a page, 2014 paper 6 part B numbered from 1 again (extract + ms),
  communication 'C2' marks, 'M1' marks in 2014 marks columns, diagram crops take axis labels / sideways titles /
  long tree-diagram labels, bar charts no longer taken for tables. checks: 59/60 no blocking (2014 MJ 62: 39/40, one
  row on a page with a broken text layer). LaTeX: 2229 parts ok, 118 picture. Golden 0 changed cuts.
- 2026-11-13: M0 pass 1 done and pushed (60 papers built on GitHub, then rebuilt locally). New for maths (ERROR_PATTERNS
  64-70): formula page -> paper.formula_list (print + LaTeX list), investigation/modelling intros -> paper intros,
  page-top instruction lines dropped, marks of 2014-2024 investigation papers from the mark scheme, communication marks
  as paper marks, equation-editor symbols (# -> × ...) fixed in print and text, uncaptioned diagrams cut as figures
  (`extract.diagrams`), LaTeX content per part (`pipeline/maths_tex.py`: 2186 parts ok, 120 fall back to the printed
  picture, KaTeX + character check), store paper.json, 4-column mark schemes Q | Answer | Marks | Partial Marks with
  Answer = Partial Marks width (Dhruv). checks: 57/60 papers no blocking (2014 MJ 62/63 marks, one piece). Physics
  untouched (golden 0 changed cuts, store identical after `dupes`).
- 2026-11-12: plan agreed with Dhruv (MATHS_PLAN.md 1). Pipeline made subject-aware without moving physics:
  pipeline/subjects.py, maths paper types from the cover, syllabus-aware selectors/session tools (SYL=0607),
  dupes per syllabus, store-only upload branches (store_pdfs.sh + upload.yml), batch record (batch_log.py).
  Golden set now 26 papers incl. 6 from 2004-2012: 0 changed cuts. Test run on 7 maths papers: cuts work,
  marks = total on 6/7, MS linked on 252/263 parts; open problems listed in MATHS_PLAN.md 3.
- PDFs in Releases: all 946 maths PDFs (2014-2026; 2019-MJ missing - Dhruv gets it before M3). Stored 2026-11-13 with
  pipeline/store_pdfs.sh in 5 parts. Old branches store-0607-part2..5 and store-0607-rest can be deleted on GitHub.

## 2002-2012 (started 2026-11-09, batches of 3 years) - why: docs/AGENT_GUIDE.md, how: docs/PLAYBOOK.md, mistakes: docs/ERROR_PATTERNS.md
- Physics finished (cleanup done 2026-11-12). Every year 2002-2026 approved; nothing pushed to
  MongoDB or Cloudinary since 2026-10-30 (Dhruv: not until the data size is known).
- 2026-11-12 cleanup: git - 49 orphan store files and pipeline/strip_svgs.py removed; history (~950 MB) left as is
  (Dhruv). Cloudinary - question_bank/ deleted with Dhruv's OK: 38,299 old-format SVGs, 1.62 GB; account now empty
  (workflow cloudinary.yml, list/delete). The 66 papers synced to MongoDB on 2026-10-30 (old format, review/published.json)
  now point at deleted images until the fresh push. Cloudinary's usage counters refresh daily (credits were 54.7/25).
- 2026-11-12: round 26 answered (50 items, 12 wrong), all fixed, 2002-2012 rebuilt twice and re-checked: 0 blocking,
  `ms_align list` empty, every mapped question's rows = its map (now for ALL 205 maps: 3 old approved maps whose entries
  sat on superscript lines fixed - 2004 ON 05 q4, 2006 MJ 05 q4, 2009 ON 06 q1), golden 0 changed cuts, nothing outside
  2002-2012 moved. New rules: MS_TABLE_RULES 20 (hard to separate -> Cambridge's grouping, our layout, one row per
  mark, headings merged), 21 (one mark over several parts = merged Marks cell), 22 (values split in order), 23 (block
  totals on the part). ERROR_PATTERNS 55-63. 2011-2012 approved (58); 2004 ON 03 and 06 re-approved.
  Approved-year changes, all improvements: ≥ glyph (2009 MJ 02 q9, 2010 ON 51 q4), part marks of block totals (data
  only, ~190 questions, totals unchanged), 17 figure crops a pixel or two wider (labels taken whole).
- 2026-11-11: batch 4 (2011-2012, 58 papers) built and checked: 0 blocking; `ms_align list` empty (65+17 questions
  mapped); ms_sweep clean (13 hits are codes printed inside Cambridge's own answer text); golden 0 changed cuts.
  Pipeline fixes: fraction bar above a line was cut out of every piece (ERROR_PATTERNS 50), 2011 MJ 52/61 had no
  mark scheme at all because the question number is printed '1.' (51), map prefixes matched against our own table (52),
  rows sorted by sub-part and not only by letter (53, MS_TABLE_RULES 19), `dupes` after any single-paper rebuild (54).
  Approved years moved in 3 questions only, all improvements: 2004 ON 06 q5 (2 pt of ink kept), 2005 MJ 05 q4 and
  2005 ON 05 q3 (row order). All three are in round 26.
- 2026-11-11: batch 1 (2002-2004, 25 papers) APPROVED. Round 22 closed (21 wrong, all mark-scheme layout -> MS_TABLE_RULES 16).
  Batch 2 (2005-2007, 30 papers) built + fixed (ERROR_PATTERNS 17-22); round 23 closed (11 wrong -> fixed); 2005-2007 APPROVED.
  Batch 3 (2008-2010, 56 papers) APPROVED after rounds 24-25 (fixes ERROR_PATTERNS 31-49: MS rows by meaning, question order, spacing, side notes, stacked codes). All 2002-2010 rebuilt; ms_align list empty; golden 0 changed cuts. Next (new chat): 2011-2012, its round re-shows the 20 round-25 fixes.
- Batch 1 = 2002-2004 (25 papers: 01 MCQ, 02 core, 03 extended, 05 practical test, 06 alt. to practical). APPROVED (round 22).
  Pipeline fixes made (golden: 0 changed cuts; 2013-2026 untouched): pre-2009 paper types (02 = core theory, 03 = extended;
  was read as MCQ), mark-scheme total from "MAXIMUM MARK" (pre-2009 only), practical-test (05) mark scheme parser
  (`ms.practical_rows`, one row per question, marks from "TOTAL n"), scanned MS (2002 ON: no false "no mark scheme" flags),
  2002 ON 05 (answer booklet pages dropped, "Question 1" headings, totals read by eye: SCAN_TOTALS/SCAN_QMARKS in run.py),
  figure crop rising past beside-text, invisible text is no caption, "For Examiner's Use" heading + drawn rule removed,
  footer code `0625/1/O/N/02`, blank page with copyright note, CMYK pictures black in browsers (render.fix_cmyk_images),
  MS label "10(a)" as one word. checks: 25 papers, 0 blocking, 9 flags (all looked at: 32 MCQ sets side by side = fine).
- 2026-11-11: F/C (target grade) column removed from old Paper 2 mark schemes (clean.strip_tier_column, Dhruv).
  Round 22 (33 items, 8 flagged) on the review page (portal.json review_url; closed rounds 9, 10, 21 removed from the page).
- DONE (was open for batch 1): old mark schemes now in our table layout (MS_TABLE_RULES 16-18, rounds 22-25).
- Known gaps (no fix possible): 2002 ON: paper 01 has no mark scheme file (no MCQ answers); other 2002 ON mark schemes are scans (page pictures); 2010 MJ variants 13, 23, 53 have no mark scheme file.
- GitHub build note: `bank.yml` "sessions" step runs `checks.py` with ids without `0625/` so it checks nothing; run checks locally.

## v5 prototype (2026-11-03) — waiting for Dhruv's approval
- Hourly task `trig_0173DCrQWm76nnTXrW52TPjC` stays OFF. `review/backlog.json` `running_since` is a stale lock from a
  crashed run (00:06 IST); not cleared yet (Dhruv asked to have it explained first).
- Built on the pilot papers only (2014 MJ 21/51/52/53/61/62/63, 2014 ON 31/51, ...): new `pipeline/store_v5.py`,
  `renumber.py`, `store_view.py`; `store.py` schema 5 (caption = layout text, tagged numbering roles, answer bands,
  tables as text via `store_options.table_picture_reason`, `caption_masked` when drawing ink shares the caption row).
  Question-bank view / print view / renumbered worksheet work. `golden.py check`: 0 changed cuts (2014 MJ 52 q04 now cuts Fig 4.1).
- Rules from Dhruv for the bank view: remove working space and full dotted lines; keep dots inside a sentence, the last
  answer line with label/unit, tables to complete, grids.
- NOT done until approval: rebuild of the other years, review page upgrade (H), BACKLOG.md update, hourly task back on.
- Known gaps: practical mark schemes are one block per question; MS row labels like "(a)(i)(ii)" not relabelled; "°C" glyph in
  some 2014 mark schemes looks odd; 63 q02 Fig 2.1 crop edge includes the neighbour's label leader (cut issue).

## Portrait mark schemes (2026-11-03) — samples sent to Dhruv, waiting for his OK
- `pipeline/ms_portrait.py`: re-wraps landscape MS rows (2016 MJ+) to 523 pt portrait, column widths by content, header once, picture rows natural size; 97.5% of 9,007 rows wrap, 2.5% scale to fit. Rules: docs/MS_TABLE_RULES.md.
  Not yet in `store.py build`. Details and next steps: docs/CONVERSATION_LOG.md (last entry).

## Done
- 2026-10-29: 134 PDFs (0625 Physics, Feb/Mar 2025 to May/Jun 2026) in `raw/`.
- 2026-10-29: Pipeline v1: watermark removal, question/part splitting, exact SVG pieces, figures,
  mark-scheme linking, test-paper builder. 66 papers → 1,200 questions; every paper's marks match its cover.
- 2026-10-29: Review round 1 (57 items): 48 ok, 9 wrong. All 9 were dashed lines/hatching + 1 figure crop.
  Cause 1: review previews were rasterised by MuPDF, which ignores SVG `stroke-dasharray`; the SVGs
  themselves were right. Previews now rendered with Chromium. Cause 2: MCQ figure finder cut figures
  (zero-width lines ignored by fitz Rect union; hatch-pattern cells reported at fake positions; vertical
  gap limit). Rewritten: prose lines separate figures, labels attached, invisible ink dropped
  (pixel check), fraction-bar-only clusters ignored.
- 2026-10-29: Storage reorganised into `bank/` (one folder per question: JSON + question/, figures/,
  markscheme/ SVGs), `bank/index.json`. Cloudinary public id = `question_bank/` + path inside bank/.
  MongoDB: database `question_bank`, collections `papers`, `questions` (our format, not QuestionV2 —
  Dhruv adapts the website). Only approved papers (`review/approvals/<paper>.json`) are synced.
- 2026-10-29: Daily scheduled Claude check set up (docs/DAILY_CHECK.md, `pipeline/check.py`,
  `pipeline/approve.py`). All 66 current papers approved.
- 2026-10-29: `.github/workflows/bank.yml`: upload PDFs to `inbox/` from phone → filed to `raw/` →
  processed → committed → Cloudinary + MongoDB. Full re-run takes ~3.5 min.
- 2026-10-29: **2015–2024 added**: 477 papers (Feb/Mar 2015 – May/Jun 2026), 8,624 questions. Every
  paper's marks match its cover; pixel coverage 0 lost ink on 6,545 pages; no footer/barcode/notice text
  inside any piece; no overlapping pieces; 59 papers (one per year x paper number) sampled visually.
  Old-paper support: 2015 numbering, standard totals (no cover total before 2020), rotated/landscape and
  column-format mark schemes, two-column MCQ keys, erratum pages, A3 and 612x859 pages scaled to A4,
  mark schemes drawn in clipped pieces (text rebuilt from characters), MS label typos ('9b(i)',
  '(b)(ii)', '7(a)((i)', '3(b)(i)1.', '(h)(l)' ranges), centred 'Question N is on the back page.' notices.
  Review queue: 34 items, all genuine Cambridge labelling differences between paper and mark scheme
  (e.g. paper 2(b)/(c) = MS 2(b)(i)/(ii)), 1 erratum, 1 question removed by Cambridge (2024MJ_21 q14).
- 2026-10-29: **Editable layer** (`pipeline/editable.py`, run by run.py): `content` blocks per node:
  text (HTML b/i/sub/sup, LaTeX `\(\frac{}{}\)`), lists, tables (real cells), figure refs, answer
  space, marks, MCQ options (text, options table, or "drawn in the diagram"). Exact SVGs stay the master.
- 2026-10-29: **Review website** `site/` → GitHub Pages (`.github/workflows/site.yml`), pictures from
  Cloudinary; "Report a problem" opens a GitHub issue labelled `review`.
- 2026-10-29: **PDFs to GitHub Releases** prepared (`pipeline/raw_store.py`, `.github/workflows/raw.yml`,
  branch `incoming-raw`); new PDFs are git-ignored in main.
- Review page: https://claude.ai/artifact/LGic38rQwKjkZze9jL1zmq — round 1 feedback in collection
  `feedback`, round 2 (9 fixed + 15 new MCQ figure checks) in `feedback_r2`. Doc id = question id.

- 2026-10-30: **Professional flow** (agreed with Dhruv, portal option A, twice-daily check, editable = text
  only): `upload.yml` (PDFs on an upload branch → Releases → process → checks → batch → main), batch tracker
  (`batch.py`, stages derived from files), automatic checks (`checks.py`: marks, coverage, page furniture,
  figure crops, editable-text score; figure/text are warnings), golden set (20 papers, `golden.py`),
  approvals and Claude checks tied to a cut hash (re-runs keep them when the cut is unchanged), review rounds
  (`review_round.py` + `site/review/index.html` on the review page), website Batches tab, `docs/UPLOAD.md`.
  Figure crops rebuilt from printed ink (tight ink + grow along lines); captions stay with their figure.
  All 477 papers: marks match, coverage 0, 0 blocking problems; 46 crop + 58 text warnings (of 8,624 questions,
  editable text mean 99.9% of printed words).

## Waiting on Dhruv
1. (done 2026-10-29: all 983 PDFs in Releases.)
2. Turn on GitHub Pages (Settings → Pages → Source: GitHub Actions) for the website.
3. Review round 3 (90 questions, review page link in review/portal.json). Round 2 was replaced by it.
4. May/Jun 2026 variant 7: mark schemes 17 and 27 exist, question papers missing.

## Next
- 2016-2019 full check-up done (2026-11-05): 2016 FM - 2020 ON COMPLETE (2026-11-06): all MS in our table (old portrait ones too), all approved = final check in git (MongoDB paused until everything is done). 2022-2026 built ahead on GitHub. 2021, 2022 and 2023 approved (round 18 closed, fixes in all years). 2013 MJ - 2026 MJ ALL FINAL in git (round 21 closed 2026-11-09; 2013-2016 FM old MS in our table). Not done: 2002-2012 (scope to confirm with Dhruv: only 7 test papers built), then cleanup (old figures in git/Cloudinary), MongoDB push of everything (sync is paused in bank.yml), symbol library, 2017 MJ qp_11 missing. New chat: start from docs/NEXT_CHAT.md. Known: 2019 ON 41 q9(a)(ii) hatched circles plain. Then 2022, 2023 ...; the older years 2013-2015 FM also need the old-portrait MS conversion (ms_layout._old_rows) when they are done; after his answers + fixes approve the remaining 2016-2019 papers, then 2020 under the new plan (build -> I check flags -> short round -> approve).

1. Daily check: read Dhruv's round 3 answers (`feedback_r3`), fix anything marked wrong, approve the 2015–2024
   backlog by the rule in docs/DAILY_CHECK.md §6. 40 flagged questions did not fit round 3 (mostly editable-text
   warnings): they go into round 4 once round 3 is closed.
2. Website issues (label `review`), fix anything wrong.
2. Topics/subtopics/keywords from the 0625 syllabus; alt text for figures.
3. Other subjects (Chemistry, Biology, Maths), then AS/A level, IB.
4. Test-paper builder on the website (reads MongoDB `question_bank.questions`).

## How to run
    pip install -r requirements.txt
    python3 pipeline/raw_store.py fetch               # original PDFs from Releases
    python3 pipeline/run.py                          # all papers (~27 min for 477)
    python3 pipeline/run.py 2025-MJ/41               # one paper
    python3 pipeline/build_test.py out.pdf 0625_2025MJ_41_q01 0625_2025MJ_41_q05:c --ms
    python3 pipeline/coverage.py                     # check nothing on the pages was missed

## Daily check log
One line per run: date, pending papers checked/approved, feedback handled, fixes, notes.
- 2026-10-29 (setup): 66 papers approved by hand after the full check. Review round 2 published, not yet answered.
  Safe push (`pipeline/push.sh`) + CLAUDE.md added so the Action, this chat and the daily check never clash.
  Action runs fail at the MongoDB step until Dhruv adds the secrets (expected).
- 2026-10-29 10:xx IST: secrets added. Cloudinary rejected 62 SVGs ("Resource is invalid") = every SVG with
  >=1000 <use> (one per glyph). render.limit_uses: drop empty-glyph uses, inline glyph paths above 900.
  Pixel-identical (Chromium, 122 files). All 66 re-approved. Run logs are not readable from Claude's
  workspace: scripts report via GitHub annotations (gh api .../check-runs/<job>/annotations).
- 2026-10-29 14:xx IST (chat session): 2015–2024 processed (see Done). 2025–26 re-approved (66): only
  whitespace at cut edges, notices/barcodes excluded, better MS codes, tighter figures, editable layer.
  411 older papers pending for the daily check. Cleaned-PDF cache now also rebuilds when clean.py changes.
- 2026-10-29 22:xx IST: figure-crop fix (axis titles / centred labels were taken as prose, so 63 of 3,483
  figure crops were cut); full re-run, all checks clean, 2025–26 re-approved (question pieces unchanged).
  2015–2024 PDFs pushed to branch `incoming-raw` → Releases. Daily check paused while Dhruv and Claude agree
  the batch/portal plan (portal A: Pages + Claude review page; twice-daily check; text-only editable layer).
- 2026-10-30 00:xx IST (chat session): new flow built (see Done). 2025–26 re-approved (66, cut hash stored).
  411 older papers at 'auto checked'; Claude-checking them via overview images, newest first.
- 2026-10-30 12:xx IST (chat session): Claude check of all 411 backlog papers (overview of every page, newest
  first). Pipeline fixes found by it: a lone '[n]' printed level with the next label is now cut below the mark
  (+ check `piece: mark at the top`); 'Question continued on next side' is page furniture; a part label printed
  in the question-number column ('(e)' on 2020 FM 52 p4) is accepted when it is the next letter; figure crops:
  bullet lists, table captions under the table, key text ('= positive particles'), cells of ruled tables,
  split prose rows ('… × 10⁶' + 'km.') and caption-only crops fixed; crops never reach past their piece.
  Full re-run (JOBS=2, ~23 min): 477 papers, 0 blocking, golden 0 changed cuts; 21 papers re-cut (11 visibly,
  each looked at again), 2025 MJ 42 re-approved (0.3 pt shift). 411 papers recorded `claude_checked`.
  Review round 3 published (90 items: 72 flagged + 18 spot checks; `--max 90` keeps a page version under 511 files).

- 2026-10-30 22:xx IST (chat session): question-store experiment (`docs/STORE_DESIGN.md`,
  `pipeline/experiments/qstore.py`): per-part layout units + figure files, MS rows as text, duplicates stored
  once. Bank fixes found by it: glyphs crossing a piece edge were cut away (render.py, 687 SVGs better, cut
  hashes unchanged); side-by-side figures split by caption; 'Fig. n' inside a table cell is not a caption.
  Full re-run: 477 papers, 0 errors, golden 0 changed cuts. Critical store test: 23 papers, 1,612 units,
  9 above 1% pixel difference (all explained: font-width '1', one italic letter, one MS tick past its row).
  Waiting for Dhruv's go-ahead before the pipeline switch-over. Cloudinary upload paused (over credits).
- 2026-11-02 (chat session): question store is now the pipeline. `pipeline/store.py` (+ store_units, store_options,
  store_text) builds `store/` from every cut: layout units, figures per label at true size, MS rows, MCQ options
  (table rows / one figure per option / text), tables as text, duplicates once, no empty meta. run.py builds it;
  the Actions verify it (review/store/<paper>.json) and feed differing pieces into review rounds. SVG pieces
  removed from bank/ (1.8 GB -> 94 MB, `strip_svgs.py`), cut hashes unchanged (golden 0). MongoDB and
  Cloudinary steps paused until all years are finalised. Site and review pictures draw from store/.
  2002-2014 PDFs (qp+ms, 434 + 153 renamed/split by `old_papers.py`) in Releases; backlog in
  review/backlog.json, hourly run docs/BACKLOG.md (scheduled task trig_0173DCrQWm76nnTXrW52TPjC, enabled
  after the first full verify). Older-paper fixes: component ids 0625_2005MJ_03, old MS label columns,
  stamp images removed (clean.py), scanned MS kept as page pictures (ms_scan).
- 2026-11-02 12:05-13:00 UTC (hourly backlog run): round 3 closed (17 of 90 answered, open >3 days; 2 wrong,
  both fixed: 2015 ON 51 q1 side-by-side figure split now ignores a third figure's ink (also better crops for
  2017 MJ 53 q2, 2022 FM 42 q3); 2015 ON 51 q4 Table 4.1 is already text in the store). 2015-2024 papers can now
  be approved by DAILY_CHECK §6; round 4 (40 leftover flagged + fixed items) not yet made. Backlog 2014 processed
  (30 papers, batch b20261102-1259, state claude_check): fixes 'Turn over for Question n' = page furniture,
  '(b) (i)' on one line with a tall fraction = one cut (no sliver). 2015-2026 extract output unchanged
  (all 477 compared), golden 0 changed cuts. Next run: overviews of the 30 2014 papers, then round 4.
- 2026-11-02 13:39-14:25 UTC (hourly backlog run): 2014 Claude check: overview of all 30 papers looked at; 27 ok, 3 needs_fix:
  figure crop starts on a prose row that an inline fraction splits ('one tenth (1/10) of …' in 2014 ON 11 q32 = ON 12 q24;
  'ρ = m/VA' with VA hanging below the line in ON 62 q1(a)(iv)). Fix drafted, not committed to the pipeline:
  pipeline/experiments/prose_rows_wip.patch (layout.split_prose_rows; mcq_figures with ends=False). Compared over all 514 papers:
  pair rule (mcq) changes only the two 2014 crops + 2018 FM 12 q38 (crop no longer includes the stem, but the store then keeps
  q38's options as one figure instead of optA-D: check before accepting). The 'end piece' rule cut option D off 2024 ON 22 q1 and
  the find_figures use changed 3 caption-only crops (2021 ON 63, 2023 ON 61, 2020 MJ 51): not used. Round 4 not made yet.
  Store 'differ' items in 2014 are MS rows with 1-2.6% extra ink (0 missing).
- 2026-11-02 14:44-15:40 UTC (hourly backlog run): 2014 crop fix finished and in the pipeline: MCQ figures use
  layout.split_prose_rows (pairs only: 'one tenth (1/10) of …' printed in pieces is prose); find_figures counts a short
  denominator hanging below the end of a prose line ('ρ = m/VA') as prose. Compared find_figures over all 2014-2026 question
  papers: only 3 crops change, all better (2014 ON 62 q1(a)(iv); 2021 ON 63 q3(c) and 2023 ON 61 q3(b)(iv) caption-only
  'Table 3.1' crops no longer take the 'hO' denominator); mcq rule: 2014 ON 11 q32 = ON 12 q24, and 2018 FM 12 q38 (stem was
  inside the option drawings; now the stem is text and the options are one figure, options_on_figure). Golden 0 changed cuts.
  2014: all 30 Claude-checked ok -> round 4 published (70 items, 40 flagged), state your_review. 2013 processed (30 papers, 0 blocking, batch b20261102-1539; 86 figure warnings to look at), state claude_check.
- 2026-11-02 16:00-16:45 UTC (hourly backlog run): round 4 has no answers yet. 2013: older papers have a 'For Examiner's Use'
  column (long vertical rule + heading at the right edge) that figure crops took as drawing ink (crops grew up to the stem line and
  out to the margin): clean.strip_examiner_column removes it (only where the rule and the heading are both found). Scanned all 477
  2014-2026 question papers: none has the column, so their cleaned PDFs are unchanged; golden 0 changed cuts. 2013 re-run: 0 blocking,
  figure warnings 86 -> 1. Claude check of 2013 started: 6 ok, ON 13 needs_fix (q34 MCQ figure crop leaves out the 'insulated
  connecting wire' labels above/below the drawing). Next run: fix that crop, overviews of the remaining 23 2013 papers.
- 2026-11-02 17:13-17:50 UTC (hourly backlog run): round 4 is being answered (2 of 70: 2014 MJ 62 q1 ok; 2014 MJ 51 q1 wrong:
  "Figs 1.1 and 1.2 missing from the figure section"). Cause: side-by-side captions printed as ONE text line ('Fig. 1.1      Fig. 1.2')
  never matched as captions, so those figures were never cropped. Fix: extract.split_captions (one line per caption, placed by
  search_for; also splits the line's ink box in find_figures); when the split figures' drawings are joined (bench line, labels between)
  each caption gets the whole row. checks.py uses the same split. Scanned all 537 2013-2026 question papers: 28 papers have such lines
  (3 in 2013, 3 in 2014, 22 in 2015-2025); all 67 new figure crops looked at (contact sheet + store SVGs in Chromium). Only those 28
  papers changed in bank/ (figures added, caption line left out of question text); golden 0 changed cuts; checks 0 blocking.
  2013 Claude check not continued this run (raw PDF fetch took 9 min). Next: rest of round 4 answers, ON 13 q34 crop, 2013 overviews.

## Own consistent MS layout, year by year (2026-11-03)
- Done: MS cut widened to the real table edge (ms.py); golden 0 changed cuts.
- Done: 2016 MJ re-run, `ms_layout.py` (own frame, header once, Total row), `ms_p` stored, review round 5 published (41 items).
- 2026-11-05: round 5 closed (37 ok, 4 wrong -> fixed). 2016 ON built; round 6 on the NEW review page (portal.json).
- 2026-11-05 13:10: round 6 closed (43 ok, 3 wrong -> option clean-cut rule). 2016 MJ APPROVED (Dhruv). Symbol library: later, after all years (also: drawn ✓/✗ -> text).
- 2016 ON APPROVED. Round 8 = 2017 MJ+ON (strict, risk-based) on review page 2017. Waiting: his round 8 answers, approval of 2017 (FM+MJ+ON), his answer on a standing approval rule. 2017 MJ qp_11 missing. Rounds 8 (2017 MJ/ON), 9 (2018), 10 (2019) on ONE review page (portal.json review_url, button per year). Standing rule: approve a year after its round once wrong items are fixed (2017 FM approved). Next: 2020.


## Usage per year (Dhruv 2026-11-09: track speed and capacity)
Effective tokens = input + 0.1 x cache reads + 2 x cache writes + 5 x output (from the session transcript). Weekly % = Dhruv
reads it in Settings > Usage before/after a year (I cannot see it).

| Years | Dates | Effective tokens (M) | Share of that stretch | Weekly % (Dhruv) |
| --- | --- | --- | --- | --- |
| 2021-2023 | 2026-11-06 | 8.2 | 34 % | - |
| 2024 (+ start 2025-26) | 2026-11-07 | 9.5 | 39 % | - |
| 2025-2026 + round 20 | 2026-11-09 | 6.6 (to 14:00) + round 20 fixes | 27 % | - |
| round 20 fixes + 2013-2015 + round 21 | 2026-11-09 12:30-18:30 | - | - | 15 % (Dhruv) |

- NOT DONE (recorded 2026-11-23): maths 2019 May/June (0607 2019-MJ) - skipped in M3 by Dhruv's choice, PDFs missing; later batch M3b. Also not done: 2002-2012, the ~60 raster MS picture redraws of M2, 3 vector-bracket defects (pattern 240), MongoDB push of everything.
