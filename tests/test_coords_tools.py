"""mouse_move and click_at: viewport-origin pointer actions, bounds and button checks, against fakes."""

import asyncio
import os

import pytest
from test_ownership import make_env, set_owner
from test_server import FakeBrowser

from zenpilot import browser as browser_mod
from zenpilot import server
from zenpilot.browser import Browser
from zenpilot.safety import Config

pytestmark = pytest.mark.ownership  # keep the real tab_ownership mode (conftest forces off otherwise)


class StubBiDi:
    def __init__(self):
        self.sent: list[tuple[str, dict]] = []

    async def send(self, method, params=None, timeout=30):
        self.sent.append((method, params or {}))
        return {}

    def expect(self, method, predicate=lambda p: True):
        return asyncio.get_running_loop().create_future()


def browser_with_viewport(w=800, h=600):
    b = Browser()
    b._bidi = StubBiDi()

    async def run(ctx, fn, *args, timeout=15):
        if fn is browser_mod.VIEWPORT_JS:
            return [w, h]
        return None

    b.run = run
    return b


def pointer_steps(b):
    """The actions of the mouse source in each input.performActions the browser sent."""
    return [p["actions"][0]["actions"] for m, p in b._bidi.sent if m == "input.performActions"]


TAB = {"id": "t1", "context": "c1", "url": "https://ok.com/form"}
MOVE = {"type": "pointerMove", "x": 10, "y": 20, "origin": "viewport"}


# -- browser level ----------------------------------------------------------


async def test_viewport_reads_inner_size():
    b = browser_with_viewport(1024, 768)
    assert await b.viewport(TAB) == (1024, 768)


async def test_move_to_sends_viewport_origin_pointer_move():
    b = browser_with_viewport()
    await b.move_to(TAB, 10, 20)
    assert pointer_steps(b) == [[MOVE]]


async def test_click_at_right_double_sends_move_then_presses_with_button_codes():
    b = browser_with_viewport()
    text = await b.click_at(TAB, 10, 20, "right", 2)
    press = [{"type": "pointerDown", "button": 2}, {"type": "pointerUp", "button": 2}]
    assert pointer_steps(b) == [[MOVE] + press * 2]
    assert isinstance(text, str)


async def test_click_at_left_single_uses_button_zero():
    b = browser_with_viewport()
    await b.click_at(TAB, 10, 20, "left", 1)
    assert pointer_steps(b) == [[MOVE, {"type": "pointerDown", "button": 0}, {"type": "pointerUp", "button": 0}]]


# -- server level -----------------------------------------------------------


class CoordBrowser(FakeBrowser):
    def __init__(self):
        super().__init__()
        self.calls: list = []

    async def viewport(self, tab):
        return (800, 600)

    async def move_to(self, tab, x, y):
        self.calls.append(("move_to", x, y))

    async def click_at(self, tab, x, y, button, count):
        self.calls.append(("click_at", x, y, button, count))
        return "Clicked at 10, 20."


@pytest.fixture
def coords(monkeypatch, tmp_path):
    cfg = Config(
        allowlist=["ok.com"],
        read_only=False,
        allow_all_sites=False,
        port=9222,
        audit_log=tmp_path / "audit.jsonl",
        auto_launch=False,
    )
    cfg.tab_ownership = "off"
    monkeypatch.setattr(server, "load_config", lambda *a, **k: cfg)
    fb = CoordBrowser()
    monkeypatch.setattr(server, "browser", fb)
    return fb, cfg


def test_coord_tools_are_registered_for_browser_batch():
    assert {"mouse_move", "click_at"} <= set(server._TOOLS)


async def test_mouse_move_reports_position(coords):
    fb, _ = coords
    assert await server.mouse_move(x=10, y=20) == "Moved to 10, 20."
    assert fb.calls == [("move_to", 10, 20)]


async def test_click_at_returns_page_diff_and_passes_defaults(coords):
    fb, _ = coords
    assert await server.click_at(x=10, y=20) == "Clicked at 10, 20."
    assert fb.calls == [("click_at", 10, 20, "left", 1)]


async def test_click_at_passes_button_and_count(coords):
    fb, _ = coords
    await server.click_at(x=10, y=20, button="right", count=2)
    assert fb.calls == [("click_at", 10, 20, "right", 2)]


EDGE = [(800, 10), (10, 600), (-1, 0), (0, -1)]
COORD_TOOLS = [
    lambda x, y: server.mouse_move(x=x, y=y),
    lambda x, y: server.click_at(x=x, y=y),
]


@pytest.mark.parametrize("call", COORD_TOOLS)
@pytest.mark.parametrize(("x", "y"), EDGE)
async def test_outside_viewport_is_tool_error(call, x, y, coords):
    fb, _ = coords
    with pytest.raises(server.ToolError, match=r"x, y outside the viewport \(800x600\)"):
        await call(x, y)
    assert fb.calls == []


async def test_last_pixel_inside_viewport_is_allowed(coords):
    fb, _ = coords
    assert await server.mouse_move(x=799, y=599) == "Moved to 799, 599."


async def test_click_at_rejects_unknown_button(coords):
    fb, _ = coords
    with pytest.raises(server.ToolError, match="button must be left, right or middle"):
        await server.click_at(x=10, y=20, button="up")
    assert fb.calls == []


async def test_click_at_rejects_bad_count(coords):
    fb, _ = coords
    with pytest.raises(server.ToolError, match="count must be 1 or 2"):
        await server.click_at(x=10, y=20, count=3)
    assert fb.calls == []


@pytest.mark.parametrize("call", COORD_TOOLS)
async def test_coord_tools_are_blocked_in_read_only(call, coords):
    fb, cfg = coords
    cfg.read_only = True
    with pytest.raises(server.ToolError, match="read-only"):
        await call(10, 20)
    assert fb.calls == []


COORD_CALLS = [
    lambda: server.mouse_move(x=10, y=20),
    lambda: server.click_at(x=10, y=20),
]


@pytest.mark.parametrize("call", COORD_CALLS)
async def test_coord_tools_block_unowned_tab_in_strict(call, tmp_path, monkeypatch):
    make_env(tmp_path, monkeypatch, "strict")
    fb = CoordBrowser()
    monkeypatch.setattr(server, "browser", fb)
    with pytest.raises(server.ToolError, match="isn't Claude's"):
        await call()
    assert fb.calls == []


@pytest.mark.parametrize("call", COORD_CALLS)
async def test_coord_tools_block_another_sessions_tab_in_strict(call, tmp_path, monkeypatch):
    make_env(tmp_path, monkeypatch, "strict")
    fb = CoordBrowser()
    monkeypatch.setattr(server, "browser", fb)
    set_owner("t1", os.getppid())
    with pytest.raises(server.ToolError, match="belongs to another Claude session"):
        await call()
    assert fb.calls == []


@pytest.mark.parametrize("call", COORD_CALLS)
async def test_coord_tools_pass_on_own_tab_in_strict(call, tmp_path, monkeypatch):
    make_env(tmp_path, monkeypatch, "strict")
    fb = CoordBrowser()
    monkeypatch.setattr(server, "browser", fb)
    set_owner("t1", os.getpid())
    assert await call()
    assert fb.calls

