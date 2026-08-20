# ExoStride — deploy notes

Static site. No build step, no server code. Upload the contents of this folder to any static
host and point `exostride.sg` at it.

```
index.html                     EN homepage
zh/index.html                  ZH homepage
guides/index.html              EN guide hub
guides/<slug>/index.html       9 EN articles
zh/guides/…                    ZH mirrors of all of the above
assets/                        images, favicons, OG images, site.css, site.js
robots.txt sitemap.xml llms.txt llms-full.txt ai.txt site.webmanifest 404.html _headers
```

## 0. Previewing it locally

Just double-click `index.html`. Every internal path is **relative**, and a small shim in
`assets/site.js` appends `index.html` to directory links when the page is opened over `file://`,
so navigation works straight off a disk. Google Fonts and GA4 need a network connection; offline,
the type falls back to a system sans and nothing else changes.

For a preview identical to production, serve the folder instead:

```bash
cd site && python3 -m http.server 8000     # then open http://localhost:8000
```

## 1. Host

Paths are relative, so the site works from a domain root, a subfolder, or a local disk without
edits. Canonical, hreflang, Open Graph and JSON-LD URLs are absolute and point at
`https://exostride.sg` — those are what to change if the domain differs (see §2).

| Host | What to do |
|---|---|
| Netlify / Cloudflare Pages | Drag the folder in. `_headers` is picked up automatically. |
| Vercel | Drop in as a static project. Translate `_headers` to `vercel.json` for the cache rules. |
| S3 + CloudFront | Sync the folder. Set `404.html` as the error document, `index.html` as the index document. |
| Nginx / Apache | Serve the folder as the docroot. Point the 404 page at `/404.html`. |

Clean URLs work out of the box: every page is an `index.html` inside its own directory.

## 2. Before go-live — the three things to change

1. **The domain.** Every canonical, hreflang, OG and JSON-LD URL is `https://exostride.sg`. If the
   domain differs, edit `SITE` at the top of `content.py` and re-run `python3 build_site.py`. Do
   not hand-edit the HTML — 22 pages carry that URL in several places each, plus the sitemap.
2. **HTTPS + www redirect.** Pick one host (apex or www) and 301 the other to it, or the canonical
   tags and the duplicate-content signal will disagree.
3. **Product price.** `product_ld()` in `build_site.py` ships an `Offer` with `availability` and
   `priceCurrency` but no `price`, because pricing isn't published. Google reports
   *"missing field price"* as a **warning, not an error** — the Product snippet still validates.
   Add `"price": "…"` to that offer as soon as there is a public figure.

## 3. After go-live — the first hour

- Google Search Console → add the property → submit `https://exostride.sg/sitemap.xml`.
  The ZH tree is covered by the same sitemap via its hreflang entries.
- Bing Webmaster Tools → same sitemap. Bing feeds Copilot, so this one matters for GEO.
- Rich Results Test on `/` and on one guide — expect **Product, FAQ, Breadcrumb, Organization,
  LocalBusiness** on the homepage and **Article, FAQ, Breadcrumb, QAPage** on guides.
- GA4 (`G-2XGXKLFTZ9`) is already on every page. Two custom events fire with no extra setup:
  - `whatsapp_click` — carries a `placement` parameter (`fab`, `band`, `rail-<slug>`, `case-…`)
  - `generate_lead` — when the fitting form is completed
  Mark `generate_lead` as a **key event** in GA4 → Admin → Events.
- Test the WhatsApp handoff on a real phone. Every CTA goes to **+65 9122 7009** with a
  context-specific pre-filled message.

## 4. Editing content

All copy lives in `content.py` (bilingual dicts). Page templates live in `build_site.py`.
Anything in `docs/` is copied into the output as-is.

```bash
python3 build_site.py      # regenerates site/ from scratch
python3 verify.py          # must report 0 errors before you ship
```

`verify.py` checks: tag balance, single H1, meta completeness, canonical self-reference and
uniqueness, the hreflang triple, JSON-LD parse + required properties, FAQ markup matching visible
text, image alt text and dimensions, broken internal links and anchors, WhatsApp number and
pre-fill, OG image existence, and sitemap-to-page parity.

## 5. Adding a tenth guide

Append a dict to `ARTICLES` in `content.py` and rebuild. The hub, sitemap, `llms.txt`,
`llms-full.txt`, footer links, breadcrumbs and both language trees update themselves.
Anchor it to a real whitespace — see `WHITESPACE` at the top of the same file, and `STRATEGY.md`.

## 6. Regenerating imagery

`build_images.py` builds the favicon set and the four Open Graph cards. The favicons are cut from
the real wordmark artwork, so the red swoosh-S is the genuine one, never redrawn. The OG
photography was generated with SOMIN `image-generate` (source files `assets/gen-*.jpg`) and is
composed under the real wordmark and the Stride Slash at exact brand hex. To re-cut the cards
after swapping a photo, edit the `OG` list and run `python3 build_images.py`.

## 7. What is deliberately not here

- **No cookie banner.** The site sets no cookies of its own. GA4 does — if you serve EU traffic,
  add consent mode.
- **No form backend.** The fitting form composes a WhatsApp message in the browser and hands off.
  Nothing is posted anywhere, so there is no personal data at rest and nothing to secure.
- **No JS framework.** ~5 KB of vanilla JS, one CSS file. Everything is in the HTML for crawlers
  and answer engines. Reveal animations are opt-in via a `js` class, so content is never hidden
  from a crawler, a no-JS visitor, or a printer.
