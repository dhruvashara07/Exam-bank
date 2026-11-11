# Conversation log and decisions (newest at the bottom — add an entry after every working session)

Purpose: a new Claude chat reads this after CONTEXT.md so it knows what was decided, why, and what Dhruv said.
Rules for Claude: append a dated entry at the end of every session (what he asked, what he answered, what was
decided, what was built, what is open). Never rewrite his decisions; if one changes, add a new entry that says so.

## Working style (stable)
- Dhruv: teacher in India (IST), reads on his phone. Short, plain answers; exact steps when he must do something.
- Plan first, explain decisions, criticise his ideas honestly, ask before big changes, "check first, then plan, then proceed".
- He is usage-conscious: do NOT rebuild everything or run expensive jobs unless approved; prefer samples first, then year by year.
- He reviews only flagged questions and a few spot checks.

## 2026-11-03 — v5 format session (claude.ai chat, IST morning)
Asked: read the docs, go through docs/V5_SPEC.md (explain + criticise), build v5 on a few hard papers incl. his round-4
problem questions, show examples (question-bank view, print view, renumbered worksheet PDF) before any rebuild.
Hourly task trig_0173DCrQWm76nnTXrW52TPjC stays OFF until he approves.

His answers / decisions:
1. Question-bank view: remove blank working space and full-width dotted answer lines. KEEP dots inside a sentence
   (fill in the blank), the last answer line with its label/unit (`m1 = ....... g`), tables to complete, grids/graphs to draw on.
2. Review page / Claude artifacts: leave public (no need for private).
3. Final website will make the "stored as text" vs picture distinction clear (not needed on the review page now).
4. He answered more than 2 questions in review round 4 (70 items: 50 ok, 20 wrong); general instruction from him:
   tables are text built from the layout (never pictures unless a cell holds a picture/graph).
5. Pilot papers for v5: yes. Claude chooses the worksheet parts itself (incl. "(b)(ii)" -> "(a)" case, cross-question reference). Read his round-4 answers: yes.
6. Stale lock in review/backlog.json (`running_since`, from a run that crashed 2026-11-03 00:06 IST): NOT cleared.
   He said: if not necessary, leave it. It blocks nothing while the task is off; clear it when the task is switched back on.
7. Renumbering safety: tested 376 cases (pilot questions x new numbers 1, 9, 10, 12): no line overflows; the only word
   overlaps (Greek letter + "/") already exist in the original layout. Worksheet numbering = questions 1..n, parts relabelled
   in print order, figure/table numbers follow, references follow.
8. Built (pilot papers only, pushed): pipeline/store_v5.py, renumber.py, store_view.py; store.py schema 5: captions are layout
   text (figure file = drawing only); if drawing ink shares the caption row the caption is blanked in the file
   (`caption_masked`, `caption_box`) and stays layout text; tables as text; tagged numbering roles; answer bands;
   golden.py check = 0 changed cuts (2014 MJ 52 q04 now cuts Fig 4.1).
9. MARK SCHEMES -> PORTRAIT (decided 11:10 IST): Cambridge mark-scheme PDFs are portrait up to 2016 FM and mostly landscape
   (4 columns Question | Answer | Marks | Guidance) from 2016 MJ to 2026. Stored landscape width 726 pt vs portrait 523 pt.
   Dhruv's decision: make them PORTRAIT like the question paper, same table look, text at the question-paper font size,
   pictures scaled to fit; text wraps to more lines (3 -> 4-5), that is fine. Reason: consistency, no rotation, good for print.
   Claude's plan: keep the original landscape layout stored; build a second "portrait" layout by re-wrapping the cell text;
   rows that cannot be re-wrapped (stacked fractions, table in a cell, graphs) are scaled to fit and listed for review;
   check = every word present in order, nothing overflows, marks add up (pixel compare is impossible for a re-wrapped layout).
10. Process agreed 11:14 IST: build SAMPLES on 3 papers (2019 MJ 42, a 2022 paper, 2014 MJ 63), show results, he approves,
    then move YEAR BY YEAR (not one big rebuild). Add this log to the repo each session.

Open at end of this entry: practical-paper mark schemes are one block per question; MS row labels like "(a)(i)(ii)" not relabelled;
"°C" glyph in some 2014 mark schemes; 63 q02 Fig 2.1 crop edge includes the neighbour's label leader; v5 rebuild of other years,
review-page upgrade (spec H), BACKLOG.md update and switching the hourly task on all wait for his approval.

