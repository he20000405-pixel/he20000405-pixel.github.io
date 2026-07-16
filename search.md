---
title: "搜索 ChatGPT、Grok、Claude 与 Gemini 订阅指南"
description: "搜索 ChongGrok 四套知识库和跨产品资源中的订阅流程、付款失败、Free 状态、续费、User ID、session 与权益排障专题。"
permalink: /search/
last_modified_at: 2026-07-16
---

<p class="eyebrow">Search</p>
# 搜索知识库

<p class="lead">输入产品、报错提示或订阅状态关键词，结果会直接打开对应的 ChatGPT、Grok、Claude、Gemini 专题或跨产品决策树。</p>

<section class="search-panel" aria-label="知识库搜索">
  <form class="search-form" action="{{ '/search/' | relative_url }}" method="get" data-search-form>
    <label class="sr-only" for="guide-search">搜索关键词</label>
    <input id="guide-search" name="q" type="search" autocomplete="off" placeholder="例如：已扣款、Free、续费、User ID、session、权益未生效" data-search-input>
    <button type="submit">搜索</button>
  </form>
  <p class="search-status" aria-live="polite" data-search-status>正在载入搜索索引。</p>
</section>

<div class="search-results" data-search-results></div>

<noscript>
  <p class="notice">当前浏览器未启用 JavaScript。请直接进入 <a href="{{ site.chatgpt_guide_url }}">ChatGPT 指南</a>、<a href="{{ site.grok_guide_url }}">Grok 指南</a>、<a href="{{ site.claude_guide_url }}">Claude 指南</a>或 <a href="{{ site.gemini_guide_url }}">Gemini 指南</a>。</p>
</noscript>

<script src="{{ '/assets/js/search.js' | relative_url }}" defer></script>
