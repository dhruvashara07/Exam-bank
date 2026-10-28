# One-time setup: Cloudinary + MongoDB

Claude's cloud workspace cannot reach Cloudinary or MongoDB, so a GitHub Action does the
uploading. Keys live in GitHub Secrets (encrypted; even Claude can't read them back).

## 1. Add two secrets
GitHub → exam-bank → Settings → Secrets and variables → Actions → New repository secret

| Name | Value |
| --- | --- |
| `CLOUDINARY_URL` | Cloudinary dashboard → "API Environment variable", looks like `cloudinary://123456:abcDEF@your-cloud` |
| `MONGODB_URI` | Your Atlas connection string **with a database name**, e.g. `mongodb+srv://user:pass@cluster0.xxx.mongodb.net/learnerspoint?retryWrites=true` |

## 2. Let GitHub reach MongoDB Atlas
Atlas → Network Access → Add IP Address → "Allow access from anywhere" (0.0.0.0/0).
GitHub's servers have changing IPs. Keep a strong database password.

## 3. First run
GitHub → exam-bank → Actions → "Question bank" → Run workflow → tick "Upload every SVG again".
About 5,200 SVGs; expect 10–20 minutes. After that it runs by itself on every push.

## What ends up where
- Cloudinary: every SVG, public id = its repo path, e.g.
  `bank/cambridge-igcse/0625-physics/2025-MJ/p41/q01/question/0625_2025MJ_41_q01_a-ii_s1`
- MongoDB (database from the URI), our own collections, not tied to any website model:
  - `bank_papers` — one document per paper (`_id` `0625_2025MJ_41`)
  - `bank_questions` — one document per question (`_id` `0625_2025MJ_41_q01`): the question JSON
    exactly as in git, with every `svg.url` filled in, plus `paper_id`, `leaf_paths`, `search` text.
    Indexed by syllabus/year/session/paper/variant/number, type, topic, keywords, and full text.
  The website adapts to this format, not the other way round.

## If images do not show
Open one `svg.url` from MongoDB. If Cloudinary refuses SVGs: Cloudinary → Settings → Security →
restricted media types → allow SVG delivery.
