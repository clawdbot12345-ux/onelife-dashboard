# Codex — PREMIUM PASS 2 QA + Publish (2026-07-02)

Theme: **"PREMIUM PASS 2 — (publish me)"** (draft slot 186060964150).
What it is: mirror of live + 9 overrides — PDP buy-column rebuilt (vendor →
serif title → price → one-line stock/delivery meta row → variant picker →
qty → CTAs → collapsed "Product notice & tag guide" → ONE bordered
assurance panel → description), quiz premium reskin (logic untouched),
cart emoji cleanup.

## QA before publish (mobile first)
1. **PDP order** on any product exactly as above — no stacked cards between
   price and CTAs.
2. **Meta row states**: normal ("In stock at Centurion · Delivery 3–7…"),
   a low-stock (≤3) product, and an out-of-stock product.
3. **Disclaimer**: collapsed by default; chevron rotates; pills + legal copy
   + tag-guide link inside (test a vegan-tagged product).
4. **Assurance panel**: sub-R400 product → "Add RX more" progress bar;
   ≥R400 → qualifies row; pickup availability appears ONCE (inside panel);
   WhatsApp row prefills the product name; promises row = one quiet line.
5. **Quiz** (/pages/supplement-quiz): steps fade/slide ~200ms; selected tile
   deep green/cream; counter updates; back/continue work; results render;
   "Add Entire Stack" + per-product ATC still hit the cart; zero emoji.
6. **Cart drawer** over R400: "You qualify for free nationwide delivery!"
   with no emoji; under R400 unchanged.
7. Regression: home, collection cards, cart still styled (premium css loads
   once).

Publish if all pass; report anomalies to Claude — do not fix theme code.

## One-click extra while you're in admin
The last emoji on the site (wave in the chat-widget greeting) is a theme
SETTING, not code: Theme editor → chat/greeting setting → remove the wave.
