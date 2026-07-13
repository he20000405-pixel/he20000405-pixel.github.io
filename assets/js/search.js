(function () {
  "use strict";

  var form = document.querySelector("[data-search-form]");
  var input = document.querySelector("[data-search-input]");
  var results = document.querySelector("[data-search-results]");
  var status = document.querySelector("[data-search-status]");
  if (!form || !input || !results || !status) return;

  var index = [];
  var params = new URLSearchParams(window.location.search);
  var initialQuery = params.get("q") || "";
  input.value = initialQuery;

  function normalize(value) {
    return String(value || "").toLocaleLowerCase("zh-CN").replace(/\s+/g, " ").trim();
  }

  function score(item, query) {
    var title = normalize(item.title);
    var product = normalize(item.product);
    var haystack = normalize([item.title, item.description, item.keywords, item.product].join(" "));
    if (!haystack.includes(query)) return -1;
    if (title === query) return 100;
    if (title.startsWith(query)) return 80;
    if (title.includes(query)) return 60;
    if (product.includes(query)) return 40;
    return 20;
  }

  function appendText(element, text) {
    element.appendChild(document.createTextNode(text));
  }

  function render(items, query) {
    results.replaceChildren();
    if (!query) {
      status.textContent = "输入产品、报错或订阅状态关键词，例如：Free、续费、User ID、session。";
      return;
    }
    if (!items.length) {
      status.textContent = "没有找到匹配专题。请尝试更短的关键词。";
      return;
    }
    status.textContent = "找到 " + items.length + " 个相关专题。";
    items.forEach(function (item) {
      var article = document.createElement("article");
      article.className = "search-result";
      var product = document.createElement("div");
      product.className = "result-product";
      appendText(product, item.product);
      var heading = document.createElement("h2");
      var link = document.createElement("a");
      link.href = item.url;
      appendText(link, item.title);
      heading.appendChild(link);
      var description = document.createElement("p");
      appendText(description, item.description);
      article.append(product, heading, description);
      results.appendChild(article);
    });
  }

  function runSearch(updateUrl) {
    var query = normalize(input.value);
    var matches = index
      .map(function (item) { return { item: item, score: score(item, query) }; })
      .filter(function (entry) { return entry.score >= 0; })
      .sort(function (a, b) { return b.score - a.score || a.item.title.localeCompare(b.item.title, "zh-CN"); })
      .map(function (entry) { return entry.item; });
    render(matches, query);
    if (updateUrl) {
      var url = new URL(window.location.href);
      if (query) url.searchParams.set("q", input.value.trim());
      else url.searchParams.delete("q");
      window.history.replaceState({}, "", url);
    }
  }

  fetch("/search-index.json", { credentials: "same-origin" })
    .then(function (response) {
      if (!response.ok) throw new Error("Search index unavailable");
      return response.json();
    })
    .then(function (data) {
      index = Array.isArray(data) ? data : [];
      runSearch(false);
    })
    .catch(function () {
      status.textContent = "搜索索引暂时不可用，请从首页进入产品知识库。";
    });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    runSearch(true);
  });
})();
