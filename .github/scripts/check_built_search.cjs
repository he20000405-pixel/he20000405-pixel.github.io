"use strict";

// Offline integration contract for the deployed search HTML, JavaScript and JSON.
// This deliberately supplements (and does not replace) browser/visual acceptance.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const ORIGIN = "https://he20000405-pixel.github.io";
const PAGE_URL = ORIGIN + "/search/";
const SCRIPT_PATH = "/assets/js/search.js";
const INDEX_PATH = "/search-index.json";
const VOID = new Set("area base br col embed hr img input link meta param source track wbr".split(" "));

function decode(value) {
  return value.replace(/&(#x[0-9a-f]+|#\d+|amp|quot|apos|lt|gt);/gi, (all, code) => {
    if (code[0] === "#") return String.fromCodePoint(parseInt(code.slice(code[1].toLowerCase() === "x" ? 2 : 1), code[1].toLowerCase() === "x" ? 16 : 10));
    return { amp: "&", quot: '"', apos: "'", lt: "<", gt: ">" }[code.toLowerCase()];
  });
}

class Element {
  constructor(tag, attrs = {}, order = -1) {
    this.tagName = tag.toUpperCase(); this.attrs = attrs; this.order = order;
    this.children = []; this.parentElement = null; this.listeners = {};
    this.hidden = Object.hasOwn(attrs, "hidden"); this.value = attrs.value || "";
  }
  appendChild(child) { child.parentElement = this; this.children.push(child); return child; }
  append(...children) { children.forEach(child => this.appendChild(child)); }
  replaceChildren(...children) { this.children = []; this.append(...children); }
  addEventListener(name, listener) { (this.listeners[name] ||= []).push(listener); }
  get textContent() { return this.children.map(child => child.textContent).join(""); }
  set textContent(text) { this.children = [{ textContent: String(text), parentElement: this }]; }
  set innerHTML(_) { throw new Error("Search must render index text safely, without innerHTML"); }
  contains(node) { return node === this || this.children.some(child => child instanceof Element && child.contains(node)); }
}

