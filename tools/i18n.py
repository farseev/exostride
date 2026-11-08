#!/usr/bin/env python3
"""ExoStride multilingual build (standard library only).

English pages at the site root are the template and the source text. Every translatable piece of
text (visible text runs, alt/aria/title attributes, meta descriptions, OG/Twitter text, JSON-LD
text, WhatsApp pre-fill messages) is a *segment*, keyed by a hash of its English text.
Translations live in i18n/<code>.json ({id: text}); i18n/source.json holds the English.

Commands
  python3 tools/i18n.py extract                 refresh i18n/source.json + i18n/pages.json
  python3 tools/i18n.py todo <code> [page ...]  print untranslated segments as  id<TAB>English
  python3 tools/i18n.py merge <code> <file>     merge  id<TAB>translation  lines (placeholders checked)
  python3 tools/i18n.py build                   normalise EN pages, render every language page that is
                                                100% translated, hreflang clusters, switcher, sitemaps
  python3 tools/i18n.py status                  coverage per language and page

Inline markup inside a segment appears as <g1>…</g1> (paired tags) and <x1/> (void tags); keep
them, in any order that reads naturally. Product names, units and the manufacturer-claim
wording must be preserved.
"""
import hashlib, html, json, os, re, sys, glob
from html.parser import HTMLParser
from urllib.parse import quote, unquote, urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://exostride.sg"
I18N = os.path.join(ROOT, "i18n")
TODAY = "2026-11-08"

# code, url dir, hreflang/html lang, og:locale, native name, short label, "Language" label, font family
LANGS = [
    ("en", "", "en-SG", "en_SG", "English", "EN", "Language", None),
    ("zh-hans", "zh", "zh-Hans-SG", "zh_SG", "简体中文", "简中", "语言", "Noto+Sans+SC:wght@400;500;700;900"),
    ("zh-hant", "zh-hant", "zh-Hant", "zh_TW", "繁體中文", "繁中", "語言", "Noto+Sans+TC:wght@400;500;700;900"),
    ("ja", "ja", "ja", "ja_JP", "日本語", "日本語", "言語", "Noto+Sans+JP:wght@400;500;700;900"),
    ("ko", "ko", "ko", "ko_KR", "한국어", "한국어", "언어", "Noto+Sans+KR:wght@400;500;700;900"),
    ("th", "th", "th", "th_TH", "ไทย", "ไทย", "ภาษา", "Noto+Sans+Thai:wght@400;500;700;900"),
    ("vi", "vi", "vi", "vi_VN", "Tiếng Việt", "VI", "Ngôn ngữ", None),
    ("id", "id", "id", "id_ID", "Bahasa Indonesia", "ID", "Bahasa", None),
    ("ms", "ms", "ms", "ms_MY", "Bahasa Melayu", "MS", "Bahasa", None),
    ("hi", "hi", "hi", "hi_IN", "हिन्दी", "हिन्दी", "भाषा", "Noto+Sans+Devanagari:wght@400;500;700;900"),
    ("fil", "fil", "fil", "tl_PH", "Filipino", "FIL", "Wika", None),
    ("es", "es", "es", "es_ES", "Español", "ES", "Idioma", None),
    ("fr", "fr", "fr", "fr_FR", "Français", "FR", "Langue", None),
    ("de", "de", "de", "de_DE", "Deutsch", "DE", "Sprache", None),
    ("pt", "pt", "pt", "pt_BR", "Português", "PT", "Idioma", None),
    ("ar", "ar", "ar", "ar_AR", "العربية", "عربي", "اللغة", "Noto+Sans+Arabic:wght@400;500;700;900"),
    ("ru", "ru", "ru", "ru_RU", "Русский", "RU", "Язык", "Noto+Sans:ital,wght@0,400;0,500;0,700;0,900;1,700;1,900"),
]
L = {l[0]: dict(code=l[0], dir=l[1], tag=l[2], og=l[3], name=l[4], short=l[5], label=l[6], font=l[7]) for l in LANGS}
CODES = [l[0] for l in LANGS]
FONT_BASE = ("https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,100,400;0,100,500;0,100,600;"
             "0,100,700;0,125,800;1,125,700;1,125,800;1,125,900&family=IBM+Plex+Mono:wght@500;600")
SUFFIX = " | ExoStride Singapore"
SUFFIX_KEY = "| ExoStride Singapore"   # translated once per language (e.g. zh: "｜ExoStride 新加坡")
SHARED_IDS = {"organization", "website", "product", "localbusiness"}

