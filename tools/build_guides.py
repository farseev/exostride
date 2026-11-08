#!/usr/bin/env python3
"""Render the English guides in content/guides/*.txt into guides/<slug>/index.html,
then rebuild the guide hub cards, llms.txt guide list and llms-full.txt guide section.

Standard library only. The nine original guides are hand-kept HTML and are left untouched;
this script only (re)writes guides that have a content file.

Content file format (see any file in content/guides/):
    key: value lines (slug, w, pillar, title, desc, keywords, q, a, stats, hero, duo, og, wa, related, date)
    ---
    markdown-ish body: '## H2', paragraphs separated by blank lines, '- ' bullets,
    '[[duo]]' to place the image pair, '? Question' + answer paragraph inside the FAQ.
    Inline links: [text](guide:slug) or [text](home:#try).
"""
import html, json, os, re, sys, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://exostride.sg"
SKELETON = os.path.join(ROOT, "guides", "hip-torque-16nm-explained", "index.html")

SECTION = {"W1": "Rehabilitation &amp; dignity", "W2": "Specs, explained",
           "W3": "Stairs &amp; the last mile", "W4": "Outdoor, measured"}
WS_SOURCE = {"W1": "aging-in-place-powered-exoskeleton", "W2": "hip-torque-16nm-explained",
             "W3": "powered-hip-assist-for-stairs", "W4": "trekking-poles-vs-powered-exoskeleton"}
ORIGINAL = ["aging-in-place-powered-exoskeleton", "exoskeleton-for-elderly-parent-caregiver-guide",
            "exoskeleton-vs-walking-frame-cane-wheelchair", "hip-torque-16nm-explained",
            "exoskeleton-battery-life-explained", "ip54-rating-tropical-climate",
            "powered-hip-assist-for-stairs", "exoskeleton-daily-commute-singapore",
            "trekking-poles-vs-powered-exoskeleton"]

# Descriptive alt text per image (used for hero/duo images on new guides)
ALT = {
    "exostride-adaptive-power-stairs-closeup.jpg": "Close-up of the ExoStride hip unit and thigh link as the wearer climbs a step",
    "exostride-climbing-stairs-confidence.jpg": "A woman wearing the ExoStride hip exoskeleton climbing an outdoor staircase",
    "exostride-commuter-hip-exoskeleton-overpass.jpg": "A commuter wearing the ExoStride hip exoskeleton crossing an overhead bridge",
    "exostride-commuter-portrait-mrt-singapore.jpg": "A commuter wearing ExoStride over office clothes at a Singapore MRT station",
    "exostride-elderly-couple-afternoon-walk.jpg": "An older couple on an afternoon walk, one wearing the ExoStride hip exoskeleton",
    "exostride-hiker-boardwalk-macritchie.jpg": "A hiker wearing ExoStride on a forest boardwalk at MacRitchie",
    "exostride-hiking-forest-trail-singapore.jpg": "A hiker wearing ExoStride on a forest trail in Singapore",
    "exostride-rainforest-boardwalk-singapore.jpg": "A walker wearing ExoStride on a rainforest boardwalk in Singapore",
    "exostride-rehabilitation-walk-park-singapore.jpg": "An older man walking in a Singapore park wearing the ExoStride hip exoskeleton",
    "exostride-station-stairs-dhoby-ghaut.jpg": "A commuter wearing ExoStride on the stairs of an MRT station",
    "exostride-summit-rest-energy-to-spare.jpg": "A hiker wearing ExoStride resting at a hilltop viewpoint",
    "exostride-wet-market-morning-run.jpg": "An older woman wearing ExoStride on a morning trip to the wet market",
    "gen-commute-stairs.jpg": "A commuter wearing a powered hip exoskeleton walking up station stairs",
    "gen-outdoor-trail.jpg": "A hiker wearing a powered hip exoskeleton on a tropical trail",
    "gen-rehab-couple.jpg": "An older couple walking together, one wearing a powered hip exoskeleton",
    "gen-rehab-stairs.jpg": "An older adult wearing a powered hip exoskeleton on a short flight of stairs",
}

