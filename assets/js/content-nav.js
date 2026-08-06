(() => {
  const article = document.querySelector('[data-article-content]');
  const toc = document.querySelector('[data-page-toc]');
  const list = document.querySelector('[data-toc-list]');
  if (!article || !toc || !list) return;

  const headings = Array.from(article.children).filter((element) => element.matches('h2'));
  if (headings.length < 2) return;

  const usedIds = new Set();
  const createId = (heading, index) => {
    const existing = heading.id.trim();
    if (existing && !usedIds.has(existing)) return existing;
    const plain = heading.textContent
      .trim()
      .toLocaleLowerCase()
      .replace(/[^\p{Letter}\p{Number}\s-]/gu, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
    return plain || `section-${index + 1}`;
  };

  const links = headings.map((heading, index) => {
    let id = createId(heading, index);
    let suffix = 2;
    while (usedIds.has(id)) {
      id = `${id}-${suffix}`;
      suffix += 1;
    }
    usedIds.add(id);
    heading.id = id;
    heading.classList.add('anchor-heading');

    const item = document.createElement('li');
    const link = document.createElement('a');
    link.href = `#${encodeURIComponent(id)}`;
    link.textContent = heading.textContent.trim();
    item.appendChild(link);
    list.appendChild(item);
    return link;
  });

  toc.hidden = false;
  const mobile = window.matchMedia('(max-width: 960px)');
  if (mobile.matches) toc.removeAttribute('open');

  const setActive = (id) => {
    links.forEach((link) => {
      const active = decodeURIComponent(link.hash.slice(1)) === id;
      link.toggleAttribute('aria-current', active);
    });
  };

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
      if (visible.length) setActive(visible[0].target.id);
    }, { rootMargin: '-96px 0px -68% 0px', threshold: 0 });
    headings.forEach((heading) => observer.observe(heading));
  }

  links.forEach((link) => {
    link.addEventListener('click', () => {
      if (mobile.matches) toc.removeAttribute('open');
    });
  });
})();
