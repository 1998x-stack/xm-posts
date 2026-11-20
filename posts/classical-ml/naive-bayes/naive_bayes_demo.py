"""Deterministic educational Naive Bayes: no external dependencies."""
from collections import Counter
from math import exp, log

DOCS = {
    "promo": ["free offer now", "free prize today", "offer prize free"],
    "work": ["project meeting today", "project report now",
             "meeting report project"],
}
VOCAB = sorted({w for docs in DOCS.values() for d in docs for w in d.split()})

def probabilities(words: str, alpha: float = 1.0, model: str = "multinomial"):
    if alpha <= 0 or model not in {"multinomial", "bernoulli"}:
        raise ValueError("alpha must be positive; unknown model")
    tokens = Counter(w for w in words.split() if w in VOCAB)
    scores = {}
    for label, docs in DOCS.items():
        score = log(len(docs) / sum(map(len, DOCS.values())))
        if model == "multinomial":
            counts = Counter(w for doc in docs for w in doc.split())
            denominator = sum(counts.values()) + alpha * len(VOCAB)
            score += sum(n * log((counts[w] + alpha) / denominator)
                         for w, n in tokens.items())
        else:
            presence = Counter(w for doc in docs for w in set(doc.split()))
            for word in VOCAB:
                theta = (presence[word] + alpha) / (len(docs) + 2 * alpha)
                score += log(theta if word in tokens else 1 - theta)
        scores[label] = score
    peak = max(scores.values())
    weights = {label: exp(score - peak) for label, score in scores.items()}
    z = sum(weights.values())
    return {label: value / z for label, value in weights.items()}

if __name__ == "__main__":
    p = probabilities("free offer")
    assert abs(p["promo"] - 12 / 13) < 1e-12
    assert abs(sum(p.values()) - 1) < 1e-12
    assert probabilities("free free meeting", model="bernoulli") == probabilities(
        "free meeting", model="bernoulli")
    assert probabilities("project meeting")["work"] > 0.9
    print("toy assertions passed", p)
