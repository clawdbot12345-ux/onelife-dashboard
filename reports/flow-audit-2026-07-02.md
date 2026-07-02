# Klaviyo Flow Trigger Audit — 2026-07-02

28 flows in the account. Focus flows (winback/abandon/post-purchase/checkout/replenish/sunset) include full trigger detail.

| Flow | Status | Trigger type | Created | Updated |
|---|---|---|---|---|
| PCOS Post-Purchase Flow | live | Metric | 2026-02-27 | 2026-05-05 |
| PCOS Welcome Flow | live | Added to List | 2026-02-27 | 2026-02-27 |
| Post-Purchase Education - Magnesium v1 | live | Added to List | 2026-05-14 | 2026-05-14 |
| Post-Purchase Thank You + Cross-sell v3 | draft | Metric | 2026-02-25 | 2026-06-18 |
| GLP-1 Education Drip | live | Added to List | 2026-03-17 | 2026-03-17 |
| Smile Loyalty - Reward Expiring | live | Metric | 2026-05-08 | 2026-05-08 |
| Win-Back 90/120 Days — 2026 design system | live | Metric | 2026-06-11 | 2026-06-11 |
| Abandoned Checkout Touch 2/3 Companion — 2026 design system | live | Metric | 2026-07-02 | 2026-07-02 |
| Win-Back Catch-Up — Lapsed 120d+ (2026 design system) | live | Added to List | 2026-07-01 | 2026-07-01 |
| Smile Loyalty - VIP Tier Achieved | live | Metric | 2026-05-08 | 2026-05-08 |
| Win-Back 60 Days v2 | live | Metric | 2026-02-25 | 2026-05-05 |
| Replenishment Reminder (API-created) | live | Metric | 2026-04-11 | 2026-05-05 |
| Win-Back Catch-Up — Lapsed 60–120d (2026 design system) | live | Added to List | 2026-07-01 | 2026-07-01 |
| Browse Abandonment v2 | live | Metric | 2026-02-25 | 2026-05-05 |
| Post-Purchase Education - Vitamin D v1 | live | Added to List | 2026-05-14 | 2026-05-14 |
| Abandoned Checkout Reminder - Standard (Email & SMS) | draft | Metric | 2026-02-20 | 2026-06-18 |
| Abandoned Checkout Consultant Check - SMS Companion (2026 design system) | live | Metric | 2026-06-13 | 2026-06-13 |
| Points Balance Nudge v3 | live | Metric | 2026-02-25 | 2026-02-25 |
| GLP-1 Non-Opener Follow-Up | live | Added to List | 2026-03-17 | 2026-03-17 |
| Smile Loyalty - Birthday Reward | live | Metric | 2026-05-08 | 2026-05-08 |
| Back in Stock — It's back (2026 design system) | live | Metric | 2026-06-10 | 2026-06-10 |
| Abandoned Checkout Consultant Check — 2026 design system | live | Metric | 2026-06-11 | 2026-06-11 |
| Welcome — One Life Health (Full Sequence) | live | Added to List | 2026-03-09 | 2026-03-09 |
| Back in Stock - SMS Companion (2026 design system) | live | Metric | 2026-06-13 | 2026-06-13 |
| Smile Loyalty - Points Expiring | live | Metric | 2026-05-08 | 2026-05-08 |
| Review Request - Precious Consultant Check (2026 design system) | live | Metric | 2026-06-13 | 2026-06-13 |
| Sunset Unengaged Subscribers - Standard | live | Added to List | 2026-05-05 | 2026-05-05 |
| Post-Purchase Cross-sell — 7 Day Consultant Check (2026 design system) | live | Metric | 2026-07-01 | 2026-07-01 |

## Focus flows — trigger detail

### PCOS Post-Purchase Flow (`R96wJV`, live)

```
trigger: {"type": "metric", "id": "WZAxyj", "trigger_filter": null}
  entry_action_id: 100644211
  profile_filter: {"condition_groups": [{"conditions": [{"type": "profile-metric", "metric_id": "WZAxyj", "measurement": "count", "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0}, "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": null}]}]}
```

### Post-Purchase Education - Magnesium v1 (`RTHzQF`, live)

```
trigger: {"type": "segment", "id": "VFfBEA"}
  entry_action_id: 106623409
  profile_filter: {"condition_groups": [{"conditions": [{"type": "profile-metric", "metric_id": "WZAxyj", "measurement": "count", "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0}, "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": null}]}]}
```

### Post-Purchase Thank You + Cross-sell v3 (`RpJP55`, draft)

```
trigger: {"type": "metric", "id": "WZAxyj", "trigger_filter": null}
  entry_action_id: 100378819
  profile_filter: {"condition_groups": [{"conditions": [{"type": "profile-metric", "metric_id": "WZAxyj", "measurement": "count", "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0}, "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": null}]}]}
```

### Win-Back 90/120 Days — 2026 design system (`SFMncG`, live)

```
trigger: {"type": "metric", "id": "WZAxyj", "trigger_filter": null}
  entry_action_id: 108886820
  profile_filter: {"condition_groups": [{"conditions": [{"type": "profile-metric", "metric_id": "WZAxyj", "measurement": "count", "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0}, "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": null}]}]}
```

### Abandoned Checkout Touch 2/3 Companion — 2026 design system (`SN89LS`, live)

