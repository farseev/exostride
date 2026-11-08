# exostride.sg

Static site for ExoStride Singapore (GitHub Pages, no build step on the server). See `DEPLOY.md` for hosting
and `STRATEGY.md` for why each guide exists. Python tools below are standard-library only.

## Layout

```
index.html, guides/…            English (en-SG) — the source and the template for every language
zh/…                            Simplified Chinese (zh-Hans-SG), kept at /zh/ (indexed URLs)
<code>/…                        other languages: zh-hant ja ko th vi id ms hi fil es fr de pt ar ru
content/guides/*.txt            source text of the guides added in Nov 2026 (rendered by build_guides.py)
i18n/source.json                every English segment, keyed by id (generated)
i18n/pages.json                 which segment ids each page uses (generated)
i18n/<code>.json                translation memory per language: {id: translation}
sitemap.xml                     sitemap index → sitemap-en.xml, sitemap-<code>.xml
tools/build_guides.py           content/guides/*.txt → guides/<slug>/index.html, hub, llms*.txt
tools/i18n.py                   segment extraction, translation merge, language build, sitemaps
tools/check_site.py             validator (h1, JSON-LD, canonical, hreflang, links, sitemaps)
```

## Add or edit an English guide

1. Write `content/guides/<slug>.txt` (copy an existing one: header fields, `---`, body; `## FAQ` with `? Question`
   lines). Label every ExoStride performance figure as a manufacturer claim. No medical advice beyond
   "talk to your doctor or physiotherapist".
2. `python3 tools/build_guides.py` (renders the page, hub card, llms.txt, llms-full.txt).
3. `python3 tools/i18n.py build && python3 tools/check_site.py` — must end with `0 errors`.

## Translate

```
python3 tools/i18n.py status                        # coverage per language
python3 tools/i18n.py todo ja / /guides/<slug>/     # untranslated segments:  id<TAB>English
# write  id<TAB>translation  lines to a file, keeping <g1>…</g1> / <x1/> placeholders
python3 tools/i18n.py merge ja ja.tsv
python3 tools/i18n.py build && python3 tools/check_site.py
```

A page is published in a language only when **all** of its segments are translated; until then it is
English-only and is left out of that language's sitemap, hreflang cluster and guide hub (the language
switcher sends that language to its home page instead). A language goes live when its home page is
complete. Keep product names and units unchanged (ExoStride, US-H-1.0Pro, 16 Nm, 2.4 kg, IP54) and keep
the manufacturer-claim labelling.

## Add a language

Add a row to `LANGS` in `tools/i18n.py` (code, URL dir, hreflang, og:locale, native name, short label,
the word for "Language", Google Fonts family if Archivo does not cover the script), add font rules to
`assets/site.css` if needed, then translate and build as above.

Every built page gets: translated title/description/body/FAQ/JSON-LD/OG, `<html lang>` (+ `dir="rtl"` for
Arabic), a self-canonical, the full hreflang cluster of the versions that exist plus `x-default` (English),
and the header language switcher (`<details class="langsw">`, keyboard accessible; GA4 event `language_switch`).
