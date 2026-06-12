# Codex task: PUBLISHING LAYER — you own all posting (WhatsApp, FB, IG, TikTok)

Date: 2026-06-12 · Authority: Naadir granted standing publish rights via Codex (chat, 2026-06-12; flag: `approvals/granted/publish-rights.flag`). Campaign-level approval = the approved calendar in `state/CALENDAR.md`. Anything NOT on the calendar still goes to Naadir first.

## Operating contract (standing, every week)
1. **Source of truth**: `state/CALENDAR.md` (Claude keeps it 4 weeks ahead). Copy comes from `creative/` packs and `codex-queue/` briefs — Claude's copy is compliance-gated; post it as written. If you must shorten for a platform, keep claim language identical (structure/function verbs only; never mention competitors or pharmacies).
2. **Produce → publish → log**: for carousel briefs, generate imagery (gpt-image-2 per your existing spec), then post at the scheduled time. Log EVERY post to `creative/POST_LOG.md`: datetime, channel, campaign tag, post URL, and (when re-visiting) views/likes/comments — Claude reads this for the weekly scoreboard.
3. **Channels**: WhatsApp Hub (the packs, exactly on schedule — VIP exclusivity means Hub ALWAYS posts before other channels), Facebook "One Life Health Supermarket", Instagram @one_life_health_supermarket, TikTok @onelifehealthstore. Add UTM params to every link you post: `?utm_source={channel}&utm_medium=social&utm_campaign={campaign-tag}`.

## Week 1 schedule (15–21 Jun) — your first publishing run
| When (SAST) | What | Source |
|---|---|---|
| Sun 14, 18:00 | Hub: VIP early access post | `creative/2026-06-14_whatsapp_week1-pack.md` (post 1) |
| Mon 15, 09:00 | Hub reminder + FB/IG post: Monday Hero (Vivid Buffered C 10% off) | pack post 2; adapt copy for FB/IG |
| Tue 16, ~12:00 | TikTok + IG: carousel "Always tired by 2pm?" | produce + post from `codex-queue/2026-06-16_tiktok_tired-by-2pm.md` |
| Wed 17, 10:00 | Hub: Vivid Day post + FB/IG Vivid IMMUNE spotlight | pack post 3 |
| Thu 18, 10:00 | Hub: community question; FB: bundle announce | pack post 4 |
| Fri 19, ~15:00 | FB/IG: proof post (staff expertise — use real store photos only, nothing staged-fake) | write from pack tone; flag to Claude if unsure |
| Sat 20, ~10:00 | TikTok + IG: carousel "Winter sleep falling apart?" | `codex-queue/2026-06-20_tiktok_winter-sleep.md` |

## One-time: Meta System User token (the durable path)
While you have browser access to Business Manager: create a System User (name: `growth-engine`), grant pages + Instagram + ads_management, generate a long-lived token, then:
`gh secret set META_SYSTEM_TOKEN --repo clawdbot12345-ux/onelife-dashboard`
Same for TikTok Business API if available. Browser posting is the bridge; APIs are the destination.

## Boundaries (absolute)
- Nothing off-calendar without Naadir's OK. No paid boosts (spend = separate approval). No DMs/replies that make health claims — route product questions to "ask the team in store". Discounts posted must match what Claude specified (≤10% unless a flag says otherwise).
