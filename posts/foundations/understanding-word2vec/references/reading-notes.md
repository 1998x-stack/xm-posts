# Word2Vec Paper Review — Source / claim map

## Primary literature

1. T. Mikolov, K. Chen, G. Corrado, J. Dean. **Efficient Estimation of Word Representations in Vector Space** (2013), https://arxiv.org/abs/1301.3781
   - Sec. 3: CBOW, Skip-gram model, computational cost.
   - Sec. 4: task-specific quality and efficiency comparisons, training settings.
   - Sec. 5: selected lexical relationships / analogical reasoning.
2. T. Mikolov, I. Sutskever, K. Chen, G. Corrado, J. Dean. **Distributed Representations of Words and Phrases and their Compositionality**, NeurIPS 2013, https://proceedings.neurips.cc/paper/2013/hash/9aa42b31882ec039965f3c4923ce901b-Abstract.html
   - Sec. 2.1: hierarchical softmax; Sec. 2.2: negative sampling and f^3/4; Sec. 2.3: subsampling; Sec. 3: evaluation; Sec. 4: phrase representation.
3. **Original word2vec.c source** https://github.com/tmikolov/word2vec/blob/master/word2vec.c
   - `TrainModelThread` branch for `cbow` vs. `skip-gram`, `syn0`, `syn1neg`, sigmoid lookup table and dynamic window.

## Pedagogical architecture references (NOT copied)

- https://colah.github.io/posts/2015-08-Understanding-LSTMs/
- https://nlp.seas.harvard.edu/annotated-transformer/

## Claim status

| Claim | Kind | Limitation |
|---|---|---|
| Context prediction can learn useful embeddings | Primary papers | Depends on data, hyperparameters, evaluation |
| Full softmax per-pair output cost is O(V·D) | Derivation | Excludes other overhead; hierarchical softmax is another alternative |
| SGNS per-pair output cost is O((k+1)·D) | Derivation | Does not imply a calibrated full-vocabulary distribution |
| Sampling noise distribution p(w) proportional to f(w)^0.75 | Paper 2 Sec 2.2 | Empirical result from the published experiment |
| Word-analogy geometry can emerge | Paper 1 Sec 5 | Not universal, especially for rare/polysemous words |
| 2D visualizations and slider scores | Synthetic teaching aids | NOT the paper’s experimental data |
| Tiny NumPy code | Independent educational implementation | NOT a reproduction of the original published benchmark |

## Implementation notes and caution

SGNS uses distinct input vectors `V` and output/context vectors `U`. On a positive pair (c, o) with negatives n_i, minimize `softplus(-U[o]·V[c]) + sum_i softplus(U[n_i]·V[c])`. The derivative w.r.t. V[c] is `(sigmoid(s_pos)-1)*U[o] + sum_i sigmoid(s_neg_i)*U[n_i]`. Negative indices can repeat, so atomic scatter-add semantics matter in an implementation.

Original C word2vec's sub-sampling check uses `ran=(sqrt(f/t)+1)*t/f` as a keep threshold; the paper's smooth schematic is `1-sqrt(t/f)` for discard probability. They are not pointwise equivalent.

Word2Vec was not the first concept of distributed word representations, and SGNS is not full softmax with a subset of probabilities retained. The article separates the architecture (CBOW/Skip-gram), learning objective (NEG versus hierarchical softmax), implementation detail (dynamic window), and observed empirical results.
