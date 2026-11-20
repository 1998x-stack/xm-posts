/* Local-only search and responsive navigation; no tracking, network or framework. */
(() => {
  const menu = document.querySelector('[data-menu-toggle]');
  const nav = document.getElementById('site-nav');
  if (menu && nav) {
    const close = () => {
      menu.setAttribute('aria-expanded', 'false');
      nav.classList.remove('is-open');
    };
    menu.addEventListener('click', () => {
      const open = menu.getAttribute('aria-expanded') !== 'true';
      menu.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
    });
    nav.addEventListener('click', event => {
      if (event.target.closest('a')) close();
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && nav.classList.contains('is-open')) {
        close();
        menu.focus();
      }
    });
  }

  // Only one index page is attached to the DOM at a time. The full catalogue
  // is a small JSON manifest; thumbnails for other pages are never created.
  const input = document.querySelector('[data-search-input]');
  const grid = document.querySelector('[data-post-grid]');
  if (!input || !grid) return;

  const select = document.querySelector('[data-category-filter]');
  const visibleCount = document.querySelector('[data-visible-count]');
  const empty = document.querySelector('[data-no-results]');
  const pager = document.querySelector('[data-home-pagination]');
  const pageSize = Math.max(1, Number(grid.dataset.pageSize) || 8);
  const initialMarkup = grid.innerHTML;
  const normalized = value => String(value || '').normalize('NFKC').trim().toLocaleLowerCase();
  const args = new URLSearchParams(location.search);
  input.value = args.get('q') || '';
  if (select && [...select.options].some(option => option.value === args.get('category'))) {
    select.value = args.get('category');
  }
  let page = Math.max(1, Number.parseInt(args.get('page'), 10) || 1);
  let catalogue = null;
  let pending = null;

  function element(tag, cls, value) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (value !== undefined) node.textContent = String(value);
    return node;
  }

  function link(label, href, cls) {
    const node = element('a', cls, label);
    node.href = href;
    return node;
  }

  function buildCard(post, index) {
    const card = element('article', 'index-card post-card');
    card.setAttribute('data-post-card', '');
    card.dataset.category = post.category;
    card.dataset.search = normalized([
      post.title, post.subtitle, post.summary, post.category, post.category_title,
      post.topic, post.topic_title, ...(post.tags || [])
    ].join(' '));

    card.append(element('span', 'index-order', String(index + 1).padStart(2, '0')));
    const imageLink = link('', post.url, 'index-image-link');
    imageLink.setAttribute('aria-label', '阅读 ' + post.title);
    const image = element('img', 'article-cover-thumb');
    image.src = post.cover_src;
    image.alt = '';
    image.loading = 'lazy';
    image.decoding = 'async';
    imageLink.append(image);
    card.append(imageLink);

    const main = element('div', 'index-main');
    const kicker = element('div', 'index-kicker');
    kicker.append(document.createTextNode(post.category_title + ' '));
    kicker.append(element('span', '', '/'));
    kicker.append(document.createTextNode(' ' + post.topic_title));
    main.append(kicker);
    const heading = element('h3');
    heading.append(link(post.title, post.url));
    main.append(heading, element('p', '', post.subtitle));
    const tags = element('div', 'index-tags');
    tags.append(element('span', '', post.reading_minutes + ' 分钟'));
    tags.append(element('span', '', post.published));
    if (post.paper) {
      const paper = link('原始论文 ↗', post.paper, 'paper-source');
      paper.target = '_blank';
      paper.rel = 'noopener noreferrer';
      paper.setAttribute('aria-label', '原始论文：' + post.title);
      tags.append(paper);
    }
    main.append(tags);
    card.append(main);
    const arrow = link('↗', post.url, 'index-arrow');
    arrow.setAttribute('aria-label', '阅读 ' + post.title);
    card.append(arrow);
    return card;
  }

  function writeLocation(push) {
    if (location.protocol !== 'http:' && location.protocol !== 'https:') return;
    const url = new URL(location.href);
    if (input.value.trim()) url.searchParams.set('q', input.value.trim());
    else url.searchParams.delete('q');
    if (select && select.value) url.searchParams.set('category', select.value);
    else url.searchParams.delete('category');
    if (page > 1) url.searchParams.set('page', String(page));
    else url.searchParams.delete('page');
    history[push ? 'pushState' : 'replaceState']({}, '', url);
  }

  function renderPager(totalPages) {
    if (!pager) return;
    pager.replaceChildren();
    pager.hidden = totalPages <= 1;
    if (totalPages <= 1) return;
    const addButton = (text, target, cls, disabled, current) => {
      const button = element('button', cls, text);
      button.type = 'button';
      button.disabled = disabled;
      if (current) button.setAttribute('aria-current', 'page');
      button.setAttribute('aria-label', current ? '当前第 ' + target + ' 页' : '转到第 ' + target + ' 页');
      button.addEventListener('click', () => {
        page = target;
        render();
        writeLocation(true);
        grid.scrollIntoView({block: 'start'});
        const selected = pager.querySelector('[aria-current="page"]');
        if (selected) selected.focus({preventScroll: true});
      });
      pager.append(button);
    };
    addButton('← 上一页', page - 1, 'page-control', page === 1, false);
    const nums = [...new Set([1, 2, page - 1, page, page + 1, totalPages - 1, totalPages])]
      .filter(n => n > 0 && n <= totalPages).sort((a, b) => a - b);
    let last = 0;
    for (const num of nums) {
      if (last && num > last + 1) pager.append(element('span', 'page-ellipsis', '…'));
      addButton(String(num), num, 'page-number' + (num === page ? ' is-current' : ''), false, num === page);
      last = num;
    }
    addButton('下一页 →', page + 1, 'page-control', page === totalPages, false);
  }

  function render() {
    if (!catalogue) return;
    const terms = normalized(input.value).split(/\s+/).filter(Boolean);
    const category = select ? select.value : '';
    const matching = catalogue.filter(post => {
      const text = normalized([
        post.title, post.subtitle, post.summary, post.category, post.category_title,
        post.topic, post.topic_title, ...(post.tags || [])
      ].join(' '));
      return (!category || post.category === category) && terms.every(term => text.includes(term));
    });
    const totalPages = Math.max(1, Math.ceil(matching.length / pageSize));
    page = Math.min(page, totalPages);
    const offset = (page - 1) * pageSize;
    const shown = matching.slice(offset, offset + pageSize);
    grid.replaceChildren(...shown.map((post, i) => buildCard(post, offset + i)));
    if (visibleCount) {
      const first = shown.length ? offset + 1 : 0;
      visibleCount.textContent = '显示 ' + first + '–' + (offset + shown.length) +
        ' / ' + matching.length + ' 篇（全库 ' + catalogue.length + ' 篇）';
    }
    if (empty) empty.hidden = matching.length !== 0;
    renderPager(totalPages);
  }

  function loadIndex() {
    if (!pending) {
      pending = (Array.isArray(window.__XM_INDEX_DATA__)
        ? Promise.resolve(window.__XM_INDEX_DATA__)
        : fetch('posts.json').then(response => {
            if (!response.ok) throw new Error('文章索引加载失败');
            return response.json();
          }))
        .then(posts => {
          if (!Array.isArray(posts)) throw new Error('文章索引格式错误');
          catalogue = posts;
          render();
          return posts;
        }).catch(() => {
          // Static first page and the archive link remain usable offline.
          grid.innerHTML = initialMarkup;
          if (visibleCount) visibleCount.textContent = '索引暂不可用，请前往文章归档';
        });
    }
    return pending;
  }

  input.addEventListener('input', () => {
    page = 1;
    if (catalogue) { render(); writeLocation(false); }
    else loadIndex().then(() => writeLocation(false));
  });
  if (select) select.addEventListener('change', () => {
    page = 1;
    if (catalogue) { render(); writeLocation(false); }
    else loadIndex().then(() => writeLocation(false));
  });
  window.addEventListener('popstate', () => {
    const state = new URLSearchParams(location.search);
    input.value = state.get('q') || '';
    if (select) select.value = state.get('category') || '';
    page = Math.max(1, Number.parseInt(state.get('page'), 10) || 1);
    render();
  });
  loadIndex();
})();
