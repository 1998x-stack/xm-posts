/* Search is local-only; article data stays in the DOM. No analytics or network calls. */
(() => {
  const input = document.querySelector('[data-search-input]');
  const cards = [...document.querySelectorAll('[data-post-card]')];
  if (!input || !cards.length) return;
  const visibleCount = document.querySelector('[data-visible-count]');
  const empty = document.querySelector('[data-no-results]');
  const normalized = s => s.normalize('NFKC').trim().toLocaleLowerCase();
  const filter = () => {
    const terms = normalized(input.value).split(/\s+/).filter(Boolean);
    let shown = 0;
    for (const card of cards) {
      const haystack = normalized(card.dataset.search || '');
      const match = terms.every(term => haystack.includes(term));
      card.hidden = !match;
      if (match) shown++;
    }
    if (visibleCount) visibleCount.textContent = `找到 ${shown} 篇文章`;
    if (empty) empty.hidden = shown !== 0;
  };
  input.addEventListener('input', filter);
  filter();
})();
