from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "posts/architectures/pre-ln-vs-post-ln/mini_norm.py"

def test_toy_layernorm_shift_and_jacobian():
    spec = spec_from_file_location("pre_post_ln_toy", SOURCE)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    module.check()

def test_standalone_svg_sources():
    folder = SOURCE.parent / "assets"
    svgs = list(folder.glob("*.svg"))
    assert len(svgs) == 5
    for file in svgs:
        data = file.read_text(encoding="utf-8")
        assert "<title>" in data and "viewBox=" in data
