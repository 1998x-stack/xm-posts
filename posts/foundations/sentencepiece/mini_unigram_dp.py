#!/usr/bin/env python3
"""Pure-stdlib teaching implementation of Unigram MAP segmentation, not SentencePiece training."""
import math
import unittest

PIECES = {"a": 0.42, "b": 0.20, "ab": 0.27, "ba": 0.11}

def best_path(text, pieces=PIECES):
    dp = [(-math.inf, ()) for _ in range(len(text)+1)]
    dp[0] = (0.0, ())
    for i in range(1, len(text)+1):
        for piece, probability in pieces.items():
            j = i - len(piece)
            if j >= 0 and text[j:i] == piece and probability > 0 and dp[j][0] != -math.inf:
                candidate = (dp[j][0] + math.log(probability), dp[j][1] + (piece,))
                if candidate[0] > dp[i][0]:
                    dp[i] = candidate
    return dp[-1]

def paths(text, pieces=PIECES):
    if text == "":
        yield ()
    for piece in pieces:
        if text.startswith(piece):
            for rest in paths(text[len(piece):], pieces):
                yield (piece,) + rest

def weight(path):
    return math.prod(PIECES[p] for p in path)

def distribution(text, alpha=1.0):
    if alpha <= 0:
        raise ValueError("alpha must be > 0")
    options = list(paths(text))
    scores = [weight(p)**alpha for p in options]
    total = sum(scores)
    return dict(zip(options, (s/total for s in scores)))

class UnitTests(unittest.TestCase):
    def test_paths(self):
        self.assertEqual(len(list(paths("aba"))), 3)
        self.assertAlmostEqual(sum(PIECES.values()), 1)
        self.assertAlmostEqual(weight(("ab", "a")), .1134)
        self.assertEqual(best_path("aba")[1], ("ab", "a"))
        self.assertAlmostEqual(math.exp(best_path("aba")[0]), .1134)
    def test_exhaustive_oracle(self):
        for text in ("a", "b", "aba", "abba", "baba"):
            score, path = best_path(text)
            self.assertEqual("".join(path), text)
            self.assertAlmostEqual(math.exp(score), max(map(weight, paths(text))))
    def test_unknown(self):
        self.assertEqual(best_path("abc"), (-math.inf, ()))
    def test_sampling(self):
        for alpha in (0.2, 1.0, 3.0):
            d = distribution("aba", alpha)
            self.assertAlmostEqual(sum(d.values()), 1)
            self.assertGreater(d[("ab", "a")], d[("a", "ba")])
        self.assertGreater(distribution("aba",3)[("ab","a")], distribution("aba",.2)[("ab","a")])

if __name__ == "__main__":
    unittest.main()
