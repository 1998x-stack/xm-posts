"""Deterministic educational RNN tests."""
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from math import isfinite

path = Path(__file__).resolve().parents[1] / "posts/architectures/rnn/mini_rnn.py"
spec = spec_from_file_location("mini_rnn", path)
mini = module_from_spec(spec)
spec.loader.exec_module(mini)


def test_bptt_matches_finite_difference():
    _, gradient = mini.loss_and_grad()
    numerical = mini.finite_difference()
    assert all(abs(a - b) < 1e-6 for a, b in zip(gradient, numerical))


def test_loss_valid_and_recurrent_signal_nonzero():
    loss, gradient = mini.loss_and_grad()
    assert loss >= 0 and isfinite(loss)
    assert len(gradient) == 3 and all(isfinite(x) for x in gradient)
    assert abs(gradient[1]) > 1e-5


def test_reject_inconsistent_or_empty_sequence():
    for x, y in [((), ()), ((1.0,), ())]:
        try:
            mini.loss_and_grad(x=x, target=y)
        except ValueError:
            pass
        else:
            raise AssertionError("Should reject inconsistent sequence lengths")


def test_narrow_mobile_has_no_document_overflow():
    """Regress 360px layout; report exact elements when an overflow appears."""
    from playwright.sync_api import sync_playwright
    from pathlib import Path
    html = (Path(__file__).resolve().parents[1] /
            "posts/architectures/rnn/index.html").read_text(encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 360, "height": 800})
        page.set_content(html, wait_until="load")
        details = page.evaluate("""() => ({
            viewport: innerWidth,
            htmlWidth: document.documentElement.scrollWidth,
            bodyWidth: document.body.scrollWidth,
            offenders: [...document.querySelectorAll('body *')].map(e => {
                const r=e.getBoundingClientRect();
                const css=getComputedStyle(e);
                return {
                    tag:e.tagName.toLowerCase(),
                    id:e.id, cls: typeof e.className === 'string' ? e.className : '',
                    text:(e.innerText||e.textContent||'').slice(0,45),
                    left:Math.round(r.left), right:Math.round(r.right),
                    width:Math.round(r.width), minWidth:css.minWidth,
                    whiteSpace:css.whiteSpace, overflowX:css.overflowX
                };
            }).filter(x => (x.right > innerWidth + 1 || x.left < -1)
              && ![...document.querySelectorAll('body *')].some(e => {
                  if (e.tagName.toLowerCase() !== x.tag || e.id !== x.id ||
                      Math.round(e.getBoundingClientRect().right) !== x.right) return false;
                  let p=e.parentElement;
                  while(p && p !== document.body){
                      if(['auto','scroll','hidden','clip'].includes(getComputedStyle(p).overflowX))return true;
                      p=p.parentElement;
                  }
                  return false;
              }))
              .sort((a,b)=>b.right-a.right).slice(0,12)
        })""")
        browser.close()
    assert details["htmlWidth"] <= 361, details
