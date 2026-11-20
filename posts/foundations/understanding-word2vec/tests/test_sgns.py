"""Correctness tests for the educational Word2Vec SGNS implementation."""
import pathlib
import sys
import unittest

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'code'))
from train_sgns import (  # noqa: E402
    pairs_from_sentences,
    sample_negatives,
    sgns_loss_and_grads,
    train,
)


class SGNSTest(unittest.TestCase):
    def test_positive_negative_gradients_against_finite_difference(self):
        c = np.array([.2, -.7, .4])
        p = np.array([.9, .5, -.2])
        n = np.array([[.6, -.1, .3], [-.2, .4, -.5]])
        _, grad = sgns_loss_and_grads(c, p, n)
        eps = 1e-6
        for name, arr, analytical in [
            ('c', c, grad.center), ('p', p, grad.positive), ('n', n, grad.negatives)
        ]:
            for ix in np.ndindex(arr.shape):
                plus, minus = arr.copy(), arr.copy()
                plus[ix] += eps
                minus[ix] -= eps
                c1, p1, n1 = (plus if name == 'c' else c), (plus if name == 'p' else p), (plus if name == 'n' else n)
                c2, p2, n2 = (minus if name == 'c' else c), (minus if name == 'p' else p), (minus if name == 'n' else n)
                numerical = (sgns_loss_and_grads(c1, p1, n1)[0] - sgns_loss_and_grads(c2, p2, n2)[0]) / (2 * eps)
                self.assertAlmostEqual(float(analytical[ix]), float(numerical), places=6)

    def test_pair_window_never_crosses_sentence(self):
        pairs = pairs_from_sentences([[0, 1], [2, 3]], window=2)
        self.assertEqual(set(pairs), {(0, 1), (1, 0), (2, 3), (3, 2)})

    def test_negative_samples_exclude_positive_target(self):
        rng = np.random.default_rng(7)
        probs = np.array([.8, .15, .05])
        ids = sample_negatives(rng, probs, 200, positive_id=0)
        self.assertFalse(np.any(ids == 0))
        self.assertEqual(len(ids), 200)

    def test_loss_reduces_on_tiny_corpus(self):
        vocab, V, U, hist = train(epochs=18, negative=2, seed=7, verbose=False)
        self.assertEqual(V.shape[0], len(vocab))
        self.assertEqual(U.shape, V.shape)
        self.assertTrue(all(np.isfinite(hist)))
        self.assertLess(hist[-1], hist[0])


if __name__ == '__main__':
    unittest.main()
