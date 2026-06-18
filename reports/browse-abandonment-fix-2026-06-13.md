# Browse Abandonment Flow — Fix Spec (2026-06-13)

**Trigger:** customer complaint — got a "Still thinking about {{ product }}? 👀"
email ~minutes after searching the site; felt surveilled, unsubscribed.

**Flow:** "Browse Abandonment v2" — ID `UMMzhC` — edit at
https://www.klaviyo.com/flow/UMMzhC/edit
(Klaviyo flow timing/filters are UI-only — no public API/MCP write, so apply by hand.)

## Current state (verified via API)
- Trigger: Viewed Product metric → **2-hour** time delay → email (template TJiVpH),
  subject `Still thinking about {{ event.Name }}? 👀`, smart-sending on.
- Profile filter: Placed Order = 0 AND Started Checkout = 0 since flow start.
- **No frequency cap** → a repeat browser gets an email on basically every visit.

## Apply these changes
1. **Time delay 2h → 72h (3 days).** (Owner's call. Note: research sweet spot for
   *conversion* is ~24h; 3 days is the gentler, lower-pressure option.)
2. **Add frequency cap (root-cause fix for "every time I search"):** flow filter
   **"Has not been in this flow in the last 30 days"** (14 acceptable).
3. **Soften the email** — browse = low intent, make it a *light* touch, not cart-style.
   Replace the subject `Still thinking about {{ event.Name }}? 👀` with a helpful,
   non-watching line, e.g. "A little something from the apothecary" / "Need a hand
   choosing?". Keep Precious voice, no urgency.
4. Keep existing no-order/no-checkout filters + Smart Sending ON. Optional: also
   require engaged-in-last-90-days so only people who want email get nudged.

## Also (raised separately, important)
The complainer felt they never opted in ("marketing mails that started at some
stage"). Audit how profiles get email-marketing consent (single-opt-in Email List
Xrk5jD, checkout, etc.) — browse/marketing should only go to explicit opt-ins (POPIA).

## Sources
- Klaviyo Help — browse abandonment flows: https://help.klaviyo.com/hc/en-us/articles/115002775252
- Klaviyo Community — managing browse/checkout best practices: https://community.klaviyo.com/marketing-30/managing-browse-abandonment-abandoned-checkout-flow-best-practices-18565
- Glaze Digital — browse abandon flow build: https://glazedigital.com/blogs/news/guide-how-to-build-browse-abandon-flow-klaviyo
- Mailchimp — browse abandonment emails: https://mailchimp.com/resources/browse-abandonment-emails/
