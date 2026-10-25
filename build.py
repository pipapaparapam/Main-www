# -*- coding: utf-8 -*-
"""Builds the static Court Rhythm site from src/.

    python build.py

Writes index.html, privacy.html, terms.html, delete-account.html, pl/index.html, pl/polityka-prywatnosci.html, pl/regulamin.html, pl/usun-konto.html,
404.html and sitemap.xml next to this file. No other dependencies.
"""
import html
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))
from strings import EN, PL  # noqa: E402

SITE = "https://www.courtrhythm.com"
EMAIL = "contact@courtrhythm.com"
PLAY_URL = ""      # set to the Google Play listing URL once it is public; empty = "Coming soon"
LAUNCH_ISO = "2026-10-31T00:00:00+01:00"   # UNUSED since v9 (countdown block removed, release plan item 22); see v9 report to restore
VERSION = "20261025f"                        # bump to bust browser caches for CSS/JS
SOCIALS = {
    "facebook": "https://www.facebook.com/share/19Qm8t7J7A/",
    "instagram": "https://www.instagram.com/courtrhythm",
    "linkedin": "https://www.linkedin.com/company/courtrhythm/",
}
COMPANY = {
    "address": "ul. Borowej Góry 6 lok. 2, 01-354 Warszawa, Polska",
    "address_en": "ul. Borowej Góry 6 lok. 2, 01-354 Warsaw, Poland",
    "krs": "0001192219",
    "nip": "5223346100",
    "regon": "542640518",
}

# Clean public URLs (canonical) and the files that serve them.
PAGES = {
    ("en", "home"): ("/", "index.html"),
    ("pl", "home"): ("/pl/", "pl/index.html"),
    ("en", "privacy"): ("/privacy.html", "privacy.html"),
    ("pl", "privacy"): ("/pl/polityka-prywatnosci.html", "pl/polityka-prywatnosci.html"),
    ("en", "terms"): ("/terms.html", "terms.html"),
    ("pl", "terms"): ("/pl/regulamin.html", "pl/regulamin.html"),
    ("en", "delete"): ("/delete-account.html", "delete-account.html"),
    ("pl", "delete"): ("/pl/usun-konto.html", "pl/usun-konto.html"),
}

assert set(EN) == set(PL), "strings.py: keys differ: %s" % (set(EN) ^ set(PL))

ICON = {
    "facebook": '<path d="M13.5 22v-8h2.6l.4-3h-3V7.2c0-.9.3-1.5 1.6-1.5H16V3.1c-.3 0-1.6-.1-3-.1-3 0-5 1.8-5 5.2V11H5.5v3h2.5v8h5.5Z"/>',
    "instagram": '<path d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5Zm0 2a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3H7Zm5 3.5A5.5 5.5 0 1 1 6.5 13 5.5 5.5 0 0 1 12 7.5Zm0 2A3.5 3.5 0 1 0 15.5 13 3.5 3.5 0 0 0 12 9.5Zm5.25-3.25a1.25 1.25 0 1 1-1.25 1.25 1.25 1.25 0 0 1 1.25-1.25Z"/>',
    "linkedin": '<path d="M6.94 8.5A1.56 1.56 0 1 1 6.94 5.4a1.56 1.56 0 0 1 0 3.1ZM5.5 9.8h2.9v9.7H5.5V9.8Zm5.1 0h2.8v1.3h.1c.4-.7 1.4-1.5 2.9-1.5 3 0 3.6 2 3.6 4.7v5.2h-2.9v-4.8c0-1.1 0-2.5-1.6-2.5s-1.8 1.2-1.8 2.4v4.9h-2.9V9.8Z"/>',
}
PHONE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="6" y="2.5" width="12" height="19" rx="2.5"/><path d="M10.5 18.5h3"/></svg>'


def rel(from_file, to_file):
    """Relative link between two output files, so the site also works from a folder preview."""
    r = os.path.relpath(to_file, os.path.dirname(from_file) or ".").replace(os.sep, "/")
    return r


