#!/usr/bin/env python3
"""Offline, dependency-free acceptance checks for the five ChongGrok builds.

Build directories: portal, chatgpt, grok, claude, gemini. No HTTP is performed.
The report deliberately separates publication blockers from advisory coverage gaps.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urldefrag, urljoin, urlsplit, urlunsplit
import xml.etree.ElementTree as ET

ORIGIN = "https://he20000405-pixel.github.io"
ROUTES = {
    "portal": "/",
    "chatgpt": "/chatgpt-plus-pro-china-guide/",
    "grok": "/supergrok-china-guide/",
    "claude": "/claude-pro-max-china-guide/",
    "gemini": "/gemini-google-ai-pro-china-guide/",
}
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def norm(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def document_url(value):
    p = urlsplit(value)
    return urlunsplit((p.scheme, p.netloc, p.path, "", ""))


def css_urls(source):
    """Read URL functions, skipping comments and unrelated quoted CSS strings.

    A regex over the whole stylesheet mistakes documentation and content strings
    for dependencies. Keep original offsets for diagnostics and respect escapes.
    """
    size = len(source)

    def string_end(start):
        quote, cursor = source[start], start + 1
        while cursor < size:
            if source[cursor] == "\\":
                cursor += 2
            elif source[cursor] == quote:
                return cursor + 1
            else:
                cursor += 1
        return size

    def space_end(start):
        while start < size:
            if source[start].isspace():
                start += 1
            elif source.startswith("/*", start):
                end = source.find("*/", start + 2)
                start = size if end < 0 else end + 2
            else:
                break
        return start

    def unescape(value):
        def replace(match):
            text = match[0][1:]
            if text in {"\n", "\r", "\r\n", "\f"}:
                return ""
            if re.fullmatch(r"[0-9a-fA-F]{1,6}\s?", text):
                code = int(text.strip(), 16)
                return chr(code) if 0 < code <= 0x10ffff and not 0xd800 <= code <= 0xdfff else "\ufffd"
            return text
        return re.sub(r"\\(?:\r\n|[\n\r\f]|[0-9a-fA-F]{1,6}[ \t\r\n\f]?|.)", replace, value)

    cursor = 0
    while cursor < size:
        if source.startswith("/*", cursor):
            cursor = space_end(cursor)
            continue
        if source[cursor] in "\"'":
            cursor = string_end(cursor)
            continue
        token = re.match(r"[-\w]+", source[cursor:])
        if token:
            start = cursor
            cursor += len(token[0])
            if token[0].lower() != "url" or cursor >= size or source[cursor] != "(":
                continue
            begin = space_end(cursor + 1)
            if begin < size and source[begin] in "\"'":
                end = string_end(begin)
                close = space_end(end)
                if end > begin + 1 and source[end - 1] == source[begin] and close < size and source[close] == ")":
                    yield unescape(source[begin + 1:end - 1]), start
                    cursor = close + 1
                else:
                    cursor = end
            else:
                end = begin
                while end < size and source[end] != ")":
                    end += 2 if source[end] == "\\" else 1
                if end < size:
                    yield unescape(source[begin:end].strip()), start
                cursor = min(end + 1, size)
        else:
            cursor += 1


def parsed_date(value):
    """Preserve date-only precision rather than inventing a midnight or offset."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Expected a nonempty ISO date or datetime string")
    value = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return date.fromisoformat(value), True
    if not re.match(r"^\d{4}-\d{2}-\d{2}[Tt ]\d{2}:\d{2}", value):
        raise ValueError("Expected YYYY-MM-DD or an ISO datetime")
    return datetime.fromisoformat(value.replace("Z", "+00:00").replace("z", "+00:00")), False


def dates_agree(left, right):
    a, a_day = left
    b, b_day = right
    if a_day or b_day:
        return (a if a_day else a.date()) == (b if b_day else b.date())
    if a.tzinfo is not None and b.tzinfo is not None:
        return a == b
    return a.replace(tzinfo=None) == b.replace(tzinfo=None)


def date_precedes(left, right):
    a, a_day = left
    b, b_day = right
    if a_day or b_day:
        return (a if a_day else a.date()) < (b if b_day else b.date())
    if a.tzinfo is not None and b.tzinfo is not None:
        return a < b
    return a.replace(tzinfo=None) < b.replace(tzinfo=None)


