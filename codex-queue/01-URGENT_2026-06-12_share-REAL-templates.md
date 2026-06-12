# Codex task: WRONG FILES — share the REAL template library, do not re-render

Naadir confirms the files committed to `creative/templates/existing/` and `creative/archive/2026-06/` are NOT his approved templates — they're fresh renders approximating them. Evidence: the genuine June ads exist and look like `creative/templates/reference/cinematic-monday-offer-digestezyme.png` (literally marked "VALID 01 JUN TO 08 JUN 2026") and `cinematic-vivid-wednesday-griffonia.png` — neither of those, nor anything from that production run, is in your committed "archive".

## What to do
1. **Find the real production assets on the Mac Mini** — the actual Mon/Wed/Thu in-store ad system outputs and its ~10 templates (the pipeline that produced the Digestezyme and Griffonia ads; check the folders/projects that feed the existing Telegram media-group delivery).
2. Commit the GENUINE files, unmodified:
   - the ~10 template definitions/masters → `creative/templates/existing/` (replace current contents)
   - the actual June ads (01–08 Jun run and any others) → `creative/archive/2026-06/`
   - July ads if produced → `creative/archive/2026-07/`
   - updated `MANIFEST.md`: which file is which template, what's parameterised
3. **Do NOT re-render, recreate, or "improve" anything in this task.** If you cannot locate the real files, say exactly that in the result file — naming what you searched — rather than substituting generated lookalikes. Mark the previously committed renders clearly as `creative/templates/drafts-not-approved/` (move them there) so nothing mistakes them for the approved library.

This blocks Naadir's design sign-off and therefore all publishing — top priority.