def head(t, lang, page, out, extra_ld=None):
    url, _ = PAGES[(lang, page)]
    alt_en = SITE + PAGES[("en", page)][0]
    alt_pl = SITE + PAGES[("pl", page)][0]
    a = lambda p: rel(out, p)  # noqa: E731
    title = t["title"] if page == "home" else "%s | Court Rhythm" % t[page + "_title"]
    desc = t["description"] if page == "home" else t[page + "_desc"]
    og_img = SITE + ("/assets/img/og-image-pl.png" if lang == "pl" else "/assets/img/og-image.png")
    ld = [{
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": SITE + "/#org",
        "name": "Court Rhythm",
        "legalName": "BEMZ Europe sp. z o.o.",
        "url": SITE + "/",
        "logo": SITE + "/assets/img/icon-512.png",
        "email": EMAIL,
        "taxID": COMPANY["nip"],
        "address": {"@type": "PostalAddress", "streetAddress": "ul. Borowej Góry 6 lok. 2",
                    "postalCode": "01-354", "addressLocality": "Warszawa", "addressCountry": "PL"},
        "sameAs": list(SOCIALS.values()),
    }, {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Court Rhythm",
        "url": SITE + "/",
        "inLanguage": ["en", "pl"],
        "publisher": {"@id": SITE + "/#org"},
    }]
    if extra_ld:
        ld.append(extra_ld)
    ld_html = "\n".join('<script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False) for x in ld)
    return f"""<!doctype html>
<html lang="{t['html_lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#0b1326">
<link rel="canonical" href="{SITE}{url}">
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="pl" href="{alt_pl}">
<link rel="alternate" hreflang="x-default" href="{alt_en}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Court Rhythm">
<meta property="og:locale" content="{t['og_locale']}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{SITE}{url}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{a('favicon.svg')}" type="image/svg+xml">
<link rel="icon" href="{a('assets/img/icon-192.png')}" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="{a('apple-touch-icon.png')}">
<link rel="manifest" href="{a('site.webmanifest')}">
<link rel="preload" href="{a('assets/fonts/jakarta-var.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{a('assets/fonts/inter-var.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{a('assets/css/site.css')}?v={VERSION}">
{ld_html}
</head>"""


def header(t, lang, page, out):
    a = lambda p: rel(out, p)  # noqa: E731
    home = a(PAGES[(lang, "home")][1])
    on_home = page == "home"
    anchor = (lambda h: "#" + h) if on_home else (lambda h: home + "#" + h)
    en_target = a(PAGES[("en", page)][1])
    pl_target = a(PAGES[("pl", page)][1])
    if lang == "en":
        langs = f'<span aria-current="true" lang="en">EN</span><a href="{pl_target}" hreflang="pl" lang="pl">PL<span class="visually-hidden"> (polski)</span></a>'
    else:
        langs = f'<a href="{en_target}" hreflang="en" lang="en">EN<span class="visually-hidden"> (English)</span></a><span aria-current="true" lang="pl">PL</span>'
    return f"""<body>
<a class="skip-link" href="#main">{t['skip']}</a>
<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="{home}" aria-label="Court Rhythm">
      <img src="{a('assets/img/logo.svg')}" alt="" width="36" height="36">
      <span>Court <span>Rhythm</span></span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
      <span class="visually-hidden">{t['menu']}</span>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
    <nav class="nav" id="site-nav" aria-label="{t['menu']}">
      <a href="{anchor('app')}">{t['nav_app']}</a>
      <a href="{anchor('privacy')}">{t['nav_privacy']}</a>
      <a href="{anchor('roadmap')}">{t['nav_roadmap']}</a>
      <a href="{anchor('team')}">{t['nav_team']}</a>
      <a href="{anchor('partners')}">{t['nav_partners']}</a>
      <a href="{anchor('contact')}">{t['nav_contact']}</a>
      <div class="lang-switch" role="group" aria-label="{t['lang_label']}">{langs}</div>
      <a class="btn btn-primary btn-small" href="{anchor('get')}">{t['nav_notify']}</a>
    </nav>
  </div>
</header>"""


def socials(t):
    items = "".join(
        f'<li><a href="{u}" rel="noopener" target="_blank"><span class="visually-hidden">{n.capitalize()}</span>'
        f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICON[n]}</svg></a></li>'
        for n, u in SOCIALS.items())
    return f'<ul class="socials" aria-label="{t["socials_label"]}">{items}</ul>'


