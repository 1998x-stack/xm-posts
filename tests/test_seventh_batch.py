"""Seventh batch: arithmetic and real Chromium keyboard/mobile validation."""
from __future__ import annotations
import math
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = {name: ROOT / "posts" / "reinforcement-learning" / name / "index.html"
         for name in ("dqn", "ppo", "sac")}

def test_hand_computed_rl_targets():
    online, frozen = (5., 4.), (1., 4.)
    assert .9 * max(frozen) == pytest.approx(3.6)
    assert .9 * frozen[max(range(2), key=lambda k: online[k])] == pytest.approx(.9)
    def lclip(p):
        ra, rb = 2*p, 2*(1-p)
        clip = lambda r: max(.8, min(1.2, r))
        return (min(ra, clip(ra)) + min(-rb, -clip(rb))) / 2
    assert lclip(.5) == pytest.approx(0)
    assert lclip(.6) == pytest.approx(.2)
    assert lclip(.9) == pytest.approx(.2)
    kl = lambda p: .5 * math.log(.5 / p) + .5 * math.log(.5 / (1-p))
    assert kl(.9) > kl(.6) > 0
    assert 1 + .9 * (min(3, 2.5) - .5 * (-.7)) == pytest.approx(3.565)

@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--no-sandbox"])
        yield b
        b.close()

@pytest.mark.parametrize("width,height", [(1440,900),(768,1024),(390,844),(360,800)])
@pytest.mark.parametrize("name", ("dqn", "ppo", "sac"))
def test_seventh_batch_browser(browser, name, width, height):
    page = browser.new_page(viewport={"width": width, "height": height})
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    page.route("https?://**", lambda route: route.abort())
    try:
        page.goto(PAGES[name].as_uri(), wait_until="load")
        assert page.locator("h1").count() == 1
        assert page.locator("main").count() == 1
        ids = page.locator("[id]").evaluate_all("(nodes)=>nodes.map(n=>n.id)")
        assert len(ids) == len(set(ids))
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 2")
        img = page.locator(".batch7-figure img")
        assert img.count() == 1
        img.scroll_into_view_if_needed()
        assert img.evaluate("(el) => el.complete && el.naturalWidth > 0")
        if name == "dqn":
            assert "y = 3.60" in page.locator("#ddqn-result").inner_text()
            assert "y = 0.90" in page.locator("#ddqn-result").inner_text()
            page.locator('[data-ddqn-case="aligned"]').focus()
            page.keyboard.press("Enter")
            assert page.locator('[data-ddqn-case="aligned"]').get_attribute("aria-pressed") == "true"
            assert page.locator("#ddqn-result").inner_text().count("y = 3.60") == 2
            page.locator('[data-ddqn-case="matched"]').click()
            assert page.locator("#ddqn-result").inner_text().count("y = 4.50") == 2
        elif name == "ppo":
            assert "Lclip = 0.200" in page.locator("#ppo-kl-readout").inner_text()
            assert "0.511 nats" in page.locator("#ppo-kl-readout").inner_text()
            page.locator("#ppo-policy-slider").focus()
            page.keyboard.press("Home")
            assert page.locator("#ppo-policy-value").inner_text() == "0.50"
            assert "0.000 nats" in page.locator("#ppo-kl-readout").inner_text()
            page.keyboard.press("End")
            assert "Lclip = 0.200" in page.locator("#ppo-kl-readout").inner_text()
        else:
            assert "y = 1 + 0.9 × 2.850 = 3.565" in page.locator("#sac-backup-result").inner_text()
            page.locator('[data-soft-alpha="1"]').focus()
            page.keyboard.press("Enter")
            assert "3.880" in page.locator("#sac-backup-result").inner_text()
            page.locator("#sac-backup-terminal").check()
            assert "y = 1.000" in page.locator("#sac-backup-result").inner_text()
        assert errors == []
    finally:
        page.close()
