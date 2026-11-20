# Quality assurance record

## Provenance

- **Primary sources:** arXiv 1301.3781, NeurIPS 2013 Word2Vec follow-up, original `tmikolov/word2vec` C implementation.
- **No borrowed illustrations:** HTML SVG and external SVG assets are redrawn, not copied from source papers/blogs.
- **Synthetic illustrations:** 2D word clusters, analogy geometric arrangement, loss slider dot products, frequency bars are **teaching examples**, not original experiment measurements.

## Automated checks — passed

1. `python -m unittest discover -s tests -v`: **4/4** passed.
   - Finite-difference check for center / positive / negative vector gradients.
   - Fixed-window pairs do not cross sentence boundaries.
   - Noise samples reject the positive target.
   - Average training loss decreased on the fixed tiny corpus.
2. `python code/train_sgns.py --epochs 12 --seed 7`: executed, mean loss **2.76956 → 2.34017** on tiny corpus. This does **not** reproduce published experimental results.
3. Browser (Chromium / Playwright, `set_content` due sandbox navigation restrictions): **passed**.
   - Desktop 1440×900 and mobile 390×844 captured.
   - No JavaScript runtime errors.
   - Center-word clicks, CBOW switch, loss slider, noise-distribution switch tested.
   - Mobile document scroll width and viewport client width both 390px.
4. Static HTML audit: all internal anchor links exist, 12 article sections, 5 inline SVG elements; independent SVG assets available.

## Limitations

- No reproducibility claim regarding Word2Vec's original datasets, throughput or published analogy accuracies.
- This is a tiny NumPy SGNS model, not the complete word2vec C implementation.
- Original source code and papers are **linked**, not bundled.
- Browser captured through in-memory `set_content` because sandbox blocks file:// and localhost navigation; on-the-wire serving and GitHub Pages deployment were not tested.