def footer(t, lang, out):
    a = lambda p: rel(out, p)  # noqa: E731
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-row">
      <a class="brand" href="{a(PAGES[(lang, 'home')][1])}"><img src="{a('assets/img/logo.svg')}" alt="" width="36" height="36"><span>Court <span>Rhythm</span></span></a>
      <ul class="footer-links">
        <li><a href="{a(PAGES[(lang, 'privacy')][1])}">{t['footer_privacy']}</a></li>
        <li><a href="{a(PAGES[(lang, 'terms')][1])}">{t['footer_terms']}</a></li>
        <li><a href="{a(PAGES[(lang, 'delete')][1])}">{t['footer_delete']}</a></li>
        <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
      </ul>
    </div>
    <p class="credits">&copy; <span data-year>2026</span> {t['footer_rights']} {t['credits']}</p>
  </div>
</footer>
<script src="{a('assets/js/site.js')}?v={VERSION}" defer></script>
</body>
</html>
"""


COURT_MAP = """<figure class="court-map">
<svg viewBox="0 0 560 500" role="img" aria-labelledby="map-title">
  <title id="map-title">{alt}</title>
  <rect width="560" height="500" fill="#081020"/>
  <path class="cm-park" d="M330 210 L520 190 L540 330 L360 350 Z"/>
  <path class="cm-park" d="M30 380 L170 372 L176 470 L36 478 Z"/>
  <g>
    <path class="cm-street major" d="M-10 248 C160 232 380 214 570 170"/>
    <path class="cm-street major" d="M248 -10 C258 160 268 330 282 510"/>
    <path class="cm-street" d="M-10 92 L570 60"/><path class="cm-street" d="M-10 360 L570 372"/>
    <path class="cm-street" d="M120 -10 L136 510"/><path class="cm-street" d="M420 -10 L404 182"/>
    <path class="cm-street" d="M404 182 L560 420"/><path class="cm-street" d="M200 92 C190 150 150 200 120 240"/>
    <path class="cm-street" d="M282 300 C330 300 360 360 350 510"/>
  </g>
  <!-- courts: basketball A, football B, volleyball C, quiet D and E -->
  <g transform="translate(150 120) rotate(-4)">
    <rect class="cm-court-fill" x="0" y="0" width="76" height="42" rx="2"/>
    <rect class="cm-court" x="0" y="0" width="76" height="42" rx="2"/><path class="cm-court" d="M38 0V42"/><circle class="cm-court" cx="38" cy="21" r="7"/>
    <path class="cm-court" d="M0 9 C14 9 18 15 18 21 C18 27 14 33 0 33 M76 9 C62 9 58 15 58 21 C58 27 62 33 76 33"/>
  </g>
  <g transform="translate(296 104) rotate(-6)">
    <rect class="cm-court-fill" x="0" y="0" width="104" height="62" rx="2"/>
    <rect class="cm-court" x="0" y="0" width="104" height="62" rx="2"/><path class="cm-court" d="M52 0V62"/><circle class="cm-court" cx="52" cy="31" r="10"/>
    <rect class="cm-court" x="0" y="17" width="14" height="28"/><rect class="cm-court" x="90" y="17" width="14" height="28"/>
  </g>
  <g transform="translate(400 262) rotate(8)">
    <rect class="cm-court-fill" x="0" y="0" width="64" height="34" rx="2"/>
    <rect class="cm-court" x="0" y="0" width="64" height="34" rx="2"/><path class="cm-court" d="M32 -4V38" stroke-width="2.4"/>
  </g>
  <g transform="translate(60 300)">
    <rect class="cm-court-fill" x="0" y="0" width="62" height="34" rx="2"/>
    <rect class="cm-court" x="0" y="0" width="62" height="34" rx="2" opacity=".6"/><path class="cm-court" d="M31 0V34" opacity=".6"/>
  </g>
  <g transform="translate(300 400) rotate(3)">
    <rect class="cm-court-fill" x="0" y="0" width="62" height="34" rx="2"/>
    <rect class="cm-court" x="0" y="0" width="62" height="34" rx="2" opacity=".6"/><path class="cm-court" d="M31 0V34" opacity=".6"/>
  </g>
  <!-- live counts (orange = people playing now) -->
  <g transform="translate(188 108)"><circle class="cm-pin-ring" r="18"/><circle class="cm-count-bg" r="18"/><text class="cm-count" text-anchor="middle" y="5.5">7</text></g>
  <g transform="translate(350 90)"><circle class="cm-pin-ring d2" r="20"/><circle class="cm-count-bg" r="20"/><text class="cm-count" text-anchor="middle" y="5.5">12</text></g>
  <g transform="translate(432 254)"><circle class="cm-pin-ring d3" r="18"/><circle class="cm-count-bg" r="18"/><text class="cm-count" text-anchor="middle" y="5.5">4</text></g>
  <g transform="translate(91 292)"><circle class="cm-quiet" r="14"/><text class="cm-quiet-text" text-anchor="middle" y="4.5">0</text></g>
  <g transform="translate(331 394)"><circle class="cm-quiet" r="14"/><text class="cm-quiet-text" text-anchor="middle" y="4.5">0</text></g>
  <!-- the rhythm line from the logo -->
  <path class="cm-pulse" d="M0 462 H170 L205 418 L245 492 L282 436 L304 460 H560"/>
  <circle class="cm-ball" cx="300" cy="414" r="9"/>
