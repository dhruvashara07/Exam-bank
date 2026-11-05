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
