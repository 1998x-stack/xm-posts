# Collaborative Filtering & Neighborhood Models

**Stable topic:** `recommender-systems/collaborative-filtering`

## Scope

Study preference estimation from other users' or items' observed feedback:

- user-user and item-item neighborhood models;
- co-rated item sets and similarity measures such as Pearson correlation;
- baseline-centered weighted rating prediction;
- explicit ratings, implicit feedback and sparsity;
- cold-start, neighborhood reliability and feedback-selection bias.

## Boundaries

- General-purpose KNN classification/regression remains in `classical-ml/nearest-neighbors`.
- Matrix factorization is a latent-factor family and should be linked as a later development, not described as the same algorithm as neighborhood CF.
- Retrieval/RAG ranks documents against a query; recommendation estimates personalized utility from user history and item interactions.

## Reading order

1. [Understanding GroupLens](../../grouplens/index.html) — 1994 open architecture, user similarity and weighted rating prediction.

This directory is a taxonomy placeholder, not a separately published article.
