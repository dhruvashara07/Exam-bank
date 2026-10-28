# One-time setup: Cloudinary + MongoDB

Claude's cloud workspace cannot reach Cloudinary or MongoDB, so a GitHub Action does the
uploading. Keys live in GitHub Secrets (encrypted; even Claude can't read them back).
If a key was ever pasted into a chat or a file, make a new one (Cloudinary → Settings → API Keys →
Generate New API Key; Atlas → Database Access → Edit user → new password) and use the new one here.

## 1. Add two secrets
GitHub → exam-bank → Settings → Secrets and variables → Actions → New repository secret

| Name | Value |
| --- | --- |
| `CLOUDINARY_URL` | `cloudinary://<API key>:<API secret>@<cloud name>` — one line, no spaces, no quotes. Cloudinary dashboard → "API Environment variable" shows it ready-made |
| `MONGODB_URI` | Your Atlas connection string, e.g. `mongodb+srv://user:pass@cluster0.xxx.mongodb.net/?retryWrites=true&w=majority` (Atlas → Connect → Drivers) |

## 2. Let GitHub reach MongoDB Atlas
Atlas → Network Access → Add IP Address → "Allow access from anywhere" (0.0.0.0/0).
GitHub's servers have changing IPs. Keep a strong database password.

## 3. First run
GitHub → Exam-bank → Actions → "Question bank" → Run workflow → tick "Upload every SVG again".
About 5,100 SVGs; expect 10–20 minutes. After that it runs by itself on every push.

## What ends up where
- Cloudinary: every SVG under the folder `question_bank/`, same folders as `bank/` in the repo, e.g.
  `question_bank/cambridge-igcse/0625-physics/2025-MJ/p41/q01/question/0625_2025MJ_41_q01_a-ii_s1`.
  Folders are created automatically by the upload; you never create them by hand.
- MongoDB database `question_bank`, our own collections, not tied to any website model
  (only papers Claude has approved — see docs/DAILY_CHECK.md):
  - `papers` — one document per paper (`_id` `0625_2025MJ_41`)
  - `questions` — one document per question (`_id` `0625_2025MJ_41_q01`): the question JSON
    exactly as in git, with every `svg.url` filled in, plus `paper_id`, `leaf_paths`, `search` text.
    Indexed by syllabus/year/session/paper/variant/number, type, topic, keywords, and full text.
  The website adapts to this format, not the other way round.

## If images do not show
Open one `svg.url` from MongoDB. If Cloudinary refuses SVGs: Cloudinary → Settings → Security →
restricted media types → allow SVG delivery.
