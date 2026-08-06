---
title: "AI 会员订阅指南搜索"
description: "搜索 ChongGrok 四套知识库和跨产品资源中的订阅流程、付款失败、Free 状态、续费、User ID、session 与权益排障专题。"
permalink: /search/
last_modified_at: 2026-07-21
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
  <div class="search-suggestions" aria-label="热门搜索">
    <a href="{{ '/search/?q=已扣款' | relative_url }}">已扣款</a>
    <a href="{{ '/search/?q=Free' | relative_url }}">仍显示 Free</a>
    <a href="{{ '/search/?q=续费' | relative_url }}">续费失败</a>
    <a href="{{ '/search/?q=User%20ID' | relative_url }}">User ID</a>
    <a href="{{ '/search/?q=session' | relative_url }}">session</a>
    <a href="{{ '/search/?q=Google%20Play' | relative_url }}">Google Play</a>
  </div>
</section>

<div class="search-results" data-search-results></div>

<nav class="search-discovery" aria-label="按产品浏览" data-search-discovery>
  <a href="{{ site.chatgpt_guide_url }}">ChatGPT 指南<span>Plus、Pro、付款与账号状态</span></a>
  <a href="{{ site.grok_guide_url }}">Grok 指南<span>SuperGrok、User ID 与 Grok Build</span></a>
  <a href="{{ site.claude_guide_url }}">Claude 指南<span>Pro、Max、User ID 与 Claude Code</span></a>
  <a href="{{ site.gemini_guide_url }}">Gemini 指南<span>Google AI 套餐、付款与权益验收</span></a>
</nav>

<noscript>
  <p class="notice">当前浏览器未启用 JavaScript。请直接进入 <a href="{{ site.chatgpt_guide_url }}">ChatGPT 指南</a>、<a href="{{ site.grok_guide_url }}">Grok 指南</a>、<a href="{{ site.claude_guide_url }}">Claude 指南</a>或 <a href="{{ site.gemini_guide_url }}">Gemini 指南</a>。</p>
</noscript>

<script src="{{ '/assets/js/search.js' | relative_url }}" defer></script>
