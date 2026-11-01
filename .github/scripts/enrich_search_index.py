"""Add searchable headings from the same five built snapshots, without editing sources."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ORIGIN = 'https://he20000405-pixel.github.io'
PRODUCTS = {
    '/chatgpt-plus-pro-china-guide/': 'chatgpt',
    '/supergrok-china-guide/': 'grok',
    '/claude-pro-max-china-guide/': 'claude',
    '/gemini-google-ai-pro-china-guide/': 'gemini',
}
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())


class Headings(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.headings = []
        self.active = None

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        inert = (self.stack and self.stack[-1][1]) or tag in {'script', 'style', 'template', 'noscript'}
        if tag == 'h1' and not inert:
            self.headings.append([])
            self.active = self.headings[-1]
        if tag not in VOID:
            self.stack.append((tag, inert))

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.active = None
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.active is not None and not (self.stack and self.stack[-1][1]):
            self.active.append(data)


def heading_for(build_root, url):
    parsed = urlsplit(url)
    if parsed.scheme + '://' + parsed.netloc != ORIGIN or parsed.query or parsed.fragment:
        raise ValueError('Search target must be a canonical knowledge-base URL: ' + url)
    route = unquote(parsed.path)
    alias = 'portal'
    for prefix, product in PRODUCTS.items():
        if route.startswith(prefix):
            alias, route = product, route[len(prefix):]
            break
    root = (build_root / alias).resolve()
    target = (root / route.lstrip('/')).resolve()
    if not target.is_relative_to(root):
        raise ValueError('Search target escapes the built site: ' + url)
    if route.endswith('/') or target.is_dir():
        target /= 'index.html'
    if target.suffix.lower() != '.html' or not target.is_file():
        raise ValueError('Search target HTML does not exist: ' + url)
    parser = Headings()
    parser.feed(target.read_text(encoding='utf-8-sig'))
    headings = [re.sub(r'\s+', ' ', ''.join(parts)).strip() for parts in parser.headings]
    if len(headings) != 1 or not headings[0]:
        raise ValueError('Search target must have one nonempty H1: ' + url)
    return headings[0]


def enrich(build_root):
    build_root = Path(build_root).resolve()
    path = build_root / 'portal/search-index.json'
    records = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(records, list) or not records:
        raise ValueError('Search index must be a nonempty array')
    for item in records:
        if not isinstance(item, dict) or not isinstance(item.get('url'), str):
            raise ValueError('Search record requires a URL')
        # Replace stale output deterministically; keep editorial result titles intact.
        item['headings'] = [heading_for(build_root, item['url'])]
    # Write only after every target has passed; a failure must not leave a partial index.
    path.write_text(json.dumps(records, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    return {'records': len(records), 'headings': len(records), 'index': str(path)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--build-root', required=True)
    args = parser.parse_args()
    print(json.dumps(enrich(args.build_root), ensure_ascii=False))
