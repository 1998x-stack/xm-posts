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

  const input = document.querySelector('[data-search-input]');
  const cards = [...document.querySelectorAll('[data-post-card]')];
  if (!input || !cards.length) return;

  const select = document.querySelector('[data-category-filter]');
  const visibleCount = document.querySelector('[data-visible-count]');
  const empty = document.querySelector('[data-no-results]');
  const more = document.querySelector('[data-load-more]');
  const pageSize = 8;
  let limit = pageSize;
  const normalized = s => String(s || '').normalize('NFKC').trim().toLocaleLowerCase();

  function render() {
    const terms = normalized(input.value).split(/\s+/).filter(Boolean);
    const category = select ? select.value : '';
    const matching = cards.filter(card => {
      const content = normalized(card.dataset.search);
      return (!category || card.dataset.category === category) && terms.every(term => content.includes(term));
    });
    const shown = matching.slice(0, limit);
    const visible = new Set(shown);
    for (const card of cards) card.hidden = !visible.has(card);
    if (visibleCount) visibleCount.textContent = '显示 ' + shown.length + ' / ' + matching.length + ' 篇（全库 ' + cards.length + ' 篇）';
    if (empty) empty.hidden = matching.length !== 0;
    if (more) more.hidden = matching.length <= limit;
  }

  input.addEventListener('input', () => { limit = pageSize; render(); });
  if (select) select.addEventListener('change', () => { limit = pageSize; render(); });
  if (more) more.addEventListener('click', () => {
    limit += pageSize;
    render();
  });
  render();
})();
