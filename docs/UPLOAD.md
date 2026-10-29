# Adding papers: upload, track, review

Everything after the upload runs by itself. You only upload, and later answer a short review round.

## 1. Upload a batch of PDFs

Any Cambridge file names work (`0625_w25_qp_42.pdf`, `0625_w25_ms_42.pdf`, `0625_w25_er.pdf` …).
Upload the question paper **and** its mark scheme. Up to 100 files at a time, each under 25 MB.

**On the laptop (browser) or phone (browser, "Desktop site" on):**
1. Open https://github.com/dhruvashara07/Exam-bank → folder **inbox** → **Add file → Upload files**.
2. Drag the PDFs (or the whole folder's files) in.
3. At the bottom choose **"Create a new branch for this commit"**. Keep the suggested name
   (e.g. `dhruvashara07-patch-1`) or type `upload-oct25`. Click **Propose changes**.
4. Close the "Open a pull request" page that appears. You do **not** need a pull request.

That's it. Do not upload into `main` directly: a new branch keeps the PDFs out of the repo's
history (they go to GitHub Releases instead) and the branch is deleted automatically when done.

**On the laptop with GitHub Desktop (many files):** create a branch named `upload-<anything>`, copy the
PDFs into the `inbox` folder, commit, **Push origin**. Same result.

## 2. What happens next (no laptop needed)

| Stage | Who | Time |
| --- | --- | --- |
| Uploaded → stored in Releases | GitHub Action "Upload batch" | minutes |
| Processed: cut into questions, mark scheme linked, editable text | Action | ~4 s per paper |
| Auto-checked: marks, missing print, page furniture, figure crops, editable text | Action | seconds |
| Claude checked: every page looked at, pipeline fixed if needed | scheduled Claude, 9:47 am and 10:47 pm IST | next run |
| Your review: flagged items + a few random ones | **you**, on the review page | when you have time |
| Approved → Published to MongoDB (and Cloudinary) | Claude + Action | next run |

You get a phone notification from Claude when a batch needs you or is published.

## 3. See where a batch is

Website → **Batches** (https://dhruvashara07.github.io/Exam-bank/#batches): each upload shows how many
papers are at each stage. Click a paper to see every question (exact / editable / side by side) with its
mark scheme and the check results. **Papers** lets you browse everything by year.

If an upload had files with names the filer did not understand, the Action leaves that branch in place
and says so in its run (Actions tab). Rename the file and upload it again.

## 4. Review

Open the review page link from Claude's notification (also on the website: **To check → review page**).
For each question compare *Rebuilt* (and *Editable*) with *Original page*:
**Looks right**, or **Something's wrong** + tick what + a short note. Answers save immediately.
Claude reads them at the next run, fixes the pipeline, and shows anything fixed in the next round.

## 5. If something looks wrong anywhere else

On the website, the **Report a problem** button on a question opens a GitHub issue with the question id
filled in. Claude reads open issues at every run.