class Node:
    def __init__(self, tag, attrs=(), parent=None, line=1):
        self.tag, self.attrs, self.parent, self.line = tag, dict(attrs), parent, line
        self.children = []

    def text(self):
        return "".join(c if isinstance(c, str) else c.text() for c in self.children)

    def find(self, predicate):
        result = []
        for child in self.children:
            if isinstance(child, str):
                continue
            if predicate(child):
                result.append(child)
            result.extend(child.find(predicate))
        return result


class Page(HTMLParser):
    def __init__(self, text, url, path):
        super().__init__(convert_charrefs=True)
        self.url, self.path, self.source = url, path, text
        self.root = Node("document")
        self.stack = [self.root]
        self.feed(text)
        self.ids = [n.attrs["id"] for n in self.find(lambda n: bool(n.attrs.get("id")))]
        self.fragment_names = set(self.ids) | {n.attrs["name"] for n in self.find(lambda n: n.tag == "a" and bool(n.attrs.get("name")))}
        self.lang = next((n.attrs.get("lang", "") for n in self.find(lambda n: n.tag == "html")), "")
        # Only the first base[href] is effective; base[target] does not count.
        base = next(iter(self.find(lambda n: n.tag == "base" and "href" in n.attrs)), None)
        self.base_url = urljoin(url, base.attrs["href"] or "") if base else url
        self.invalid_base = base if urlsplit(self.base_url).scheme not in {"http", "https"} else None

    def find(self, predicate):
        return self.root.find(predicate)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.stack[-1], self.getpos()[0])
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)

    def meta(self, key):
        return self.find(lambda n: n.tag == "meta" and (n.attrs.get("name", "").lower() == key or n.attrs.get("property", "").lower() == key))

    def alternates(self):
        return self.find(lambda n: n.tag == "link" and "alternate" in n.attrs.get("rel", "").split() and n.attrs.get("hreflang"))

    def excluded(self):
        # Verification documents and deliberate noindex/redirect/404 pages are not articles.
        # Keep parameter/value pairs together, including whitespace around ':'.
        # max-image-preview:none is not the standalone directive none.
        robots = {directive.lower() for n in self.meta("robots") + self.meta("googlebot")
                  for directive in re.findall(r"[^\s,:]+(?:\s*:\s*[^\s,]+)?", n.attrs.get("content") or "")}
        if robots.intersection({"noindex", "none"}) or self.path.name.lower() == "404.html":
            return True
        if re.fullmatch(r"google[0-9a-f]+\.html", self.path.name, re.I) and self.source.strip().startswith("google-site-verification:"):
            return True
        return False