</svg>
<figcaption>{caption}</figcaption>
</figure>"""


def home(t, lang):
    out = PAGES[(lang, "home")][1]
    a = lambda p: rel(out, p)  # noqa: E731
    privacy = a(PAGES[(lang, "privacy")][1])
    qr = a("assets/img/qr-%s.svg" % lang)
    addr = COMPANY["address_en"] if lang == "en" else COMPANY["address"]
    android_store = (f'<a class="store" href="{PLAY_URL}" rel="noopener">{PHONE}<span><b>{t["store_android"]}</b><small>{t["store_get"]}</small></span></a>'
                     if PLAY_URL else
                     f'<span class="store" aria-disabled="true">{PHONE}<span><b>{t["store_android"]}</b><small>{t["store_soon"]}</small></span></span>')
    subj = html.escape(t["part_subject"]).replace(" ", "%20")
    ball = lambda n: a("assets/img/%s.svg" % n)  # noqa: E731
    page = head(t, lang, "home", out) + header(t, lang, "home", out) + f"""
<main id="main">

<section class="hero" aria-labelledby="hero-title">
  <div class="wrap hero-grid">
    <div>
      <p class="status"><span class="live-dot" aria-hidden="true"></span>{t['status']}</p>
      <h1 id="hero-title">{t['h1_1']}<span class="line-2">{t['h1_2']}</span></h1>
      <p class="lead">{t['lead']}</p>
      <div class="cta-row">
        <a class="btn btn-primary" href="#get">{t['cta_notify']}</a>
        <a class="btn btn-secondary" href="#partners">{t['cta_partner']}</a>
      </div>
      <ul class="sports" aria-label="{t['sports_label']}">
        <li><img src="{ball('basketball')}" alt="" width="22" height="22">{t['basketball']}</li>
        <li><img src="{ball('soccer')}" alt="" width="22" height="22">{t['football']}</li>
        <li><img src="{ball('volleyball')}" alt="" width="22" height="22">{t['volleyball']}</li>
      </ul>
      <p class="motto">{t['motto_pre']} <em>{t['motto']}</em></p>
    </div>
    {COURT_MAP.format(alt=html.escape(t['map_alt']), caption=t['map_caption'])}
  </div>
</section>

<section class="section" aria-labelledby="why-title">
  <div class="wrap">
    <div class="section-head">
      <h2 id="why-title">{t['why_h2']}</h2>
      <p>{t['why_p']}</p>
    </div>
    <ul class="problem-list">
      <li><h3>{t['why_1_h']}</h3><p>{t['why_1_p']}</p></li>
      <li><h3>{t['why_2_h']}</h3><p>{t['why_2_p']}</p></li>
      <li><h3>{t['why_3_h']}</h3><p>{t['why_3_p']}</p></li>
    </ul>
  </div>
</section>