// Read only active elements. Comments, script/style text, templates and noscript
// content must not manufacture search elements or executable script references.
function parsePage(html) {
  const nodes = [], stack = [];
  const tags = /<!--[\s\S]*?(?:-->|$)|<![^>]*>|<\/?[a-z][^>"']*(?:(?:"[^"]*"|'[^']*')[^>"']*)*>/gi;
  let match;
  while ((match = tags.exec(html))) {
    const raw = match[0];
    if (raw.startsWith("<!")) continue;
    const tag = /^<\/?([\w:-]+)/.exec(raw)[1].toLowerCase();
    if (raw.startsWith("</")) {
      const index = stack.map(item => item.tagName.toLowerCase()).lastIndexOf(tag);
      if (index >= 0) stack.splice(index);
      continue;
    }
    const attrs = {};
    const attrText = raw.slice(/^<[\w:-]+/.exec(raw)[0].length, -1);
    const attribute = /([^\s=/>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g;
    let attr;
    while ((attr = attribute.exec(attrText))) {
      const key = attr[1].toLowerCase();
      if (!Object.hasOwn(attrs, key)) attrs[key] = decode(attr[2] ?? attr[3] ?? attr[4] ?? "");
    }
    const node = new Element(tag, attrs, match.index);
    node.inert = stack.some(item => item.inert) || tag === "template" || tag === "noscript";
    if (stack.length) stack.at(-1).appendChild(node);
    nodes.push(node);
    if (["script", "style", "textarea", "title"].includes(tag)) {
      const closing = new RegExp("</" + tag + "\\s*>", "gi");
      closing.lastIndex = tags.lastIndex;
      const end = closing.exec(html);
      node.textContent = html.slice(tags.lastIndex, end ? end.index : html.length);
      tags.lastIndex = end ? closing.lastIndex : html.length;
    } else if (!VOID.has(tag)) stack.push(node);
  }
  return nodes.filter(node => !node.inert);
}

function localFile(root, url) {
  assert.equal(url.origin, ORIGIN, "Search assets must resolve to the knowledge-base origin: " + url.href);
  const file = path.resolve(root, "." + decodeURIComponent(url.pathname));
  const relative = path.relative(root, file);
  assert.ok(relative && !relative.startsWith("..") && !path.isAbsolute(relative), "Asset path escapes the built site");
  assert.ok(fs.existsSync(file) && fs.statSync(file).isFile(), "Built search asset does not exist: " + url.pathname);
  return file;
}

function loadBuild(buildRoot) {
  const root = path.resolve(buildRoot, "portal");
  const html = fs.readFileSync(path.join(root, "search", "index.html"), "utf8");
  const nodes = parsePage(html);
  const base = nodes.find(node => node.tagName === "BASE" && Object.hasOwn(node.attrs, "href"));
  const baseUrl = new URL(base ? base.attrs.href : PAGE_URL, PAGE_URL);
  const searchNodes = {};
  for (const key of ["form", "input", "results", "status", "discovery"]) {
    const found = nodes.filter(node => Object.hasOwn(node.attrs, "data-search-" + key));
    assert.equal(found.length, 1, "Built search page must contain one active data-search-" + key);
    searchNodes[key] = found[0];
  }
  assert.equal(searchNodes.form.tagName, "FORM", "Search form must be a real form");
  assert.equal(searchNodes.input.tagName, "INPUT", "Search input must be a real input");
  assert.ok(searchNodes.form.contains(searchNodes.input), "Search input must belong to the search form");
  assert.ok(!Object.hasOwn(searchNodes.input.attrs, "disabled"), "Search input must be enabled");
  assert.equal(searchNodes.input.attrs.name, "q", "Search query field must be named q");
  assert.ok(nodes.some(node => searchNodes.form.contains(node) &&
    ((node.tagName === "BUTTON" && (node.attrs.type || "submit").toLowerCase() === "submit") ||
     (node.tagName === "INPUT" && node.attrs.type === "submit")) && !Object.hasOwn(node.attrs, "disabled")),
  "Search form must contain an enabled submit control");
  const scripts = nodes.filter(node => node.tagName === "SCRIPT" && node.attrs.src &&
    new URL(node.attrs.src, baseUrl).pathname === SCRIPT_PATH);
  assert.equal(scripts.length, 1, "Built search page must load exactly one search.js script");
  const script = scripts[0];
  assert.ok(!Object.hasOwn(script.attrs, "nomodule"), "Search script must run in current browsers");
  assert.ok(!Object.hasOwn(script.attrs, "async"), "Search script must not race the form with async loading");
  assert.ok(!script.attrs.type || ["text/javascript", "application/javascript"].includes(script.attrs.type.toLowerCase()),
    "Search script must use the supported classic JavaScript type");
  assert.ok(Object.hasOwn(script.attrs, "defer") || Object.values(searchNodes).every(node => node.order < script.order),
    "Search script must execute after its page elements exist");
  const scriptUrl = new URL(script.attrs.src, baseUrl);
  const source = fs.readFileSync(localFile(root, scriptUrl), "utf8");
  return { root, source, baseUrl, scriptUrl, nodes, searchNodes };
}

function validateIndex(items) {
  assert.ok(Array.isArray(items) && items.length, "Built search index must be a nonempty array");
  for (const [index, item] of items.entries()) {
    assert.ok(item && typeof item === "object", "Invalid search record " + index);
    for (const key of ["title", "product", "description", "keywords", "url"]) {
      assert.equal(typeof item[key], "string", "Search record " + index + " must contain string " + key);
    }
    assert.ok(item.title.trim() && item.product.trim(), "Search titles and products must not be empty");
    assert.equal(new URL(item.url, PAGE_URL).origin, ORIGIN, "Search result must link to this knowledge base");
  }
}

async function openSearch(buildRoot, query = "") {
  const build = loadBuild(buildRoot);
  const location = new URL(PAGE_URL);
  if (query) location.searchParams.set("q", query);
  const requests = [], requestFailures = [];
  let index, savedUrl;
  const context = vm.createContext({
    document: {
      baseURI: build.baseUrl.href,
      querySelector(selector) {
        const match = /^\[([^\]]+)\]$/.exec(selector);
        assert.ok(match, "Unsupported search selector: " + selector);
        return build.nodes.find(node => Object.hasOwn(node.attrs, match[1])) || null;
      },
      createElement(tag) { return new Element(tag); },
      createTextNode(text) { return { textContent: String(text) }; }
    },
    window: { location, history: { replaceState(_, __, value) { savedUrl = new URL(value, location); } } },
    URL, URLSearchParams, Set, Intl,
    fetch: async value => {
      try {
        const url = new URL(String(value), build.baseUrl);
        requests.push(url.href);
        assert.equal(url.origin + url.pathname, ORIGIN + INDEX_PATH, "Search must request the actual built /search-index.json");
        const text = fs.readFileSync(localFile(build.root, url), "utf8");
        index = JSON.parse(text);
        validateIndex(index);
        return { ok: true, json: async () => JSON.parse(text) };
      } catch (error) { requestFailures.push(error); throw error; }
    }
  });
  new vm.Script(build.source, { filename: build.scriptUrl.pathname }).runInContext(context, { timeout: 2000 });
  for (let count = 0; count < 4; count++) await new Promise(resolve => setImmediate(resolve));
  assert.equal(requestFailures.length, 0, requestFailures.map(error => error.message).join("; "));
  assert.equal(requests.length, 1, "Search script must actually load the index once");
  assert.ok(build.searchNodes.form.listeners.submit?.length, "Built script did not attach a submit handler");
  const rendered = () => build.searchNodes.results.children.flatMap(article => {
    const anchors = [];
    function visit(node) {
      if (node.tagName === "A") anchors.push({ href: new URL(node.href, PAGE_URL).href, title: node.textContent });
      for (const child of node.children || []) visit(child);
    }
    visit(article);
    return anchors;
  });
  return {
    ...build, index, requests, rendered,
    search(value) {
      context.__searchValue = value;
      context.__searchForm = build.searchNodes.form;
      context.__searchInput = build.searchNodes.input;
      vm.runInContext(`__searchInput.value = __searchValue;
        __searchPrevented = false;
        __searchForm.listeners.submit.forEach(handler => handler({ preventDefault() { __searchPrevented = true; } }));`, context, { timeout: 2000 });
      assert.ok(context.__searchPrevented, "Search submit must prevent a navigation/reload");
      assert.equal(savedUrl?.searchParams.get("q") || "", value.trim(), "Search must preserve the submitted query in the URL");
    }
  };
}