```
definition unavailable
```

### Win-Back Catch-Up — Lapsed 120d+ (2026 design system) (`ScdmZL`, live)

```
trigger: {"type": "segment", "id": "WKxHdK"}
  entry_action_id: 110833420
  profile_filter: {"condition_groups": [{"conditions": [{"type": "profile-marketing-consent", "consent": {"channel": "email", "can_receive_marketing": true, "consent_status": {"subscription": "subscribed", "filters": null}}}]}, {"conditions": [{"type": "profile-metric", "metric_id": "WZAxyj", "measurement": "count", "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0}, "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": null}]}]}
```

### Win-Back 60 Days v2 (`TGZYKa`, live)

```
trigger: {"type": "metric", "id": "WZAxyj", "trigger_filter": null}
  entry_action_id: 100378536
  profile_filter: {"condition_groups": [{"conditions": [{"type": "profile-metric", "metric_id": "WZAxyj", "measurement": "count", "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0}, "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": null}]}]}
```

### Replenishment Reminder (API-created) (`TNBkZK`, live)

```
definition unavailable
```

### Win-Back Catch-Up — Lapsed 60–120d (2026 design system) (`UGhyug`, live)

```
trigger: {"type": "segment", "id": "TaFWcM"}
  entry_action_id: 110833418
  profile_filter: {"condition_groups": [{"conditions": [{"type": "profile-marketing-consent", "consent": {"channel": "email", "can_receive_marketing": true, "consent_status": {"subscription": "subscribed", "filters": null}}}]}, {"conditions": [{"type": "profile-metric", "metric_id": "WZAxyj", "measurement": "count", "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0}, "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": null}]}]}
```

### Browse Abandonment v2 (`UMMzhC`, live)

```
trigger: {"type": "metric", "id": "S65qWH", "trigger_filter": null}
  entry_action_id: 100378547
  profile_filter: {"condition_groups": [{"conditions": [{"type": "profile-metric", "metric_id": "WZAxyj", "measurement": "count", "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0}, "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": null}]}, {"conditions": [{"type": "profile-metric", "metric_id": "WnzuVG", "measurement": "count", "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0}, "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": null}]}]}
```

### Post-Purchase Education - Vitamin D v1 (`Unn2d2`, live)

```
trigger: {"type": "segment", "id": "V4ez3X"}
  entry_action_id: 106623480
  profile_filter: {"condition_groups": [{"conditions": [{"type": "profile-metric", "metric_id": "WZAxyj", "measurement": "count", "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0}, "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": null}]}]}
```

### Abandoned Checkout Reminder - Standard (Email & SMS) (`VAjbpG`, draft)

```
trigger: {"type": "metric", "id": "WnzuVG", "trigger_filter": null}
  entry_action_id: 100119668
  profile_filter: {"condition_groups": [{"conditions": [{"type": "profile-metric", "metric_id": "WZAxyj", "measurement": "count", "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0}, "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": null}]}, {"conditions": [{"type": "profile-not-in-flow", "timeframe_filter": {"type": "date", "operator": "in-the-last", "unit": "day", "quantity": 7}}]}]}
```

### Abandoned Checkout Consultant Check - SMS Companion (2026 design system) (`VSECqx`, live)

```
trigger: {"type": "metric", "id": "WnzuVG", "trigger_filter": null}
  entry_action_id: 109099491
  profile_filter: {"condition_groups": [{"conditions": [{"type": "profile-metric", "metric_id": "WZAxyj", "measurement": "count", "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0}, "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": null}]}, {"conditions": [{"type": "profile-not-in-flow", "timeframe_filter": {"type": "date", "operator": "in-the-last", "unit": "day", "quantity": 7}}]}, {"conditions": [{"type": "profile-marketing-consent", "consent": {"channel": "sms", "can_receive_marketing": true, "consent_status": {"subscription": "subscribed", "filters":
```

### Abandoned Checkout Consultant Check — 2026 design system (`WY4cae`, live)

```
trigger: {"type": "metric", "id": "WnzuVG", "trigger_filter": null}
  entry_action_id: 108886998
  profile_filter: {"condition_groups": [{"conditions": [{"type": "profile-metric", "metric_id": "WZAxyj", "measurement": "count", "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0}, "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": null}]}, {"conditions": [{"type": "profile-not-in-flow", "timeframe_filter": {"type": "date", "operator": "in-the-last", "unit": "day", "quantity": 7}}]}]}
```

### Sunset Unengaged Subscribers - Standard (`YrtdaV`, live)

```
trigger: {"type": "segment", "id": "Y9crXj"}
  entry_action_id: 105762429
  profile_filter: {"condition_groups": [{"conditions": [{"type": "profile-metric", "metric_id": "WF5waK", "measurement": "count", "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0}, "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": null}]}, {"conditions": [{"type": "profile-metric", "metric_id": "Y6n86M", "measurement": "count", "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0}, "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": null}]}]}
```

### Post-Purchase Cross-sell — 7 Day Consultant Check (2026 design system) (`YxRABd`, live)

```
trigger: {"type": "metric", "id": "WZAxyj", "trigger_filter": null}
  entry_action_id: 110833278
  profile_filter: {"condition_groups": [{"conditions": [{"type": "profile-metric", "metric_id": "WZAxyj", "measurement": "count", "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0}, "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": null}]}]}
```
