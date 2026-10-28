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
| `run.py` | Runs everything for some or all papers; writes `bank/`, `bank/index.json`, `review/queue.json`. Also finds uncaptioned MCQ figures |
| `build_test.py` | Builds a test PDF from chosen questions/parts in the original layout (+ mark scheme) |
| `coverage.py` | Check: every bit of ink on every question page is inside some segment |
| `review_assets.py` | Images for the phone review page (rendered with Chromium, as a browser shows them) |
| `sync_cloudinary.py`, `sync_mongo.py` | Run in GitHub Actions (`.github/workflows/bank.yml`) |

A *segment* is a strip of one page belonging to one label path (Q4 stem, 4(a) stem, 4(a)(ii)).
Printing the segments in order reproduces the paper exactly, answer space included.