INLINE = {"a", "abbr", "b", "br", "code", "em", "i", "mark", "q", "s", "small", "span", "strong", "sub", "sup",
          "time", "u", "wbr", "img"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr", "param"}
SKIP = {"script", "style", "svg", "noscript", "template"}
ATTRS = ("alt", "title", "aria-label", "placeholder")
META_NAMES = {"description", "keywords", "twitter:title", "twitter:description", "twitter:image:alt"}
META_PROPS = {"og:title", "og:description", "og:image:alt"}
LD_TEXT_KEYS = {"name", "headline", "description", "abstract", "text", "articleSection", "keywords", "caption",
                "slogan", "disambiguatingDescription", "category"}
KEEP_RE = re.compile(r"^(?:ExoStride(?: Singapore| US-H-1\.0Pro)?|US-H-1\.0Pro|HT Science(?: & Development Pte\. Ltd\.)?|"
                     r"[\d\s.,:+×x–\-−%°~<>/()·]*(?:\s?(?:Nm|kg|IP54|Wh|m|O₂|SGD))?[\d\s.,:+×x–\-−%°~<>/()·]*)$")
PH_RE = re.compile(r"</?g\d+>|<x\d+/>")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def sid(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]


def norm(s):
    return re.sub(r"[ \t\n\r\f\v]+", " ", s).strip(" \t\n\r\f\v")


def translatable(t):
    return bool(t) and bool(re.search(r"[^\W\d_]", t)) and not KEEP_RE.match(t)


# ---------------------------------------------------------------- parsing
class Tok:
    __slots__ = ("kind", "tag", "attrs", "start", "end", "raw", "el")

    def __init__(self, kind, tag, attrs, start):
        self.kind, self.tag, self.attrs, self.start, self.end, self.raw, self.el = kind, tag, attrs, start, None, None, None


class El:
    __slots__ = ("tag", "attrs", "open", "close", "children", "parent")

    def __init__(self, tag, attrs, open_i, parent):
        self.tag, self.attrs, self.open, self.close, self.children, self.parent = tag, dict(attrs), open_i, None, [], parent


class Parser(HTMLParser):
    def __init__(self, doc):
        super().__init__(convert_charrefs=False)
        self.doc = doc
        self.lines = [0]
        for m in re.finditer("\n", doc):
            self.lines.append(m.end())
        self.toks = []

    def off(self):
        ln, col = self.getpos()
        return self.lines[ln - 1] + col

    def add(self, kind, tag=None, attrs=()):
        t = Tok(kind, tag, attrs, self.off())
        self.toks.append(t)

    def handle_starttag(self, tag, attrs): self.add("start", tag, attrs)
    def handle_startendtag(self, tag, attrs): self.add("startend", tag, attrs)
    def handle_endtag(self, tag): self.add("end", tag)
    def handle_data(self, d): self.add("data")
    def handle_entityref(self, n): self.add("data")
    def handle_charref(self, n): self.add("data")
    def handle_comment(self, d): self.add("other")
    def handle_decl(self, d): self.add("other")
    def handle_pi(self, d): self.add("other")
    def unknown_decl(self, d): self.add("other")


def parse(doc):
    p = Parser(doc)
    p.feed(doc)
    p.close()
    toks = p.toks
    for i, t in enumerate(toks):
        t.end = toks[i + 1].start if i + 1 < len(toks) else len(doc)
        t.raw = doc[t.start:t.end]
    root = El("#root", (), -1, None)
    cur = root
    for i, t in enumerate(toks):
        if t.kind in ("start", "startend"):
            el = El(t.tag, t.attrs, i, cur)
            t.el = el
            cur.children.append(("el", el))
            if t.kind == "start" and t.tag not in VOID:
                cur = el
            else:
                el.close = i
        elif t.kind == "end":
            x = cur
            while x is not root and x.tag != t.tag:
                x = x.parent
            if x is not root:
                x.close = i
                cur = x.parent
        elif t.kind == "data":
            cur.children.append(("tok", i))
        # comments etc. are ignored structurally
    return toks, root


# ---------------------------------------------------------------- segmentation
class Seg:
    __slots__ = ("kind", "text", "id", "a", "b", "tags", "lead", "trail", "suffix", "tok", "attr")


def text_of_children(toks, children, tagmap):
    """Serialise a run of children into placeholder text; tagmap collects g/x numbers -> token idx."""
    out = []

    def ser(kind, x):
        if kind == "tok":
            out.append(html.unescape(toks[x].raw))
        else:
            n = len(tagmap) + 1
            if x.close is None or x.close == x.open or x.tag in VOID:
                tagmap.append(("x", x.open, None))
                out.append("<x%d/>" % n)
            else:
                tagmap.append(("g", x.open, x.close))
                out.append("<g%d>" % n)
                for c in x.children:
                    ser(*c)
                out.append("</g%d>" % n)
    for c in children:
        ser(*c)
    return "".join(out)


def is_inline(child):
    kind, x = child
    return kind == "tok" or (x.tag in INLINE)


def has_direct_text(toks, run):
    return any(k == "tok" and toks[x].raw.strip() for k, x in run)


def segments(doc):
    toks, root = parse(doc)
    segs = []

    def visit(el):
        if el.tag in SKIP or el.attrs.get("translate") == "no" or el.attrs.get("hidden") is not None and el.tag != "div":
            return
        runs, run = [], []
        for c in el.children:
            if is_inline(c) and not (c[0] == "el" and c[1].tag in SKIP):
                run.append(c)
            else:
                if run:
                    runs.append(("run", run)); run = []
                runs.append(("blk", c))
        if run:
            runs.append(("run", run))
        for kind, r in runs:
            if kind == "blk":
                if r[0] == "el":
                    visit(r[1])
                continue
            if has_direct_text(toks, r):
                make_run_seg(r)
            else:
                for k, x in r:
                    if k == "el":
                        visit(x)

    def first_tok(c):
        return c[1] if c[0] == "tok" else c[1].open

    def last_tok(c):
        return c[1] if c[0] == "tok" else (c[1].close if c[1].close is not None else c[1].open)

    def make_run_seg(r):
        # trim whitespace-only text tokens at both ends
        while r and r[0][0] == "tok" and not toks[r[0][1]].raw.strip():
            r = r[1:]
        while r and r[-1][0] == "tok" and not toks[r[-1][1]].raw.strip():
            r = r[:-1]
        if not r:
            return
        tagmap = []
        raw_text = text_of_children(toks, r, tagmap)
        a, b = toks[first_tok(r[0])].start, toks[last_tok(r[-1])].end
        lead = re.match(r"\s*", doc[a:b]).group(0)
        trail = re.search(r"\s*$", doc[a:b]).group(0)
        t = norm(raw_text)
        s = Seg()
        s.kind, s.a, s.b, s.tags, s.lead, s.trail, s.tok, s.attr = "run", a, b, tagmap, lead, trail, None, None
        s.suffix = ""
        if t.endswith(SUFFIX) and not tagmap:
            t, s.suffix = t[: -len(SUFFIX)], SUFFIX
        s.text = t
        s.id = sid(t)
        if not translatable(PH_RE.sub("", t)):
            s.id = None
        segs.append(s)

    visit(root)
    # attribute segments (all elements, including those inside runs)
    for i, t in enumerate(toks):
        if t.kind not in ("start", "startend"):
            continue
        at = dict(t.attrs)
        names = []
        for a in ATTRS:
            if at.get(a):
                names.append(a)
        if t.tag == "meta" and at.get("content") and (at.get("name") in META_NAMES or at.get("property") in META_PROPS):
            names.append("content")
        if t.tag == "a" and at.get("href", "").startswith("https://wa.me/") and "?text=" in at.get("href", ""):
            names.append("wa")
        for a in names:
            if a == "wa":
                val = unquote(at["href"].split("?text=", 1)[1])
            else:
                val = at[a]
            val = norm(val)
            s = Seg()
            s.kind, s.tok, s.attr, s.tags, s.lead, s.trail, s.a, s.b = "attr", i, a, [], "", "", None, None
            s.suffix = ""
            if val.endswith(SUFFIX):
                val, s.suffix = val[: -len(SUFFIX)], SUFFIX
            s.text = val
            s.id = sid(val) if translatable(val) else None
            segs.append(s)
    # JSON-LD
    for i, t in enumerate(toks):
        if t.kind == "start" and t.tag == "script" and dict(t.attrs).get("type") == "application/ld+json":
            d = json.loads(toks[i + 1].raw)
            for val in ld_texts(d):
                s = Seg()
                s.kind, s.tok, s.attr, s.tags, s.lead, s.trail, s.a, s.b, s.suffix = "ld", i + 1, None, [], "", "", None, None, ""
                s.text = val
                s.id = sid(val) if translatable(val) else None
                segs.append(s)
    return toks, segs


def ld_texts(d, skip=False):
    out = []
    if isinstance(d, dict):
        skip = skip or d.get("@type") in ("Organization", "WebSite")
        for k, v in d.items():
            if isinstance(v, str):
                if not skip and k in LD_TEXT_KEYS:
                    v2 = v[: -len(SUFFIX)] if v.endswith(SUFFIX) else v
                    out.append(norm(v2))
            else:
                out += ld_texts(v, skip)
    elif isinstance(d, list):
        for v in d:
            out += ld_texts(v, skip)
    return out


# ---------------------------------------------------------------- pages
def en_pages():
    pages = ["index.html", "guides/index.html"]
    pages += sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, "guides", "*", "index.html")))
    return pages