esc = lambda s: html.escape(s, quote=True)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def parse(path):
    raw = read(path)
    head, body = raw.split("\n---\n", 1)
    meta = {}
    for line in head.splitlines():
        if line.strip() and not line.startswith("#"):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    meta["body"] = body
    return meta


def inline(s, depth="../../"):
    """markdown links + escape; text is written plain (no raw HTML) in content files."""
    out, pos = [], 0
    for m in re.finditer(r"\[([^\]]+)\]\((guide|home):([^)]*)\)", s):
        out.append(esc(s[pos:m.start()]).replace("&#x27;", "&#x27;"))
        kind, target = m.group(2), m.group(3)
        href = depth + ("guides/" + target + "/" if kind == "guide" else target)
        out.append('<a href="%s">%s</a>' % (href, esc(m.group(1))))
        pos = m.end()
    out.append(esc(s[pos:]))
    return "".join(out)


def plain(s):
    return re.sub(r"\[([^\]]+)\]\((guide|home):[^)]*\)", r"\1", s)


def render_body(meta):
    """returns (article_html_before_faq, faq list[(q,a)], wordcount)"""
    blocks, faq = [], []
    words = len(plain(meta["a"]).split())
    lines = meta["body"].strip().split("\n")
    para, lst, in_faq, q = [], [], False, None
    duo = [x.strip() for x in meta.get("duo", "").split(",") if x.strip()]

    def flush():
        nonlocal para, lst, q, words
        if para:
            text = " ".join(para)
            words += len(plain(text).split())
            if in_faq and q is not None:
                faq.append((q, text)); q = None
            else:
                blocks.append("<p>%s</p>" % inline(text))
            para = []
        if lst:
            words += sum(len(plain(i).split()) for i in lst)
            blocks.append('<ul class="pts">%s</ul>' % "".join("<li><span>%s</span></li>" % inline(i) for i in lst))
            lst = []

    for ln in lines:
        s = ln.strip()
        if not s:
            flush(); continue
        if s.startswith("## "):
            flush()
            if s[3:].strip().lower() == "faq":
                in_faq = True; continue
            words += len(s[3:].split())
            blocks.append('<h2 class="disp">%s</h2>' % esc(s[3:].strip()))
        elif s == "[[duo]]":
            flush()
            if len(duo) == 2:
                blocks.append('<div class="duo">' + "".join(
                    '<div class="ph"><img src="../../assets/%s" alt="%s" loading="lazy" width="800" height="1020"></div>'
                    % (d, esc(ALT[d])) for d in duo) + "</div>")
        elif s.startswith("- "):
            if para: flush()
            lst.append(s[2:])
        elif s.startswith("? "):
            flush(); q = s[2:].strip(); words += len(q.split())
        else:
            if lst: flush()
            para.append(s)
    flush()
    return "".join(blocks), faq, words


def ws_notes():
    out = {}
    for w, slug in WS_SOURCE.items():
        h = read(os.path.join(ROOT, "guides", slug, "index.html"))
        m = re.search(r'<div class="ws-note">.*?</div>', h, re.S)
        out[w] = m.group(0)
    return out


def ld(obj):
    return '<script type="application/ld+json">%s</script>' % json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def wa(text):
    return "https://wa.me/6591227009?text=" + urllib.parse.quote(text, safe="")


