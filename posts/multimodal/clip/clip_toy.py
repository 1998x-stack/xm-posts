"""Small, dependency-free CLIP objective demonstrations.

This module illustrates normalized embeddings, the in-batch similarity matrix,
symmetric image-to-text/text-to-image cross entropy, and zero-shot ranking.
It is not a neural network implementation or a reproduction of CLIP training.
"""
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence


Vector = Sequence[float]


def _normalize(vector: Vector) -> list[float]:
    if not vector:
        raise ValueError("vectors must not be empty")
    values = [float(value) for value in vector]
    norm = math.sqrt(sum(value * value for value in values))
    if norm == 0.0:
        raise ValueError("zero vectors cannot be L2-normalized")
    return [value / norm for value in values]


def _dot(left: Vector, right: Vector) -> float:
    if len(left) != len(right):
        raise ValueError("embedding dimensions must match")
    return sum(float(a) * float(b) for a, b in zip(left, right))


def _softmax(logits: Sequence[float]) -> list[float]:
    if not logits:
        raise ValueError("softmax requires at least one logit")
    peak = max(logits)
    exps = [math.exp(value - peak) for value in logits]
    total = sum(exps)
    return [value / total for value in exps]


def similarity_matrix(
    image_features: Sequence[Vector],
    text_features: Sequence[Vector],
    temperature: float = 0.07,
) -> list[list[float]]:
    """Return cosine similarities divided by temperature."""
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    if len(image_features) != len(text_features) or not image_features:
        raise ValueError("image/text batches must have the same non-zero size")
    images = [_normalize(vector) for vector in image_features]
    texts = [_normalize(vector) for vector in text_features]
    if len({len(vector) for vector in images + texts}) != 1:
        raise ValueError("all embedding dimensions must match")
    return [
        [_dot(image, text) / temperature for text in texts]
        for image in images
    ]


def symmetric_contrastive_loss(
    image_features: Sequence[Vector],
    text_features: Sequence[Vector],
    temperature: float = 0.07,
) -> tuple[float, list[list[float]]]:
    """Compute mean bidirectional in-batch cross-entropy and scaled logits."""
    logits = similarity_matrix(image_features, text_features, temperature)
    batch_size = len(logits)

    image_to_text = [_softmax(row) for row in logits]
    text_to_image = [
        _softmax([logits[row][column] for row in range(batch_size)])
        for column in range(batch_size)
    ]

    epsilon = 1e-300
    loss_i2t = -sum(
        math.log(max(image_to_text[index][index], epsilon))
        for index in range(batch_size)
    ) / batch_size
    loss_t2i = -sum(
        math.log(max(text_to_image[index][index], epsilon))
        for index in range(batch_size)
    ) / batch_size
    return (loss_i2t + loss_t2i) / 2.0, logits


def zero_shot_scores(
    image_feature: Vector,
    candidate_text_features: Mapping[str, Vector],
    temperature: float = 0.07,
) -> list[tuple[str, float, float]]:
    """Return (label, cosine similarity, softmax probability), highest first."""
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    if not candidate_text_features:
        raise ValueError("at least one candidate text is required")
    image = _normalize(image_feature)
    candidates = [
        (label, _normalize(vector))
        for label, vector in candidate_text_features.items()
    ]
    if any(len(vector) != len(image) for _, vector in candidates):
        raise ValueError("image and text embedding dimensions must match")
    similarities = [(label, _dot(image, vector)) for label, vector in candidates]
    probabilities = _softmax([score / temperature for _, score in similarities])
    results = [
        (label, score, probability)
        for (label, score), probability in zip(similarities, probabilities)
    ]
    return sorted(results, key=lambda item: item[2], reverse=True)


if __name__ == "__main__":
    image_batch = [[1.0, 0.0], [0.0, 1.0]]
    text_batch = [[0.9, 0.1], [0.1, 0.9]]
    loss, logits = symmetric_contrastive_loss(
        image_batch, text_batch, temperature=0.1
    )
    print(f"symmetric loss: {loss:.6f}")
    print("scaled similarity matrix:")
    for row in logits:
        print("  " + " ".join(f"{value:7.3f}" for value in row))
    print("zero-shot:", zero_shot_scores(
        [1.0, 0.0],
        {"dog": [0.9, 0.1], "cat": [0.1, 0.9]},
        temperature=0.1,
    ))
