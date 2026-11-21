import importlib.util
from pathlib import Path
import sys
import pytest

spec = importlib.util.spec_from_file_location("sarathi_demo", Path(__file__).with_name("mini_sarathi.py"))
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
step, schedule = module.plan_step, module.schedule_prefill


def test_budget_and_chunk_progress():
    batches = list(schedule(2, 13, 8))
    assert [b.prefill_chunk for b in batches] == [6, 6, 1]
    assert batches[-1].remaining_prefill == 0
    assert sum(b.prefill_chunk for b in batches) == 13
    assert all(b.decode_tokens == 2 and b.decode_tokens + b.prefill_chunk <= 8 for b in batches)


def test_small_budget_more_rounds():
    assert len(list(schedule(2, 13, 4))) > len(list(schedule(2, 13, 8)))


def test_invalid_inputs():
    with pytest.raises(ValueError):
        step(3, 12, 2)
    with pytest.raises(ValueError):
        step(1, -1, 8)
    with pytest.raises(ValueError):
        list(schedule(2, 12, 2))


def test_zero_prefill():
    assert list(schedule(0, 0, 5)) == []
