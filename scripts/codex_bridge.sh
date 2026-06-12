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
CODEX_BIN="${CODEX_BIN:-/opt/homebrew/bin/codex}"
PYTHON_BIN="${PYTHON_BIN:-/opt/homebrew/bin/python3}"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${PATH:-}"

mkdir -p "$HOME/.onelife"
LOCK_DIR="$HOME/.onelife/codex_bridge.lock"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "[bridge] another run is active; exiting"
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

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
  [[ "$name" == *.result.md ]] && continue

  echo "[bridge] picking up $name"
  result="$DONE/${name%.md}.result.md"

  # >>> CODEX: task execution block. Contract:
  # - input: the brief file path ($brief)
  # - output: produced assets go to creative/ (use the campaign tag in the brief as folder/file prefix)
  # - on success: exit 0
  if [[ -f scripts/codex_bridge_builtin.py ]]; then
    set +e
    "$PYTHON_BIN" scripts/codex_bridge_builtin.py "$brief" "$result"
    builtin_status=$?
    set -e
    if [[ "$builtin_status" -eq 0 ]]; then
      echo "[bridge] builtin completed $name"
    elif [[ "$builtin_status" -eq 2 ]]; then
      "$CODEX_BIN" exec \
        --dangerously-bypass-approvals-and-sandbox \
        -C "$REPO_DIR" \
        -o "$result" \
        "Execute the task brief at $brief in this repo. Write all outputs to the locations the brief specifies, defaulting to creative/. Keep secrets out of outputs. Do not move or rename the brief; the bridge will move it after success. When done, summarize exactly what you produced." \
        || { echo "[bridge] codex failed on $name"; continue; }
    else
      echo "[bridge] builtin failed on $name"
      continue
    fi
  else
    "$CODEX_BIN" exec \
      --dangerously-bypass-approvals-and-sandbox \
      -C "$REPO_DIR" \
      -o "$result" \
      "Execute the task brief at $brief in this repo. Write all outputs to the locations the brief specifies, defaulting to creative/. Keep secrets out of outputs. Do not move or rename the brief; the bridge will move it after success. When done, summarize exactly what you produced." \
      || { echo "[bridge] codex failed on $name"; continue; }
  fi
  # <<< CODEX

  if [[ -f "$brief" ]]; then
    git mv "$brief" "$DONE/$name"
  elif [[ -f "$DONE/$name" ]]; then
    echo "[bridge] $name already moved to $DONE"
  else
    echo "[bridge] $name missing after task; skipping move"
  fi
  git add -A
  if git diff --cached --quiet; then
    echo "[bridge] no commit needed for $name"
  else
    git commit -m "codex-bridge: completed $name" || true
  fi
done

# Omni daily sync (Mac Mini reaches port 59029; cloud cannot). No-op if creds file absent.
if [[ -f "$HOME/.onelife/omni_url" ]]; then
  OMNI_REPORT_URL="$(cat "$HOME/.onelife/omni_url")" python3 scripts/fetch_omni.py || echo "[bridge] omni sync failed (non-fatal)"
  git add -A data/omni && git commit -m "codex-bridge: omni daily sync" || true
fi

git push -q origin "$BRANCH" || true
echo "[bridge] done"
