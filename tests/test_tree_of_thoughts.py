import ast
import importlib.util
from fractions import Fraction
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "posts" / "reasoning" / "tree-of-thoughts" / "game24_exact.py"
)
SPEC = importlib.util.spec_from_file_location("game24_exact", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def evaluate_arithmetic(node):
    if isinstance(node, ast.Expression):
        return evaluate_arithmetic(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return Fraction(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -evaluate_arithmetic(node.operand)
    if isinstance(node, ast.BinOp):
        left = evaluate_arithmetic(node.left)
        right = evaluate_arithmetic(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            if right == 0:
                raise ZeroDivisionError
            return left / right
    raise AssertionError(f"Unsupported arithmetic node: {ast.dump(node)}")


def test_reference_game_has_an_exact_solution():
    solution = MODULE.solve_game24([4, 9, 10, 13])
    assert solution is not None
    assert len(solution) == 3
    final_expression = ast.parse(solution[-1], mode="eval")
    assert evaluate_arithmetic(final_expression) == 24


def test_unsolved_input_returns_none():
    assert MODULE.solve_game24([1, 1, 1, 1]) is None


def test_exact_solver_rejects_wrong_input_size():
    try:
        MODULE.solve_game24([4, 9, 10])
    except ValueError as exc:
        assert "exactly four" in str(exc)
    else:
        raise AssertionError("Expected ValueError for non-four-number input")
