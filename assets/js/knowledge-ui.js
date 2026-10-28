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
  // Hero, tables and the reading rail are emitted by the static template.
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
  const links = Array.from(list.querySelectorAll('a'));
  if (links.length !== headings.length) return;
  toc.open = !mobile.matches;
  toc.dataset.tocReady = 'true';
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
  // Keep deep links aligned after the mobile directory adopts its compact state.
  if (location.hash) {
    try {
      const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (target) requestAnimationFrame(() => target.scrollIntoView());
    } catch (_) { /* Malformed fragments do not prevent reading. */ }
  }
})();