async function checkBuild(buildRoot) {
  const page = await openSearch(buildRoot);
  assert.equal(page.rendered().length, 0, "Empty initial search must not render the full index");
  assert.ok(page.searchNodes.status.textContent.trim(), "Search status must explain the initial state");
  const samples = [...new Set(page.index.map(item => item.product))]
    .map(product => page.index.find(item => item.product === product));
  const checked = [];
  for (const item of samples) {
    page.search(item.title);
    const matches = page.rendered();
    const expected = new URL(item.url, PAGE_URL).href;
    assert.ok(matches.some(match => match.href === expected && match.title === item.title), "Built search did not render the indexed article: " + item.title);
    for (const match of matches) assert.ok(page.index.some(entry => new URL(entry.url, PAGE_URL).href === match.href && entry.title === match.title), "Search rendered a result outside the built index");
    checked.push({ query: item.title, expected });
  }
  const first = samples[0];
  const initial = await openSearch(buildRoot, first.title);
  assert.ok(initial.rendered().some(item => item.href === new URL(first.url, PAGE_URL).href), "Query-string search must work on first load");
  page.search("unfindablefixturetoken987654321xyz");
  assert.equal(page.rendered().length, 0, "An unknown query must clear previous results");
  page.search("");
  assert.equal(page.rendered().length, 0, "Clearing search must clear results");
  assert.equal(page.searchNodes.discovery.hidden, false, "Clearing search must restore product links");
  return { passed: true, page: PAGE_URL, script: page.scriptUrl.href, indexRequests: page.requests,
    indexEntries: page.index.length, checkedQueries: checked, queryStringSearch: true, emptyAndNoMatch: true };
}

async function main() {
  const args = process.argv.slice(2);
  let buildRoot = "build", reportPath;
  for (let i = 0; i < args.length; i += 2) {
    assert.ok(args[i + 1], "Missing argument value: " + args[i]);
    if (args[i] === "--build-root") buildRoot = args[i + 1];
    else if (args[i] === "--report") reportPath = args[i + 1];
    else throw new Error("Unknown argument: " + args[i]);
  }
  let report;
  try { report = await checkBuild(buildRoot); }
  catch (error) { report = { passed: false, error: error.message }; process.exitCode = 1; }
  if (reportPath) {
    fs.mkdirSync(path.dirname(path.resolve(reportPath)), { recursive: true });
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + "\n");
  }
  console.log(JSON.stringify(report, null, 2));
}

module.exports = { checkBuild, loadBuild, parsePage };
if (require.main === module) main().catch(error => { console.error(error); process.exitCode = 1; });
