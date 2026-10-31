"use strict";

// Isolated publication failures: no requests, no mutation of the supplied build.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { checkBuild } = require("./check_built_search.cjs");
const PAGE = "portal/search/index.html";
const SCRIPT = "portal/assets/js/search.js";
const INDEX = "portal/search-index.json";

const fixtureHtml = `<!doctype html><html><head></head><body>
<form data-search-form><input name="q" data-search-input><button type="submit">Search</button></form>
<p data-search-status></p><div data-search-results></div><nav data-search-discovery></nav>
<script src="/assets/js/search.js?v=fixture" defer></script></body></html>`;
const fixtureScript = `(function () {
  const form = document.querySelector('[data-search-form]');
  const input = document.querySelector('[data-search-input]');
  const results = document.querySelector('[data-search-results]');
  const status = document.querySelector('[data-search-status]');
  const discovery = document.querySelector('[data-search-discovery]');
  if (!form || !input || !results || !status) return;
  let items = [];
  input.value = new URLSearchParams(window.location.search).get('q') || '';
  function render() {
    results.replaceChildren();
    status.textContent = 'Search ready';
    discovery.hidden = false;
    if (!input.value) return;
    items.filter(item => item.title.includes(input.value)).forEach(item => {
      const article = document.createElement('article');
      const link = document.createElement('a');
      link.href = item.url;
      link.textContent = item.title;
      article.appendChild(link);
      results.appendChild(article);
    });
  }
  fetch("/search-index.json").then(response => response.json()).then(data => { items = data; render(); }).catch(() => { status.textContent = 'Unavailable'; });
  form.addEventListener('submit', event => {
    event.preventDefault();
    const url = new URL(window.location.href);
    if (input.value) url.searchParams.set('q', input.value); else url.searchParams.delete('q');
    window.history.replaceState({}, '', url);
    render();
  });
})();`;

function write(root, relative, value) {
  const target = path.join(root, relative);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, value, "utf8");
}

function replace(root, relative, before, after) {
  const text = fs.readFileSync(path.join(root, relative), "utf8");
  assert.ok(typeof before === "string" ? text.includes(before) : before.test(text), "Test mutation not applied: " + before);
  write(root, relative, text.replace(before, after));
}

async function main() {
  const args = process.argv.slice(2);
  assert.ok(!args.length || (args.length === 2 && args[0] === "--build-root"), "Usage: node test_built_search.cjs [--build-root build]");
  const buildRoot = args[1];
  const source = buildRoot ? Object.fromEntries([PAGE, SCRIPT, INDEX].map(file => [file, fs.readFileSync(path.join(buildRoot, file), "utf8")])) : {
    [PAGE]: fixtureHtml,
    [SCRIPT]: fixtureScript,
    [INDEX]: JSON.stringify([{ product: "Grok", title: "Grok fixture guide", description: "Useful guide", keywords: "grok", url: "/grok-guide/" }])
  };
  const temporaryParent = fs.realpathSync(os.tmpdir());
  const temporary = fs.mkdtempSync(path.join(temporaryParent, "chonggrok-search-gate-"));
  const results = [];
  async function test(name, change, expectedError) {
    const root = path.join(temporary, String(results.length));
    for (const [file, text] of Object.entries(source)) write(root, file, text);
    await change(root);
    if (expectedError) await assert.rejects(() => checkBuild(root), expectedError, name);
    else assert.equal((await checkBuild(root)).passed, true, name);
    results.push(name);
  }
  try {
    await test("actual page/script/index connection passes", () => {});
    await test("removed script is rejected", root => replace(root, PAGE, /<script\b[^>]*src="\/assets\/js\/search\.js[^>]*><\/script>/i, ""), /load exactly one search\.js/);
    await test("script in a comment cannot satisfy loading", root => replace(root, PAGE, /<script\b[^>]*src="\/assets\/js\/search\.js[^>]*><\/script>/i, match => "<!--" + match + "-->"), /load exactly one search\.js/);
    await test("script in a template cannot satisfy loading", root => replace(root, PAGE, /<script\b[^>]*src="\/assets\/js\/search\.js[^>]*><\/script>/i, match => "<template>" + match + "</template>"), /load exactly one search\.js/);
    for (const key of ["form", "input", "results", "status", "discovery"]) {
      await test("missing " + key + " is rejected", root => replace(root, PAGE, "data-search-" + key, "data-removed-" + key), new RegExp("one active data-search-" + key));
    }
    await test("commented fake form does not satisfy actual DOM", root => {
      replace(root, PAGE, "data-search-form", "data-removed-form");
      replace(root, PAGE, "</body>", '<!-- <form data-search-form></form> --></body>');
    }, /one active data-search-form/);
    await test("duplicate controls are rejected", root => replace(root, PAGE, "</body>", '<input data-search-input name="q"></body>'), /one active data-search-input/);
    await test("disabled input is rejected", root => replace(root, PAGE, "data-search-input", "disabled data-search-input"), /input must be enabled/);
    await test("inert script type is rejected", root => replace(root, PAGE, 'src="/assets/js/search.js', 'type="text/plain" src="/assets/js/search.js'), /classic JavaScript/);
    await test("async race is rejected", root => replace(root, PAGE, 'src="/assets/js/search.js', 'async src="/assets/js/search.js'), /async loading/);
    await test("missing built script file is rejected", root => fs.unlinkSync(path.join(root, SCRIPT)), /asset does not exist/);
    await test("wrong fetch URL is rejected", root => replace(root, SCRIPT, 'fetch("/search-index.json"', 'fetch("/__missing_search_index__.json"'), /actual built \/search-index\.json/);
    await test("external fetch URL is rejected", root => replace(root, SCRIPT, 'fetch("/search-index.json"', 'fetch("https://example.com/search-index.json"'), /actual built \/search-index\.json/);
    await test("missing built index is rejected", root => fs.unlinkSync(path.join(root, INDEX)), /asset does not exist/);
    await test("invalid index JSON is rejected", root => write(root, INDEX, "not valid json"), /JSON|Unexpected token/);
    await test("non-array index is rejected", root => write(root, INDEX, "{}"), /nonempty array/);
    await test("empty index is rejected", root => write(root, INDEX, "[]"), /nonempty array/);
    await test("invalid record fields are rejected", root => write(root, INDEX, '[{"title":"fixture"}]'), /must contain string/);
    await test("empty script cannot pass static checks", root => write(root, SCRIPT, "// Script accidentally empty"), /actually load the index/);
    await test("submit handler is required", root => replace(root, SCRIPT, /form\.addEventListener\(["']submit["']/, 'form.addEventListener("unused"'), /submit handler/);
    await test("script path respects the document base", root => {
      replace(root, PAGE, "</head>", '<base href="https://he20000405-pixel.github.io/assets/"></head>');
      replace(root, PAGE, 'src="/assets/js/search.js', 'src="js/search.js');
    });
    await test("document base cannot silently move the index to another origin", root => replace(root, PAGE, "</head>", '<base href="https://example.com/"></head>'), /knowledge-base origin|actual built/);
    console.log(JSON.stringify({ passed: true, tests: results.length, testedBuiltArtifacts: Boolean(buildRoot), cases: results }, null, 2));
  } finally {
    // The only recursive removal is this verified, freshly created temp folder.
    const resolved = fs.realpathSync(temporary);
    assert.equal(path.dirname(resolved), temporaryParent);
    assert.ok(path.basename(resolved).startsWith("chonggrok-search-gate-"));
    fs.rmSync(resolved, { recursive: true, force: true });
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
