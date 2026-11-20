"""Pedagogical shape/parameter accounting for AlexNet; NOT a reproduction of the network."""
from __future__ import annotations


def conv_out(size: int, kernel: int, stride: int = 1, padding: int = 0) -> int:
    """Spatial output size for dilation=1, integer convolution/pooling."""
    if min(size, kernel, stride) <= 0 or padding < 0:
        raise ValueError("spatial size, kernel and stride must be positive; padding nonnegative")
    result = (size + 2 * padding - kernel) // stride + 1
    if result <= 0:
        raise ValueError("kernel larger than effective input")
    return result


def grouped_conv_params(cin: int, cout: int, kernel: int, groups: int = 1, bias: bool = True) -> int:
    """Kernel weights + optional bias; assumes groups split both channel counts."""
    if min(cin, cout, kernel, groups) <= 0 or cin % groups or cout % groups:
        raise ValueError("grouping must evenly partition positive channel dimensions")
    return cout * (cin // groups) * kernel * kernel + (cout if bias else 0)


def fc_params(inputs: int, outputs: int, bias: bool = True) -> int:
    if inputs <= 0 or outputs <= 0:
        raise ValueError("feature counts must be positive")
    return inputs * outputs + (outputs if bias else 0)


def shape_trace(n: int, p1: int) -> tuple[int, int, int, int]:
    """Two *explicit* shape-consistent conventions, not historical CUDA verification."""
    h1 = conv_out(n, 11, stride=4, padding=p1)
    h2 = conv_out(h1, 3, stride=2)
    h3 = conv_out(h2, 3, stride=2)
    h4 = conv_out(h3, 3, stride=2)
    return h1, h2, h3, h4


if __name__ == "__main__":
    assert shape_trace(227, 0) == (55, 27, 13, 6)
    assert shape_trace(224, 2) == (55, 27, 13, 6)
    assert grouped_conv_params(96, 256, 5, groups=2) == 307456
    assert grouped_conv_params(96, 256, 5, groups=1) == 614656
    assert fc_params(6 * 6 * 256, 4096) == 37752832
    print("AlexNet shape and parameter sanity checks passed")
