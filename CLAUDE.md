# Rules for any Claude session in this repo
(this chat on claude.ai, the daily scheduled check, or Claude Code on a laptop — all follow the same rules)

- Start: `git pull --rebase`, then follow `docs/START_HERE.md` (what to read, in order; the batch cycle; what to do
  before ending). Background and judgement: `docs/AGENT_GUIDE.md`.
- Never `git push` directly. Always `pipeline/push.sh "message"`: it waits for a running GitHub
  Action, rebases, rebuilds generated files on a clash and never force-pushes.
  Commit messages end with the Co-Authored-By / Claude-Session lines. Only exception: `pipeline/store_pdfs.sh`
  pushes its own new `store-*` branch (PDFs to Releases, never main).
- Writers to this repo: Dhruv (uploads to `inbox/`), the "Question bank" GitHub Action (bot commits
  processing papers), and Claude sessions. Only one Claude session should work on the pipeline at a
  time; if `push.sh` reports a real conflict, look at both sides and merge by hand — never discard.
- Layout and file roles: `README.md`, `pipeline/README.md`, `pipeline/paths.py`.
- Flow: upload (`docs/UPLOAD.md`) → Actions (store in Releases, process, `checks.py`, batch) → scheduled Claude
  check (`docs/DAILY_CHECK.md`: overview of every page, review round for Dhruv, approve) → MongoDB.
  Original PDFs are in GitHub Releases (`raw/manifest.json`): `pipeline/raw_store.py fetch <papers>`.
- Physics 0625 is finished and frozen. Before pushing a pipeline change: `python3 pipeline/golden.py check` must
  report 0 changed cuts and `git status` must show nothing changed under `0625-physics`. Subject differences live
  in `pipeline/subjects.py`; maths-only code is gated. Maths selectors carry the syllabus (`0607/2021-MJ/41`).
- Quality gate: a paper reaches MongoDB only via `pipeline/approve.py` after a full visual check
  (`docs/DAILY_CHECK.md`). Fix the pipeline, not single JSON files.
- Look at SVGs with Chromium (playwright), not MuPDF (MuPDF drops dashed strokes).
- Never put keys in the repo or chat (GitHub Secrets only); never delete original PDFs (local raw/ or Release assets); never write to
  MongoDB or Cloudinary directly (the Action does that).
- Before ending: `docs/START_HERE.md` section 4 (batch log, PROGRESS, CONVERSATION_LOG, patterns, NEXT_CHAT), then `pipeline/push.sh`.
