---
name: leadgen-funnel
description: "Build, deploy, and audit click-tracking lead-generation / quiz funnels (Instapage-style): fear-hook landing pages, multi-parameter affiliate URLs, consent tracking (TrustedForm), form capture, and ad attribution. Use when asked to create a landing page, lead magnet funnel, squeeze page, opt-in page, quiz funnel, or to audit/teardown an existing funnel URL for tracking, compliance, and conversion structure."
---

# Lead-Gen Funnel Builder

Build the **funnel**, not just the page: gated content → consent → capture → route → follow-up.

## When to use
- "Build me a landing page / squeeze page / opt-in page / lead magnet funnel"
- "Clone this funnel" (given a competitor or partner URL — e.g. an Instapage/ClickFunnels page)
- "Audit this funnel URL" (what does it track, is it compliant, how does it convert)
- Affiliate/lead-routing setups where `sub1..sub5`, `transaction_id`, or `msid` matter

## Ethics gate (READ BEFORE BUILDING)

This skill is for **legitimate offers**: your own product, a client's real service, or a
real affiliate offer you may lawfully promote. It builds fear-hook *structure* because that
structure converts — but **never** fabricate claims, fake government legitimacy, invent
scarcity that does not exist, or imply an endorsement nobody gave.

Refuse or rework when asked to:
- Impersonate a government body or official ("Government wants your dollar worth less" framing
  is allowed as *rhetoric about policy*; a fake seal, "IRS-approved", or a counterfeit agency
  header is not).
- Fabricate testimonials, credentials, or results.
- Run `sub1..sub5` routing to a marked-up lead-buyer with no disclosure that the form sells data.
- Bypass consent/consent-tracking requirements (TrustedForm/Jornaya exist for TCPA compliance).

Every build must ship: a clear **offer description**, a **privacy/disclosure link**, and a
**real** unsubscribe or contact path. If the user pressures otherwise, stop and say why.

## Funnel anatomy (the reference structure)

```
Ad / email / social  →  [FUNNEL PAGE]  →  thank-you / booking  →  nurture sequence
                         │
                         ├─ 1. Hook        fear / curiosity / status-gap headline
                         ├─ 2. Agitate     "this is happening to YOU" (specific, not vague)
                         ├─ 3. Mechanism   why it works — the credibility bridge
                         ├─ 4. Proof       numbers, names, screenshots (REAL ones only)
                         ├─ 5. Lead magnet "FREE <Guide> — no cost, no obligation"
                         ├─ 6. Form        name + email (+phone if sales calls)
                         ├─ 7. CTA         one action, repeated, above and below fold
                         ├─ 8. Risk-rev    "we never sell your data" (must be TRUE)
                         └─ 9. Tracking    attribution + consent, wired pre-launch
```

See `references/funnel-anatomy.md` for the per-section copy formulas, and
`references/tracking-audit.md` for how to read an existing funnel's tracking chain.

## Build workflow

1. **Establish the contract.**
   Collect: offer + real payout/price, target audience, traffic source (ad/email/organic),
   lead magnet, capture fields, destination after opt-in, and whether phone/SMS consent is
   needed (changes compliance load).
   *Done when:* every field above has an answer or an explicit "not needed".

2. **Pick the template.**
   - `assets/funnel-page.html` — single-file responsive fear-hook page (no build step).
   - `assets/quiz-funnel.html` — multi-step quiz variant for higher-intent capture.
   *Done when:* one template is chosen and its placeholders are listed.

3. **Write the copy into the template.**
   Use the section formulas. Keep hook ≤ 12 words, sub-headline ≤ 20, CTA ≤ 4 words.
   Run `python3 scripts/funnel_lint.py <file>` to check claim/compliance placement.
   *Done when:* lint passes and every placeholder is filled with real offer copy.

4. **Wire tracking.**
   - Attribution: parse and preserve `sub1..sub5`, `transaction_id`, `msid` from `?query`.
   - Consent: emit a TrustedForm-compatible consent capture before submit.
   - Analytics: GA4/GTM event on `view` and `lead_submit`.
   *Done when:* `scripts/build_funnel.py` has injected the tracking block and the page
   still renders (open it locally).

5. **Route the lead.**
   Point the form `action` at the real endpoint (webhook, Sendiio, AgentMail, CRM).
   Include the attribution payload so the source survives.
   *Done when:* one real test submission lands in the destination and the source params
   appear correctly.

6. **Deploy.**
   Vercel (preferred for this fleet) or any static host. Custom domain optional.
   *Done when:* the live URL loads and a test lead arrives end-to-end.

7. **Verify end-to-end.**
   - Load page → params preserved in hidden fields
   - Submit → destination receives lead + attribution
   - Thank-you shown → GA4 `lead_submit` fires
   - Lighthouse mobile ≥ 90 performance
   *Done when:* all four pass; report the live URL.

## Auditing someone else's funnel

Run `scripts/funnel_audit.py <url>` — it extracts the tracking chain, pixels, form fields,
redirect hops, and copy structure, then prints a risk report (fear-marketing flags, data-sale
indicators, missing disclosures). This is the teardown used on the Priority Gold funnel.

## Pitfalls

- **Heatmap/consent scripts make the page look empty to `web_fetch`.** Instapage/Unbounce
  pages render via JS; `readability` extraction often returns only the footer disclaimer.
  Fetch raw HTML with `curl -A "<browser UA>"` (see audit script) before concluding.
- **Never hotlink remote CDNs for client pages** — self-host fonts/images (fleet rule).
- **`sub1..sub5` are untrusted input.** Sanitize before reflecting into the DOM or a
  downstream URL; they are a common XSS/redirect-open vector.
- **Consent must precede submit**, not be bundled silently — that is the TCPA exposure point.
- Telegram delivery: after building, offer the file (files go out via Telegram `sendDocument`).
