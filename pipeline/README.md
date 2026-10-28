# Pipeline

| File | Does |
| --- | --- |
| `clean.py` | Deletes the PapaCambridge watermark layer (2026 files) from the PDF content stream |
| `layout.py` | Page geometry: content area, ink boxes, label positions, symbol-font fixes |
| `extract.py` | Splits a paper into questions → parts → printable segments; marks, answer space, figures, MCQ options |
| `ms.py` | Mark schemes: MCQ key; structured rows by label (1(b)(iii)) as text + exact regions |
| `render.py` | Cuts a page region to a standalone vector SVG (text as outlines, off-crop content deleted) |
| `run.py` | Runs everything for one or all papers; writes `data/`, `assets/`, `review/queue.json` |
| `build_test.py` | Builds a test PDF from chosen questions/parts in the original layout (+ mark scheme) |

A *segment* is a strip of one page belonging to one label path (Q4 stem, 4(a) stem, 4(a)(ii)).
Printing the segments in order reproduces the paper exactly, answer space included.
Cloudinary public id of every SVG = `igcse/<syl>/<year>-<session>/<pv>/<file name without .svg>`.
