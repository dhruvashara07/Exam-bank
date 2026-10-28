# One-time setup: Cloudinary + MongoDB sync

Claude's cloud workspace cannot reach Cloudinary or MongoDB, so a GitHub Action does the
uploading. Your keys live in GitHub Secrets: never in chat, never in the repo.

## 1. Add two secrets
GitHub → exam-bank → Settings → Secrets and variables → Actions → New repository secret

| Name | Value |
| --- | --- |
| `CLOUDINARY_URL` | Cloudinary dashboard → "API Environment variable", looks like `cloudinary://123456:abcDEF@your-cloud` |
| `MONGODB_URI` | Same value as `MONGODB_URI` in learnerspoint's `.env.local` (must include the database name, e.g. `...mongodb.net/learnerspoint?...`) |

## 2. Let GitHub reach MongoDB Atlas
Atlas → Network Access → Add IP Address → "Allow access from anywhere" (0.0.0.0/0).
GitHub's servers have changing IPs. Keep a strong database password.

## 3. First run
GitHub → exam-bank → Actions → "Sync to Cloudinary and MongoDB" → Run workflow (leave "Upload every SVG" ticked).
About 5,000 SVGs; expect 10–20 minutes. After that it runs by itself on every push that changes questions.

## 4. If images do not show
Open one image URL from a question in MongoDB. If Cloudinary refuses SVGs, check
Cloudinary → Settings → Security → restricted media types, and allow SVG delivery.

## 5. learnerspoint schema (QuestionV2.ts)
Add these two fields so the website can read the exact-layout data:

```ts
source: String,                          // already exists; used as the question id
pastPaper: { type: Schema.Types.Mixed }, // full pipeline JSON: segments, answer space, text, mark scheme
```
and an index: `questionSchemaV2.index({ source: 1 })`.
