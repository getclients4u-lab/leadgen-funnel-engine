# Lead-Gen Funnel Engine

Build, deploy, and audit **click-tracking lead-generation funnels** — the
Instapage/Unbounce style "free guide" landing pages used by affiliate and
lead-routing offers.

This repo is both a **working tool** (build a funnel from a JSON config) and a
**reference** (audit any funnel URL and see exactly what it tracks).

## What's inside

```
SKILL.md                  agent-facing workflow + ethics gate
scripts/build_funnel.py   config JSON -> single-file landing page
scripts/funnel_audit.py   teardown any funnel URL -> tracking + risk report
scripts/funnel_lint.py    pre-launch compliance / claim check
assets/funnel-page.html   responsive single-file template (no build step)
examples/                 ready-to-run sample configs
docs/                     anatomy + tracking reference
```

## Quick start

```bash
# 1. audit someone else's funnel (see what it tracks)
python3 scripts/funnel_audit.py "https://example.com/offer?sub1=93&msid=123"

# 2. build your own
python3 scripts/build_funnel.py --config examples/retirement-shield.json --out ./dist/index.html

# 3. check it before you ship
python3 scripts/funnel_lint.py ./dist/index.html
```

Then deploy `dist/` to any static host (Vercel is one command).

## What the template gets right

| Concern | How it's handled |
|---|---|
| Attribution | `sub1..sub5`, `transaction_id`, `msid`, `utm_*`, click IDs captured into hidden fields **and** `sessionStorage`, so the source survives navigation |
| Consent (TCPA) | Consent checkbox is **required before submit**; attestation payload (timestamp, page, UA, cert URL) is captured with the lead |
| Injection | `sub*` values are sanitized to `[A-Za-z0-9._:-]`, max 128 chars — untrusted input is never reflected raw |
| Analytics | GA4 `view_offer` / `lead_submit` + Meta `Lead` events |
| Disclosures | Privacy, terms, "no obligation", "not financial advice" shipped by default |
| Claims | Lint **fails the build** on `guaranteed return`, `risk-free`, `IRS-approved`, etc. |

## Ethics

This tool builds fear-hook **structure** because that structure converts. It
refuses to fabricate claims, fake government legitimacy, invent scarcity, or
route lead data to a buyer without disclosure. Every build must ship a real
offer description, a privacy link, and a working opt-out. See `SKILL.md`.

## Audit output, by example

Run against a real gold-IRA funnel, the audit reports:

```
kinds: ad-attribution, behavior-analytics, consent-tracking, form-capture, funnel-builder
sub/utm/click params : {'sub1': '93', 'sub2': '9f3c…', 'transaction_id': 'aaf3…', 'msid': '56091_93'}
captures email: True   phone: True
RISK FLAGS: fear-marketing x9
VERDICT: HIGH RISK — fear-driven, tracked lead capture
```

## License

MIT
