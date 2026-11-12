# Progress

Read this first in every session. Update it before ending a session.

## 2002-2012 (started 2026-11-09, batches of 3 years) - why: docs/AGENT_GUIDE.md, how: docs/PLAYBOOK.md, mistakes: docs/ERROR_PATTERNS.md
- NEXT: waiting for Dhruv's next plan (cleanup done 2026-11-12). Every year 2002-2026 approved; nothing pushed to
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
