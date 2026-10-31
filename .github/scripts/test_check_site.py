#!/usr/bin/env python3
"""Regression tests for real publication failures, using isolated temporary builds."""
import argparse
import html
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).with_name("check_site.py")
spec = importlib.util.spec_from_file_location("check_site", SCRIPT)
check_site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_site)
ORIGIN, ROUTES = check_site.ORIGIN, check_site.ROUTES
ARTICLE = ORIGIN + ROUTES["grok"] + "guides/example/"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def page(url, body="", lang="zh-CN", alternates=None, robots=""):
    alternate_html = "".join(f'<link rel="alternate" hreflang="{k}" href="{v}">' for k, v in (alternates or {}).items())
    schema = {"@context": "https://schema.org", "@type": "WebPage", "url": url, "dateModified": "2020-01-01"}
    return f'''<!doctype html><html lang="{lang}"><head>
<title>Fixture guide</title><meta name="description" content="A useful guide">
<meta property="og:locale" content="{'en_US' if lang == 'en' else 'zh_CN'}">
<meta name="robots" content="{robots}"><link rel="canonical" href="{url}">
{alternate_html}<script type="application/ld+json">{json.dumps(schema)}</script>
</head><body><h1>Fixture guide</h1>{body}</body></html>'''


def sitemap(urls):
    return '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{html.escape(u)}</loc><lastmod>2020-01-01</lastmod></url>" for u in urls) + "</urlset>"


