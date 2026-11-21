"""A dependency-free toy demo of response-only SFT loss masking.

This is not a language model trainer. It verifies which next-token targets
contribute to a causal language-model negative log-likelihood.
"""
from math import exp, log

IGNORE_INDEX = -100


def build_labels(token_ids, assistant_mask):
    """Keep assistant target IDs; mask context positions with -100."""
    if len(token_ids) != len(assistant_mask):
        raise ValueError("token_ids and assistant_mask must have equal length")
    return [
        token_id if is_target else IGNORE_INDEX
        for token_id, is_target in zip(token_ids, assistant_mask)
    ]


def mean_masked_next_token_nll(logits, token_ids, target_mask):
    """Mean NLL; logits[t] predicts token_ids[t + 1]."""
    if len(token_ids) != len(target_mask):
        raise ValueError("token_ids and target_mask must have equal length")
    if len(logits) != len(token_ids) - 1:
        raise ValueError("causal logits must have sequence_length - 1 rows")

    losses = []
    for step, row in enumerate(logits):
        target_position = step + 1
        if not target_mask[target_position]:
            continue
        target_id = token_ids[target_position]
        if not row or target_id < 0 or target_id >= len(row):
            raise ValueError("target token is outside the logits vocabulary")
        maximum = max(row)
        log_partition = maximum + log(sum(exp(value - maximum) for value in row))
        losses.append(log_partition - row[target_id])

    if not losses:
        raise ValueError("no supervised target tokens")
    return sum(losses) / len(losses)


def main():
    token_ids = [0, 1, 2, 3]
    assistant_mask = [False, False, True, True]
    labels = build_labels(token_ids, assistant_mask)
    logits = [
        [0.0, 5.0, 0.0, 0.0],
        [0.0, 0.0, 2.0, 0.0],
        [0.0, 0.0, 0.0, 2.0],
    ]
    loss = mean_masked_next_token_nll(logits, token_ids, assistant_mask)
    assert labels == [IGNORE_INDEX, IGNORE_INDEX, 2, 3]
    assert abs(loss - 0.3407529539131309) < 1e-12
    print("labels:", labels)
    print("response-only mean NLL:", round(loss, 6))


if __name__ == "__main__":
    main()