def page_path(rel):
    """'guides/x/index.html' -> '/guides/x/'"""
    p = "/" + rel[: -len("index.html")]
    return p


def lang_path(code, path):
    d = L[code]["dir"]
    return ("/" + d + path) if d else path


def load_tm(code):
    p = os.path.join(I18N, code + ".json")
    return json.loads(read(p)) if os.path.exists(p) else {}


def save_tm(code, tm):
    write(os.path.join(I18N, code + ".json"), json.dumps(dict(sorted(tm.items())), ensure_ascii=False, indent=0) + "\n")


def guide_slugs_in_hub(doc):
    return re.findall(r'<a class="gcard" href="\.\./guides/([^/]+)/">', doc)


def filter_hub(doc, available):
    """Drop guide cards whose language version does not exist; drop emptied clusters; fix ItemList."""
    def card(m):
        return m.group(0) if m.group(1) in available else ""
    doc = re.sub(r'<a class="gcard" href="\.\./guides/([^/]+)/">.*?</a>', card, doc, flags=re.S)
    doc = re.sub(r'<div class="clu">\s*<div class="clu-h">.*?</div>\s*<div class="cards"></div>\s*</div>', "", doc, flags=re.S)
    m = re.search(r'<script type="application/ld\+json">(\{"@context":"https://schema.org","@type":"CollectionPage".*?)</script>', doc)
    if m:
        d = json.loads(m.group(1))
        items = [it for it in d["mainEntity"]["itemListElement"] if it["url"].rstrip("/").rsplit("/", 1)[1] in available]
        for i, it in enumerate(items):
            it["position"] = i + 1
        d["mainEntity"]["itemListElement"] = items
        d["mainEntity"]["numberOfItems"] = len(items)
        doc = doc.replace(m.group(0), '<script type="application/ld+json">%s</script>' % json.dumps(d, ensure_ascii=False, separators=(",", ":")))
    return doc


