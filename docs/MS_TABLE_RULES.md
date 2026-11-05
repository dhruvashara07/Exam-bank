# Mark-scheme tables: types, rules and guidelines (portrait layout)

Status: rules APPROVED in principle by Dhruv (2026-11-03, answers in section 6); prototype built, samples sent, waiting for his look. Numbers come from a scan of every stored mark-scheme row
(2013 – 2026). Goal: one portrait table per mark scheme (like the question paper), column widths set by their content.

## 1. What tables exist (landscape era 2016 MJ – 2026 MJ: 9,007 rows; older years are already portrait)

| Type | What it looks like | Rows | Share |
|---|---|---|---|
| **T1 Standard** | Question \| Answer \| Marks (3 columns; some papers also draw a closing border) — theory and practical | ~8,390 | 93% |
| **T2 With guidance** | Question \| (MP label) \| Answer \| Marks \| Guidance (4–5 columns); practical papers 5/6 and a few theory papers | ~500 | 5.5% |
| **T3 Table inside the answer** | the Answer cell holds its own table, 6–18 columns (values, tick tables) | ~30 | 0.3% |
| **T4 Row with a picture** | a drawing / graph / logic gate in the answer | ~100 | 1.1% |
| **T5 Unusual** | dashed lines, white boxes, fraction bars, columns not detectable | ~130 | 1.4% |
| **T6 Old portrait era** | 2013 – 2016 FM mark schemes: already portrait, columns by position, mostly no vertical rules | ~2,900 rows | — |
| **T7 Multiple-choice key** | Papers 1 and 2: one letter per question (stored as `answer`, drawn by us) | — | — |
| **T8 Scans** | 2002 ON: page pictures | — | — |

## 2. How much space the columns really need (T1, all rows)

| Column | Content (widest line) | Printed width now |
|---|---|---|
| Question label ("3(b)(ii)") | typical 32 pt; 90% ≤ 36; 99% ≤ 43 | 58 – 64 pt |
| Marks ("B1", "C1 A1" stacked) | typical 14 pt; 90% ≤ 15 | 45 – 50 pt |
| Answer | wraps; 50% of rows fit in < 260 pt, 5% need > 580 pt | 610 – 625 pt |

So about 35 pt of the 523 pt page is wasted by the two narrow columns; the answer column gets that space back.

## 3. Rules for column widths (all types)
1. **Width follows content.** column width = widest line in that column + 12 pt padding (6 each side).
2. **Same widths for every row of one mark scheme** (one question, or one worksheet page) so it reads as ONE table.
   Widths are taken from the widest content of the whole mark scheme, not row by row.
3. **Defaults (T1):** question column 48 pt (widen to content + 12 if a label is longer, e.g. "10(b)(iii)"); marks column 34 pt;
   Answer = everything else (about 441 pt on a 523 pt page, was ~415).
4. **Header row** (only if we show one): at its own widths "Question" needs 54 pt and "Marks" 36 pt. Option: write "Q" / "Marks" or draw the header once at the top. (Question to Dhruv.)
5. **T2:** the label/marks columns follow rule 1. Remaining width is shared by Answer and Guidance in proportion to
   their demand (widest-line p90), each at least 120 pt so lines never become one word per line; an MP-label column
   ("MP1 variable chosen") = content + 12.
6. **T3 (table in the answer):** each inner column = widest cell + 8 pt; if the total is wider than the Answer column, shrink
   columns down to their longest single word; if still too wide → scale the row to fit (rule 12).

## 4. Rules for the content inside cells
1. Text keeps the printed font size (11 pt like the question paper) and style (bold, italic, underline, sub/superscript, colour).
2. Lines are re-wrapped at the column width. A line that runs to the right edge continues on the next; a short line is a hard break (lists stay lists).
3. Gaps inside a line are kept, so equations stay as printed ("P = 1.2 × 2.8 × 260 = 870 W").
4. Sub/superscripts stay glued to their word; underlines move with their words (split per line when the phrase wraps).
5. Bullets and "(a)", "(i)", "1." start a new paragraph with a hanging indent.
6. Blank lines between marking points stay; each mark ("B1") stays level with the first line of its marking point.
7. Right-aligned text ("Total: 7") stays right-aligned in the Answer column.
8. A row grows only as tall as its text needs; a row is not split across pages unless taller than a page.
9. Table borders keep their colour (black or the light grey of 2016/2025) and are redrawn for the new width.
10. **Row with a picture (T4):** picture keeps its own size (shrunk only if wider than the Answer column); text wraps around/above it. (Prototype still scales the whole row to 72% — to be fixed.)
11. Question label stays centred in its column, as printed.
12. **Fallback:** anything the rules cannot handle (T5, unknown marks) is scaled to fit the page and listed in the review with the reason. Target: under 3% of rows (prototype: 2.8%).

## 5. Checks (instead of the pixel check, which cannot compare a re-wrapped table)
- every word of the original row is present, same order; nothing past the right margin;
- marks total of the portrait row = marks total of the original;
- widths: no cell narrower than its longest word;
- spot-check pictures of ~10 rows per year, all fallback rows listed.

## 6. Dhruv's answers (2026-11-03, 13:2x IST)
1. Header row: **once at the top** of each mark scheme, short names ("Q", "Answer", "Marks", "Guidance").
2. Old portrait years (2013 – 2016 FM): **keep as printed**.
3. Rows with a picture: **natural size** (shrunk only if wider than the Answer column); text wraps; picture beside text -> scale fallback.

## 6b. Built and measured (prototype `pipeline/ms_portrait.py`, viewer `pipeline/ms_portrait_view.py`)
- Column widths per mark scheme from content (rule 3): question column 40 – 48 pt for 96% of questions (was 58 – 64), marks column 34 pt
  for nearly all (was 45 – 50); labels centred, marks right-aligned, header once at the top.
- All 9,007 landscape rows (2016 MJ – 2026 MJ): 8,778 (97.5%) re-wrapped; 229 (2.5%) scale to fit:
  100 unknown rules (dashed/white boxes), 57 drawn symbol in the row, 42 fraction bar, 18 table inside a cell, 8 picture with text beside it,
  4 other. Word check: 0 problems. Row height grows x1.00 (median), x1.26 (95%), x1.83 (max).

## 7. Plan
1. (done) Dhruv's answers. 2. (done) `ms_portrait.py` updated: widths by content, picture rows, header once. 3. Sample pictures sent; on approval store the portrait layout (`layout_p`) per row in `store.py build`; verify; year by year from 2016 MJ.

## 8. Our own consistent layout (Dhruv 2026-11-03/05) — `pipeline/ms_layout.py`, stored as `ms_p` per question
- Not a copy of the printed table: every year looks the same.
- Header: built by us, grey, once at the top: **Q | Answer | Marks** (| **Guidance** when the paper has that column).
  Printed names ("Question", "Expected answer", "Mark") are mapped; only their order is used.
- Frame: black left and right border on every row, a line under every row.
- Rows are first trimmed to their own table (empty page margins beside the printed table are dropped), then re-wrapped.
- Total: its own last row, "Total" right-aligned next to the Marks column, the number in the Marks column.
  If the mark scheme prints no total (2016 MJ 43), our Total row uses the question's marks.
- Cut: the mark-scheme row cut follows the real table edges left and right (ms.py), so nothing printed is lost.
- Ignored when recognising the table: the sliver of the grey header row above the first row on a page, white cell backgrounds.
- MCQ options that are separate drawings: the printed letter A–D is not part of the picture (the page shows the letter).
