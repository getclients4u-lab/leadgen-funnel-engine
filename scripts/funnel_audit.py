#!/usr/bin/env python3
"""
funnel_audit.py — teardown + risk report for an existing landing/funnel page.

Usage:
    python3 funnel_audit.py <url> [--json out.json]

Because JS-heavy builders (Instapage, Unbounce, ClickFunnels) render client-side,
readability extractors see almost nothing. This script fetches RAW HTML with a
browser UA and analyses the real markup.
"""
import sys, re, json, subprocess, urllib.parse, html

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

# Known tracking / consent / attribution hosts -> what they mean
TRACKERS = {
    "trustedform.com": ("consent-tracking", "Records consent for TCPA compliance (required for phone/SMS leads)."),
    "jornaya.com": ("consent-tracking", "LeadiD consent token, TCPA evidence."),
    "fastcdn.co": ("form-capture", "Unbounce/lead form submission endpoint."),
    "instapage.com": ("funnel-builder", "Page hosted on Instapage (click-tracking funnel)."),
    "instapagemetrics.com": ("behavior-analytics", "Click/scroll/heatmap telemetry."),
    "heatmap-events-collector": ("behavior-analytics", "Session recording / heatmaps."),
    "googletagmanager": ("ad-attribution", "GTM container; ad + conversion attribution."),
    "google-analytics": ("analytics", "GA4 measurement."),
    "facebook.net": ("ad-pixel", "Meta pixel; audience building + retargeting."),
    "fbq(": ("ad-pixel", "Meta pixel init."),
    "tiktok.com": ("ad-pixel", "TikTok pixel."),
    "linkedin.com/px": ("ad-pixel", "LinkedIn insight tag."),
    "hotjar": ("behavior-analytics", "Session recording."),
    "clarity.ms": ("behavior-analytics", "Microsoft Clarity session replay."),
    "doubleclick": ("ad-attribution", "Google ad click tracking."),
}

# Attribution params commonly used for lead routing / affiliate payout
SUB_PARAMS = ["sub1", "sub2", "sub3", "sub4", "sub5", "transaction_id", "msid",
              "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term",
              "gclid", "fbclid", "ttclid", "aff_id", "affid", "ref", "clickid"]

FEAR_WORDS = ["before it's too late", "before its too late", "fight back", "under attack",
              "chilling", "trap snaps", "while you still can", "gutted", "they come for yours",
              "collapse", "crash is coming", "survive", "crisis", "destroy", "wiped out"]
URGENCY_WORDS = ["today only", "limited time", "expires", "act now", "last chance",
                 "spots left", "while supplies last", "hurry"]
FINANCIAL_CLAIM_WORDS = ["guaranteed return", "risk-free", "risk free", "no risk",
                         "double your", "guaranteed profit", "safe investment",
                         "irs-approved", "tax-free retirement", "government-approved"]
DISCLOSURE_HINTS = ["privacy policy", "terms", "disclaimer", "not investment advice",
                    "we do not sell", "consent", "unsubscribe", "opt-out",
                    "no obligation", "seek your own"]


def fetch(url):
    p = subprocess.run(["curl", "-sL", "--max-time", "30", "-A", UA, url],
                       capture_output=True, text=True)
    return p.stdout or ""


def visible_text(h):
    h = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<[^>]+>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(h)).strip()


