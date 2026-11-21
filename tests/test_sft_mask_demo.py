from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples"))
from sft_mask_demo import (  # noqa: E402
    IGNORE_INDEX,
    build_labels,
    mean_masked_next_token_nll,
)


def test_response_only_labels_mask_context_and_keep_end_token():
    token_ids = [0, 1, 2, 3]
    mask = [False, False, True, True]
    assert build_labels(token_ids, mask) == [IGNORE_INDEX, IGNORE_INDEX, 2, 3]


def test_response_only_loss_ignores_context_prediction_logits():
    token_ids = [0, 1, 2, 3]
    mask = [False, False, True, True]
    logits_a = [
        [0.0, 5.0, 0.0, 0.0],
        [0.0, 0.0, 2.0, 0.0],
        [0.0, 0.0, 0.0, 2.0],
    ]
    logits_b = [
        [100.0, -100.0, -100.0, -100.0],
        [0.0, 0.0, 2.0, 0.0],
        [0.0, 0.0, 0.0, 2.0],
    ]
    loss_a = mean_masked_next_token_nll(logits_a, token_ids, mask)
    loss_b = mean_masked_next_token_nll(logits_b, token_ids, mask)
    assert loss_a == pytest.approx(0.3407529539131309)
    assert loss_b == pytest.approx(loss_a)


def test_masked_loss_rejects_empty_target_set():
    with pytest.raises(ValueError, match="no supervised target tokens"):
        mean_masked_next_token_nll(
            [[0.0, 1.0], [1.0, 0.0]],
            [0, 1, 0],
            [False, False, False],
        )


def test_label_builder_checks_mask_length():
    with pytest.raises(ValueError, match="equal length"):
        build_labels([1, 2], [True])
