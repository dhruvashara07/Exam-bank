# Pipeline

| File | Does |
| --- | --- |
| `paths.py` | Where everything lives (bank layout, Cloudinary ids). Every script goes through it |
| `inbox.py` | Files Cambridge-named PDFs from `inbox/` into `raw/` |
| `clean.py` | Deletes the PapaCambridge watermark layer and Cambridge page furniture (barcode, corner marks) |
| `layout.py` | Page geometry: content area, ink boxes, label positions, symbol-font fixes |
| `extract.py` | Splits a paper into questions → parts → printable segments; marks, answer space, captioned figures, MCQ options |
| `ms.py` | Mark schemes: MCQ key; structured rows by label (1(b)(iii)) as text + exact regions |
| `render.py` | Cuts a page region to a standalone vector SVG (text as outlines, off-crop content deleted) |
| `check.py`, `approve.py` | Daily check: report + contact sheets for pending papers; approve papers for MongoDB |
| `run.py` | Runs everything for some or all papers; writes `bank/`, `bank/index.json`, `review/queue.json`. Also finds uncaptioned MCQ figures |
| `build_test.py` | Builds a test PDF from chosen questions/parts in the original layout (+ mark scheme) |
| `coverage.py` | Check: every bit of ink on every question page is inside some segment |
| `review_assets.py` | Images for the phone review page (rendered with Chromium, as a browser shows them) |
| `editable.py` | Editable copy of each question (`content` blocks: text with b/i/sub/sup/LaTeX, tables, figure refs, answer space, options) |
| `checks.py` | Automatic checks per paper → `review/checks/<paper>.json` (marks, coverage, page furniture in pieces, figure crops, editable-text score) |
| `golden.py` | Golden set (`tests/golden/`): hand-checked papers whose cut must not change by surprise; `cut_hash` for approvals |
| `overview.py` | One image per paper with every cut box (Claude's visual check) |
| `claude_check.py` | Records Claude's check per paper → `review/claude/` |
| `batch.py` | Upload batches and the stage of every paper (`review/batches/`) |
| `review_round.py` | Builds a review round for Dhruv's review page; closes it with his answers (`review/rounds/`) |
| `raw_store.py` | Original PDFs in GitHub Releases (`raw/manifest.json`): upload / fetch |
| `sync_cloudinary.py`, `sync_mongo.py` | Run in GitHub Actions (`bank.yml`, `upload.yml`); Mongo sync writes `review/published.json` |

Workflows: `upload.yml` (PDFs uploaded on an `upload*` / `*-patch-*` branch → Releases → process → checks →
batch → main → Cloudinary), `bank.yml` (push to main: process inbox on main, Cloudinary, MongoDB for approved
papers), `raw.yml` (bulk PDFs on branch `incoming-raw` → Releases), `site.yml` (review website on Pages).
Procedure for the scheduled check: `docs/DAILY_CHECK.md`; for Dhruv: `docs/UPLOAD.md`.

A *segment* is a strip of one page belonging to one label path (Q4 stem, 4(a) stem, 4(a)(ii)).
Printing the segments in order reproduces the paper exactly, answer space included.