<section class="section" id="app" aria-labelledby="how-title">
  <div class="wrap">
    <div class="section-head">
      <h2 id="how-title">{t['how_h2']}</h2>
      <p>{t['how_p']}</p>
    </div>
    <ol class="steps">
      <li><h3>{t['step_1_h']}</h3><p>{t['step_1_p']}</p></li>
      <li><h3>{t['step_2_h']}</h3><p>{t['step_2_p']}</p></li>
      <li><h3>{t['step_3_h']}</h3><p>{t['step_3_p']}</p></li>
    </ol>
    <h3 class="features-title">{t['feat_h']}</h3>
    <dl class="features">
      <div><dt>{t['f1_t']}</dt><dd>{t['f1_d']}</dd></div>
      <div><dt>{t['f2_t']}</dt><dd>{t['f2_d']}</dd></div>
      <div><dt>{t['f3_t']}</dt><dd>{t['f3_d']}</dd></div>
      <div><dt>{t['f4_t']}</dt><dd>{t['f4_d']}</dd></div>
      <div><dt>{t['f5_t']}</dt><dd>{t['f5_d']}</dd></div>
      <div><dt>{t['f6_t']}</dt><dd>{t['f6_d']}</dd></div>
    </dl>
    <!-- SCREENSHOTS: when real app screenshots or short clips arrive, add a gallery here.
         Use only real screenshots from the app (PNG/WebP, max 1080 px wide, with width/height
         attributes and descriptive alt text). Short clips: MP4 + WebM, muted, playsinline,
         with a poster image and no autoplay sound. -->
  </div>
</section>

<section class="section" id="privacy" aria-labelledby="privacy-title">
  <div class="wrap privacy-band">
    <div>
      <p class="big-zero" aria-hidden="true">0</p>
      <p class="big-zero-caption"><span class="visually-hidden">0 </span>{t['priv_zero_caption']}</p>
    </div>
    <div>
      <h2 id="privacy-title" style="font-size:clamp(1.6rem,3vw,2.2rem);margin-bottom:28px">{t['priv_h2']}</h2>
      <ul class="check-list">
        <li><strong>{t['p1_t']}</strong><span>{t['p1_d']}</span></li>
        <li><strong>{t['p2_t']}</strong><span>{t['p2_d']}</span></li>
        <li><strong>{t['p3_t']}</strong><span>{t['p3_d']}</span></li>
        <li><strong>{t['p4_t']}</strong><span>{t['p4_d']}</span></li>
        <li><strong>{t['p5_t']}</strong><span>{t['p5_d']}</span></li>
      </ul>
      <p style="margin-top:28px"><a href="{privacy}">{t['priv_link']}</a></p>
    </div>
  </div>
</section>

<section class="section" id="roadmap" aria-labelledby="road-title">
  <div class="wrap">
    <div class="section-head">
      <h2 id="road-title">{t['road_h2']}</h2>
      <p>{t['road_p']}</p>
    </div>
    <ol class="roadmap">
      <li class="is-next"><span class="when">{t['r1_when']}</span><h3>{t['r1_h']}</h3><p>{t['r1_p']}</p></li>
      <li><span class="when">{t['r2_when']}</span><h3>{t['r2_h']}</h3><p>{t['r2_p']}</p></li>
      <li><span class="when">{t['r3_when']}</span><h3>{t['r3_h']}</h3><p>{t['r3_p']}</p></li>
      <li><span class="when">{t['r4_when']}</span><h3>{t['r4_h']}</h3><p>{t['r4_p']}</p></li>
    </ol>
    <div class="later">
      <h3>{t['later_h']}</h3>
      <ul>
        <li><strong>{t['l1_t']}</strong><span>{t['l1_d']}</span></li>
        <li><strong>{t['l2_t']}</strong><span>{t['l2_d']}</span></li>
        <li><strong>{t['l3_t']}</strong><span>{t['l3_d']}</span></li>
      </ul>
    </div>
  </div>
</section>

