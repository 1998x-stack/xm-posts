import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location("batching_demo", Path(__file__).with_name("mini_batching.py"))
module = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = module
spec.loader.exec_module(module)
Request, schedule = module.Request, module.schedule


def test_late_join_and_early_exit():
    jobs = [Request("A", 0, 2), Request("B", 0, 4), Request("C", 2, 2)]
    trace = list(schedule(jobs))
    assert trace[0] == (0, ["A", "B"], [])
    assert trace[1] == (1, ["A", "B"], ["A"])
    assert trace[2] == (2, ["B", "C"], [])
    assert trace[3] == (3, ["B", "C"], ["B", "C"])
    assert all(j.generated == j.target for j in jobs)


def test_arrival_validation():
    with pytest.raises(ValueError):
        Request("broken", -1, 1)
    with pytest.raises(ValueError):
        Request("broken", 0, 0)


def test_duplicate_names_rejected():
    with pytest.raises(ValueError):
        list(schedule([Request("same", 0, 1), Request("same", 0, 2)]))
