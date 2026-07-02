# Codex Handoff — Vivid Health Store (hgywg0-w7.myshopify.com) · v4 FINAL, 2026-07-02

**Supersedes v3.** The owner has walked-through GO; this is the closing round.
Branch: `claude/vivid-health-audit-redesign-9fmzon` · Never touch onelifehealth.myshopify.com.
No text baked into imagery, ever (bottle labels in photos fine; rendered slogans/wordmarks/buttons not).

## What's already done — do NOT redo

Theme round-2 (yours) verified · **product-media cleanup COMPLETE** (Claude's pipeline had the
permissions yours lacked: 97/97 banned media deleted — IMG-* masters, WhatsApp files, all
infographics — zero errors; log `vivid/backend/media-remediate-result.json`) · **all 3 stacks now
carry real product media** (your per-stack hero art attached via CDN) · hero renders lead every
gallery + og:image · **stack copy/composition rewritten to the real range by Claude (owner
decision — see below)** · subscribe flow, quiz, search, sourcing grid, all code QA items live.

## 🔴 Task 1 — Commit the 51 label-panel shots

You generated them (`output/vivid-round2-remediation-20260702/`) but they only exist in your
workspace. **Commit them to `vivid/assets/store/label-panels/` on the branch**, named
`vivid-{product-handle}-label.jpg|webp` so each file maps to its product handle unambiguously.
Claude's pipeline then uploads them all as product media (position 2, straight after the hero).
Requirements per the direction doc §3.1(2): straight-on, label fills the frame, every milligram
legible, ≤250KB. **Before committing, confirm none carry "ANGUS CASTUS" or "DIETARY SUPPLEMENT"**
(§3.4) — regenerate any that do.

## 🔴 Task 2 — Re-shoot the 3 stack heroes to the CORRECTED compositions

The owner has ruled: stack copy/composition is rewritten to the real Vivid range (already live —
read each PDP before shooting). Your current stack art shows wrong/unbranded bottles. Re-shoot each
group composition showing exactly these real Vivid bottles, same warm stone/botanical series,
1:1 + 3:4 crops, no text overlays:

| Stack | Bottles in shot (real SKUs, live on the store) | Prop |
|---|---|---|
| `comrades-recovery-stack` | **Turmeric Plus · MSM · L-Glutamine** | running shoe toe / race number, subtle |
| `highveld-hayfever-stack` | **Quercetin Complex · Mullein · Buffered C** | fynbos/grass sprig |
| `perimenopause-essentials` | **Agnus Castus · Sage · Maca · Griffonia (5-HTP)** — four bottles | linen + sage sprig |

Deliver the same way: commit to `vivid/assets/store/stacks/` OR upload directly as product media
in admin (replacing the current single hero on each stack, not appending). If committing, Claude
pushes them through the pipeline.

## Task 3 — Admin/app launch items (unchanged from v3, still open)

| # | Item |
|---|---|
| 1 🔴 | **Subscriptions billing app** (plans sell correctly but nothing bills recurring orders) + ONE test subscription checkout |
| 2 🔴 | **Judge.me reviews** (PDP reviews are hardcoded "SAMPLE") — install, enable post-purchase requests, then tell Claude to remove the sample block |
| 3 🔴 | **Inventory**: 16/58 sold out incl. Buffered C · 300 — restock or hide |
| 4 | Payments: Payflex/PayJustNow + Ozow (Claude adds installment messaging after) |
| 5 | Klaviyo + repo secret `VIVID_KLAVIYO_API_KEY` |
| 6 | GA4/Meta/TikTok pixels |
| 7 | Vivid price rounding (58 products, owner sign-off first; Vivid store ONLY) |
| 8 | Domain decision + connect |
| 9 | Shipping rates vs the R400 promise |
| 10 | Manufacturer COAs → unlocks Claude's batch-lookup build |

## Definition of done (this closing round)

- [ ] 51 label panels committed to `vivid/assets/store/label-panels/` (handle-named, §3.4-clean)
- [ ] 3 corrected stack heroes delivered (committed or uploaded, matching the live compositions)
- [ ] Post a completion note on the branch; Claude uploads panels, re-runs the design QA, and
      reports the final scorecard to the owner
- [ ] Admin items 1–3 done (or blockers reported); 4–10 scheduled
