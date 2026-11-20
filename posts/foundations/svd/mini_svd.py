import numpy as np

# pip install numpy ; 这是确定性算例，不是论文实验复现
A = np.array([[3., 0.], [0., 2.], [0., 0.]])
U, s, Vh = np.linalg.svd(A, full_matrices=False)
assert U.shape == (3, 2) and s.shape == (2,) and Vh.shape == (2, 2)
assert np.allclose((U * s) @ Vh, A)
assert np.allclose(s, [3., 2.])

k = 1
Ak = (U[:, :k] * s[:k]) @ Vh[:k, :]
assert np.linalg.matrix_rank(Ak) == 1
assert np.isclose(np.linalg.norm(A - Ak, "fro"), 2.)
assert np.isclose(np.linalg.norm(A - Ak, 2), 2.)

# 不要直接对 A.T @ A 求 eig 来替代稳健 SVD:
# 当条件数很大时，平方会放大数值问题。
print("SVD reconstruction and rank-1 error OK")
