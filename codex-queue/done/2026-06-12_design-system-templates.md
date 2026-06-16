# Codex task: ONE LIFE DESIGN SYSTEM — template library (PRIORITY: blocks all social publishing)

Date: 2026-06-12 · From: creative-director QA + Naadir's direction ("heaps of templates; Claude = brain/writer, Codex = image execution")

## QA verdict on the first two carousels: REJECTED for publishing — re-render required
What was right: layout skeleton, branding (logo chip, N/6 pager, store-strip footer), compliant copy placement.
What failed: **the imagery is programmatic vector placeholder art** (clip-art shelves, abstract shapes), not the **gpt-image-2 photorealistic lifestyle imagery** the briefs specified. Your builtin handler rendered these; for carousels and all customer-facing imagery, the builtin renderer is QA-banned. **Every visual base layer must come from the image model.** Text/logo overlay composited afterwards is fine (and preferred for crisp typography).

## The mandate
Build a reusable template library. Claude fills the copy slots weekly; you render and (once access exists) publish. **Render ONE sample of each template first → commit to `creative/templates/{template-id}/sample/` → STOP for Naadir's review.** Nothing publishes until he approves the look. After approval, a template is standing — no further design approvals, only copy changes.

## Brand frame (applies to every template)
ICP: women 35–50, upper-class, high-LSM, Gauteng. Premium, warm, real South African contexts — natural light, believable homes/kitchens/desks/stores; NO gym-bro aesthetics, no US-suburbia stock look, no plastic AI faces (avoid close-up synthetic faces; favour hands, environments, over-shoulder, soft depth). Palette: deep One Life green + warm neutrals (match existing logo chip). Typography overlay: clean bold sans for hooks, high contrast. Every template carries: logo chip (top-left), store strip footer "Centurion | Glen Village | Edenvale · onelife.co.za | free delivery over R400".

## Template library v1 (12 templates)
| ID | Template | Sizes | Notes |
|---|---|---|---|
| T01 | Carousel master — 6 slide roles (Hook/Pain/Mechanism/Proof/Participation/CTA) | 1080×1920 | The flagship. Photoreal lifestyle base per slide; mechanism slide may use clean diagram ON a photographic backdrop |
| T02 | Monday Hero offer card | 1080×1080 + 1080×1920 | Product packshot hero + offer badge (% slot), price slot |
| T03 | Vivid Day | both | Vivid-branded frame, "made in-house" story slot, product trio |
| T04 | Bundle/Stack card (Thu) | both | 2–3 products composed as a "stack", per-item + bundle price slots |
| T05 | Proof/review | both | Real photo frame (staff/store photos supplied by Naadir — NEVER generated people presented as staff) + quote slot + stars |
| T06 | Community/poll story | 1080×1920 | Question slot + 2–3 option chips |
| T07 | Hub VIP recruit card | both | "VIP gets it first" mechanic explainer + WhatsApp join CTA |
| T08 | GBP offer post | 1200×900 | Per-store variant slots (store name, offer) |
| T09 | Email hero header | 1200×600 | Must match the existing email design system (one hero image policy) |
| T10 | Back-in-stock alert | 1080×1080 | Product + "it's back" frame |
| T11 | Education quote/myth-bust card | both | For FB/IG text-led education posts |
| T12 | Seasonal campaign frame (current: SA winter) | overlay layer | Swappable seasonal accent for T01–T04 |

## Execution order
1. T01 sample first — **re-render BOTH week-1 carousels with it** (copy unchanged from the briefs in `codex-queue/done/`). These are needed for Tue 16 / Sat 20 Jun.
2. T02 sample (week-1 Monday Hero: Vivid Buffered C 10% — needed Mon 15, but social posting is blocked on account access anyway; email header T09 variant is the Monday priority).
3. T03–T12 in order.
4. Commit each sample as it's done (don't batch-wait); Claude QAs from the cloud and assembles the review set for Naadir.

## Standing rule going forward
Brief files from Claude will reference template IDs + copy slots only (e.g. `T02: product=X, offer=10%, dates=...`). You render from the approved template. Any brief asking for a NEW look = new template = sample + review first.