def audit(url):
    raw = fetch(url)
    low = raw.lower()
    text = visible_text(raw)
    tlow = text.lower()
    final = raw  # single-hop; redirect chain reported separately by --hops

    report = {"url": url, "bytes": len(raw), "findings": {}}

    # --- tracking chain ---
    found = []
    for host, (kind, why) in TRACKERS.items():
        if host in low:
            found.append({"host": host, "kind": kind, "why": why})
    report["findings"]["trackers"] = found
    report["findings"]["tracker_kinds"] = sorted({f["kind"] for f in found})

    # --- attribution params ---
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    report["findings"]["attribution_params"] = {k: v[0] for k, v in q.items() if k in SUB_PARAMS}
    report["findings"]["unknown_params"] = [k for k in q if k not in SUB_PARAMS]
    report["findings"]["is_tracked_link"] = bool(report["findings"]["attribution_params"])

    # --- form fields ---
    fields = []
    for inp in re.findall(r"<input[^>]*>", low):
        name = re.search(r'name="([^"]*)"', inp)
        typ = re.search(r'type="([^"]*)"', inp)
        fields.append({"name": name.group(1) if name else None,
                       "type": typ.group(1) if typ else None})
    report["findings"]["form_fields"] = fields
    report["findings"]["captures_phone"] = any(
        f["type"] in ("tel", "phone") or (f["name"] and "phone" in f["name"]) for f in fields)
    report["findings"]["captures_email"] = any(
        f["type"] == "email" or (f["name"] and "email" in f["name"]) for f in fields)

    # --- copy structure: headings ---
    heads = []
    for tag in ("h1", "h2", "h3"):
        for m in re.findall(r"<%s[^>]*>(.*?)</%s>" % (tag, tag), raw, re.S | re.I):
            t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(m))).strip()
            if t:
                heads.append({"tag": tag.upper(), "text": t[:180]})
    report["findings"]["headings"] = heads

    # --- risk flags ---
    flags = []
    for w in FEAR_WORDS:
        if w in tlow:
            flags.append({"type": "fear-marketing", "match": w})
    for w in URGENCY_WORDS:
        if w in tlow:
            flags.append({"type": "manufactured-urgency", "match": w})
    for w in FINANCIAL_CLAIM_WORDS:
        if w in tlow:
            flags.append({"type": "financial-claim", "match": w})
    disc = [d for d in DISCLOSURE_HINTS if d in tlow or d in low]
    report["findings"]["risk_flags"] = flags
    report["findings"]["disclosures_present"] = disc
    report["findings"]["missing_disclosures"] = [
        d for d in ("privacy policy", "terms", "unsubscribe") if d not in disc]
    report["findings"]["data_sale_risk"] = (
        report["findings"]["is_tracked_link"]
        and report["findings"]["captures_phone"]
        and "privacy policy" not in disc)

    # --- thin content check (JS-rendered pages) ---
    report["findings"]["visible_text_chars"] = len(text)
    report["findings"]["js_rendered_likely"] = len(text) < 1500 and len(raw) > 20000
    report["findings"]["text_sample"] = text[:600]

    return report


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    url = sys.argv[1]
    rep = audit(url)
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        json.dump(rep, open(out, "w"), indent=2)
        print("wrote", out)

    f = rep["findings"]
    print("=" * 66)
    print("FUNNEL AUDIT:", rep["url"][:90])
    print("=" * 66)
    print(f"raw bytes           : {rep['bytes']:,}")
    print(f"visible text chars  : {f['visible_text_chars']:,}"
          + ("   <-- JS-rendered (extractors see little)" if f["js_rendered_likely"] else ""))
    print()
    print("TRACKING CHAIN")
    for t in f["trackers"] or [{"host": "(none detected)", "kind": "-", "why": ""}]:
        print(f"  - {t['host']:<34} {t['kind']}")
    print(f"  kinds: {', '.join(f['tracker_kinds']) or '-'}")
    print()
    print("ATTRIBUTION")
    print(f"  sub/utm/click params : {f['attribution_params'] or '-'}")
    print(f"  other params         : {f['unknown_params'] or '-'}")
    print(f"  tracked link?        : {f['is_tracked_link']}")
    print()
    print("CAPTURE")
    print(f"  email: {f['captures_email']}   phone: {f['captures_phone']}   fields: {len(f['form_fields'])}")
    print()
    print("HEADINGS")
    for h in f["headings"][:8]:
        print(f"  {h['tag']}: {h['text'][:110]}")
    print()
    print("RISK FLAGS")
    if f["risk_flags"]:
        for r in f["risk_flags"][:14]:
            print(f"  [!] {r['type']:<22} \"{r['match']}\"")
    else:
        print("  none detected")
    print()
    print("DISCLOSURES")
    print(f"  present : {f['disclosures_present'] or '-'}")
    print(f"  MISSING : {f['missing_disclosures'] or '-'}")
    print(f"  data-sale risk (tracked + phone + no privacy): {f['data_sale_risk']}")
    print()
    verdict = ("HIGH RISK — fear-driven, tracked lead capture"
               if len(f["risk_flags"]) >= 4 and f["is_tracked_link"] else
               "MODERATE — review disclosures and offer substance"
               if f["is_tracked_link"] or f["risk_flags"] else
               "LOW flags — still verify the offer's substance independently")
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