# ---------------------------------------------------------------- chrome normalisation (EN source)
def switcher_placeholder():
    return '<details class="langsw" translate="no"></details>'


L10N_EN = [("hi", "Hi, I'd like to learn about ExoStride and book a fitting."), ("ref", "Ref"), ("name", "Name"),
           ("scenario", "Scenario"), ("date", "Date"), ("tel", "Tel"), ("email", "Email"), ("notes", "Notes")]


def normalise_en(doc):
    doc = re.sub(r'<div class="lang" role="group" aria-label="Language">.*?</div>', switcher_placeholder(), doc, flags=re.S)
    doc = re.sub(r'<details class="langsw" translate="no">.*?</details>', switcher_placeholder(), doc, flags=re.S)
    if 'id="f-try"' in doc and 'id="t-l10n"' not in doc:
        block = '<div class="l10n" id="t-l10n" aria-hidden="true">' + "".join(
            '<span data-k="%s">%s</span>' % (k, html.escape(v, quote=False)) for k, v in L10N_EN) + "</div>\n   </form>"
        doc = doc.replace("</form>", block, 1)
    return doc


# ---------------------------------------------------------------- rendering
def esc_text(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\xa0", "&nbsp;")


def rebuild_tag(tok, new_attrs):
    """Re-serialise a start tag with some attribute values replaced, keeping the original order/quoting."""
    raw = tok.raw
    for name, val in new_attrs.items():
        pat = re.compile(r'(\s%s=")([^"]*)(")' % re.escape(name))
        raw, n = pat.subn(lambda m: m.group(1) + val + m.group(3), raw, count=1)
    return raw


def relpath(from_dir, target):
    """from_dir like '/ja/guides/x/', target like '/assets/a.jpg' or '/ja/guides/' -> relative href."""
    import posixpath
    r = posixpath.relpath(target, from_dir)
    if r == ".":
        return "./"
    if target.endswith("/") and not r.endswith("/"):
        r += "/"
    return r


def resolve(base_dir, href):
    parts = [p for p in base_dir.split("/") if p]
    path, frag = (href.split("#", 1) + [""])[:2] if "#" in href else (href, None)
    segs = path.split("/")
    out = list(parts)
    for i, s in enumerate(segs):
        if s == "..":
            if out:
                out.pop()
        elif s in (".", ""):
            continue
        else:
            out.append(s)
    trailing = path.endswith("/") or path == "" or path.endswith("..")
    res = "/" + "/".join(out) + ("/" if trailing and out else "")
    if res == "//":
        res = "/"
    return res, frag


class Ctx:
    def __init__(self, code, avail):
        self.code = code
        self.avail = avail  # set of EN page paths available in this language

    def map_page(self, path):
        """EN site path -> path in this language if that page exists in it."""
        if self.code == "en":
            return path
        if path in self.avail:
            return lang_path(self.code, path)
        return path

    def map_url(self, url):
        if not url.startswith(SITE):
            return url
        rest = url[len(SITE):]
        if rest == "":
            return url
        path, _, frag = rest.partition("#")
        if frag in SHARED_IDS:
            return url
        if not (path.endswith("/")):
            return url
        return SITE + self.map_page(path) + (("#" + frag) if frag else "")


def render(doc, en_rel, code, tm, avail, clusters):
    """Return (html, missing_ids) for EN page en_rel rendered in language code."""
    ctx = Ctx(code, avail)
    en_path = page_path(en_rel)
    out_path = lang_path(code, en_path)
    toks, segs = segments(doc)
    missing = set()

    suffix_tr = SUFFIX if code == "en" else tm.get(sid(SUFFIX_KEY), SUFFIX)
    if code != "en" and sid(SUFFIX_KEY) not in tm and any(x.suffix for x in segs):
        missing.add(sid(SUFFIX_KEY))

    def tr(seg):
        if seg.id is None or code == "en":
            return seg.text
        v = tm.get(seg.id)
        if v is None:
            missing.add(seg.id)
            return seg.text
        return v

    # 1) new start-tag text for every start tag: translated attrs + rewritten links
    newtag = {}
    attr_tr = {}
    for s in segs:
        if s.kind == "attr":
            attr_tr.setdefault(s.tok, {})[s.attr] = tr(s) + (suffix_tr if s.suffix else "")
    for i, t in enumerate(toks):
        if t.kind not in ("start", "startend"):
            continue
        at = dict(t.attrs)
        repl = {}
        for a, v in attr_tr.get(i, {}).items():
            if a == "wa":
                base = at["href"].split("?text=", 1)[0]
                repl["href"] = html.escape(base + "?text=" + quote(v, safe=""), quote=True)
            else:
                repl[a] = html.escape(v, quote=True)
        for a in ("href", "src"):
            v = at.get(a)
            if v is None or re.match(r"^(?:[a-z]+:|//|#)", v):
                continue
            path, frag = resolve(en_path, v)
            tgt = path
            if tgt.endswith("/") or tgt == "/":
                tgt = ctx.map_page(tgt)
            newv = relpath(out_path, tgt) + (("#" + frag) if frag else "")
            if code != "en" or newv != v:
                repl[a] = html.escape(newv, quote=True)
        newtag[i] = rebuild_tag(t, repl) if repl else t.raw

    edits = []
    covered = []
    for s in segs:
        if s.kind != "run":
            continue
        txt = tr(s)
        tags = s.tags
        pieces = []
        pos = 0
        for m in PH_RE.finditer(txt):
            pieces.append(esc_text(txt[pos:m.start()]))
            ph = m.group(0)
            n = int(re.search(r"\d+", ph).group(0)) - 1
            kind, o, c = tags[n]
            if ph.startswith("</"):
                pieces.append(toks[c].raw)
            else:
                pieces.append(newtag.get(o, toks[o].raw))
            pos = m.end()
        pieces.append(esc_text(txt[pos:]))
        edits.append((s.a, s.b, s.lead + "".join(pieces) + esc_text(suffix_tr if s.suffix else "") + s.trail))
        covered.append((s.a, s.b))
    for i, t in enumerate(toks):
        if t.kind in ("start", "startend") and newtag[i] != t.raw:
            if not any(a <= t.start < b for a, b in covered):
                edits.append((t.start, t.end, newtag[i]))
    # JSON-LD
    ld_map = {}
    for s in segs:
        if s.kind == "ld":
            ld_map[s.text] = tr(s)
    for i, t in enumerate(toks):
        if t.kind == "start" and t.tag == "script" and dict(t.attrs).get("type") == "application/ld+json":
            d = json.loads(toks[i + 1].raw)
            d = ld_transform(d, ld_map, ctx, L[code]["tag"], suffix_tr)
            edits.append((toks[i + 1].start, toks[i + 1].end, json.dumps(d, ensure_ascii=False, separators=(",", ":"))))
    edits.sort(key=lambda e: e[0])
    res, pos = [], 0
    for a, b, txt in edits:
        if a < pos:
            raise RuntimeError("overlapping edits in %s" % en_rel)
        res.append(doc[pos:a]); res.append(txt); pos = b
    res.append(doc[pos:])
    out = "".join(res)
    out = head_fixups(out, code, en_path, out_path, clusters.get(en_path, ["en"]))
    out = out.replace(switcher_placeholder(), switcher(code, en_path, out_path, clusters))
    return out, missing


def ld_transform(d, ld_map, ctx, tag, suffix_tr, skip=False):
    if isinstance(d, dict):
        skip2 = skip or d.get("@type") in ("Organization", "WebSite")
        o = {}
        for k, v in d.items():
            if isinstance(v, str):
                if k == "inLanguage":
                    o[k] = tag
                elif not skip2 and k in LD_TEXT_KEYS:
                    suf = SUFFIX if v.endswith(SUFFIX) else ""
                    key = norm(v[: -len(suf)] if suf else v)
                    o[k] = ld_map.get(key, key) + (suffix_tr if suf else "")
                elif v.startswith(SITE):
                    o[k] = ctx.map_url(v)
                else:
                    o[k] = v
            else:
                o[k] = ld_transform(v, ld_map, ctx, tag, suffix_tr, skip2)
        return o
    if isinstance(d, list):
        return [ld_transform(v, ld_map, ctx, tag, suffix_tr, skip) for v in d]
    return d


def head_fixups(doc, code, en_path, out_path, cluster):
    lg = L[code]
    url = SITE + out_path
    attrs = 'lang="%s"' % lg["tag"] + (' dir="rtl"' if code == "ar" else "")
    doc = re.sub(r'<html lang="[^"]*"(?: dir="rtl")?>', "<html %s>" % attrs, doc, count=1)
    doc = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="%s">' % url, doc, count=1)
    alts = "".join('<link rel="alternate" hreflang="%s" href="%s%s">' % (L[c]["tag"], SITE, lang_path(c, en_path)) for c in cluster)
    alts += '<link rel="alternate" hreflang="x-default" href="%s%s">' % (SITE, en_path)
    doc = re.sub(r'(?:<link rel="alternate" hreflang="[^"]*" href="[^"]*">)+', alts, doc, count=1)
    doc = re.sub(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="%s">' % url, doc, count=1)
    doc = re.sub(r'<meta property="og:locale:alternate" content="[^"]*">\n?', "", doc)
    others = "".join('<meta property="og:locale:alternate" content="%s">\n' % L[c]["og"] for c in cluster if c != code)
    doc = re.sub(r'<meta property="og:locale" content="[^"]*">\n?', '<meta property="og:locale" content="%s">\n%s' % (lg["og"], others), doc, count=1)
    fam = FONT_BASE + "&family=" + (lg["font"] or "Noto+Sans+SC:wght@400;500;700;900") + "&display=swap"
    if code == "ru":
        fam = FONT_BASE + "&family=" + lg["font"] + "&family=Noto+Sans+SC:wght@400;500;700;900&display=swap"
    doc = re.sub(r'<link href="https://fonts\.googleapis\.com/css2\?[^"]*" rel="stylesheet">',
                 lambda m: '<link href="%s" rel="stylesheet">' % fam, doc, count=1)
    return doc


def switcher(code, en_path, out_path, clusters):
    shipped = clusters.get("/", ["en"])  # languages whose home exists
    have = clusters.get(en_path, ["en"])
    lis = []
    for c in shipped:
        tgt = lang_path(c, en_path) if c in have else lang_path(c, "/")
        cur = ' aria-current="true"' if c == code else ""
        lis.append('<li><a href="%s" hreflang="%s" lang="%s"%s>%s</a></li>' % (
            relpath(out_path, tgt), L[c]["tag"], L[c]["tag"], cur, L[c]["name"]))
    return ('<details class="langsw" translate="no"><summary aria-label="%s: %s"><span>%s</span></summary><ul>%s</ul></details>'
            % (L[code]["label"], L[code]["name"], L[code]["short"], "".join(lis)))


# ---------------------------------------------------------------- commands
def cmd_extract(quiet=False):
    src, pages = {}, {}
    for rel in en_pages():
        doc = normalise_en(read(os.path.join(ROOT, rel)))
        _, segs = segments(doc)
        ids = []
        for s in segs:
            if s.id:
                src[s.id] = s.text
                if s.id not in ids:
                    ids.append(s.id)
        if any(s.suffix for s in segs) and sid(SUFFIX_KEY) not in ids:
            ids.append(sid(SUFFIX_KEY)); src[sid(SUFFIX_KEY)] = SUFFIX_KEY
        pages[page_path(rel)] = ids
    write(os.path.join(I18N, "source.json"), json.dumps(dict(sorted(src.items())), ensure_ascii=False, indent=0) + "\n")
    write(os.path.join(I18N, "pages.json"), json.dumps(pages, ensure_ascii=False, indent=0) + "\n")
    if not quiet:
        words = sum(len(v.split()) for v in src.values())
        print("%d pages, %d unique segments, %d words" % (len(pages), len(src), words))
    return src, pages


def page_ids_for(code, path, pages, avail_guides):
    """ids needed for a page in a language (hub filtered to available guides)."""
    if path == "/guides/":
        doc = normalise_en(read(os.path.join(ROOT, "guides/index.html")))
        doc = filter_hub(doc, avail_guides)
        _, segs = segments(doc)
        return list(dict.fromkeys(s.id for s in segs if s.id))
    return pages[path]


def availability(code, src, pages, tm):
    """Which EN page paths are fully translated in code (hub/home handled after guides)."""
    if code == "en":
        return set(pages)
    avail = set()
    guides = set()
    for path, ids in pages.items():
        if path.startswith("/guides/") and path != "/guides/":
            if all(i in tm for i in ids):
                avail.add(path); guides.add(path.split("/")[2])
    if all(i in tm for i in pages["/"]):
        avail.add("/")
        if guides and all(i in tm for i in page_ids_for(code, "/guides/", pages, guides)):
            avail.add("/guides/")
    if "/" not in avail:
        return set()
    return avail


def cmd_todo(code, which):
    src, pages = cmd_extract(quiet=True)
    tm = load_tm(code)
    seen = set()
    sel = which or list(pages)
    for path in sel:
        if not path.startswith("/"):
            path = "/" + path.strip("/") + "/" if path.strip("/") else "/"
            if path != "/" and not path.startswith("/guides/"):
                path = "/guides" + path
        if path == "/guides/":
            guides = {p.split("/")[2] for p in pages if p.startswith("/guides/") and p != "/guides/"}
            ids = page_ids_for(code, path, pages, guides)
        else:
            ids = pages[path]
        for i in ids:
            if i not in tm and i not in seen:
                seen.add(i)
                print("%s\t%s" % (i, src[i]))


def check_ph(en, tr):
    a = sorted(PH_RE.findall(en)); b = sorted(PH_RE.findall(tr))
    return a == b


def cmd_merge(code, f):
    src = json.loads(read(os.path.join(I18N, "source.json")))
    tm = load_tm(code)
    bad, n = 0, 0
    for ln in read(f).splitlines():
        if not ln.strip() or "\t" not in ln:
            continue
        i, t = ln.split("\t", 1)
        i, t = i.strip(), t.strip()
        if i not in src:
            print("unknown id", i); bad += 1; continue
        if not check_ph(src[i], t):
            print("placeholder mismatch", i, src[i][:60], "||", t[:60]); bad += 1; continue
        tm[i] = t; n += 1
    save_tm(code, tm)
    print("merged %d, rejected %d -> i18n/%s.json (%d entries)" % (n, bad, code, len(tm)))


def cmd_status():
    src, pages = cmd_extract(quiet=True)
    for code in CODES[1:]:
        tm = load_tm(code)
        av = availability(code, src, pages, tm)
        need = set(i for ids in pages.values() for i in ids)
        print("%-8s %4d/%4d segments  %2d/%2d pages live" % (code, len(need & set(tm)), len(need), len(av), len(pages)))


def cmd_build():
    src, pages = cmd_extract(quiet=True)
    # normalise EN sources in place (switcher placeholder + form l10n block)
    for rel in en_pages():
        p = os.path.join(ROOT, rel)
        doc = read(p)
        n = normalise_en(doc)
        if n != doc:
            write(p, n)
    tms = {c: load_tm(c) for c in CODES[1:]}
    avail = {"en": set(pages)}
    for c in CODES[1:]:
        avail[c] = availability(c, src, pages, tms[c])
    clusters = {path: [c for c in CODES if path in avail[c]] for path in pages}
    report = {}
    written = []
    for rel in en_pages():
        en_path = page_path(rel)
        base = normalise_en(read(os.path.join(ROOT, rel)))
        for c in CODES:
            if en_path not in avail[c]:
                continue
            doc = base
            if en_path == "/guides/" and c != "en":
                doc = filter_hub(doc, {p.split("/")[2] for p in avail[c] if p.startswith("/guides/") and p != "/guides/"})
            out, missing = render(doc, rel, c, tms.get(c, {}), avail[c], clusters)
            if missing:
                raise RuntimeError("%s %s missing %d" % (c, en_path, len(missing)))
            dest = os.path.join(ROOT, lang_path(c, en_path).lstrip("/"), "index.html")
            write(dest, out)
            written.append(lang_path(c, en_path))
    # stale language pages (page no longer fully translated): refuse unless --prune (never touch EN)
    stale = []
    for c in CODES[1:]:
        d = os.path.join(ROOT, L[c]["dir"])
        for f in glob.glob(os.path.join(d, "**", "index.html"), recursive=True):
            rp = "/" + os.path.relpath(f, ROOT)[: -len("index.html")]
            if rp not in written:
                if "--prune" in sys.argv:
                    os.remove(f)
                else:
                    stale.append(rp)
    if stale:
        sys.exit("refusing to drop %d existing language pages (missing translations?): %s ... — translate them or rerun with --prune"
                 % (len(stale), ", ".join(stale[:5])))
    write_sitemaps(pages, avail, clusters)
    write_llms(avail)
    print("built %d pages; languages live: %s" % (len(written), ", ".join("%s(%d)" % (c, len(avail[c])) for c in CODES if avail[c])))


def hero_image(path):
    rel = (path.lstrip("/") or "") + "index.html"
    h = read(os.path.join(ROOT, rel))
    m = re.search(r'<meta property="og:image" content="([^"]+)"', h)
    return m.group(1) if m else None


def write_sitemaps(pages, avail, clusters):
    files = []
    for c in CODES:
        if not avail[c]:
            continue
        rows = []
        for path in pages:
            if path not in avail[c]:
                continue
            loc = SITE + lang_path(c, path)
            alts = "".join('<xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>' % (L[x]["tag"], SITE, lang_path(x, path)) for x in clusters[path])
            alts += '<xhtml:link rel="alternate" hreflang="x-default" href="%s%s"/>' % (SITE, path)
            pr = "1.0" if path == "/" else ("0.9" if path == "/guides/" else "0.8")
            cf = "weekly" if path in ("/", "/guides/") else "monthly"
            img = hero_image(path)
            imgx = "<image:image><image:loc>%s</image:loc></image:image>" % img if img else ""
            rows.append("<url><loc>%s</loc>%s<lastmod>%s</lastmod><changefreq>%s</changefreq><priority>%s</priority>%s</url>" % (loc, alts, TODAY, cf, pr, imgx))
        name = "sitemap-%s.xml" % c
        write(os.path.join(ROOT, name), '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + "\n".join(rows) + "\n</urlset>\n")
        files.append(name)
    for f in glob.glob(os.path.join(ROOT, "sitemap-*.xml")):
        if os.path.basename(f) not in files:
            os.remove(f)
    idx = '<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(
        "<sitemap><loc>%s/%s</loc><lastmod>%s</lastmod></sitemap>" % (SITE, f, TODAY) for f in files) + "\n</sitemapindex>\n"
    write(os.path.join(ROOT, "sitemap.xml"), idx)


def write_llms(avail):
    p = os.path.join(ROOT, "llms.txt")
    t = read(p)
    live = [c for c in CODES if avail[c]]
    langs = ", ".join("%s (%s)" % (L[c]["name"], L[c]["tag"]) for c in live)
    t = re.sub(r"^- Languages: .*$", "- Languages: " + langs, t, count=1, flags=re.M)
    block = ["## Other languages", ""]
    for c in live[1:]:
        n = len([x for x in avail[c] if x.startswith("/guides/") and x != "/guides/"])
        block.append("- [%s — home](%s%s)%s" % (L[c]["name"], SITE, lang_path(c, "/"),
                     (" · [guides](%s%s) (%d translated)" % (SITE, lang_path(c, "/guides/"), n)) if "/guides/" in avail[c] else ""))
    block = "\n".join(block) + "\n\n"
    if "## Other languages" in t:
        t = re.sub(r"## Other languages\n.*?\n\n(?=## )", block, t, flags=re.S)
    else:
        t = t.replace("## Optional", block + "## Optional", 1)
    write(p, t)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(0)
    if a[0] == "extract":
        cmd_extract()
    elif a[0] == "todo":
        cmd_todo(a[1], a[2:])
    elif a[0] == "merge":
        cmd_merge(a[1], a[2])
    elif a[0] == "status":
        cmd_status()
    elif a[0] == "build":
        cmd_build()
    else:
        print(__doc__)
