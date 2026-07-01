# Flow Extension Build — 2026-07-01

Assets created in Klaviyo (inert until wired):

| Asset | ID |
|---|---|
| touch2_template | `SCi9Vy` |
| touch3_template | `RZh7iV` |
| postpurchase_template | `VA8SjT` |
| segment_lapsed_60_120 | `TaFWcM` |
| segment_lapsed_120plus | `WKxHdK` |


## Wiring steps (Klaviyo UI, ~15 minutes)

### A. Abandoned checkout: extend "Abandoned Checkout Consultant Check — 2026 design system" (`WY4cae`)
1. Open the flow → after the existing email add **Time delay: 1 day**.
2. Add **Email** → Import template *[FLOW] Abandoned Checkout Touch 2*.
   On this email set flow filter: **Placed Order zero times since starting this flow**.
3. Add **Time delay: 1 day** → **Email** → template *[FLOW] Abandoned Checkout Touch 3*,
   same flow filter. Set both emails LIVE (top-right status per action).
4. Leave the SMS companion flow untouched.

### B. Post-purchase cross-sell (new flow, 3 minutes)
1. Create flow → **Metric trigger: Placed Order**.
2. Flow filter: **Placed Order zero times since starting this flow** (so a repeat
   purchase exits them) — and to avoid overlap: **has not been in flow PCOS
   Post-Purchase** (or rely on the PCOS trigger-filter fix below).
3. **Time delay: 7 days** → **Email** → template *[FLOW] Post-Purchase Cross-sell*.
4. Set live.

### C. PCOS Post-Purchase mistarget fix (`R96wJV`)
Open the flow → Trigger setup → add trigger filter:
**where Items contains Pcositol** (add other PCOS SKUs). Today it fires on
EVERY order — 302 wrong-audience sends in June, R0.

### D. Winback catch-up (uses the two new segments)
1. Clone **Win-Back 60 Days v2** → change trigger to **Added to segment:
   Winback Catch-Up — Lapsed 60–120d** → set LIVE. New segments populate
   shortly after creation; members entering the segment enter the flow.
2. Clone again for **Winback Catch-Up — Lapsed 120d+** (use the 90/120 flow's
   deeper-discount email if preferred) → set LIVE.
3. Keep the existing metric-triggered winback flows live for future lapses;
   add flow filter **has not been in** either catch-up flow to prevent doubles.
