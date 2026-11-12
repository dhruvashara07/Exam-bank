#!/usr/bin/env bash
# Store many original PDFs in GitHub Releases WITHOUT processing them (e.g. a new subject before its
# pipeline is ready). Takes Cambridge-named PDFs from a folder, puts them in inbox/ on a NEW branch
# store-<name> made from origin/main, and pushes that branch (never main, never force). The "Upload batch"
# Action then stores them in Releases, writes raw/manifest.json to main and deletes the branch.
# Usage: pipeline/store_pdfs.sh <name> <folder with PDFs>      e.g. pipeline/store_pdfs.sh 0607-a /tmp/pdfs
set -euo pipefail
cd "$(dirname "$0")/.."
name="${1:?name}"; src="${2:?folder}"
br="store-${name}"
wt=$(mktemp -d)
git fetch -q origin main
git worktree add -q -b "$br" "$wt" origin/main
mkdir -p "$wt/inbox"
find "$src" -maxdepth 2 -iname '*.pdf' -exec cp {} "$wt/inbox/" \;
n=$(ls "$wt/inbox" | grep -ic '\.pdf$' || true)
git -C "$wt" add -f inbox
git -C "$wt" commit -q -m "Store ${n} PDFs (${name}), not processed"
git -C "$wt" push -q origin "$br"
git worktree remove --force "$wt"
git branch -D "$br" >/dev/null
echo "pushed ${br} with ${n} PDFs; watch the 'Upload batch' Action"
