#!/usr/bin/env python3
"""
funnel_lint.py — pre-launch check for a built funnel page.

Checks copy limits, required disclosures, tracking wiring, and unsafe
patterns. Exit 1 if any ERROR-level issue is found.

Usage:
    python3 funnel_lint.py <file.html>
"""
import sys, re, html, os

ERRORS, WARNS, OKS = [], [], []


def text_of(h):
    h = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"ERROR: file not found: {path}"); sys.exit(1)
    raw = open(path, encoding="utf-8").read()
    low = raw.lower()
    text = text_of(raw)
    tlow = text.lower()

    # placeholders
    left = re.findall(r"\{\{[A-Z_0-9]+\}\}", raw)
    if left:
        ERRORS.append(f"unfilled placeholders: {sorted(set(left))}")
    else:
        OKS.append("all placeholders filled")

    # required disclosures
    for need, label in [(("privacy policy",), "privacy policy link"),
                        (("terms",), "terms link")]:
        if not any(n in low for n in need):
            ERRORS.append(f"missing {label}")
        else:
            OKS.append(f"{label} present")
    if "no obligation" not in tlow and "no cost" not in tlow:
        WARNS.append("no 'no cost / no obligation' reassurance near the form")
    if "not financial" not in tlow and "not investment advice" not in tlow and "not legal" not in tlow:
        WARNS.append("no 'not financial advice' disclaimer in footer")

    # consent must exist and precede submit
    if 'name="consent_given"' not in low:
        ERRORS.append("no consent checkbox (TCPA exposure)")
    else:
        OKS.append("consent checkbox present")
    if "consent_payload" not in low:
        WARNS.append("consent not captured into payload (TrustedForm/cert pattern missing)")

    # tracking
    if "sub1" not in low or "attribution" not in low:
        WARNS.append("attribution params not wired into the form")
    else:
        OKS.append("attribution params wired")
    if "gtag(" not in low and "gtm.js" not in low:
        WARNS.append("no analytics event (GTM/GA4) — you will be blind on traffic")

    # sanitization of reflected params
    if re.search(r"sub1.*innerHTML", low, re.S) or "document.write" in low:
        ERRORS.append("untrusted param reflected unsafely (document.write / innerHTML)")

    # external hotlinks (fleet rule: self-host for client sites)
    ext = re.findall(r'(?:src|href)="(https?://(?!www\.googletagmanager|fonts\.googleapis|api\.trustedform)[^"]+)"', raw)
    if ext:
        WARNS.append(f"{len(ext)} external asset link(s) — self-host images/fonts before launch")

    # unfilled fake-claim guard
    for bad in ["guaranteed return", "risk-free", "risk free", "irs-approved", "government-approved"]:
        if bad in tlow:
            ERRORS.append(f"prohibited claim present: '{bad}'")

    # copy length heuristics
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", raw, re.S | re.I)
    if h1:
        n = len(re.sub(r"<[^>]+>", "", html.unescape(h1.group(1))).split())
        if n > 12:
            WARNS.append(f"hook is {n} words (target <= 12)")
        else:
            OKS.append(f"hook length ok ({n} words)")

    # report
    print("=" * 62)
    print("FUNNEL LINT:", os.path.basename(path))
    print("=" * 62)
    for o in OKS:
        print("  [ok]   " + o)
    for w in WARNS:
        print("  [warn] " + w)
    for e in ERRORS:
        print("  [FAIL] " + e)
    print()
    if ERRORS:
        print(f"RESULT: FAIL ({len(ERRORS)} error(s), {len(WARNS)} warning(s))")
        sys.exit(1)
    print(f"RESULT: PASS ({len(WARNS)} warning(s))")


if __name__ == "__main__":
    main()