<section class="section" id="team" aria-labelledby="team-title">
  <div class="wrap">
    <div class="section-head">
      <h2 id="team-title">{t['team_h2']}</h2>
      <p>{t['team_p']}</p>
    </div>
    <div class="team">
      <article class="person">
        <div class="monogram" aria-hidden="true">BB</div>
        <div><h3>Bartosz Biernat</h3><p class="role">{t['bb_role']}</p><p>{t['bb_bio']}</p></div>
      </article>
      <article class="person">
        <div class="monogram" aria-hidden="true">ZK</div>
        <div><h3>Zsófia Kuttner</h3><p class="role">{t['zk_role']}</p><p>{t['zk_bio']}</p></div>
      </article>
    </div>
  </div>
</section>

<section class="section" id="partners" aria-labelledby="part-title">
  <div class="wrap">
    <div class="section-head partner-head">
      <h2 id="part-title">{t['part_h2']}</h2>
      <p>{t['part_p']}</p>
    </div>
    <div class="partner-showcase">
      <p class="partner-showcase-intro">{t['sponsor_intro']}</p>
      <div class="sponsor-grid" aria-label="{t['sponsor_title']}">
        <article class="sponsor-card">
          <div class="sponsor-mark" aria-hidden="true">M</div>
          <div class="sponsor-copy">
            <span class="sponsor-label">{t['sponsor_1_label']}</span>
            <h3>{t['sponsor_1_title']}</h3>
            <p>{t['sponsor_1_text']}</p>
          </div>
        </article>
        <article class="sponsor-card">
          <div class="sponsor-mark" aria-hidden="true">S</div>
          <div class="sponsor-copy">
            <span class="sponsor-label">{t['sponsor_2_label']}</span>
            <h3>{t['sponsor_2_title']}</h3>
            <p>{t['sponsor_2_text']}</p>
          </div>
        </article>
        <article class="sponsor-card">
          <div class="sponsor-mark" aria-hidden="true">G</div>
          <div class="sponsor-copy">
            <span class="sponsor-label">{t['sponsor_3_label']}</span>
            <h3>{t['sponsor_3_title']}</h3>
            <p>{t['sponsor_3_text']}</p>
          </div>
        </article>
        <article class="sponsor-card">
          <div class="sponsor-mark" aria-hidden="true">C</div>
          <div class="sponsor-copy">
            <span class="sponsor-label">{t['sponsor_4_label']}</span>
            <h3>{t['sponsor_4_title']}</h3>
            <p>{t['sponsor_4_text']}</p>
          </div>
        </article>
      </div>
    </div>
    <div class="cta-row partner-cta"><a class="btn btn-primary" href="mailto:{EMAIL}?subject={subj}">{t['part_cta']}</a></div>
  </div>
</section>

<section class="section" id="get" aria-labelledby="get-title">
  <div class="wrap get">
    <div>
      <div class="section-head" style="margin-bottom:0">
        <h2 id="get-title">{t['get_h2']}</h2>
        <p>{t['get_p']}</p>
      </div>
      <div class="stores">
        {android_store}
        <span class="store" aria-disabled="true">{PHONE}<span><b>{t['store_ios']}</b><small>{t['store_soon']}</small></span></span>
      </div>
      <p class="store-note">{t['store_note']}</p>
    </div>
    <div class="scan scan-side">
      <img src="{qr}" alt="{t['qr_alt']}" width="112" height="112">
      <p><strong>{t['scan_t']}</strong>{t['scan_p']}</p>
    </div>
  </div>
</section>

<section class="section" id="contact" aria-labelledby="contact-title">
  <div class="wrap company">
    <div>
      <h2 id="contact-title" style="font-size:clamp(2rem,4.2vw,3.3rem)">{t['contact_h2']}</h2>
      <p style="color:var(--muted);margin-top:16px">{t['contact_p']}</p>
      <a class="contact-mail" href="mailto:{EMAIL}">{EMAIL}</a>
      {socials(t)}
    </div>
    <div>
      <h3 style="font-size:1.35rem;margin-bottom:20px">{t['company_h']}</h3>
      <dl class="registry">
        <dt>{t['reg_name']}</dt><dd>{t['reg_name_v']}</dd>
        <dt>{t['reg_addr']}</dt><dd>{addr}</dd>
        <dt>{t['reg_krs']}</dt><dd>{COMPANY['krs']}</dd>
        <dt>{t['reg_court']}</dt><dd>{t['reg_court_v']}</dd>
        <dt>{t['reg_nip']}</dt><dd>{COMPANY['nip']}</dd>
        <dt>{t['reg_regon']}</dt><dd>{COMPANY['regon']}</dd>
        <dt>{t['reg_capital']}</dt><dd>{t['reg_capital_v']}</dd>
        <dt>{t['reg_board']}</dt><dd>{t['reg_board_v']}</dd>
      </dl>
      <p class="registry-note">{t['reg_note']}</p>
    </div>
  </div>