## 2026-11-03 (later, 11:30 IST) — portrait mark schemes: sample built, waiting for Dhruv's look
Dhruv: "sample, then give results, then year by year". Built `pipeline/ms_portrait.py` (+ `ms_portrait_view.py` picture tool); NOT yet part
of `store.py build` (nothing stored; the store still holds the landscape layout only).
Result over ALL stored landscape rows (2016 MJ - 2026 MJ, 9,007 rows): 8,759 (97.2%) re-wrapped to portrait at the question-paper
font size; 248 (2.8%) fall back to "scale to fit" (99 picture/drawn symbol in the row, 85 unknown rules (dashed or white boxes),
42 fraction bar, 18 table inside a cell, 4 other). Word check (all words present, nothing past the margin): 1 problem row
(2022 FM p32 q11 11(a), overflow). Wrapped rows grow in height by at most ~1.7x (2026 practical tables), typical rows +1-2 lines.
Handled: 3-, 4- and 5-column tables, marks column kept at its width and aligned to its lines, blank gaps between marking points,
bullets with hanging indent, sub/superscripts, underlines follow their words, right-aligned "Total:", grey rule colours.
Next (needs his OK on the samples): store the portrait layout as `layout_p` per row in store.build, verify (word check + spot pictures),
improve picture rows (keep the picture at natural size, wrap the text), then year by year.

## 2026-11-03 (13:15 - 14:00 IST) — mark-scheme table analysis, rules, narrower columns
Dhruv: question-number and marks columns are too wide; widths must follow content; first analyse the table types, then make rules and a report; ask if needed.
Done: scan of every stored MS row -> docs/MS_TABLE_RULES.md (types T1-T8, content widths: question label typically 32 pt (99% <= 43), marks about 14 pt;
printed columns were 58-64 and 45-50). Report sent to him.
His answers: header row ONCE AT THE TOP (short names Q / Answer / Marks); old portrait years 2013-2016 FM KEEP AS PRINTED; rows with a picture NATURAL SIZE.
Also: he does NOT want side-by-side pictures of two tables - the final MS is ONE portrait table, question after question (the side-by-side was only my comparison).
Built: widths by content (per mark scheme, same for all rows), label centred / marks right-aligned, picture rows at natural size, header row, glue of
unspaced words ("30 s"). Result: 97.5% of 9,007 rows re-wrapped, 2.5% scale-to-fit, 0 word-check problems.
Open: his OK on the new sample pictures; then store `layout_p` per row (+ header) in store.build, verify, year by year from 2016 MJ. The v5 rebuild of all years and
the other open items (see earlier entries) still wait for approval; hourly task still OFF, stale lock untouched.

## 2026-11-03 ~15:00 IST — cropped table (2016 MJ 41 q10), own consistent layout, year by year
- Dhruv saw picture 4 (diode row): right/left borders cut, "Total" without number.
- Cause: MS cut box was always x 58 – 784 (page width − 58). Some papers print the table wider (2016 MJ 41/42/62/63: words to x 791–798, border to 803), so marks digits, totals and the right border were lost in the STORED data (not a portrait problem). 2016 MJ papers 31–33, 43, 51–53, 61 fit. Other years not yet measured.
- Fix (pipeline/ms.py): cut right edge = max(784, real text/vertical-rule extent + 3). `golden.py check`: 0 changed cuts. Needs re-run of the year to refresh stored rows.
- Dhruv: not strict about the original layout; wants ONE consistent layout of our own.
- His answers: Total = own last row of the question's table; frame = full black frame (left/right borders, lines between rows), same every year; first year = 2016 MJ; review = review page + tracker, next year only after he ticks the year.
- Plan per year: (1) re-cut with the wider box, (2) rebuild rows in portrait with own frame + Total row, (3) check (all words, marks total, nothing past edge), (4) put on review page + tracker, (5) Dhruv ticks, (6) next year.
- Not touched: hourly task stays OFF; stale lock not cleared.

## 2026-11-03 ~16:30 IST — Year 1 (2016 MJ) built in the new layout, review round 5
- Dhruv: "do 1 year, we check at the end, give me the review link"; new qp + ms layout (figure labels as text, portrait MS).
- Done for 2016 MJ (18 papers): re-run with the wider MS cut (ms.py), v5 store (captions as text), NEW `pipeline/ms_layout.py`: portrait MS per question with our own frame (black left/right border, line under every row), header once (Q | Answer | Marks, "Mark" -> "Marks"), "Total" as its own last row (Total left of the marks column, number under Marks), stray narrow columns/borders dropped. Stored as `ms_p` in each question JSON (store.build; header attached after the header file exists). Review pictures use `ms_p`.
- 78 non-MCQ questions: 295 rows wrapped, 18 rows scaled (fallback, e.g. 41 q01 one row), 0 word-check problems.
- Review round 5 (41 items, 5 flagged) published on the review page; round 4 (2014) was replaced. Needs: Dhruv's look, then Claude check, then tracker/approval, then 2016 ON.
- Known: a row scaled to fit looks smaller inside a wrapped table (fallback); tiny border nub at the right edge on the last row before Total.

