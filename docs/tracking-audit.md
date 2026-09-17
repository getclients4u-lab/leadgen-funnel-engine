# Tracking Audit — reading a funnel's tracking chain

When you audit a competitor's (or a partner's) funnel, you are answering:
**who gets paid, for what, and is the visitor told?** The page's own pixels
answer that better than its copy does.

## The three layers

Every serious funnel has three independent layers. A funnel missing one leaks
money; a funnel missing two is amateur.

### 1. Attribution — *where did they come from?*

Carried in the URL and persisted forward:

| Param | Meaning |
|---|---|
| `sub1`..`sub5` | Free-form slots the *advertiser* fills per traffic source |
| `transaction_id` | Unique click/lead id for reconciliation with the buyer |
| `msid` | Media/source id — often `<offer_id>_<sub_id>` |
| `utm_*` | Campaign taxonomy (source/medium/campaign/content/term) |
| `gclid`/`fbclid`/`ttclid` | Platform click ids (ad-level attribution) |

If you see `sub*` **and** a `transaction_id`, you are looking at an
**affiliate/lead-buying** funnel. Someone is paid per lead, and the id is how
they prove which click produced it.

**Failure mode:** params read on landing but not persisted into the form.
The lead arrives with no source, and the affiliate never gets credited.

### 2. Consent — *did they agree?*

| Vendor | Role |
|---|---|
| `trustedform.com` | Records a certificate of consent (TCPA evidence) |
| `jornaya.com` / LeadiD | Same idea, different vendor |
| `activeprospect` | Parent of TrustedForm |

Presence of a consent vendor is **not** proof of good practice — it proves
someone in the chain expects litigation risk. It is required whenever phone
numbers are captured and dialed.

**Failure mode:** consent bundled into the submit click with no checkbox, or
captured *after* submission. Both are indefensible in a TCPA complaint.

### 3. Analytics — *what did they do?*

| Vendor | Role |
|---|---|
| `googletagmanager` | GTM container — ad + conversion attribution |
| `google-analytics` | GA4 |
| `facebook.net` / `fbq(` | Meta pixel — retargeting audiences |
| `instapagemetrics` / `hotjar` / `clarity.ms` | Heatmaps, session replay |

Session replay is the one people miss. It records typing and scrolling —
which is why `input[type=password]` masking exists.

## Teardown method

`scripts/funnel_audit.py` fetches **raw HTML with a browser UA**. This matters:
builders like Instapage render client-side, so readability extractors return
almost nothing. A 120 KB page with 3 KB of visible text is a JS-rendered
funnel — audit the markup, not the readable text.

The script reports: tracker hosts + kinds, attribution params, form fields,
heading structure, risk flags (fear/urgency/claim language), disclosures
present vs missing, and a coarse data-sale risk heuristic.

## Interpreting the verdict

| Signal | Reading |
|---|---|
| Tracker chain + `sub*` + phone capture | Lead-gen funnel with real payout |
| Consent vendor present | Chain expects TCPA exposure — a good sign, conditionally |
| Fear copy + no named author + no offer substance | Marketing to impulse, not to buyers |
| Tracked + phone capture + **no privacy policy** | Strong data-sale indicator |
| `sub*` reflected into DOM unsafely | XSS/redirect-open vector |

**A funnel being well-built says nothing about the offer being good.** The
tracking shows the *business model* is real and monetized. Judge the offer
separately — fees, counterparty, regulator history, and whether you'd buy it
without the headline.
