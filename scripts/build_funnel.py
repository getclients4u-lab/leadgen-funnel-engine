#!/usr/bin/env python3
"""
build_funnel.py — instantiate a funnel template with copy + tracking wiring.

Usage:
    python3 build_funnel.py --template fear-hook --out ./index.html \
        --config funnel.config.json

Reads a JSON config, fills the template placeholders, injects the tracking
(attribution + consent + analytics) block, and writes the final single-file page.

funnel.config.json shape:
{
  "offer_name": "…",
  "hook": "…",                     # <= 12 words
  "subhead": "…",                  # <= 20 words
  "agitate": ["…", "…", "…"],      # 2-4 lines
  "mechanism": "…",
  "proof": ["…", "…"],
  "magnet_name": "…",
  "magnet_desc": "…",
  "cta": "SEND MY GUIDE",          # <= 4 words
  "privacy_url": "https://…/privacy",
  "terms_url": "https://…/terms",
  "form_action": "https://…",      # webhook / CRM / Sendiio
  "brand": "Your Brand",
  "brand_url": "https://…",
  "ga4_id": "G-XXXXXXX",           # optional; omit to skip
  "require_phone": false
}
"""
import json, os, sys, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "..", "assets", "funnel-page.html")

TRACKING_BLOCK = r"""
<!-- ===== funnel tracking: attribution + consent + analytics ===== -->
<script>
(function () {
  var KEEP = ["sub1","sub2","sub3","sub4","sub5","transaction_id","msid",
              "utm_source","utm_medium","utm_campaign","utm_content","utm_term",
              "gclid","fbclid","ttclid","aff_id","affid","ref","clickid"];
  function clean(v){ return String(v == null ? "" : v).replace(/[^A-Za-z0-9._:\-]/g, "").slice(0, 128); }
  var q = new URLSearchParams(location.search);
  var payload = {};
  KEEP.forEach(function (k) { if (q.has(k)) payload[k] = clean(q.get(k)); });

  // persist attribution through the session so it survives navigation
  try { sessionStorage.setItem("funnel_attr", JSON.stringify(payload)); } catch (e) {}
  try { if (!Object.keys(payload).length) payload = JSON.parse(sessionStorage.getItem("funnel_attr") || "{}"); } catch (e) {}

  // reflect into hidden fields (sanitized above -> safe)
  window.__funnelAttr = payload;
  document.addEventListener("DOMContentLoaded", function () {
    Object.keys(payload).forEach(function (k) {
      var el = document.querySelector('input[name="' + k + '"]');
      if (!el) {
        el = document.createElement("input");
        el.type = "hidden"; el.name = k;
        var f = document.querySelector("form"); if (f) f.appendChild(el);
      }
      el.value = payload[k];
    });
  });

  // consent capture (TrustedForm-compatible pattern): record attestation BEFORE submit
  window.__funnelConsent = null;
  window.__captureConsent = function () {
    window.__funnelConsent = {
      ts: new Date().toISOString(),
      page: location.href,
      ua: navigator.userAgent,
      // In production, swap this for the real TrustedForm script and use its cert id:
      // <script src="https://api.trustedform.com/trustedform.js?..."> then window.TrustedFormCertUrl
      cert_url: (window.TrustedFormCertUrl || null),
      consent_text_version: "v1"
    };
    return window.__funnelConsent;
  };

  window.__funnelSubmit = function (ev) {
    var f = ev.target;
    var consent = document.querySelector('input[name="consent_given"]');
    if (consent && !consent.checked) {
      ev.preventDefault();
      alert("Please tick the consent box so we may contact you.");
      return false;
    }
    window.__captureConsent();
    var c = document.createElement("input");
    c.type = "hidden"; c.name = "consent_payload";
    c.value = JSON.stringify(window.__funnelConsent);
    f.appendChild(c);

    var g = document.createElement("input");
    g.type = "hidden"; g.name = "attribution";
    g.value = JSON.stringify(payload);
    f.appendChild(g);

    if (window.gtag) {
      gtag("event", "lead_submit", { offer: "__OFFER__", source: payload.utm_source || payload.sub1 || "direct" });
    }
    if (window.fbq) { fbq("track", "Lead"); }
    return true;
  };

  document.addEventListener("DOMContentLoaded", function () {
    var f = document.querySelector("form");
    if (f) f.addEventListener("submit", window.__funnelSubmit);
    if (window.gtag) gtag("event", "view_offer", { offer: "__OFFER__" });
  });
})();
</script>
__GA4__
"""


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--template", default=TPL)
    a = ap.parse_args()

    cfg = json.load(open(a.config))
    tpl = open(a.template, encoding="utf-8").read()

    repl = {
        "{{OFFER_NAME}}": esc(cfg.get("offer_name", "Your Offer")),
        "{{HOOK}}": esc(cfg.get("hook", "")),
        "{{SUBHEAD}}": esc(cfg.get("subhead", "")),
        "{{MECHANISM}}": esc(cfg.get("mechanism", "")),
        "{{MAGNET_NAME}}": esc(cfg.get("magnet_name", "Free Guide")),
        "{{MAGNET_DESC}}": esc(cfg.get("magnet_desc", "")),
        "{{CTA}}": esc(cfg.get("cta", "GET IT NOW")),
        "{{PRIVACY_URL}}": cfg.get("privacy_url", "#"),
        "{{TERMS_URL}}": cfg.get("terms_url", "#"),
        "{{FORM_ACTION}}": cfg.get("form_action", "#"),
        "{{BRAND}}": esc(cfg.get("brand", "")),
        "{{BRAND_URL}}": cfg.get("brand_url", "#"),
    }
    for k, v in repl.items():
        tpl = tpl.replace(k, v)

    # lists
    agit = "".join(f"<p class='line'>{esc(x)}</p>" for x in cfg.get("agitate", []))
    tpl = tpl.replace("{{AGITATE}}", agit)
    proof = "".join(f"<li>{esc(x)}</li>" for x in cfg.get("proof", []))
    tpl = tpl.replace("{{PROOF}}", proof)

    # optional phone field
    if cfg.get("require_phone"):
        tpl = tpl.replace("{{PHONE_FIELD}}",
            '<input type="tel" name="phone" placeholder="Phone (for your free call)" required>')
    else:
        tpl = tpl.replace("{{PHONE_FIELD}}", "")

    # tracking
    ga4 = ""
    if cfg.get("ga4_id"):
        ga4 = ("<script async src='https://www.googletagmanager.com/gtag/js?id=%s'></script>\n"
               "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
               "gtag('js',new Date());gtag('config','%s');</script>" % (cfg["ga4_id"], cfg["ga4_id"]))
    tpl = tpl.replace("{{TRACKING}}",
                      TRACKING_BLOCK.replace("__OFFER__", esc(cfg.get("offer_name", ""))).replace("__GA4__", ga4))

    open(a.out, "w", encoding="utf-8").write(tpl)
    left = [p for p in repl if p in tpl] + [p for p in ("{{AGITATE}}", "{{PROOF}}", "{{PHONE_FIELD}}", "{{TRACKING}}") if p in tpl]
    print(f"wrote {a.out} ({len(tpl):,} bytes)")
    print("unfilled placeholders:", left if left else "none")


if __name__ == "__main__":
    main()
