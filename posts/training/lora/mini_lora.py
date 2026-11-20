"""Minimal LoRA linear algebra, standard-library only; not a training reproduction."""
def matvec(matrix, vector):
    return [sum(a * x for a, x in zip(row, vector)) for row in matrix]

def low_rank_forward(W0, A, B, x, alpha=1.0):
    r = len(A)
    base = matvec(W0, x)
    delta = matvec(B, matvec(A, x))
    return [v + alpha / r * d for v, d in zip(base, delta)]

def merged_weight(W0, A, B, alpha=1.0):
    r = len(A)
    return [[W0[i][j] + alpha / r * sum(B[i][t] * A[t][j]
            for t in range(r)) for j in range(len(W0[0]))]
            for i in range(len(W0))]

W0 = [[1.0, 0.0], [0.0, 1.0]]
A = [[1.0, 0.0]]            # r=1, k=2
B = [[0.0], [2.0]]          # d=2, r=1
x = [3.0, 4.0]
assert low_rank_forward(W0, A, B, x) == [3.0, 10.0]
assert matvec(merged_weight(W0, A, B), x) == [3.0, 10.0]
assert low_rank_forward(W0, A, [[0.0], [0.0]], x) == [3.0, 4.0]
assert 8 * (4096 + 4096) == 65_536