## 2026-11-05 12:10 IST — round 5 answered, fixes, 2016 ON started
- Round 5 (2016 MJ): 37 ok, 4 wrong; closed (review/rounds/5.json). Fixes (pipeline, not single files):
  23 q31 review legend listed the bank's 2 figures, store has 1 -> legend from the store (review_svgs fig_ids);
  33 q10 header "Expected answer" -> own header names always Q | Answer | Marks (| Guidance) (ms_layout._header_unit);
  41 q01/q04 rows scaled: grey header remnant (y<=0.6) and white cell backgrounds made `_rules` fail -> ignored (2016 MJ fallback rows 18 -> 4);
  paper 43 prints no Total -> own Total row from the question's marks (ms_layout._own_total).
- Dhruv: MCQ options that are separate pictures must NOT carry the printed A-D letter -> diagram_options(with_labels) crops the drawing only, letter blanked if inside (letter_masked). Units stay with their number ("1.0 cm").
- Dhruv asked about a reusable symbol/notation library (voltmeter etc.). Answer: rendering stays exact vectors (best fidelity); library = later separate step (find repeated small drawings, store once as symbols, tag questions; notation list for the editor). Waiting for his choice.
- approve.py for 2016 MJ was blocked by the permission check: needs Dhruv's explicit "approve 2016 MJ".
- 2016 ON processing in the new layout -> round 6 (2016 ON + the 4 fixed items).
- (later, same day) 2016 ON built. New fixes found while checking it (pipeline): MS cut also widened to the LEFT (2016 ON 43 labels at x 56 were cut off);
  rows trimmed to their own table (`ms_layout._tighten`: empty page margins were becoming blank columns); header built entirely by us from the
  columns (Q | Answer | Marks [| Guidance]); Marks column min 40 pt; underline on part of one word ("evaporation/evaporated") kept instead of scaling.
  2016 MJ + ON re-run (cut change; golden 0 changed cuts). Scaled rows: MJ 2, ON 3. Every question ends with a Total row except 3 (Total inside a scaled row).
