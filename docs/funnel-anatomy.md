# Funnel Anatomy — the 9 sections and their copy formulas

Every converting lead-gen page is the same nine sections. The **order** matters more
than the wording: identity → threat → mechanism → proof → offer → action.

## 1. Hook (H1, ≤ 12 words)

One sentence that names a **specific** threat or desire. Two viable modes:

- **Fear/urgency** — "The Government Wants Your Dollar To Be Worth Less"
- **Gain/curiosity** — "How Savers Are Repositioning Before The Next Rate Cycle"

Rules: name a *concrete* thing, not a vague benefit. "Shield Your Savings" loses to
"Inflation Is Quietly Taxing Your Retirement Savings." Numbers beat adjectives.

## 2. Sub-headline (≤ 20 words)

Expands the hook with **who it's for** and **what they get**. No new claim here —
this is where you make the promise specific enough to qualify the audience.

## 3. Agitate (2–4 short lines)

The bridge from "that's true" to "that affects me." Each line should escalate:
general fact → personal consequence → cost of inaction.

Use **second person**. "Your savings" beats "savings." Name the cost of doing
nothing in concrete units (dollars, years, purchasing power).

## 4. Mechanism

*Why* your thing works. This is the credibility hinge — without it the page is
just fear plus a form. One paragraph, plain language. If the mechanism can't be
said simply, you don't have one yet.

## 5. Proof

Numbers, names, screenshots, credentials — **only real ones.** The lint script
fails the build on fabricated-claim patterns. If you have nothing, use
"what you get" bullets instead of testimonials. Never invent social proof.

## 6. Lead magnet

The thing they trade an email for. Must be:
- **Specific** ("Retirement Shield Guide" not "Free Report")
- **Real** (you actually have to deliver it)
- **Fast** (instant download > "we'll call you")

The offer line "100% free — no cost, no obligation" measurably lifts opt-in and is
also good disclosure practice.

## 7. Form

Field count is the single biggest conversion lever.

| Fields | Typical use | Trade-off |
|---|---|---|
| Email only | Free guide, content | Highest volume, lowest intent |
| + First name | Nurture sequence | Personalization, ~5% drop |
| + Phone | Sales call, high ticket | 50–70% drop, needs TCPA consent |

Iron rule: **every field you add must be used in the next 24 hours.** An unused
field is pure friction.

## 8. Consent (not optional)

Consent must be **affirmative and precede submit** — a pre-ticked box is invalid
and is the exact exposure TCPA/TrustedForm exist to document. Ship:

- A visible unchecked checkbox
- A short statement of what they're agreeing to
- Timestamp + page + UA + cert URL captured into the lead payload

## 9. Tracking

See `tracking-audit.md`. The three layers — attribution, consent, analytics —
must all be wired *before* traffic starts, because you cannot retroactively
attribute leads you didn't tag.

## CTA rules

- **One** action. Two competing CTAs halve both.
- ≤ 4 words, first person where possible ("Send My Guide" > "Submit")
- Repeat it above and below the fold
- Never "Learn More" — it costs a click and pays nothing

## Common failure modes

| Symptom | Cause |
|---|---|
| High traffic, no leads | Hook doesn't name a specific threat; or form has too many fields |
| Leads, no sales | Magnet attracts browsers not buyers — magnet and offer misaligned |
| Leads don't close | No attribution, so sales can't see source; or no follow-up sequence |
| Legal complaint | Consent absent/bundled, or a claim the lint should have caught |
