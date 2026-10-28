/* Progressive presentation only: original article content remains in the HTML. */
(() => {
  'use strict';
  const body = document.body;
  const english = document.documentElement.lang.startsWith('en');
  const mobile = window.matchMedia('(max-width: 900px)');
  const nav = document.querySelector('.site-nav');
  const toggle = document.querySelector('.nav-toggle');
  body.classList.add('js-ready');

  if (nav && toggle) {
    const setMenu = (open) => {
      nav.toggleAttribute('data-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', english ? (open ? 'Close navigation' : 'Open navigation') : (open ? '关闭主导航' : '打开主导航'));
    };
    toggle.addEventListener('click', () => setMenu(!nav.hasAttribute('data-open')));
    nav.addEventListener('click', (event) => { if (event.target.closest('a')) setMenu(false); });
    document.addEventListener('click', (event) => {
      if (!nav.contains(event.target) && !toggle.contains(event.target)) setMenu(false);
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && nav.hasAttribute('data-open')) { setMenu(false); toggle.focus(); }
    });
    mobile.addEventListener('change', () => setMenu(false));
  }

  const article = document.querySelector('[data-article-content]');
  const hero = document.querySelector('[data-page-hero]');
  if (!article || !hero) return;
  const kind = body.dataset.pageKind || 'article';
  const site = body.dataset.site || 'portal';
  body.classList.add(kind);
  const h1 = article.querySelector('h1');
  const productHero = article.querySelector(':scope > .product-hero');
  if (kind === 'landing' && productHero) {
    hero.append(productHero);
  } else if (kind === 'article') {
    const eyebrow = article.querySelector(':scope > .eyebrow, .resource-hero .eyebrow, .lab-hero .eyebrow');
    if (eyebrow) hero.append(eyebrow);
    if (h1) hero.append(h1);
  } else {
    for (const node of Array.from(article.childNodes)) {
      if (node.nodeType !== Node.ELEMENT_NODE || ['H1', 'P'].includes(node.tagName)) hero.append(node);
      else break;
    }
  }
  hero.hidden = !hero.textContent.trim();

  const labels = { chatgpt: 'OpenAI / ChatGPT', grok: 'xAI / Grok', claude: 'Anthropic / Claude', gemini: 'Google / Gemini' };
  const script = document.querySelector('script[src*="/assets/js/knowledge-ui.js"]');
  if (labels[site] && script) {
    const brand = document.createElement('div');
    brand.className = 'hero-brand';
    const symbol = document.createElement('span');
    symbol.className = 'product-symbol';
    const img = document.createElement('img');
    img.src = new URL('../images/brands/' + site + '.svg', script.src).href;
    img.alt = '';
    img.width = 36;
    img.height = 36;
    symbol.append(img);
    const label = document.createElement('span');
    label.textContent = labels[site];
    brand.append(symbol, label);
    hero.prepend(brand);
  }

  // Keep long headings readable without rewriting their words.
  if (kind === 'landing' && site === 'chatgpt' && h1 && h1.textContent.includes(' 国内')) {
    const text = h1.textContent;
    const split = text.indexOf('国内');
    const first = document.createElement('span');
    const second = document.createElement('span');
    first.className = second.className = 'title-line';
    first.textContent = text.slice(0, split);
    second.textContent = text.slice(split);
    h1.replaceChildren(first, second);
  }

  if (kind === 'landing' && !article.querySelector('.product-search') && !hero.querySelector('.product-search')) {
    const form = document.createElement('form');
    form.className = 'product-search added-search';
    form.action = body.dataset.searchUrl || 'https://he20000405-pixel.github.io/search/';
    form.method = 'get';
    form.setAttribute('role', 'search');
    const label = document.createElement('label');
    label.htmlFor = 'product-search-extra';
    label.textContent = english ? 'Search all product guides' : '搜索 ChatGPT、Grok、Claude、Gemini 知识库';
    const control = document.createElement('div');
    control.className = 'search-control';
    const input = document.createElement('input');
    input.id = 'product-search-extra'; input.name = 'q'; input.type = 'search';
    input.placeholder = english ? 'For example: payment failed, still Free' : '例如：付款失败、仍显示 Free';
    const button = document.createElement('button');
    button.type = 'submit'; button.textContent = english ? 'Search' : '搜索';
    control.append(input, button); form.append(label, control); hero.append(form);
  }

  article.querySelectorAll('table').forEach((table) => {
    if (table.parentElement.classList.contains('table-scroll')) return;
    const wrapper = document.createElement('div');
    wrapper.className = 'table-scroll'; wrapper.tabIndex = 0;
    wrapper.setAttribute('role', 'region');
    wrapper.setAttribute('aria-label', english ? 'Scrollable comparison table' : '可横向滚动的对照表');
    table.before(wrapper); wrapper.append(table);
  });
  article.querySelectorAll('.faq-section details, .faq-list details').forEach((details) => {
    details.open = true;
  });
  article.querySelectorAll('.guide-grid').forEach((grid) => {
    const cards = Array.from(grid.querySelectorAll(':scope > .guide-card'));
    if (cards.length === 7) {
      grid.classList.add('seven-grid');
      cards.slice(3).forEach((card) => card.classList.add('seven-bottom'));
    }
  });
  article.querySelectorAll('.intent-grid').forEach((grid) => {
    if (grid.children.length === 4) grid.classList.add('four-intents');
    if (grid.children.length === 5) grid.classList.add('five-intents');
  });
  article.querySelectorAll('.directory-grid').forEach((grid) => {
    if (grid.children.length !== 5) return;
    const card = grid.lastElementChild;
    card.classList.add('resource-wide');
    const left = document.createElement('div'); const right = document.createElement('div');
    Array.from(card.children).forEach((child, i) => (i < 3 ? left : right).append(child));
    card.append(left, right);
  });

  const rail = document.querySelector('[data-reading-rail]');
  const toc = document.querySelector('[data-page-toc]');
  const list = document.querySelector('[data-toc-list]');
  if (kind !== 'article' || !rail || !toc || !list) return;
  const headings = Array.from(article.querySelectorAll('h2'));
  if (headings.length < 2) return;
  const usedIds = new Set(Array.from(document.querySelectorAll('[id]')).map((element) => element.id));
  const links = headings.map((heading, index) => {
    if (!heading.id) {
      let id = 'section-' + (index + 1);
      while (usedIds.has(id)) id += '-2';
      heading.id = id; usedIds.add(id);
    }
    const item = document.createElement('li'); const link = document.createElement('a');
    link.href = '#' + encodeURIComponent(heading.id); link.textContent = heading.textContent.trim();
    item.append(link); list.append(item);
    return link;
  });
  rail.hidden = false; toc.hidden = false; toc.open = !mobile.matches;
  document.querySelector('.content-layout').classList.add('reading-layout');
  article.querySelectorAll('.resource-preview, .lab-preview').forEach((figure) => {
    figure.classList.add('rail-preview'); rail.append(figure);
  });
  const activate = (id) => links.forEach((link) => {
    const active = decodeURIComponent(link.hash.slice(1)) === id;
    link.parentElement.classList.toggle('is-active', active);
    if (active) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current');
  });
  activate(headings[0].id);
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
      if (visible.length) activate(visible[0].target.id);
    }, { rootMargin: '-10% 0px -75% 0px' });
    headings.forEach((heading) => observer.observe(heading));
  }
  links.forEach((link) => link.addEventListener('click', () => {
    activate(decodeURIComponent(link.hash.slice(1)));
    if (mobile.matches) toc.open = false;
  }));
  mobile.addEventListener('change', () => { toc.open = !mobile.matches; });
  // Moving the original heading must not break existing deep links.
  if (location.hash) {
    try {
      const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (target) requestAnimationFrame(() => target.scrollIntoView());
    } catch (_) { /* Malformed fragments do not prevent reading. */ }
  }
})();
