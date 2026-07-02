# ⛔ STOP — do not apply this plan (wrong store)

**To Codex / any agent:** `plan-2026-07-02T125406Z.csv` targets **2,203 products
on onelifehealth.myshopify.com (One Life Health)**. The owner's standing
instruction is explicit: **the One Life store must not be modified as part of
Vivid work** (see the warning banner in `codex-vivid-handoff-2026-07-02.md`).
One Life prices may also be POS/ERP-owned — mass changes could break till sync.

Handoff task **3.6 is scoped to the Vivid store only** (hgywg0-w7.myshopify.com,
58 products, IDs in `vivid/backend/products.json`). If a rounding plan is
wanted, regenerate it against that store and post it for owner approval before
applying anything.

Verified 2026-07-02: this plan has NOT been applied (live spot-checks match
`old_price`). Keep it that way unless the owner separately and explicitly
approves One Life price changes.
