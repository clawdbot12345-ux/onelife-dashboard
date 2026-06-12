#!/bin/bash
# Codex bridge — runs on the Mac Mini every 15 min (launchd/cron).
# Ends the human-relay loop: Claude writes task files to codex-queue/,
# this watcher hands them to Codex, results get committed back.
# Setup instructions: codex-queue/2026-06-12_AUTONOMY-SETUP.md
set -euo pipefail

REPO_DIR="${REPO_DIR:-$HOME/onelife-dashboard}"
BRANCH="${BRANCH:-claude/end-to-end-goal-tdcj0f}"   # switch to main after PR #16 merges
QUEUE="codex-queue"
DONE="$QUEUE/done"

cd "$REPO_DIR"
git fetch -q origin "$BRANCH"
git checkout -q "$BRANCH"
git pull -q --rebase origin "$BRANCH"
mkdir -p "$DONE"

shopt -s nullglob
for brief in "$QUEUE"/*.md; do
  name="$(basename "$brief")"
  # AUTONOMY-SETUP and README style files are not tasks
  [[ "$name" == *AUTONOMY-SETUP* ]] && continue

  echo "[bridge] picking up $name"

  # >>> CODEX: replace this block with your own invocation. Contract:
  # - input: the brief file path ($brief)
  # - output: produced assets go to creative/ (use the campaign tag in the brief as folder/file prefix)
  # - on success: exit 0
  codex exec --full-auto "Execute the task brief at $brief in this repo. Write all outputs to the locations the brief specifies (default: creative/). When done, summarise what you produced in a sibling file ${brief%.md}.result.md" || { echo "[bridge] codex failed on $name"; continue; }
  # <<< CODEX

  git mv "$brief" "$DONE/$name"
  git add -A
  git commit -m "codex-bridge: completed $name" || true
done

# Omni daily sync (Mac Mini reaches port 59029; cloud cannot). No-op if creds file absent.
if [[ -f "$HOME/.onelife/omni_url" ]]; then
  OMNI_REPORT_URL="$(cat "$HOME/.onelife/omni_url")" python3 scripts/fetch_omni.py || echo "[bridge] omni sync failed (non-fatal)"
  git add -A data/omni && git commit -m "codex-bridge: omni daily sync" || true
fi

git push -q origin "$BRANCH" || true
echo "[bridge] done"
