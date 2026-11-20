"""Minimal, deterministic MobileNet V1 operator examples. Pure Python; no ML framework."""
from __future__ import annotations


def cost(*, k: int, m: int, n: int, h: int, w: int) -> tuple[int, int]:
    """Full and depthwise+pointwise MACs with the same output spatial dimensions."""
    if min(k, m, n, h, w) <= 0:
        raise ValueError("Dimensions must be positive")
    s = h * w
    return k * k * m * n * s, (k * k * m + m * n) * s


def check_factorized_equivalence() -> bool:
    """For a deliberately factorizable full kernel, compare both forward paths."""
    x = [
        [[1, 2], [3, 4], [5, 6]],
        [[7, 8], [9, 10], [11, 12]],
        [[13, 14], [15, 16], [17, 18]],
    ]  # 3x3 spatial, 2 input channels
    depthwise = [
        [[1, 0], [2, 1], [0, -1]],
        [[0, 2], [1, 0], [1, 1]],
        [[-1, 1], [0, 1], [2, 0]],
    ]
    pointwise = [[2, -1], [1, 3]]  # M=2 -> N=2
    # A standard full kernel W[i,j,m,n] = D[i,j,m] * P[m,n].
    full = [
        [
            [
                [depthwise[i][j][m] * pointwise[m][n] for n in range(2)]
                for m in range(2)
            ]
            for j in range(3)
        ]
        for i in range(3)
    ]
    standard = [
        sum(x[i][j][m] * full[i][j][m][n]
            for i in range(3) for j in range(3) for m in range(2))
        for n in range(2)
    ]
    per_channel = [
        sum(x[i][j][m] * depthwise[i][j][m]
            for i in range(3) for j in range(3))
        for m in range(2)
    ]
    separated = [
        sum(per_channel[m] * pointwise[m][n] for m in range(2))
        for n in range(2)
    ]
    return standard == separated


if __name__ == "__main__":
    full, ds = cost(k=3, m=32, n=64, h=56, w=56)
    assert full == 57_802_752 and ds == 7_325_696
    assert check_factorized_equivalence()
    print("full:", full, "separable:", ds, "ratio:", round(full / ds, 2))
