"use strict";

// Dependency-free browser behavior checks. Run with: node scripts/test_search.cjs
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const root = path.resolve(__dirname, "..");
const source = fs.readFileSync(path.join(root, "assets/js/search.js"), "utf8");

// This index uses only quoted scalar fields; fail rather than silently misread a new format.
function readIndex() {
  const items = [];
  for (const line of fs.readFileSync(path.join(root, "_data/guides.yml"), "utf8").split(/\r?\n/)) {
    if (!line.trim() || line.trim().startsWith("#")) continue;
    const match = line.match(/^(- |  )(product|title|description|url|keywords):\s*(".*")\s*$/);
    assert.ok(match, "Unsupported index line: " + line);
    if (match[1] === "- ") items.push({});
    items.at(-1)[match[2]] = JSON.parse(match[3]);
  }
  return items;
}

class Element {
  constructor(tag) { this.tag = tag; this.children = []; this.textContent = ""; this.hidden = false; this.listeners = {}; }
  appendChild(child) { this.children.push(child); return child; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  addEventListener(name, listener) { this.listeners[name] = listener; }
  set innerHTML(_) { throw new Error("Search must not render index text as HTML"); }
}

async function browser(items, options = {}) {
  const nodes = Object.fromEntries(["form", "input", "results", "status", "discovery"].map(name => [name, new Element(name)]));
  const location = new URL("https://example.test/search/?q=" + encodeURIComponent(options.query || ""));
  let savedUrl;
  vm.runInNewContext(source, {
    document: {
      querySelector(selector) { return nodes[selector.match(/data-search-(\w+)/)[1]]; },
      createElement(tag) { return new Element(tag); },
      createTextNode(text) { return { tag: "text", textContent: text }; }
    },
    window: { location, history: { replaceState(_, __, url) { savedUrl = url; } } },
    URL, URLSearchParams, Set,
    Intl: options.noSegmenter ? { Segmenter: undefined } : Intl,
    fetch: options.pending ? () => new Promise(() => {}) : async () => {
      if (options.failed) throw new Error("offline");
      return { ok: options.httpError !== true, json: async () => options.invalid ? {} : items };
    }
  });
  await new Promise(resolve => setImmediate(resolve));
  return {
    nodes,
    search(query) { nodes.input.value = query; nodes.form.listeners.submit({ preventDefault() {} }); },
    urls() { return nodes.results.children.map(article => article.children[1].children[0].href); },
    savedUrl() { return savedUrl; }
  };
}

async function main() {
  const items = readIndex();
  const page = await browser(items);
  assert.equal(page.urls().length, 0);
  assert.equal(page.nodes.discovery.hidden, false);
  assert.match(page.nodes.status.textContent, /输入产品/);

  const cases = [
    ["Grok Bot 额度", "grok-bot"],
    ["grok 403", "grok-build-login-403"],
    ["已扣款仍是 Free", "paid-but-still-free"],
    ["ChatGPT付款失败怎么办", "chatgpt-payment-errors"],
    ["Your credit card was declined.", "chatgpt-payment-errors"],
    ["Your card has been declined", "chatgpt-payment-errors"],
    ["We were unable to authenticate your payment method", "chatgpt-payment-errors"],
    ["Ｕｓｅｒ　ＩＤ", "user-id"]
  ];
  for (const [query, expected] of cases) {
    page.search(query);
    assert.ok(page.urls().some(url => url.includes(expected)), query + " must find " + expected);
    assert.equal(page.nodes.discovery.hidden, true);
    console.log(query + " -> " + page.urls().length + " results; first: " + page.urls()[0]);
  }
  page.search("grok 403");
  assert.ok(!page.urls()[0].includes("/en/"), "Chinese should lead comparable matches");
  assert.ok(page.urls().some(url => url.includes("/en/")), "English matches must remain accessible");
  page.search("Gemini 家庭组");
  const familyTopics = page.urls();
  assert.ok(familyTopics.some(url => url.includes("gemini-own-account-upgrade")));
  assert.ok(familyTopics.length < items.filter(item => item.product === "Gemini").length, "A topic query must not return every Gemini page");
  for (const query of [
    "Gemini 加入家庭组", "Gemini 家庭组无法加入", "Gemini 家庭组不能加入",
    "请问 Gemini 家庭组为什么没法加入", "我想加入 Gemini 家庭组怎么办"
  ]) {
    page.search(query);
    assert.deepEqual([...page.urls()].sort(), [...familyTopics].sort(), query + " must preserve the family-group topic");
    assert.match(page.nodes.status.textContent, /未找到完全匹配/);
    assert.equal(page.savedUrl().searchParams.get("q"), query, "Keep the user's original question in the URL");
    console.log(query + " -> " + page.urls().length + " related results");
  }
  for (const query of ["Gemini 无法加入", "无法加入", "Gemini Pro 不能加入", "Gemini 家庭组无法加入 火星求职"]) {
    page.search(query);
    assert.equal(page.urls().length, 0, query + " must not relax away the product or unknown topic");
    assert.match(page.nodes.status.textContent, /没有找到/);
  }
  page.search("量子土豆不存在 abcxyzqwerty987");
  assert.equal(page.urls().length, 0);
  assert.equal(page.nodes.discovery.hidden, false);
  assert.match(page.nodes.status.textContent, /没有找到/);
  page.search("the is and");
  assert.equal(page.urls().length, 0, "Stop words alone must not return the entire index");
  page.search("");
  assert.equal(page.urls().length, 0);
  assert.equal(page.savedUrl().searchParams.has("q"), false);

  const fixtures = [
    { title: "Grok 403", product: "Grok", keywords: "403", description: "", url: "/exact/" },
    { title: "Grok Build 403 排查", product: "Grok", keywords: "grok 403", description: "", url: "/words/" },
    { title: "English uniquephrase", product: "Grok", keywords: "", description: "", url: "/en/only/" },
    { title: "Google", product: "Gemini", keywords: "", description: "", url: "/google/" },
    { title: "<img src=x onerror=alert(1)>", product: "safe", keywords: "markup", description: "<script>evil</script>", url: "/safe/" }
  ];
  const controlled = await browser(fixtures);
  controlled.search("grok 403");
  assert.equal(controlled.urls()[0], "/exact/", "Exact title must outrank scattered word matches");
  controlled.search("uniquephrase");
  assert.deepEqual(controlled.urls(), ["/en/only/"]);
  assert.match(controlled.nodes.status.textContent, /英文/);
  controlled.search("go");
  assert.equal(controlled.urls().length, 0, "Go must not match Google as a substring");
  controlled.search("markup");
  const rendered = controlled.nodes.results.children[0];
  assert.equal(rendered.children[1].children[0].children[0].textContent, fixtures[4].title);
  assert.equal(rendered.children[2].children[0].textContent, fixtures[4].description);

  const familyFixtures = [
    { title: "Gemini 家庭组", product: "Gemini", keywords: "家庭组", description: "资格核对", url: "/gemini/family/" },
    { title: "Grok 家庭组无法加入", product: "Grok", keywords: "家庭组", description: "", url: "/grok/family/" },
    { title: "Gemini Pro", product: "Gemini", keywords: "套餐", description: "", url: "/gemini/plan/" }
  ];
  const topicPage = await browser(familyFixtures);
  topicPage.search("Gemini 家庭组无法加入");
  assert.deepEqual(topicPage.urls(), ["/gemini/family/"], "Related search must retain the explicit product and topic");
  const exactFamily = await browser([
    ...familyFixtures,
    { title: "Gemini 家庭组无法加入", product: "Gemini", keywords: "", description: "", url: "/gemini/exact/" }
  ]);
  exactFamily.search("Gemini 家庭组无法加入");
  assert.deepEqual(exactFamily.urls(), ["/gemini/exact/"], "Do not introduce relaxed results when an exact answer exists");
  assert.doesNotMatch(exactFamily.nodes.status.textContent, /未找到完全匹配/);

  for (const options of [{ failed: true }, { httpError: true }, { invalid: true }]) {
    const broken = await browser(items, { ...options, query: "grok" });
    assert.match(broken.nodes.status.textContent, /暂时不可用/);
    assert.equal(broken.nodes.discovery.hidden, false);
    broken.search("chatgpt");
    assert.match(broken.nodes.status.textContent, /暂时不可用/);
    assert.equal(broken.urls().length, 0);
  }
  const loading = await browser(items, { pending: true });
  loading.search("grok");
  assert.match(loading.nodes.status.textContent, /正在载入/);
  assert.equal(loading.nodes.discovery.hidden, false);
  const fallback = await browser(items, { noSegmenter: true });
  for (const query of ["Grok Bot 额度", "grok 403", "已扣款仍是 Free", "Gemini 加入家庭组", "Gemini 家庭组无法加入", "我想加入 Gemini 家庭组怎么办"]) {
    fallback.search(query);
    assert.ok(fallback.urls().length > 0, query + " must work without Intl.Segmenter");
  }
  console.log("PASS: real index queries, conservative natural-question fallback, product/topic constraints, exact-match priority, language retention, no matches, empty input, safe text rendering, loading and three failure modes; " + items.length + " index entries.");
}

main().catch(error => { console.error(error); process.exitCode = 1; });
