"""Exact-arithmetic Game of 24 helper for the Tree of Thoughts explainer.

This is a deterministic symbolic search/verifier, not an LLM ToT reproduction.
"""
from fractions import Fraction
from itertools import combinations


def solve_game24(numbers):
    """Return intermediate expressions ending at 24, or None if unsolved.

    Each input number is represented once. Fraction avoids floating-point
    rounding, and both operand orders are explored for subtraction/division.
    """
    if len(numbers) != 4:
        raise ValueError("Game of 24 expects exactly four numbers")

    items = [(Fraction(number), str(number)) for number in numbers]

    def search(state):
        if len(state) == 1:
            value, _expression = state[0]
            return [] if value == 24 else None

        for i, j in combinations(range(len(state)), 2):
            a, expr_a = state[i]
            b, expr_b = state[j]
            rest = [value for index, value in enumerate(state)
                    if index not in (i, j)]

            candidates = [
                (a + b, f"({expr_a} + {expr_b})"),
                (a - b, f"({expr_a} - {expr_b})"),
                (b - a, f"({expr_b} - {expr_a})"),
                (a * b, f"({expr_a} * {expr_b})"),
            ]
            if b != 0:
                candidates.append((a / b, f"({expr_a} / {expr_b})"))
            if a != 0:
                candidates.append((b / a, f"({expr_b} / {expr_a})"))

            for value, expression in candidates:
                result = search(rest + [(value, expression)])
                if result is not None:
                    return [expression] + result

        return None

    return search(items)


if __name__ == "__main__":
    solution = solve_game24([4, 9, 10, 13])
    print(solution[-1] if solution else "No solution found")