def build_page(meta, titles, skel, notes):
    slug = meta["slug"]; url = "%s/guides/%s/" % (SITE, slug)
    title = meta["title"]; full = title + " | ExoStride Singapore"
    desc = meta["desc"]; date = meta.get("date", "2026-11-08")
    w = meta["w"]; sec = SECTION[w]; og = meta.get("og", "og-default.jpg")
    hero = meta["hero"]
    art, faq, words = render_body(meta)
    stats = "".join('<div><b>%s</b><span>%s</span></div>' % (esc(a.strip()), esc(b.strip()))
                    for a, b in (x.split("|") for x in meta["stats"].split(";;")))
    faq_html = '<h2 class="disp" id="faq">Frequently asked questions</h2><div class="faq">' + "".join(
        '<details%s><summary>%s</summary><div class="a">%s</div></details>' % (" open" if i == 0 else "", esc(q), inline(a))
        for i, (q, a) in enumerate(faq)) + "</div>"
    related = [r.strip() for r in meta["related"].split(",")]
    rel_html = "".join('<li><a href="../../guides/%s/">%s</a></li>' % (r, esc(titles.get(r) or sys.exit('unknown related guide: '+r))) for r in related)
    wa_url = esc(wa(meta["wa"]))

    lds = [
        re.search(r'<script type="application/ld\+json">\{"@context":"https://schema.org","@type":"Organization".*?</script>', skel).group(0),
        re.search(r'<script type="application/ld\+json">\{"@context":"https://schema.org","@type":"WebSite".*?</script>', skel).group(0),
        ld({"@context": "https://schema.org", "@type": "Article", "@id": url + "#article", "headline": title, "name": title,
            "description": desc, "abstract": plain(meta["a"]), "inLanguage": "en-SG",
            "mainEntityOfPage": {"@type": "WebPage", "@id": url},
            "image": {"@type": "ImageObject", "url": "%s/assets/%s" % (SITE, og), "width": 1200, "height": 630},
            "datePublished": date, "dateModified": date,
            "author": {"@id": SITE + "/#organization"}, "publisher": {"@id": SITE + "/#organization"},
            "about": {"@id": SITE + "/#product"}, "mentions": [{"@type": "Product", "name": "ExoStride US-H-1.0Pro"}],
            "keywords": meta["keywords"], "articleSection": html.unescape(sec), "wordCount": words,
            "isAccessibleForFree": True}),
        ld({"@context": "https://schema.org", "@type": "QAPage", "inLanguage": "en-SG",
            "mainEntity": {"@type": "Question", "name": meta["q"], "text": meta["q"], "answerCount": 1,
                           "acceptedAnswer": {"@type": "Answer", "text": plain(meta["a"]), "url": url + "#answer"}}}),
        ld({"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "en-SG",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in faq]}),
        ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": SITE + "/guides/"},
            {"@type": "ListItem", "position": 3, "name": title, "item": url}]}),
        ld({"@context": "https://schema.org", "@type": "WebPage", "@id": url + "#webpage", "url": url, "name": full,
            "description": desc, "inLanguage": "en-SG", "isPartOf": {"@id": SITE + "/#website"},
            "primaryImageOfPage": {"@type": "ImageObject", "url": "%s/assets/%s" % (SITE, hero)},
            "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".answer", "h1"]}}),
    ]
    gtag = skel[skel.index('<script async src="https://www.googletagmanager.com'):skel.index("</head>")]
    nav = skel[skel.index('<body>'):skel.index('<div class="art-head">')]
    nav = nav.replace('<a href="../../zh/guides/hip-torque-16nm-explained/" hreflang="zh-Hans-SG"', '<a href="../../zh/guides/"')
    nav = nav.replace("hip-torque-16nm-explained", slug)
    svg = re.search(r'<svg viewBox="0 0 24 24" aria-hidden="true">.*?</svg>', skel).group(0)
    footer = skel[skel.index("<footer>"):]
    e = esc
    page = f"""<!DOCTYPE html>
<html lang="en-SG">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(full)}</title>
<meta name="description" content="{e(desc)}">
<meta name="keywords" content="{e(meta['keywords'])}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en-SG" href="{url}"><link rel="alternate" hreflang="x-default" href="{url}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
<meta name="googlebot" content="index, follow, max-snippet:-1, max-image-preview:large">
<meta name="author" content="HT Science &amp; Development Pte. Ltd.">
<meta name="publisher" content="HT Science &amp; Development Pte. Ltd.">
<meta name="geo.region" content="SG">
<meta name="geo.placename" content="Singapore">
<meta name="theme-color" content="#141519">
<meta name="format-detection" content="telephone=yes">
<meta property="og:type" content="article">
<meta property="og:site_name" content="ExoStride Singapore">
<meta property="og:locale" content="en_SG">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{e(full)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE}/assets/{og}">
<meta property="og:image:secure_url" content="{SITE}/assets/{og}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(full)}">
<meta property="article:published_time" content="{date}"><meta property="article:modified_time" content="{date}"><meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(full)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{SITE}/assets/{og}">
<meta name="twitter:image:alt" content="{e(full)}">
<link rel="icon" href="../../assets/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="../../assets/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="../../assets/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="../../assets/favicon-16x16.png">
<link rel="icon" type="image/png" sizes="192x192" href="../../assets/favicon-192x192.png">
<link rel="apple-touch-icon" sizes="180x180" href="../../assets/apple-touch-icon.png">
<link rel="manifest" href="../../site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="image" href="../../assets/{hero}">
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,100,400;0,100,500;0,100,600;0,100,700;0,125,800;1,125,700;1,125,800;1,125,900&family=IBM+Plex+Mono:wght@500;600&family=Noto+Sans+SC:wght@400;500;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/site.css">
<script>if('IntersectionObserver' in window)document.documentElement.className+=' js';</script>
{''.join(lds)}{gtag}</head>
{nav}<div class="art-head">
 <div class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="../../">Home</a>
   <span>/</span><a href="../../guides/">Guides</a>
   <span>/</span>{sec}</nav>
  <h1 class="disp">{e(title)}</h1>
  <div class="art-meta">
   <span class="on">{e(meta['pillar'])}</span>
   <span>{sec}</span>
   <span>Updated {date}</span>
  </div>
 </div>
</div>
<figure class="art-hero"><img src="../../assets/{hero}" alt="{e(ALT[hero])}"
  fetchpriority="high" width="800" height="533"></figure>
<main id="main"><div class="artwrap">
<article>
 <div class="answer" id="answer"><span class="lab">The short answer</span>
  <p><strong>{e(meta['q'])}</strong></p>
  <p>{inline(meta['a'])}</p></div>
 <div class="artstats">{stats}</div>{art}{faq_html}{notes[w]}</article><aside class="rail">
 <div class="card">
  <h2>Talk to the Singapore team</h2>
  <p>Exclusive Singapore seller. A guided fitting on your own route — home, trail or commute.</p>
  <a class="btn wa" href="{wa_url}" target="_blank" rel="noopener" data-wa="rail-{slug}"><span>Chat on WhatsApp</span></a>
  <p style="margin:14px 0 0;font-size:13px">Tel <a href="tel:+6583550979" style="color:var(--crimson)">+65 8355 0979</a></p>
 </div>
 <div class="card">
  <h2>US-H-1.0Pro at a glance</h2>
  <div class="spec"><span>Peak assist torque</span><b>16 Nm</b></div><div class="spec"><span>Weight</span><b>2.4 kg</b></div><div class="spec"><span>Ingress protection</span><b>IP54</b></div><div class="spec"><span>Assistance per charge</span><b>Up to 4 h</b></div><div class="spec"><span>Full charge</span><b>2 h</b></div>
 </div>
 <div class="card">
  <h2>Related guides</h2>
  <ul>{rel_html}</ul>
 </div>
</aside>
</div><section class="band">
 <div class="wrap">
  <h2 class="disp">Try it on your own route.</h2>
  <p>Exclusive Singapore seller. A guided fitting on your own route — home, trail or commute.</p>
  <div class="cta-row">
   <a class="btn wa" href="https://wa.me/6591227009?text=Hi%2C%20I%27d%20like%20to%20learn%20about%20ExoStride%20and%20book%20a%20fitting%20in%20Singapore." target="_blank" rel="noopener" data-wa="band"><span>Chat on WhatsApp</span></a>
   <a class="btn ghost" href="../../#try"><span>Book a fitting</span></a>
  </div>
 </div>
</section></main><a class="wafab" href="{wa_url}" target="_blank" rel="noopener" data-wa="fab" aria-label="WhatsApp us">{svg}<span>WhatsApp us</span></a>{footer}"""
    return page, words, faq


def original_meta(slug):
    h = read(os.path.join(ROOT, "guides", slug, "index.html"))
    g = lambda p: html.unescape(re.search(p, h, re.S).group(1))
    sec = g(r'<span>/</span>([^<]*)</nav>')
    w = {html.unescape(v): k for k, v in SECTION.items()}[sec]
    return {"slug": slug, "title": g(r'<h1 class="disp">(.*?)</h1>'), "desc": g(r'<meta name="description" content="([^"]*)"'),
            "hero": g(r'art-hero"><img src="../../assets/([^"]+)"'), "pillar": g(r'<span class="on">([^<]*)</span>'), "w": w}


def all_guides():
    new = [parse(os.path.join(ROOT, "content", "guides", f)) for f in sorted(os.listdir(os.path.join(ROOT, "content", "guides"))) if f.endswith(".txt")]
    new.sort(key=lambda m: int(m.get("order", "999")))
    return [original_meta(s) for s in ORIGINAL], new


def build_hub(guides):
    p = os.path.join(ROOT, "guides", "index.html")
    h = read(p)
    a = h.index('<main id="main"><section><div class="wrap">') + len('<main id="main"><section><div class="wrap">')
    b = h.index('</div></section><section class="band">')
    clusters = re.findall(r'<div class="clu">\s*<div class="clu-h">.*?</div>', h[a:b], re.S)
    out = []
    for w, head in zip(["W1", "W2", "W3", "W4"], clusters):
        cards = "".join(
            '<a class="gcard" href="../guides/%s/"><img src="../assets/%s" alt="%s" loading="lazy" width="800" height="533"><div class="in"><span class="kick">%s</span><h3>%s</h3><p>%s</p><span class="go">Read the guide →</span></div></a>'
            % (g["slug"], g["hero"], esc(g["title"]), esc(g["pillar"]), esc(g["title"]), esc(g["desc"])) for g in guides if g["w"] == w)
        out.append(head + '\n  <div class="cards">' + cards + "</div>\n </div>")
    h = h[:a] + "".join(out) + h[b:]
    # intro + CollectionPage ItemList
    n = len(guides)
    h = re.sub(r'(<p style="color:#B9BEC7;margin-top:18px;max-width:62ch">)[^<]*(</p>)',
               r'\1Plain-language guides on what a powered hip exoskeleton changes — at home, in recovery, on the stairs, on the commute and on a climb. Every performance figure is labelled as a manufacturer claim.\2', h)
    m = re.search(r'<script type="application/ld\+json">(\{"@context":"https://schema.org","@type":"CollectionPage".*?)</script>', h)
    d = json.loads(m.group(1))
    d["description"] = "Plain-language guides to powered hip exoskeletons: rehabilitation and everyday dignity, specs and claims explained, stairs and commutes, and measured outdoor comparisons — with the Singapore context."
    d["mainEntity"]["numberOfItems"] = n
    d["mainEntity"]["itemListElement"] = [{"@type": "ListItem", "position": i + 1, "url": "%s/guides/%s/" % (SITE, g["slug"]), "name": g["title"]} for i, g in enumerate(guides)]
    h = h.replace(m.group(0), ld(d))
    h = re.sub(r'(<meta (?:name|property)="(?:description|og:description|twitter:description)" content=")[^"]*(")',
               lambda mm: mm.group(1) + esc(d["description"]) + mm.group(2), h)
    write(p, h)


def build_llms(guides, new_meta):
    p = os.path.join(ROOT, "llms.txt")
    t = read(p)
    lines = ["- [Guides index](%s/guides/): %d plain-language guides." % (SITE, len(guides))]
    for g in guides:
        lines.append("- [%s](%s/guides/%s/): %s" % (g["title"], SITE, g["slug"], g["desc"]))
    t = re.sub(r"- \[Guides index\].*?\n(?=\n## )", "\n".join(lines) + "\n", t, flags=re.S)
    write(p, t)
    # llms-full: append generated section for new guides (idempotent)
    p = os.path.join(ROOT, "llms-full.txt")
    t = read(p)
    marker_a, marker_b = "<!-- generated-guides:start -->\n", "<!-- generated-guides:end -->\n"
    if marker_a in t:
        t = t[:t.index(marker_a)] + t[t.index(marker_b) + len(marker_b):]
    parts = [marker_a]
    for m in new_meta:
        parts.append("### %s\n\nURL: %s/guides/%s/\n\nQuestion: %s\n\nAnswer: %s\n\n" % (m["title"], SITE, m["slug"], m["q"], plain(m["a"])))
        _, faq, _ = render_body(m)
        for line in m["body"].strip().split("\n"):
            s = line.strip()
            if s.lower() == "## faq":
                break
            if s == "[[duo]]":
                continue
            parts.append(("#### " + s[3:] if s.startswith("## ") else plain(s)) + "\n")
        parts.append("\n" + "".join("- Q: %s\n  A: %s\n" % (q, plain(a)) for q, a in faq) + "\n")
    parts.append(marker_b)
    t = t.replace("## Editorial method", "".join(parts) + "## Editorial method", 1)
    write(p, t)


def update_sitemap(new):
    """Add English-only <url> entries for new guides (the i18n build later rewrites sitemaps fully)."""
    p = os.path.join(ROOT, "sitemap.xml")
    t = read(p)
    if "<sitemapindex" in t:
        return
    add = []
    for m in new:
        u = "%s/guides/%s/" % (SITE, m["slug"])
        if "<loc>%s</loc>" % u in t:
            continue
        add.append('<url><loc>%s</loc><xhtml:link rel="alternate" hreflang="en-SG" href="%s"/><xhtml:link rel="alternate" hreflang="x-default" href="%s"/><lastmod>%s</lastmod><changefreq>monthly</changefreq><priority>0.8</priority><image:image><image:loc>%s/assets/%s</image:loc></image:image></url>\n'
                   % (u, u, u, m.get("date", "2026-11-08"), SITE, m["hero"]))
    t = t.replace("</urlset>", "".join(add) + "</urlset>")
    t = re.sub(r"(<loc>https://exostride.sg/(?:zh/)?guides/</loc>.*?<lastmod>)[^<]*", r"\g<1>2026-11-08", t)
    write(p, t)


def main():
    orig, new = all_guides()
    if '--draft' in sys.argv:
        new_slugs = {m['slug'] for m in new}
        for m in new:
            m['related'] = ','.join(r for r in m['related'].split(',') if r.strip() in new_slugs or r.strip() in ORIGINAL) or ORIGINAL[0]
    titles = {g["slug"]: g["title"] for g in orig + new}
    skel = read(SKELETON); notes = ws_notes()
    report = []
    for m in new:
        page, words, faq = build_page(m, titles, skel, notes)
        write(os.path.join(ROOT, "guides", m["slug"], "index.html"), page)
        report.append((m["slug"], m["w"], words, len(faq), len(m["title"]), len(m["desc"])))
    build_hub(orig + new)
    build_llms(orig + new, new)
    update_sitemap(new)
    for r in report:
        print("%-55s %s words=%4d faq=%d title=%d desc=%d" % r)
    print(len(new), "guides built")


if __name__ == "__main__":
    main()