- Option pictures still wrong (flagged in round 6, not fixed yet): 2016 ON 12 q21 (option A has part of the question sentence), 23 q15 (table-row options),
  11 q06 (check B), 2016 MJ 12 q06 (piece of next option's label).
- Review round 6 = NEW review page (old one full: 511-file limit): review/portal.json review_url updated. 47 items (8 rechecks/known issues first).

## 2026-11-05 13:10 IST — round 6 answered, 2016 MJ approved
- Round 6: 43 ok, 3 wrong (all option pictures). Dhruv's rule: split MCQ options into separate pictures ONLY when a clean cut is possible;
  otherwise keep ONE whole figure (with its letters). Done in store_options.diagram_options: no drawing piece or label may cross into
  another option's cell, nothing of another option may show inside an option's crop, question sentences (>=5 words or ending "?") are not labels.
  2016 MJ 12 q06, 2016 ON 12 q21, 23 q15, 11 q06 are now one whole figure each (checked: no sentence, all labels whole).
- 23 q15: options are a table of drawn ✓/✗ (not text) -> whole figure for now; turning drawn ✓/✗ into text goes with the symbol library.
- Dhruv: "approve 2016 MJ" -> claude_check ok + approve.py for the 18 papers. "symbol library later" (after all years).
- 2016 ON not approved yet (needs his word). Next: 2017 FM.

## 2026-11-05 ~14:30 IST — 2017 FM built, option-picture split made safe, round 7
- 2017 FM processed (6 papers; 125 MS rows all re-wrapped, 0 problems, every question with header + Total row).
- While checking option pictures found real defects in the split (also in 2016): straight lines have no area so they were dropped from
  option crops (wires/wave lines missing); a PDF path holding many lines was skipped as a "frame"; a cell split could give one option
  lines of its neighbour. Fixes (store_options): pieces get their stroke width; only a single-rectangle path is a frame; an option
  whose pieces have a >30 pt empty gap is not split; FINAL TEST: every drawn piece and label near the options must appear WHOLE in
  exactly one option picture, otherwise ONE whole figure. 2016 MJ/ON + 2017 FM MCQ papers rebuilt: 32 split sets (all looked at), 24 whole.
- Round 7 published on the review page (27 items: 3 rechecks + 2017 FM). 2016 ON still waits for Dhruv's "approve".

## 2026-11-05 15:52 IST — speed-up: one year per round, risk-based review
- Dhruv: approve 2016 ON (done); round 7: 26 ok, 1 wrong (2017 FM 12 q20: wanted 5 pictures = question drawing + 4 clean options)
  -> option columns are now cut at the WIDEST white gap between letters (_free_cut), all splits re-checked.
- Dhruv: do a whole YEAR at a time, faster; stricter tests; show him only flagged items and those I think need him; check whether random samples are worth it.
- Trend rounds 5-7: random samples 96 -> 4 wrong (all round 5, MS layout, fixed globally); rounds 6-7 0/60 wrong. All wrong answers ever: option pictures or MS layout.
- New: review_round.py --risk --spot N: items = automatic flags + risk_reasons() (option splits, shrunk MS row, missing/incorrect own Total, header,
  MS word-check, table as picture) + N random per round. Year = one round.
- Asked him for a standing approval rule ("approve a year when its round has no wrong items left after the fix"); until then he says "approve <year>".
- 2017 MJ + ON processing; round 8 = all of 2017.
- (16:30-17:30) 2017 MJ+ON processed. My pre-check found + fixed: long option labels treated as question text (only "?" sentences or text
  outside every option cell are sentences); practical MS label "4 MP1" not recognised -> Q4 rows under Q3 (ms.label_text strips MPn;
  2016-2017 practical papers re-run; golden 0); printed Total that disagrees with the marks -> we show the question's marks, flagged.
  New strict checks in risk_reasons: MS rows of another question, more than one Total row. Rounds keep only figs.jpg per question.
  2017 MJ qp_11 is missing from raw/ and Releases (told Dhruv).
- Round 8 (all of 2017 MJ+ON, 54 items, 49 risk items + 5 random) on a NEW page per year: review/portal.json updated.
- (17:45) 2018 (FM+MJ+ON, 42 papers) processed and pre-checked: 0 blocking; all 33 split option sets looked at. Fixed: options sharing a
  "key" legend are never split (2018 MJ 12 q36, 2018 ON 11 q37 -> one whole figure). MCQ 2016-2018 rebuilt, golden 0 changed cuts.
  Round 9 (2018, 50 items: 45 risk + 5 random) on its own page (portal.json "pages").
- (18:15) 2019 processed + pre-checked (42 papers, 0 blocking). Fixed: 2019 ON 42 mark scheme is a landscape page printed shrunk on
  portrait paper -> footer found higher up (ms.py) and rows scaled back to 11 pt (ms_layout._unshrink) so it gets our layout;
  options sharing a compass rose (N E S W) stay whole. Golden 0. Round 10 (2019, 64 items) on its own page.

## 2026-11-05 17:29 IST — one review link; standing approval rule
- Dhruv was confused by 3 separate pages (rounds 8, 9, 10). Now ONE page (review_url in portal.json) with a button per round/year
  (2017 | 2018 | 2019), progress shown on each button; rounds live in r<n>/ folders listed in rounds.json (site/review/index.html
  supports this). Old per-year pages are no longer used (none had answers). Figures merged into the "Rebuilt" picture to stay under 511 files.
- STANDING RULE (Dhruv): a year is approved after its review round once the wrong items are fixed: no separate "approve" message needed.
  Applied: 2017 FM approved (round 7 done, its wrong item fixed). 2017 MJ/ON, 2018, 2019 get approved when rounds 8/9/10 are answered and fixed.
- 17:37 Dhruv: keep adding rounds to the one link as years are done; take a round off when he finishes it; he starts at round 8; go on up to 2021.
  New pipeline/review_page.py (add/drop/files) keeps out/review/page/ = the published page. The "wait for 2019 run" task that ran 47 min
  was my waiting loop matching its own command line (pgrep -f): stopped; no more waiting loops.

## 2026-11-05 18:44 IST — new review plan: I check flags first, pattern by flag type, one year at a time
- Dhruv: pause 2020/2021. He had not noticed the flag reasons before 2019 and may have missed some; most flags turned out correct.
  New loop per YEAR: build -> I check every flagged item myself and improve the pipeline -> only items I am unsure of go to his round
  -> his corrections -> approve. Be pattern-aware: learn which flag types are really wrong.
- Precision of flag types (rounds 5-10, his answers): MS row shrunk 95% wrong, figure crop cut 80%, MS no Total 80%,
  stored copy differs 11%, option split 10%, random 4%. So: fix the first three myself; check the others myself, show only doubtful ones.
- Round 10 (2019): 20 wrong. Decisions: truth-table options stay pictures (my choice, he said "you choose"); "no MS in pdf" flags are not shown.
- Figure crop mend (store.fit_crop): take in short labels half inside / just outside (axis labels, axis-number rows, "diagram 1"),
  cut question sentences half/fully inside above/below the drawing, take in drawings crossing an edge (<=40 pt), never past the caption,
  never answer lines or part labels. Dry run 2016-2019: 147 of 2822 figures change, sheets checked.
- Asked him: when I am sure a fix is right, show it once or approve directly?

## 2026-11-05 — full check-up of 2016-2019 (Dhruv: "do full check up of 2016 to 2019 so we are assured that that is fully approved")
- His accidental "retry" started a parallel branch (commit 8e92e514, pipeline/audit.py); kept it, only one session now.
- Audit of 2292 questions: 60 flags. Real problems fixed in the pipeline (all years):
  fraction bars lost in re-wrapped MS rows (about 20 rows, incl. approved years) -> such rows are drawn cell-wise and keep the bar;
  inner-table vertical rules dropped in cell rows (2017 ON 42 q9b); stroked zero-height underlines had no ink;
  short underline pieces / underlined words no longer make a row fall back; empty band + printed Total cut from cell rows;
  figure crops took in the tail line of a wrapped question sentence ('pattern.', 'provided.') -> cut out;
  own Total added unless a real 'Total: n' is printed (2018 FM 42 q9, 2019 FM 42 q1).
- Cleared myself: 9 'no MS row' (Cambridge numbers MS parts differently from the QP, content complete), 9 marks sums (OR / 3 x B1),
  15 'stored differs' (photos/anti-aliasing, checked the two biggest side by side).
- Round 13 "2016-2019 final" on the one review page: 5 items (2017 ON 41 q8 table, 2019 MJ 62 q4 formula, 3 samples of the new fraction/table rows).
  Rounds 8-11 taken off the page (r11 = 2020, unanswered, to be redone under the new plan).
- 21:46 Round 13: all 5 wrong. Dhruv: MS rows with fractions/tables must use the NORMAL font size and grow taller ("do that for others also");
  make a guideline; inner tables recreated at that size; 2017 ON 41 q8 rows messed/repeated; 2019 MJ 62 q4 formula as text, not image.
  Fixed in the pipeline (docs/MS_TABLE_RULES.md section 9): band-by-band cell rows at normal size, narrower inner-table columns,
  re-wrap of too-wide text bands, MS rows in printed order, heading rows, grand-total cell dropped, formula rows beside a figure cut out of it.
  2016-2019 rebuilt; audit clean (only kinds I clear). Round 14 (7 items: his 5 + 2 of the same kind) on the page, round 13 closed and removed.

## 2026-11-06 — round 14, then 2020
- 11:26 Round 14: 6 ok, 1 wrong: 2017 ON 41 Q8 "why numbering is weird please check original". Checked: our MS matches the printed MS
  exactly (the MS gives one full (a)(b)(c) answer set per process: 8 Hydroelectric, 8 Tidal flow, 8 Waves); kept as printed, told Dhruv.
- He: "update our convo and context, and if that que fixed then move to 2020".
- 2016-2019 approval: approve.py was blocked by the permission check (needs his explicit "approve"); asked him.
  2016 FM is not part of this: it belongs to the old portrait-MS era (2013 - 2016 FM, kept as printed, no own header).
- 2020 started under the new plan: rebuild with all fixes -> audit -> I check every flag -> short round with only doubtful items.
- 2020 (new plan): rebuild + audit, 33 flags, all checked by me. Fixed in the pipeline: page-split continuation rows (empty Q column, header
  strip), bands spanning all columns ("Additional graph notes") re-flowed into the Answer column with hanging indents, figure crops end
  at their caption, inner-table edges at the row bottom kept, indented tables use their blank space before any shrink.
  Cleared myself: Cambridge numbering slips (2020 ON 41 "7(b)" twice), printed mark codes (2020 ON 42 1(b) B1), OR routes.
  2016-2020 rebuilt: no figure flags, no shrunk MS rows. Round 15 "2020" (4 items, new row kinds only) on the page; round 14 removed.
- 12:36 Dhruv: EVERY mark scheme in our guideline layout, all years (consistency) - also the old portrait ones (overrides the
  earlier "2013 - 2016 FM keep as printed"). Approve = final check in git; MongoDB stays paused until everything is done.
  For a layout decision I make: send a side-by-side picture (original | ours) in the message instead of review items.
  Round 15 answers: 2020 FM 32 q6 centre the inner table in its cell + bottom edge ("responsive": landscape original -> portrait ours);
  2020 MJ 31 q11 page split = one cell, one Q label, no line across the Q column; 2020 ON 51 q4 only MP1-MP7 (notes under the table
  are not this question's MS); 2020 MJ 53 q3 'Method' is question text (already so).
- Done: old portrait MS -> our table (ms_layout._old_rows: one row per part, labels n(a)(i), marks bold, our Total, printed
  [Total] dropped, superscripts kept on their line); centred inner tables with their bottom edge; one Q cell across page splits;
  notes printed under the table dropped. 2016 FM - 2020 ON rebuilt, audit clean (only kinds I clear), 90 papers approved
  (final check in git; MongoDB sync is paused in bank.yml). 2016-2020 complete. Next: 2021 under the new plan.

## 2026-11-06 afternoon — build ahead on GitHub, 2021
- 13:36-13:40 Dhruv agreed: GitHub builds the coming years in the background (bank.yml workflow_dispatch input 'sessions',
  pipeline/session_papers.py); I check one year at a time; he can chat meanwhile. 2022-FM .. 2026-MJ built in 9 minutes
  (about 45 s per session on GitHub; my earlier "45 min per year" estimate was this container). My pushes use SKIP_WAIT=1
  while a long build runs. 2025/2026 were approved long ago in the old layout: re-check them like every other year.
- 2021 check (all flags looked at): inner tables read as extra MS columns -> drawn inside the answer (expected column count
  from the printed header names); store.py builds every MS again once the paper's header file exists; figure crops may follow
  their drawing past the caption (2021 ON 63 q1 magnified scale, growth limit 50 pt); side-by-side 'or' alternative tables are
  reflowed at the normal size (text wraps inside each cell, underlines and subscripts kept) instead of being shrunk.
  This also improved 8 mark schemes in 2016-2021 (incl. approved years): side-by-side pictures sent.
- Round 16 "2021" (4 items) on the review page.
- 18:56 Round 16: 2021 FM 32 q11 inner table must keep the ORIGINAL alignment (centred) - general rule "horizontal responsiveness";
  2021 ON 32 q6(a) marks column has sub-row lines; lines of the 9(b)/6(c)(i) tables stopped short. All fixed (MS rules section 10).
  2021 approved (final check in git). He: "2016-2021 full and final after review fix, now next".
- 2022 check: side-by-side figures keep only their own ink (only when a neighbour figure's box overlaps beside ours; the
  neighbour's words inside our crop are blanked); hidden text under MS label pictures dropped; white lines skipped;
  a fraction wraps with its text line. Round 17 "2022" (4 items) on the page.
- 20:26 Round 17: 3 ok; 2022 FM 62 q2 -> his rule: side-by-side figures that cannot be cut without overlap = ONE whole picture
  of both (nothing blanked) (MS rules section 11). 9(b) middle line now starts/ends on the row lines. Rebuilt 2016-2022 (this also
  merged 2018 MJ 63 Fig 1.3+1.4, 2020 ON 33 and 41 Fig 3.1+3.2: labels intertwined; checked). 2022 approved (final in git). Next: 2023.
- 2023 check: MS rows were cut at the last text line when the answer is a PICTURE (ms.py row extent now includes pictures,
  rotation-aware, no 6 pt specks): 25 rows in 2016-2026 re-cut (incl. approved years; all checked side by side, fixed);
  bullet-list lines above a figure stay question text (fit_crop); a table with a note under it reflows at normal size;
  baselines within 3 pt are one line in reflowed cells. Round 18 "2023" (4 items) on the page.
- KNOWN, not fixed: 2019 ON 41 q9(a)(ii) MS - the hatched circles (protons) show as plain circles (the hatching is a pattern of
  tiny images we cannot place); told Dhruv.
- 21:44 Round 18 (2023): 1 ok, 3 wrong + his notes. Fixed in the pipeline (all years rebuilt, every changed question checked side by side):
  inner-table top edge kept apart from the sub-row line (a sub-row rule must run across the whole answer cell); a lost table
  top/bottom edge drawn; the same inner-table design in several sub-rows = ONE set of column widths (his rule: max needed);
  notes printed UNDER the table ("Additional graph notes") are not the last question's row (ms.py: row ends where the column
  rules end; 2020-2023 ON 51/52 q4); diode row no longer swallows the next row's picture; MS pictures off the cell rules;
  hatched shapes (tile patterns) rasterized; row lines that stopped 1-4 pt short of the frame now meet it (1000+ rows, all
  years); a one-line 'MP2   text' wraps under its text; label/marks words move as one piece ('8 (a)(ii)', '2 × 1');
  '• ' bullets with a space recognised (2023 MJ 41 q7 bullets had run together); a line filling its cell is not 'centred';
  a note under an inner table no longer blocks the table's own indent (2022 ON 42 q2 table back to its printed width);
  the PAPER total '[Total: 80]' dropped from the last row (2016 MJ 43); symbol-font characters (× ± ° • γ ...) drawn in
  Liberation Sans = printed width (DejaVu was a third wider and ran into the next word: '±1°', '×10').
  New audit checks: ms_edges (line in the air / short of the frame), ms_bullet, ms_overlap. 2016-2024: 0 of these.
- Answered him: shared code = the pipeline makes every JSON, so a fix is made once and the years are rebuilt; only changed
  questions are committed and checked. Unflagged questions pass the audit but are not all looked at by eye (honest).
- 2023 approved (final in git). Next: 2024.
- 22:01 Dhruv: "all images are good"; asked what "shared code" means (answered: the pipeline makes every JSON); "continue, give me
  2024, don't leave any error unresolved".
- 2024 check (and every changed question 2016-2024 looked at side by side, ~110): fixed in the pipeline: sub/superscripts stay with
  their line in an inner table (a² b², 2024 MJ 42 q1); an underline moves with its word in a narrowed table; lines Cambridge
  wrapped inside a reflowed table cell are joined before re-wrapping (2024 MJ 43 q10); a row cut a few pt below its own bottom
  rule ends on it (double line, 2024 ON 31 q7(c)); symbol characters still wider than printed are drawn a little smaller
  ('ΔθOR'); Symbol-font big-bracket pieces mapped to real bracket pieces (2023 MJ 43 q1 showed 'æ ö ç è ø').
  New audit checks: double row line, underline not under its word, bracket letters. All 2016-2024: 0 of these.
  Not fixed (Cambridge): 2024 MJ 21 q14 "Question Discounted" in the MS (no answer key - correct as printed).
- Round 19 "2024" (5 fixes worth a look) on the review page; round 18 removed.
## 2026-11-07 — round 19, 2024 approved
- 20:17 Round 19: 3 ok, 2 wrong. 2024 MJ 43 q10(c): Cambridge drew no rule before the empty Marks cell -> the row got 2 columns;
  fixed (a row that lost a column rule gets it back from the other rows of the question, `_common_columns`). 2024 ON 31 q7(c):
  his rule = tick in the exact centre of its box, label a small space after it on the box's middle line (MS rules 12).
  Found while checking: labels printed in the MIDDLE of their cell (2019 ON 33 q11, 2016 MJ 41 q10(a)(ii)) were cut 4 pt above
  the label, splitting cells; ms.py now starts such a row at the Q-column rule above (scanned all 2016+ MS: only these 2 papers).
- He asked why the build took > 1 hour (my full local re-cut of 2016-2024, not GitHub) and about "Review website" failure emails
  (two Pages deploys at once cancelled each other; site.yml now queues deploys: cancel-in-progress false).
- 2024 approved (final in git). Next: 2025 (re-check in the new layout), then 2026.
## 2026-11-07 / 11-09 — 2025 + 2026 together, round 20
- 20:39 (11-07) Dhruv: "do both together and generate review for both" (2025-2026); repeated 11-09.
- 2025-2026 rebuilt with the latest code (66 papers, 4 min). Checked every flag + ~70 questions side by side; every MS that
  changed in approved years 2016-2024 (~110) checked side by side. Fixed in the pipeline:
  2026 MJ new 4-column MS (Guidance): own total row and header (examiner note under the header dropped), Guidance laid out
  per cell (spanning cells stay one, pictures kept side by side, root signs/fraction bars move with words), empty Guidance
  cell keeps its rule; colour-emoji ticks (2025 FM 42 q6) kept as pictures; a PDF run spanning two baselines split into
  words (2026 MJ 41 q7); fractions stay on their line (baselines within 1.5 pt one line; sub/superscripts follow their
  word; no-space words never split); text set out in columns without rules inside a cell (2019 FM 42 q11 gamma/beta pairs);
  Guidance paragraphs split at bold keywords and blank lines.
- Round 20 "2025-2026" (7 items, 2 marked doubtful: small inner table 2026 MJ 43 q5, bracket list 2026 MJ 32 q3) on the page;
  round 19 removed.
## 2026-11-09 — round 20 closed, 2025-2026 final
- 14:05 Round 20: 1 ok, 6 wrong. His asks: a consistent guideline for the Guidance column (column widths in proportion,
  pictures: readable size, move to their own line rather than shrink) - written as MS rules 13; ticks drawn as real ticks;
  normal font size for inner tables; Guidance lined up with its Answer line; fractions/roots in Guidance tidy.
  All fixed in the pipeline (ticks: dingbat + colour emoji -> ✓/✗/✔; touching pictures (>= 50 pt) = one picture; >= 60 %
  or own full-width line; inner table may use the whole Answer cell with slimmer padding before any shrink; brace lists
  re-wrapped at normal size with the brace stretched; Guidance anchored to Answer lines; a word printed across the row's
  bottom line makes the row grow). Every changed MS 2016-2026 checked side by side (one bug of mine found and fixed: small
  pieces of one drawing were merged, 2025 ON 43 q7). 2025-2026 final (approvals kept: cuts unchanged).
- He asked to track usage per year (tokens and weekly %): PROGRESS.md has a usage table; I can count tokens, he reads the
  weekly % in Settings > Usage.
- Older years: he did not answer which range -> I took 2013-2015 (already built, nearest the current syllabus); 2002-2012
  left for later (only a few papers built). His answer: old mark schemes go into our table (yes).
- 2013-2015 rebuilt and checked (~30 side by side + every flag). Fixed: answer '92' read as a label; plain-font and combined
  labels ('(iii)(iv)(v)'); Cambridge letter slip fixed from the question paper; braces/underlines stay with their part's row;
  brace joining two parts = one row; symbols in re-encoded fonts read by shape ('R' -> '='); marks column ('[1]', 'B1 [4]',
  'max. B2'); Q column widens for long labels (MS rules 14). Memory: a full-page 8x render took 3 GB (machine ran out and the
  build hung) -> rendered in strips, pixel-identical; 2016 MJ - 2026 unchanged (checked), golden 0 changed.
- Round 21 "2013-2015" (8 items) on the page; round 20 removed.
- 18:26 Round 21: 5 ok, 3 wrong (braces odd / over the row line; no [] in marks; '[5]' is a part total). Fixed for all
  old-layout MS (2013-2016 FM). 2013-2015 approved (96 papers, final in git). 2013 - 2026 ALL FINAL.
- He: usage today 15 % of the weekly limit (12:30 - 18:26). Asked how to use less and to prepare a new chat:
  docs/NEXT_CHAT.md written (start prompt + how to work cheaply).
## 2026-11-09 evening - new chat, 2002-2012 (Dhruv: "option A": 2002-2012 in 3-year batches, then cleanup + MongoDB push)
- Workflow agreed: 3-year build on GitHub, I check every flag, one short review round, fixes, approve, push; use usage only where it pays.
- Batch 1 (2002-2004) built on GitHub, then fixed locally (see PROGRESS.md "2002-2012"). Found: GitHub build had read old paper numbers wrongly.
  All 25 papers match their mark totals, 0 blocking checks. Old-layout mark schemes still to be put in our table (question to Dhruv).
## 2026-11-11 - questions on batch 1
- New chat: not after every batch by rule; when a chat gets long (about one 3-year batch per chat).
- Review round for each batch goes on the SAME review page (review/portal.json review_url), a new button per round.
- F/C column = target grade of each mark in old core Paper 2 mark schemes. Dhruv: add it to our table for those years
  (MS_TABLE_RULES 15). Batch 1 round waits for the old mark schemes to be in our table.
- Dhruv: no target-grade (F/C) column, remove it (done). Round 22 published for 2002-2004; finish review + fixes in this
  chat, then a new chat for batch 2.


- Round 22 answers: part totals shown twice, codes in the Answer column, 'TOTAL' text; 2003 ON 03 q11 MS numbering is
  Cambridge's slip. All fixed as rule 16; batch 1 approved. Dhruv: keep a list of error patterns so no mistake repeats
  (docs/ERROR_PATTERNS.md) and a step doc for new chats (docs/PLAYBOOK.md). Then do 2005-2007 here, new chat after.
\n
- Batch 2 (2005-2007) built and fixed; round 23 published (same review page). After it: fix, approve, new chat.
- Round 23 done; fixes = ERROR_PATTERNS 23-30; 2005-2007 approved. Dhruv asked: are old MS text or pictures? Text (re-typeset in our table, same as all years); only 2002 ON MS are page scans. Next: 2008-2010 in this chat.

