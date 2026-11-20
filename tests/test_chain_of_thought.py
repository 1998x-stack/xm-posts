"""Smoke-test the standalone CoT teaching protocol without model access."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "posts" / "reasoning" / "chain-of-thought" / "mini_cot.py"

def test_cot_prompt_structure_and_parser():
    completed = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "assertions passed" in completed.stdout
    assert "no model invoked" in completed.stdout