</section>

<section class="closing" aria-labelledby="closing-title">
  <div class="wrap">
    <svg class="closing-pulse" viewBox="0 0 1200 90" aria-hidden="true"><path d="M0 60 H640 L680 18 L725 86 L765 34 L790 58 H1200"/><circle cx="785" cy="14" r="10"/></svg>
    <h2 id="closing-title">{t['closing']}</h2>
    <p>{t['closing_p']}</p>
    <div class="cta-row"><a class="btn btn-primary" href="#get">{t['cta_notify']}</a></div>
  </div>
</section>

</main>
""" + footer(t, lang, out)
    return out, page


def privacy(t, lang, page="privacy"):
    out = PAGES[(lang, page)][1]
    a = lambda p: rel(out, p)  # noqa: E731
    body = open(os.path.join(ROOT, "src", "%s.%s.html" % (page, lang)), encoding="utf-8").read()
    body = (body.replace("{EMAIL}", EMAIL).replace("{HOME}", a(PAGES[(lang, "home")][1]))
            .replace("{PRIVACY}", a(PAGES[(lang, "privacy")][1])))
    # table of contents from the h2 ids
    toc = "".join('<li><a href="#%s">%s</a></li>' % (i, re.sub("<[^>]+>", "", h))
                  for i, h in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body))
    html_page = head(t, lang, page, out) + header(t, lang, page, out) + f"""
<main id="main" class="doc">
  <div class="wrap doc-grid">
    <nav class="toc" aria-label="{t['toc']}"><p>{t['toc']}</p><ol>{toc}</ol></nav>
    <article class="doc-body">
{body}
    </article>
  </div>
</main>
""" + footer(t, lang, out)
    return out, html_page


def not_found():
    # GitHub Pages serves 404.html at any path, so links here are absolute.
    t = EN
    return "404.html", f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t['nf_title']} | Court Rhythm</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#0b1326">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/css/site.css?v={VERSION}">
</head>
<body>
<main class="wrap notfound">
  <div>
    <a class="brand" href="/" style="justify-content:center;margin-bottom:40px"><img src="/assets/img/logo.svg" alt="" width="36" height="36"><span>Court <span>Rhythm</span></span></a>
    <h1>{t['nf_title']}</h1>
    <p>{t['nf_p']} <span lang="pl">{PL['nf_p']}</span></p>
    <div class="cta-row" style="justify-content:center">
      <a class="btn btn-primary" href="/">{t['nf_cta']}</a>
      <a class="btn btn-secondary" href="/pl/" lang="pl">{PL['nf_cta']}</a>
    </div>
  </div>
</main>
</body>
</html>
"""


def sitemap():
    today = date.today().isoformat()
    urls = []
    for page in ("home", "privacy", "terms", "delete"):
        for lang in ("en", "pl"):
            loc = SITE + PAGES[(lang, page)][0]
            alts = "".join('\n    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (l2, SITE + PAGES[(l2, page)][0]) for l2 in ("en", "pl"))
            alts += '\n    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % (SITE + PAGES[("en", page)][0])
            urls.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today}</lastmod>{alts}\n  </url>")
    return "sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n"


def main():
    outputs = [home(EN, "en"), home(PL, "pl"), privacy(EN, "en"), privacy(PL, "pl"), privacy(EN, "en", "terms"), privacy(PL, "pl", "terms"), privacy(EN, "en", "delete"), privacy(PL, "pl", "delete"), not_found(), sitemap()]
    for path, content in outputs:
        full = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        print("wrote", path, len(content.encode("utf-8")), "bytes")


if __name__ == "__main__":
    main()