def objects(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from objects(item)
    elif isinstance(value, list):
        for item in value:
            yield from objects(item)


def page_entities(value, canonical, base_url):
    """Select the current page's entities, not cited/parent/listed works.

    Top-level page objects remain candidates even with a wrong URL, so a typo
    cannot escape validation. Follow explicit mainEntity relationships, including
    graph @id references, while keeping citation and isPartOf metadata separate.
    """
    kinds = {"WebPage", "CollectionPage", "Article", "TechArticle", "BlogPosting"}

    def types(obj):
        value = obj.get("@type", [])
        return {value} if isinstance(value, str) else {v for v in value if isinstance(v, str)} if isinstance(value, list) else set()

    def roots(item):
        if isinstance(item, list):
            for child in item:
                yield from roots(child)
        elif isinstance(item, dict):
            yield item
            yield from roots(item.get("@graph"))

    nodes = list(objects(value))
    by_id = {urljoin(base_url, obj["@id"]): obj for obj in nodes if isinstance(obj.get("@id"), str) and obj.get("@type")}
    referenced = set()
    for obj in nodes:
        for relation in ("citation", "isPartOf", "hasPart", "itemListElement"):
            related = obj.get(relation)
            for reference in (related if isinstance(related, list) else [related]):
                if isinstance(reference, str):
                    referenced.add(urljoin(base_url, reference))
            for reference in objects(related):
                if isinstance(reference.get("@id"), str):
                    referenced.add(urljoin(base_url, reference["@id"]))

    def matches_page(obj):
        main = obj.get("mainEntityOfPage")
        main = main.get("@id", main.get("url")) if isinstance(main, dict) else main
        # A cited work may have a document-local node id (#reference-1) while
        # describing a completely different URL. Node identity alone does not
        # make it the current page; explicit mainEntity links are followed below.
        return any(isinstance(v, str) and document_url(urljoin(base_url, v)) == canonical
                   for v in (obj.get("url"), main))

    selected = {}
    pending = []
    for obj in roots(value):
        kind = types(obj)
        ident = urljoin(base_url, obj["@id"]) if isinstance(obj.get("@id"), str) else None
        if (kind & kinds and (ident not in referenced or matches_page(obj))) or ("WebSite" in kind and isinstance(obj.get("url"), str) and document_url(urljoin(base_url, obj["url"])) == canonical):
            pending.append(obj)
    while pending:
        obj = pending.pop()
        if id(obj) in selected:
            continue
        selected[id(obj)] = obj
        for relation in ("mainEntity", "mainEntityOfPage"):
            values = obj.get(relation, [])
            values = values if isinstance(values, list) else [values]
            for child in values:
                if isinstance(child, str):
                    child = by_id.get(urljoin(base_url, child))
                elif isinstance(child, dict) and not child.get("@type") and isinstance(child.get("@id"), str):
                    child = by_id.get(urljoin(base_url, child["@id"]), child)
                if isinstance(child, dict) and types(child) & kinds:
                    pending.append(child)
    return set(selected)


class Auditor:
    def __init__(self, build_root):
        self.build_root = Path(build_root).resolve()
        self.pages, self.by_path, self.maps = {}, {}, {}
        self.map_dates, self.page_dates = {}, {}
        self.errors, self.warnings = [], []
        self.external = set()
        self.stats = Counter()
        self._issues = set()

    def issue(self, code, message, page=None, line=None, warning=False):
        url = page.url if isinstance(page, Page) else str(page or "")
        key = (warning, code, message, url, line)
        if key in self._issues:
            return
        self._issues.add(key)
        row = {"code": code, "message": message, "url": url}
        if isinstance(page, Page):
            row["file"] = str(page.path.relative_to(self.build_root)).replace("\\", "/")
        if line:
            row["line"] = line
        (self.warnings if warning else self.errors).append(row)

    def local_path(self, url):
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != urlsplit(ORIGIN).netloc:
            return None
        path = unquote(parsed.path)
        repo = "portal"
        for name, prefix in ROUTES.items():
            if name != "portal" and (path.startswith(prefix) or path == prefix.rstrip("/")):
                repo = name
                path = path[len(prefix.rstrip("/")):]
                break
        base = self.build_root / repo
        candidate = (base / path.lstrip("/")).resolve()
        if not candidate.is_relative_to(base.resolve()):
            return base / "__invalid_path_outside_build__"
        if path.endswith("/") or candidate.is_dir():
            candidate /= "index.html"
        return candidate

    def target(self, raw, page, line=None, fragments=True):
        if not raw:
            return None
        try:
            url = urljoin(page.base_url if isinstance(page, Page) else str(page), raw)
            parsed = urlsplit(url)
            path = self.local_path(url)
        except (ValueError, OSError) as exc:
            self.issue("INVALID_URL", f"Invalid URL {raw!r}: {exc}", page, line)
            return None
        if path is None:
            if parsed.scheme in {"http", "https"}:
                self.external.add(urldefrag(url)[0])
            return None
        self.stats["internalReferences"] += 1
        if not path.is_file():
            self.issue("MISSING_TARGET", f"Missing generated target: {url}", page, line)
            return None
        fragment = unquote(parsed.fragment).split(":~:", 1)[0]
        if fragments and fragment and path.suffix.lower() in {".html", ".svg"}:
            self.stats["fragmentReferences"] += 1
            target = self.by_path.get(path)
            if target is None:
                target = Page(path.read_text(encoding="utf-8-sig"), document_url(url), path)
            if fragment not in target.fragment_names:
                self.issue("MISSING_FRAGMENT", f"Missing fragment #{fragment}: {document_url(url)}", page, line)
        return path

    def load(self):
        for repo, prefix in ROUTES.items():
            base = self.build_root / repo
            if not base.is_dir():
                self.issue("MISSING_BUILD", f"Missing build directory: {repo}")
                continue
            for path in sorted(base.rglob("*.html")):
                relative = path.relative_to(base).as_posix()
                route = relative[:-len("index.html")] if relative.endswith("/index.html") or relative == "index.html" else relative
                url = ORIGIN + prefix + route
                try:
                    page = Page(path.read_text(encoding="utf-8-sig"), url, path.resolve())
                    self.pages[url], self.by_path[path.resolve()] = page, page
                except (UnicodeError, ValueError) as exc:
                    self.issue("HTML_READ", f"Cannot parse {path}: {exc}")
        self.stats["htmlPages"] = len(self.pages)

    def check_links(self):
        for page in self.pages.values():
            if page.invalid_base:
                self.issue("BASE_URL", "base href must resolve to an HTTP(S) URL", page, page.invalid_base.line)
            for ident, count in Counter(page.ids).items():
                if count > 1:
                    self.issue("DUPLICATE_ID", f"Duplicate id: {ident}", page)
            for node in page.find(lambda n: True):
                # A base URL changes resolution; it is not itself a fetched resource.
                if node.tag == "base":
                    continue
                for key in ("href", "src", "poster"):
                    if node.attrs.get(key):
                        self.target(node.attrs[key], page, node.line)
                srcset = node.attrs.get("srcset", "")
                if srcset and not srcset.lstrip().startswith("data:"):
                    for entry in srcset.split(","):
                        if entry.strip():
                            self.target(entry.strip().split()[0], page, node.line)
                if node.tag == "meta" and (node.attrs.get("property") in {"og:image", "og:image:url", "twitter:image"} or node.attrs.get("name") == "twitter:image"):
                    self.target(node.attrs.get("content", ""), page, node.line)
                if node.tag == "meta" and node.attrs.get("http-equiv", "").lower() == "refresh":
                    match = re.search(r"(?:^|;)\s*url\s*=\s*(.+)$", node.attrs.get("content", ""), re.I)
                    if match:
                        self.target(match[1].strip(" '\""), page, node.line)
        for repo, prefix in ROUTES.items():
            for path in sorted((self.build_root / repo).rglob("*.css")):
                url = ORIGIN + prefix + path.relative_to(self.build_root / repo).as_posix()
                text = path.read_text(encoding="utf-8-sig")
                for value, offset in css_urls(text):
                    if value and not value.startswith(("#", "data:")):
                        self.target(value, url, text[:offset].count("\n") + 1)

    def check_maps(self):
        all_mapped = set()
        for repo, prefix in ROUTES.items():
            path = self.build_root / repo / "sitemap.xml"
            try:
                tree = ET.fromstring(path.read_text(encoding="utf-8-sig"))
                if tree.tag != NS + "urlset":
                    raise ValueError("Expected a sitemap urlset in the standard namespace")
                entries = tree.findall(NS + "url")
                if not entries:
                    raise ValueError("Sitemap is empty")
            except (OSError, ET.ParseError, ValueError) as exc:
                self.issue("SITEMAP_PARSE", f"{repo}/sitemap.xml: {exc}")
                continue
            urls = []
            for entry in entries:
                loc = norm(entry.findtext(NS + "loc"))
                urls.append(loc)
                parsed = urlsplit(loc)
                if not loc.startswith(ORIGIN + prefix) or parsed.query or parsed.fragment or parsed.scheme != "https":
                    self.issue("SITEMAP_URL", f"Unexpected sitemap URL: {loc}", loc)
                if repo == "portal" and any(parsed.path.startswith(p) for r, p in ROUTES.items() if r != "portal"):
                    self.issue("SITEMAP_OWNER", f"Product URL is listed in root sitemap: {loc}", loc)
                target = self.target(loc, ORIGIN + prefix, fragments=False)
                page = self.by_path.get(target)
                if target and (page is None or page.excluded()):
                    self.issue("SITEMAP_NOINDEX", "Sitemap target is not an indexable HTML page", loc)
                lastmod = norm(entry.findtext(NS + "lastmod"))
                if lastmod:
                    try:
                        self.map_dates[loc] = (lastmod, parsed_date(lastmod))
                    except ValueError:
                        self.issue("SITEMAP_DATE", f"Invalid lastmod: {lastmod}", loc)
            duplicates = [u for u, count in Counter(urls).items() if count > 1]
            for url in duplicates:
                self.issue("SITEMAP_DUPLICATE", "Duplicate sitemap loc", url)
            self.maps[repo] = urls
            overlap = all_mapped.intersection(urls)
            for url in overlap:
                self.issue("SITEMAP_DUPLICATE", "URL repeated across sitemaps", url)
            all_mapped.update(urls)
        self.stats["mappedPages"] = len(all_mapped)
        for url, page in self.pages.items():
            if not page.excluded() and url not in all_mapped:
                self.issue("MISSING_SITEMAP_PAGE", "Indexable HTML page is absent from sitemap", page)

    def check_schema(self, page, canonical):
        scripts = page.find(lambda n: n.tag == "script" and n.attrs.get("type", "").lower() == "application/ld+json")
        if not scripts:
            self.issue("JSONLD_MISSING", "Indexable page has no JSON-LD", page)
        parsed_scripts = []
        for script in scripts:
            try:
                value = json.loads(script.text())
                if not isinstance(value, (dict, list)) or not value:
                    raise ValueError("Expected a nonempty JSON-LD object or list")
            except (ValueError, TypeError) as exc:
                self.issue("JSONLD_PARSE", str(exc), page, script.line)
                continue
            parsed_scripts.append((script, value))
        # References may point to an entity defined in another script on this page.
        current_entities = page_entities([value for _, value in parsed_scripts], canonical, page.base_url)
        for script, value in parsed_scripts:
            for obj in objects(value):
                types = obj.get("@type", [])
                types = [types] if isinstance(types, str) else types
                if not isinstance(types, list) or any(not isinstance(t, str) for t in types):
                    self.issue("JSONLD_TYPE", "@type must be a string or list", page, script.line)
                    continue
                page_type = id(obj) in current_entities
                if page_type:
                    for field in ("datePublished", "dateModified"):
                        if field in obj:
                            self.record_page_date(page, field, obj[field], script.line, "JSONLD_DATE")
                if page_type and set(types).intersection({"WebPage", "CollectionPage", "Article", "TechArticle", "BlogPosting"}):
                    own = obj.get("url")
                    if isinstance(own, str) and document_url(urljoin(page.base_url, own)) != canonical:
                        self.issue("JSONLD_PAGE_URL", f"Page schema URL differs from canonical: {own}", page, script.line)
                    main = obj.get("mainEntityOfPage")
                    main = main.get("@id") if isinstance(main, dict) else main
                    if isinstance(main, str) and document_url(urljoin(page.base_url, main)) != canonical:
                        self.issue("JSONLD_PAGE_URL", f"mainEntityOfPage differs from canonical: {main}", page, script.line)
                if "BreadcrumbList" in types or "ItemList" in types:
                    items = obj.get("itemListElement")
                    if not isinstance(items, list) or not items:
                        self.issue("JSONLD_LIST", "Structured list has no items", page, script.line)
                        continue
                    is_breadcrumb = "BreadcrumbList" in types
                    positions, schema_crumbs = [], []
                    for item in items:
                        if not isinstance(item, dict):
                            # schema.org permits URL/Text ItemList entries, unlike breadcrumbs.
                            if is_breadcrumb:
                                self.issue("JSONLD_LIST", "Breadcrumb item must be an object", page, script.line)
                            continue
                        if "position" in item:
                            positions.append(item["position"])
                        target = item.get("item", item.get("url"))
                        if isinstance(target, dict):
                            target = target.get("@id", target.get("url"))
                        if isinstance(target, str):
                            self.target(target, page, script.line)
                        if is_breadcrumb:
                            if not norm(item.get("name")) or not isinstance(target, str):
                                self.issue("JSONLD_BREADCRUMB", "Breadcrumb requires name and item URL", page, script.line)
                            else:
                                schema_crumbs.append((norm(item["name"]), urljoin(page.base_url, target)))
                    if (is_breadcrumb or positions) and positions != list(range(1, len(items) + 1)):
                        self.issue("JSONLD_POSITIONS", "Structured list positions must be consecutive from 1", page, script.line)
                    if "numberOfItems" in obj and str(obj["numberOfItems"]) != str(len(items)):
                        self.issue("JSONLD_LIST_COUNT", "numberOfItems differs from actual items", page, script.line)
                    if is_breadcrumb:
                        visible = page.find(lambda n: n.tag == "nav" and "breadcrumbs" in n.attrs.get("class", "").split())
                        if visible:
                            crumbs = []
                            for node in visible[0].children:
                                if isinstance(node, str) or node.tag not in {"a", "span"} or node.attrs.get("aria-hidden") == "true" or not norm(node.text()):
                                    continue
                                crumbs.append((norm(node.text()), urljoin(page.base_url, node.attrs.get("href", page.url))))
                            # Visible short labels and descriptive schema names may differ;
                            # compare target order and count, not editorial wording.
                            if [u for _, u in crumbs] != [u for _, u in schema_crumbs]:
                                self.issue("BREADCRUMB_MISMATCH", "Visible and structured breadcrumb targets differ", page, script.line)

    def record_page_date(self, page, field, value, line, code):
        try:
            parsed = parsed_date(value)
        except (ValueError, TypeError) as exc:
            self.issue(code, f"Invalid {field}: {value!r} ({exc})", page, line)
            return
        self.page_dates.setdefault(page.url, {}).setdefault(field, []).append((value, parsed, line))
        self.stats["pageDateFieldsChecked"] += 1

    def check_page_dates(self, page):
        for meta, field in (("article:published_time", "datePublished"), ("article:modified_time", "dateModified")):
            for node in page.meta(meta):
                self.record_page_date(page, field, node.attrs.get("content"), node.line, "METADATA_DATE")
        dates = self.page_dates.get(page.url, {})
        for field, values in dates.items():
            for index, (raw, parsed, line) in enumerate(values):
                for other_raw, other_parsed, _ in values[index + 1:]:
                    if not dates_agree(parsed, other_parsed):
                        self.issue("PAGE_DATE_MISMATCH", f"Conflicting {field} values: {raw!r} and {other_raw!r}", page, line)
        for published, pub_date, _ in dates.get("datePublished", []):
            for modified, mod_date, line in dates.get("dateModified", []):
                if date_precedes(mod_date, pub_date):
                    self.issue("PAGE_DATE_ORDER", f"dateModified {modified!r} precedes datePublished {published!r}", page, line)
        if page.url in self.map_dates:
            lastmod, map_date = self.map_dates[page.url]
            for modified, mod_date, line in dates.get("dateModified", []):
                if not dates_agree(mod_date, map_date):
                    self.issue("SITEMAP_DATE_MISMATCH", f"dateModified {modified!r} differs from sitemap lastmod {lastmod!r}", page, line)

    def check_metadata(self):
        for page in self.pages.values():
            if page.excluded():
                # Even noindex pages must not ship malformed JSON.
                for node in page.find(lambda n: n.tag == "script" and n.attrs.get("type") == "application/ld+json"):
                    try:
                        json.loads(node.text())
                    except ValueError as exc:
                        self.issue("JSONLD_PARSE", str(exc), page, node.line)
                continue
            self.stats["indexablePages"] += 1
            for tag in ("title", "h1"):
                nodes = page.find(lambda n: n.tag == tag)
                if len(nodes) != 1 or not norm(nodes[0].text()):
                    self.issue("METADATA_" + tag.upper(), f"Expected one nonempty {tag}", page)
            descriptions = page.meta("description")
            if len(descriptions) != 1 or not norm(descriptions[0].attrs.get("content")):
                self.issue("METADATA_DESCRIPTION", "Expected one nonempty meta description", page)
            canon = page.find(lambda n: n.tag == "link" and "canonical" in n.attrs.get("rel", "").split())
            canonical = canon[0].attrs.get("href", "") if len(canon) == 1 else ""
            if canonical != page.url:
                self.issue("CANONICAL", f"Expected canonical {page.url}; got {canonical!r}", page)
            og_urls = page.meta("og:url")
            if len(og_urls) > 1:
                self.issue("OG_URL", "Duplicate og:url fields", page)
            for node in og_urls:
                if node.attrs.get("content") != canonical:
                    self.issue("OG_URL", f"og:url differs from canonical: {node.attrs.get('content')!r}", page, node.line)
            if not page.lang:
                self.issue("LANGUAGE", "Missing HTML lang", page)
            locale = page.meta("og:locale")
            expected = {"en": "en_US", "zh-cn": "zh_CN"}.get(page.lang.lower())
            if expected and (len(locale) != 1 or locale[0].attrs.get("content") != expected):
                self.issue("LOCALE", f"Expected og:locale={expected} for lang={page.lang}", page)
            elif not expected:
                self.issue("LANGUAGE_UNKNOWN", f"Language not covered by locale checks: {page.lang}", page, warning=True)
            self.check_schema(page, canonical)
            self.check_page_dates(page)
            alternate_nodes = page.alternates()
            alternate = {n.attrs["hreflang"].lower(): urljoin(page.base_url, n.attrs.get("href", "")) for n in alternate_nodes}
            if len(alternate) != len(alternate_nodes):
                self.issue("HREFLANG_DUPLICATE", "Duplicate hreflang code", page)
            for code, target in alternate.items():
                destination = self.by_path.get(self.local_path(target))
                if destination is None or destination.excluded():
                    self.issue("HREFLANG_TARGET", f"Missing indexable alternate: {target}", page)
                    continue
                if code != "x-default" and destination.lang.lower() != code:
                    self.issue("HREFLANG_LANGUAGE", f"Alternate {code} targets lang={destination.lang}: {target}", page)
                reverse = {n.attrs["hreflang"].lower(): urljoin(destination.base_url, n.attrs.get("href", "")) for n in destination.alternates()}
                if reverse != alternate:
                    self.issue("HREFLANG_RECIPROCAL", f"Alternate set not reciprocal: {target}", page)

    def check_search(self):
        path = self.build_root / "portal" / "search-index.json"
        try:
            records = json.loads(path.read_text(encoding="utf-8-sig"))
            if not isinstance(records, list) or not records:
                raise ValueError("Expected a nonempty search index list")
        except (OSError, ValueError) as exc:
            self.issue("SEARCH_FORMAT", str(exc), ORIGIN + "/search-index.json")
            return
        urls = []
        for index, item in enumerate(records):
            if not isinstance(item, dict) or any(not isinstance(item.get(k), str) or not item[k].strip() for k in ("product", "title", "description", "url")) or not isinstance(item.get("keywords"), str):
                self.issue("SEARCH_RECORD", f"Invalid required fields at record {index + 1}", ORIGIN + "/search-index.json")
                continue
            url = item["url"]
            urls.append(url)
            target = self.local_path(url)
            if not url.startswith(ORIGIN + "/") or target is None:
                self.issue("SEARCH_URL", f"Search target is not an absolute knowledge-base URL: {url}")
                continue
            self.target(url, ORIGIN + "/search-index.json")
            page = self.by_path.get(target)
            if page is None or page.excluded():
                self.issue("SEARCH_URL", f"Search target is not an indexable HTML page: {url}")
        for url, count in Counter(urls).items():
            if count > 1:
                self.issue("SEARCH_DUPLICATE", "Duplicate search URL", url)
        self.stats["searchRecords"] = len(records)
        self.stats["uniqueSearchURLs"] = len(set(urls))
        for url, page in self.pages.items():
            if not page.excluded() and re.search(r"/guides/.+", urlsplit(url).path) and url not in urls:
                self.issue("SEARCH_COVERAGE", "Article is not yet in the portal search index; update the portal after publishing the article", page, warning=True)

    def run(self):
        for check in (self.load, self.check_links, self.check_maps, self.check_metadata, self.check_search):
            try:
                check()
            except (OSError, ValueError, TypeError, KeyError) as exc:
                self.issue("CHECK_EXCEPTION", f"{check.__name__} could not complete: {type(exc).__name__}: {exc}")
        self.stats["externalURLsNotRequested"] = len(self.external)
        return {
            "checkedAt": datetime.now(timezone.utc).isoformat(),
            "passed": not self.errors,
            "buildRoot": str(self.build_root),
            "summary": dict(self.stats),
            "sitemapCounts": {repo: len(urls) for repo, urls in self.maps.items()},
            "errors": self.errors,
            "warnings": self.warnings,
            "limits": ["No external HTTP requests, article fact checking, search-engine indexing or browser layout verification.", "Missing portal search coverage is advisory to allow article-first cross-repository publication.", "Titles/descriptions are checked for presence, not identical wording or factual accuracy."],
        }


def annotation(row, kind):
    def escape(text):
        return str(text).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    location = ""
    if row.get("file"):
        location = " file=" + escape(row["file"]).replace(",", "%2C").replace(":", "%3A")
        if row.get("line"):
            location += ",line=" + str(row["line"])
    print(f"::{kind}{location}::{escape('[' + row['code'] + '] ' + row.get('url', '') + ' ' + row['message'])}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-root", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    report = Auditor(args.build_root).run()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for row in report["errors"]:
        annotation(row, "error")
    for row in report["warnings"]:
        annotation(row, "warning")
    print(json.dumps({"passed": report["passed"], "summary": report["summary"], "errors": len(report["errors"]), "warnings": len(report["warnings"]), "report": str(args.report)}, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
