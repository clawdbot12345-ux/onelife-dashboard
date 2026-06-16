# Codex task: AUTONOMY SETUP — the last task a human ever relays

Goal: after this, Naadir is out of the loop. Claude (cloud) ⇄ git repo ⇄ Codex (Mac Mini) runs hands-free.

## 1. Install the bridge watcher (15-min cycle)
The script is at `scripts/codex_bridge.sh`. It: pulls the branch → executes any new task brief in `codex-queue/` → commits outputs to `creative/` → moves the brief to `codex-queue/done/` → runs the Omni sync → pushes.

- Open the script and **adapt the marked `>>> CODEX` block to your own preferred invocation** (you know your CLI/setup best — the contract is documented inline).
- Store the Omni report URL once: `mkdir -p ~/.onelife && echo '<full report url from Naadir>' > ~/.onelife/omni_url && chmod 600 ~/.onelife/omni_url`
- Install as launchd job (or cron), every 15 min:
  ```
  */15 * * * * REPO_DIR=$HOME/onelife-dashboard /bin/bash $HOME/onelife-dashboard/scripts/codex_bridge.sh >> $HOME/.onelife/bridge.log 2>&1
  ```
- Also set the GitHub secret so cloud workflows can reach Omni independently of the Mac Mini:
  `gh secret set OMNI_REPORT_URL --repo clawdbot12345-ux/onelife-dashboard < ~/.onelife/omni_url`

## 2. Social logins (when Naadir hands them over)
Store in the Mac Mini keychain. Test posting access on FB ("One Life Health Supermarket"), IG (@one_life_health_supermarket), TikTok (@onelifehealthstore). Until Meta/TikTok API tokens exist, you are the posting layer: when a brief in `codex-queue/` is tagged `channel: social-post`, produce the asset AND publish it via browser automation, then log the post URL in the `.result.md`.

## 3. Branch note
Everything currently lives on `claude/end-to-end-goal-tdcj0f` (PR #16). After it merges, change `BRANCH=main` in the bridge env.

## Definition of done
- Bridge running on schedule (first log lines in `~/.onelife/bridge.log`)
- `OMNI_REPORT_URL` secret set
- The two pending carousel briefs (`2026-06-16_tiktok_tired-by-2pm.md`, `2026-06-20_tiktok_winter-sleep.md`) picked up and produced into `creative/`
- Omni v2 report exploration done (see `codex-queue/2026-06-12_omni-reports-v2.md` — run it through the same bridge)
