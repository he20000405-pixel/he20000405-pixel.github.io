(function () {
  "use strict";

  var form = document.querySelector("[data-search-form]");
  var input = document.querySelector("[data-search-input]");
  var results = document.querySelector("[data-search-results]");
  var status = document.querySelector("[data-search-status]");
  var discovery = document.querySelector("[data-search-discovery]");
  if (!form || !input || !results || !status) return;

  var index = [];
  var indexState = "loading";
  var segmenter = typeof Intl.Segmenter === "function"
    ? new Intl.Segmenter("zh-CN", { granularity: "word" }) : null;
  var stopWords = new Set([
    "的", "了", "是", "已", "还", "仍", "仍是", "还是", "仍然", "我", "我的", "请问", "怎么", "怎么办", "如何", "为什么", "有", "在", "与", "和",
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "to", "of", "for", "with", "and", "or", "i", "my", "you", "your", "this", "that", "how", "do", "does"
  ]);
  var params = new URLSearchParams(window.location.search);
  var initialQuery = params.get("q") || "";
  input.value = initialQuery;

  function normalize(value) {
    return String(value || "").normalize("NFKC").toLocaleLowerCase("zh-CN")
      .replace(/[^\p{L}\p{N}]+/gu, " ").trim();
  }

  function queryTerms(query) {
    // Remove conversational phrases before segmentation; keep error and product terms.
    var text = query.replace(/怎么办|为什么|请问|如何|仍然是|仍是|还是/g, " ");
    var parts = segmenter ? Array.from(segmenter.segment(text), function (part) { return part.segment; })
      : (text.match(/[a-z0-9]+|[\u3400-\u9fff]+/g) || []);
    var terms = [];
    var chineseLetters = "";
    function flush() {
      if (chineseLetters) terms.push(chineseLetters);
      chineseLetters = "";
    }
    parts.forEach(function (part) {
      if (stopWords.has(part)) { flush(); return; }
      // Some browser dictionaries split terms such as 扣款 or 额度 into single characters.
      if (/^[\u3400-\u9fff]$/.test(part)) { chineseLetters += part; return; }
      flush();
      if (/^[\p{L}\p{N}]+$/u.test(part)) terms.push(part);
    });
    flush();
    return Array.from(new Set(terms));
  }

  function containsTerm(text, term) {
    if (/^[a-z0-9]+$/.test(term)) {
      return new RegExp("(^|[^a-z0-9])" + term + "($|[^a-z0-9])").test(text);
    }
    return text.includes(term);
  }

  function score(item, query, terms) {
    var title = normalize(item.title);
    var product = normalize(item.product);
    var keywords = normalize(item.keywords);
    var description = normalize(item.description);
    var haystack = [title, product, keywords, description].join(" ");
    if (!query || !terms.length) return -1;
    if (!terms.every(function (term) { return containsTerm(haystack, term); })) return -1;
    if (title === query) return 1000;
    if (title.startsWith(query)) return 800;
    if (title.includes(query)) return 600;
    if (haystack.includes(query)) return 500;
    return Math.min(199, terms.reduce(function (total, term) {
      return total + (containsTerm(title, term) ? 10 : 0)
        + (containsTerm(keywords, term) ? 8 : 0)
        + (containsTerm(product, term) ? 6 : 0)
        + (containsTerm(description, term) ? 4 : 0);
    }, 0));
  }

  function appendText(element, text) {
    element.appendChild(document.createTextNode(text));
  }

  function render(items, query) {
    results.replaceChildren();
    if (discovery) discovery.hidden = Boolean(query && items.length);
    if (!query) {
      status.textContent = "输入产品、报错或订阅状态关键词，例如：Free、续费、User ID、session。";
      return;
    }
    if (!items.length) {
      status.textContent = "没有找到匹配专题。请尝试更短的关键词。";
      return;
    }
    var onlyEnglish = items.every(function (item) { return /\/en\//.test(item.url); });
    status.textContent = onlyEnglish
      ? "未找到匹配的中文专题，以下是 " + items.length + " 个相关英文专题。"
      : "找到 " + items.length + " 个相关专题。";
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
    if (updateUrl) {
      var url = new URL(window.location.href);
      if (query) url.searchParams.set("q", input.value.trim());
      else url.searchParams.delete("q");
      window.history.replaceState({}, "", url);
    }
    if (indexState !== "ready") {
      results.replaceChildren();
      if (discovery) discovery.hidden = false;
      status.textContent = indexState === "failed"
        ? "搜索索引暂时不可用，请从下方进入产品知识库。"
        : "正在载入搜索索引，请稍候。";
      return;
    }
    var terms = queryTerms(query);
    var matches = index
      .map(function (item) { return { item: item, score: score(item, query, terms) }; })
      .filter(function (entry) { return entry.score >= 0; })
      .sort(function (a, b) {
        // Exact phrases outrank separated words. Within the same match tier, show Chinese first.
        return Math.floor(b.score / 200) - Math.floor(a.score / 200)
          || Number(/\/en\//.test(a.item.url)) - Number(/\/en\//.test(b.item.url))
          || b.score - a.score || a.item.title.localeCompare(b.item.title, "zh-CN");
      })
      .map(function (entry) { return entry.item; });
    render(matches, query);
  }

  fetch("/search-index.json", { credentials: "same-origin" })
    .then(function (response) {
      if (!response.ok) throw new Error("Search index unavailable");
      return response.json();
    })
    .then(function (data) {
      if (!Array.isArray(data)) throw new Error("Invalid search index");
      index = data;
      indexState = "ready";
      runSearch(false);
    })
    .catch(function () {
      indexState = "failed";
      runSearch(false);
    });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    runSearch(true);
  });
})();
