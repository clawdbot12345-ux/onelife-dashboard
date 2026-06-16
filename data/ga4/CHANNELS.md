# GA4 channel correction

The raw GA4 `sessionDefaultChannelGroup` is preserved in `session_default_channel_group`.
The dashboard should use `corrected_channel_group` and only count rows where
`include_in_acquisition` is `true` for acquisition reporting.

## Rules

| Rule | Match | Output |
| --- | --- | --- |
| Internal/payment exclusion | Source or medium contains PayFast, checkout, customer account, Shopify account, Shop app, myshopify, onelife.co.za, or accounts.google.com | `corrected_channel_group = "Excluded - internal/payment"`, `include_in_acquisition = false` |
| Email app correction | Source or medium contains email, e-mail, newsletter, Klaviyo, Gmail, mail.google, googlemail, Outlook, Hotmail, iCloud, Yahoo Mail, webmail, or l.wl.co | `corrected_channel_group = "Email"`, `include_in_acquisition = true` |
| Default | No correction match | Keep GA4's `session_default_channel_group`, `include_in_acquisition = true` |

These rules correct known One Life issues where PayFast/account/login returns
polluted acquisition and Gmail/email-app referrals landed outside Email.
