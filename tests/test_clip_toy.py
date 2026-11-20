import math
import pytest

from posts.multimodal.clip.clip_toy import (
    similarity_matrix,
    symmetric_contrastive_loss,
    zero_shot_scores,
)


def test_matching_pairs_have_larger_diagonal_logits():
    images = [[1.0, 0.0], [0.0, 1.0]]
    texts = [[0.9, 0.1], [0.1, 0.9]]
    logits = similarity_matrix(images, texts, temperature=0.1)
    assert logits[0][0] > logits[0][1]
    assert logits[1][1] > logits[1][0]


def test_symmetric_loss_is_finite_nonnegative_and_small_for_aligned_pairs():
    images = [[1.0, 0.0], [0.0, 1.0]]
    texts = [[0.9, 0.1], [0.1, 0.9]]
    loss, _ = symmetric_contrastive_loss(images, texts, temperature=0.1)
    assert math.isfinite(loss)
    assert 0.0 <= loss < 0.01


def test_zero_shot_ranks_best_matching_candidate_first():
    results = zero_shot_scores(
        [1.0, 0.0],
        {"dog": [0.9, 0.1], "cat": [0.1, 0.9]},
        temperature=0.1,
    )
    assert results[0][0] == "dog"
    assert results[0][1] > results[1][1]
    assert sum(item[2] for item in results) == pytest.approx(1.0)


@pytest.mark.parametrize("temperature", [0.0, -0.1])
def test_nonpositive_temperature_is_rejected(temperature):
    with pytest.raises(ValueError, match="temperature"):
        similarity_matrix([[1.0]], [[1.0]], temperature=temperature)


def test_zero_vector_is_rejected():
    with pytest.raises(ValueError, match="zero vectors"):
        similarity_matrix([[0.0, 0.0]], [[1.0, 0.0]])


def test_mismatched_batch_size_is_rejected():
    with pytest.raises(ValueError, match="same non-zero size"):
        similarity_matrix([[1.0, 0.0]], [], temperature=0.1)


def test_mismatched_embedding_dimensions_are_rejected():
    with pytest.raises(ValueError, match="dimensions"):
        similarity_matrix([[1.0, 0.0]], [[1.0, 0.0, 0.0]], temperature=0.1)