class PublicationFailures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for repo, prefix in ROUTES.items():
            write(self.root / repo / "index.html", page(ORIGIN + prefix))
            write(self.root / repo / "sitemap.xml", sitemap([ORIGIN + prefix]))
        write(self.root / "grok/guides/example/index.html", page(ARTICLE, '<h2 id="第一步">Step</h2><a href="../../">Back</a>'))
        write(self.root / "grok/sitemap.xml", sitemap([ORIGIN + ROUTES["grok"], ARTICLE]))
        write(self.root / "portal/index.html", page(ORIGIN + "/", f'<a href="{ARTICLE}?mode=read#%E7%AC%AC%E4%B8%80%E6%AD%A5">Read</a><link rel="stylesheet" href="/assets/style.css?v=123"><img alt="" src="/assets/icon.svg">'))
        write(self.root / "portal/assets/style.css", 'body { background-image: url("icon.svg?v=123"); }')
        write(self.root / "portal/assets/icon.svg", '<svg xmlns="http://www.w3.org/2000/svg"><path id="icon"/></svg>')
        write(self.root / "portal/old/index.html", f'<html><head><meta name="robots" content="noindex, follow"><meta http-equiv="refresh" content="0; url={ARTICLE}"></head><body><a href="{ARTICLE}">Continue</a></body></html>')
        write(self.root / "grok/google123abc.html", "google-site-verification: google123abc.html")
        self.index = [{"product": "Grok", "title": "Example", "description": "Example guide", "keywords": "example", "url": ARTICLE}]
        self.write_index()

    def write_index(self):
        write(self.root / "portal/search-index.json", json.dumps(self.index))

    def replace(self, relative, before, after):
        path = self.root / relative
        content = path.read_text(encoding="utf-8")
        self.assertIn(before, content)
        write(path, content.replace(before, after))

    def run_audit(self):
        # A network call in any future checker is an error, including external links.
        with patch("socket.socket", side_effect=AssertionError("No network in acceptance checks")):
            return check_site.Auditor(self.root).run()

    def assert_blocked(self, code):
        result = self.run_audit()
        self.assertFalse(result["passed"], result)
        self.assertIn(code, [x["code"] for x in result["errors"]], result)

    def test_good_build_query_encoded_fragment_redirect_and_old_dates(self):
        result = self.run_audit()
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["summary"]["mappedPages"], 6)
        self.assertEqual(result["summary"]["searchRecords"], 1)
        self.assertEqual(result["warnings"], [])

    def test_missing_cross_repository_page(self):
        self.replace("portal/index.html", ARTICLE + "?", ARTICLE + "missing/?")
        self.assert_blocked("MISSING_TARGET")

    def test_missing_fragment(self):
        self.replace("portal/index.html", "#%E7%AC%AC%E4%B8%80%E6%AD%A5", "#missing-step")
        self.assert_blocked("MISSING_FRAGMENT")

    def test_missing_stylesheet_dependency(self):
        self.replace("portal/assets/style.css", 'icon.svg', 'missing.svg')
        self.assert_blocked("MISSING_TARGET")

    def test_css_comments_and_content_strings_are_not_dependencies(self):
        write(self.root / "portal/assets/style.css", '''
/* Example only: background-image: url("example-only.svg"); */
body { content: "url('not-a-resource.svg')"; background: url("icon.svg?note=/*literal*/"); }
/* url(another-example.svg) */
''')
        result = self.run_audit()
        self.assertTrue(result["passed"], result)
        self.replace("portal/assets/style.css", 'icon.svg?note=', 'missing.svg?note=')
        self.assert_blocked("MISSING_TARGET")

    def test_css_quoted_urls_comments_and_escapes(self):
        write(self.root / "portal/assets/style.css", r'''body {
background: URL(/* a comment */ "ic\6fn.svg" /* another comment */);
content: "escaped \" url(fake.svg)";
}''')
        self.assertTrue(self.run_audit()["passed"])
        self.replace("portal/assets/style.css", r'ic\6fn.svg', r'miss\69ng.svg')
        self.assert_blocked("MISSING_TARGET")

    def test_base_href_changes_relative_links_and_fragment_targets(self):
        article = "grok/guides/example/index.html"
        self.replace(article, 'href="../../"', 'href="../example/#第一步"')
        self.assertTrue(self.run_audit()["passed"])
        self.replace(article, '</head>', f'<base href="{ORIGIN}/"></head>')
        self.assert_blocked("MISSING_TARGET")

    def test_base_first_href_relative_urls_and_target_only_base(self):
        article = "grok/guides/example/index.html"
        self.replace(article, 'href="../../"', 'href="example/#第一步"')
        self.replace(article, '</head>', '<base target="_blank"><base href="../"><base href="/ignored/"></head>')
        result = self.run_audit()
        self.assertTrue(result["passed"], result)
        self.replace(article, 'href="example/#第一步"', 'href="example/#missing"')
        self.assert_blocked("MISSING_FRAGMENT")

    def test_base_target_only_and_unsupported_scheme(self):
        article = "grok/guides/example/index.html"
        self.replace(article, '</head>', '<base target="_blank"></head>')
        self.assertTrue(self.run_audit()["passed"])
        self.replace(article, '</head>', '<base href="data:text/html,ignored"></head>')
        self.assert_blocked("BASE_URL")

    def test_duplicate_id(self):
        self.replace("grok/guides/example/index.html", '</body>', '<div id="第一步"></div></body>')
        self.assert_blocked("DUPLICATE_ID")

    def test_broken_jsonld(self):
        self.replace("grok/guides/example/index.html", '"@context":', '"@context" BROKEN:')
        self.assert_blocked("JSONLD_PARSE")

    def test_metadata_failures(self):
        original = (self.root / "grok/guides/example/index.html").read_text(encoding="utf-8")
        cases = [
            ('<h1>Fixture guide</h1>', '', "METADATA_H1"),
            ('content="A useful guide"', 'content=""', "METADATA_DESCRIPTION"),
            (f'rel="canonical" href="{ARTICLE}"', f'rel="canonical" href="{ORIGIN}/"', "CANONICAL"),
            ('content="zh_CN"', 'content="en_US"', "LOCALE"),
        ]
        for old, new, code in cases:
            with self.subTest(code=code):
                write(self.root / "grok/guides/example/index.html", original.replace(old, new))
                self.assert_blocked(code)

    def test_existing_og_url_must_match_canonical(self):
        self.replace("grok/guides/example/index.html", "</head>", f'<meta property="og:url" content="{ARTICLE}"></head>')
        self.assertTrue(self.run_audit()["passed"])
        self.replace("grok/guides/example/index.html", f'property="og:url" content="{ARTICLE}"', f'property="og:url" content="{ORIGIN}/"')
        self.assert_blocked("OG_URL")

    def test_existing_dates_invalid_reversed_and_conflicting(self):
        original = (self.root / "grok/guides/example/index.html").read_text(encoding="utf-8")
        cases = [
            ('"dateModified": "2020-01-01"', '"dateModified": "not-a-date"', "JSONLD_DATE"),
            ('"dateModified": "2020-01-01"', '"datePublished": "2020-02-31", "dateModified": "2020-01-01"', "JSONLD_DATE"),
            ('"dateModified": "2020-01-01"', '"datePublished": "2020-01-02", "dateModified": "2020-01-01"', "PAGE_DATE_ORDER"),
            ('</head>', '<meta property="article:modified_time" content="2020-01-02"></head>', "PAGE_DATE_MISMATCH"),
            ('</head>', '<meta property="article:published_time" content="invalid"></head>', "METADATA_DATE"),
        ]
        for old, new, code in cases:
            with self.subTest(code=code):
                write(self.root / "grok/guides/example/index.html", original.replace(old, new))
                self.assert_blocked(code)

    def test_existing_modified_date_matches_sitemap(self):
        self.replace("grok/guides/example/index.html", '"dateModified": "2020-01-01"', '"dateModified": "2020-01-02"')
        self.assert_blocked("SITEMAP_DATE_MISMATCH")

    def test_equivalent_date_precision_and_timezone_are_allowed(self):
        # A longstanding date is valid; dates are never forced to today.
        self.replace("grok/sitemap.xml", "2020-01-01</lastmod>", "2020-01-01T00:00:00+08:00</lastmod>")
        self.assertTrue(self.run_audit()["passed"])
        self.replace("grok/guides/example/index.html", '"dateModified": "2020-01-01"', '"dateModified": "2020-01-01T00:00:00+08:00"')
        self.replace("grok/guides/example/index.html", "</head>", '<meta property="article:modified_time" content="2019-12-31T16:00:00Z"></head>')
        self.assertTrue(self.run_audit()["passed"])

    def test_dates_are_not_required_and_sitewide_dates_are_separate(self):
        self.replace("grok/guides/example/index.html", ', "dateModified": "2020-01-01"', '')
        self.assertTrue(self.run_audit()["passed"])
        site = {"@context": "https://schema.org", "@type": "WebSite", "url": ORIGIN + "/", "dateModified": "2010-01-01"}
        self.replace("grok/guides/example/index.html", '</body>', '<script type="application/ld+json">' + json.dumps(site) + '</script></body>')
        self.assertTrue(self.run_audit()["passed"])

    def test_cited_article_and_parent_dates_are_separate(self):
        article = "grok/guides/example/index.html"
        citation = {"@type": "Article", "url": "https://example.com/reference/", "datePublished": "2010-01-01", "dateModified": "2011-01-01"}
        for relation in ("citation", "isPartOf"):
            self.replace(article, '"dateModified": "2020-01-01"', '"dateModified": "2020-01-01", ' + json.dumps(relation) + ': ' + json.dumps(citation))
        result = self.run_audit()
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["summary"]["pageDateFieldsChecked"], 6)

    def test_graph_citation_reference_is_separate_from_primary_article(self):
        citation = {"@id": "https://example.com/reference/#article", "@type": "Article", "url": "https://example.com/reference/", "dateModified": "2011-01-01"}
        primary = {"@id": ARTICLE + "#article", "@type": "Article", "url": ARTICLE, "dateModified": "2020-01-01", "citation": {"@id": citation["@id"]}}
        graph = {"@context": "https://schema.org", "@graph": [primary, citation]}
        self.replace("grok/guides/example/index.html", '</body>', '<script type="application/ld+json">' + json.dumps(graph) + '</script></body>')
        result = self.run_audit()
        self.assertTrue(result["passed"], result)
        self.replace("grok/guides/example/index.html", '"dateModified": "2020-01-01", "citation"', '"dateModified": "2019-01-01", "citation"')
        self.assert_blocked("SITEMAP_DATE_MISMATCH")

    def test_primary_schema_wrong_url_and_nested_main_entity_still_block(self):
        article = "grok/guides/example/index.html"
        original = (self.root / article).read_text(encoding="utf-8")
        for schema in (
            {"@type": "Article", "url": "https://example.com/wrong/"},
            {"@type": "WebPage", "url": ARTICLE, "mainEntity": {"@type": "Article", "url": "https://example.com/wrong/"}},
            {"@type": "Article", "url": ARTICLE, "mainEntityOfPage": {"@id": "https://example.com/wrong/"}},
        ):
            with self.subTest(schema=schema):
                write(self.root / article, original.replace('</body>', '<script type="application/ld+json">' + json.dumps(schema) + '</script></body>'))
                self.assert_blocked("JSONLD_PAGE_URL")

    def test_citation_reference_across_jsonld_scripts_is_separate(self):
        citation = {"@id": "https://example.com/reference/#article", "@type": "Article", "url": "https://example.com/reference/", "dateModified": "2011-01-01"}
        self.replace("grok/guides/example/index.html", '"dateModified": "2020-01-01"', '"dateModified": "2020-01-01", "citation": ' + json.dumps(citation["@id"]))
        self.replace("grok/guides/example/index.html", '</body>', '<script type="application/ld+json">' + json.dumps(citation) + '</script></body>')
        result = self.run_audit()
        self.assertTrue(result["passed"], result)

    def test_local_fragment_citation_id_does_not_make_it_the_current_page(self):
        citation = {"@id": ARTICLE + "#reference-1", "@type": "Article", "url": "https://example.com/reference/", "dateModified": "2011-01-01"}
        primary = {"@id": ARTICLE + "#article", "@type": "Article", "url": ARTICLE, "dateModified": "2020-01-01", "citation": {"@id": citation["@id"]}}
        graph = {"@context": "https://schema.org", "@graph": [primary, citation]}
        self.replace("grok/guides/example/index.html", '</body>', '<script type="application/ld+json">' + json.dumps(graph) + '</script></body>')
        result = self.run_audit()
        self.assertTrue(result["passed"], result)

    def test_explicit_main_entity_is_checked_even_if_it_is_also_cited(self):
        wrong = {"@id": ARTICLE + "#wrong", "@type": "Article", "url": "https://example.com/wrong/", "dateModified": "2011-01-01"}
        primary = {"@type": "WebPage", "url": ARTICLE, "mainEntity": {"@id": wrong["@id"]}, "citation": {"@id": wrong["@id"]}}
        graph = {"@context": "https://schema.org", "@graph": [primary, wrong]}
        self.replace("grok/guides/example/index.html", '</body>', '<script type="application/ld+json">' + json.dumps(graph) + '</script></body>')
        self.assert_blocked("JSONLD_PAGE_URL")

    def test_main_entity_graph_reference_dates_are_checked(self):
        graph = {"@context": "https://schema.org", "@graph": [
            {"@type": "WebPage", "url": ARTICLE, "mainEntity": {"@id": ARTICLE + "#article"}},
            {"@id": ARTICLE + "#article", "@type": "Article", "url": ARTICLE, "dateModified": "2019-01-01"},
        ]}
        self.replace("grok/guides/example/index.html", '</body>', '<script type="application/ld+json">' + json.dumps(graph) + '</script></body>')
        self.assert_blocked("SITEMAP_DATE_MISMATCH")

    def test_sitemap_missing_page(self):
        write(self.root / "grok/sitemap.xml", sitemap([ORIGIN + ROUTES["grok"]]))
        self.assert_blocked("MISSING_SITEMAP_PAGE")

    def test_sitemap_bad_xml_duplicates_and_noindex(self):
        for text, code in [("<broken>", "SITEMAP_PARSE"), (sitemap([ORIGIN + ROUTES["grok"], ARTICLE, ARTICLE]), "SITEMAP_DUPLICATE"), (sitemap([ORIGIN + ROUTES["grok"], ARTICLE, ORIGIN + "/old/"]), "SITEMAP_NOINDEX")]:
            with self.subTest(code=code):
                write(self.root / "grok/sitemap.xml", text)
                self.assert_blocked(code)

    def test_robots_none_excludes_sitemap_and_search_targets(self):
        article = "grok/guides/example/index.html"
        original = (self.root / article).read_text(encoding="utf-8")
        for name in ("robots", "googlebot"):
            for directives in ("none", " NoNe ", "follow, NONE", "none nofollow", "noindex nofollow"):
                with self.subTest(name=name, directives=directives):
                    write(self.root / article, original.replace('<meta name="robots" content="">', f'<meta name="{name}" content="{directives}">'))
                    result = self.run_audit()
                    self.assertFalse(result["passed"], result)
                    self.assertTrue({"SITEMAP_NOINDEX", "SEARCH_URL"}.issubset({row["code"] for row in result["errors"]}), result)

    def test_robots_parameter_none_does_not_mean_noindex(self):
        article = "grok/guides/example/index.html"
        original = (self.root / article).read_text(encoding="utf-8")
        for directives in ("max-image-preview:none", "index, follow, max-image-preview: none", "max-image-preview:none, noimageindex", "index follow max-image-preview: none"):
            with self.subTest(directives=directives):
                write(self.root / article, original.replace('name="robots" content=""', f'name="robots" content="{directives}"'))
                result = self.run_audit()
                self.assertTrue(result["passed"], result)

    def test_search_invalid_target_duplicate_and_format(self):
        self.index[0]["url"] = ARTICLE + "missing/"
        self.write_index()
        self.assert_blocked("SEARCH_URL")
        self.index[0]["url"] = ARTICLE
        self.index.append(dict(self.index[0]))
        self.write_index()
        self.assert_blocked("SEARCH_DUPLICATE")
        write(self.root / "portal/search-index.json", '{}')
        self.assert_blocked("SEARCH_FORMAT")

    def test_new_article_missing_from_portal_is_advisory(self):
        self.index[0]["url"] = ORIGIN + ROUTES["grok"]
        self.write_index()
        result = self.run_audit()
        self.assertTrue(result["passed"], result)
        self.assertEqual([x["code"] for x in result["warnings"]], ["SEARCH_COVERAGE"])

    def test_external_unreachable_url_never_blocks(self):
        self.replace("portal/index.html", '</body>', '<a href="https://unreachable.invalid/no-such-page">External</a></body>')
        result = self.run_audit()
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["summary"]["externalURLsNotRequested"], 1)

    def test_hreflang_reciprocity_and_target_language(self):
        en = ORIGIN + "/en/"
        pairs = {"zh-CN": ORIGIN + "/", "en": en, "x-default": ORIGIN + "/"}
        write(self.root / "portal/index.html", page(ORIGIN + "/", alternates=pairs))
        write(self.root / "portal/en/index.html", page(en, lang="en", alternates=pairs))
        write(self.root / "portal/sitemap.xml", sitemap([ORIGIN + "/", en]))
        self.assertTrue(self.run_audit()["passed"])
        self.replace("portal/en/index.html", f'<link rel="alternate" hreflang="zh-CN" href="{ORIGIN}/">', '')
        self.assert_blocked("HREFLANG_RECIPROCAL")
        write(self.root / "portal/en/index.html", page(en, lang="zh-CN", alternates=pairs))
        self.assert_blocked("HREFLANG_LANGUAGE")

    def test_breadcrumb_targets_and_list_count(self):
        crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": ORIGIN + "/"}, {"@type": "ListItem", "position": 2, "name": "Example", "item": ARTICLE}]}
        visible = f'<nav class="breadcrumbs"><a href="{ORIGIN}/">Home</a><span aria-hidden="true">/</span><span>Example</span></nav>'
        body = visible + '<script type="application/ld+json">' + json.dumps(crumb) + '</script><h2 id="第一步">Step</h2>'
        write(self.root / "grok/guides/example/index.html", page(ARTICLE, body))
        self.assertTrue(self.run_audit()["passed"])
        crumb["itemListElement"][0]["item"] = ORIGIN + ROUTES["chatgpt"]
        write(self.root / "grok/guides/example/index.html", page(ARTICLE, visible + '<script type="application/ld+json">' + json.dumps(crumb) + '</script><h2 id="第一步">Step</h2>'))
        self.assert_blocked("BREADCRUMB_MISMATCH")
        crumb["numberOfItems"] = 99
        write(self.root / "grok/guides/example/index.html", page(ARTICLE, '<script type="application/ld+json">' + json.dumps(crumb) + '</script>'))
        self.assert_blocked("JSONLD_LIST_COUNT")

    def test_cli_exit_report_and_annotation(self):
        report = self.root / "evidence/report.json"
        command = [sys.executable, "-B", str(SCRIPT), "--build-root", str(self.root), "--report", str(report)]
        good = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
        self.assertTrue(json.loads(report.read_text(encoding="utf-8"))["passed"])
        self.replace("portal/index.html", ARTICLE + "?", ARTICLE + "missing/?")
        bad = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(bad.returncode, 1, bad.stdout + bad.stderr)
        self.assertIn("::error", bad.stdout)
        self.assertFalse(json.loads(report.read_text(encoding="utf-8"))["passed"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-root", type=Path, help="Also check a real five-site build without writing a report")
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PublicationFailures)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    if args.build_root:
        report = check_site.Auditor(args.build_root).run()
        print(json.dumps({"realBuildPassed": report["passed"], "summary": report["summary"], "errors": report["errors"], "warnings": report["warnings"]}, ensure_ascii=False))
        if not report["passed"]:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
