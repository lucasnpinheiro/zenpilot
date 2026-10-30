"""Tab ownership in _tab(): strict, sessions and off, with the browser faked."""

import os

import pytest
from test_server import FakeBrowser

from zenpilot import safety, server
from zenpilot.safety import Config

pytestmark = pytest.mark.ownership

PORT = 9222


class OwnBrowser(FakeBrowser):
    closed = None

    async def new_tab(self):
        return "t9"

    async def close_tab(self, tab):
        self.closed = tab["id"]

    def tab_id_of(self, context):
        return {"c1": "t1", "c2": "t2"}.get(context)

    async def type(self, ref, text, submit):
        return f"Typed into {ref}."

    async def form_input(self, ref, value):
        return f"Set {ref}."

    async def activate(self, tab):
        pass

    async def tab(self, tab_id):
        if tab_id == "t9":
            return {"id": "t9", "context": "c9", "url": "about:blank", "title": "", "active": False}
        return await super().tab(tab_id)


def make_env(tmp_path, monkeypatch, mode):
    config = Config(["ok.com"], False, False, PORT, tmp_path / "audit.jsonl", auto_launch=False)
    config.report_dir = tmp_path / "reports"
    config.tab_ownership = mode
    monkeypatch.setattr(server, "load_config", lambda: Config(**vars(config) | {"allowlist": list(config.allowlist)}))
    monkeypatch.setattr(server, "browser", OwnBrowser())
    monkeypatch.setattr(server, "_declined", {})
    monkeypatch.setattr(server, "_stop_told", False)


@pytest.fixture
def strict(tmp_path, monkeypatch):
    make_env(tmp_path, monkeypatch, "strict")


@pytest.fixture
def sessions(tmp_path, monkeypatch):
    make_env(tmp_path, monkeypatch, "sessions")


@pytest.fixture
def off(tmp_path, monkeypatch):
    make_env(tmp_path, monkeypatch, "off")


def set_owner(tab_id, pid):
    safety.save_state(f"owners-{PORT}", {tab_id: {"pid": pid, "since": 1.0}})


UNOWNED = "Tab t1 isn't Claude's. Call attach_tab('t1') to ask the user for it, or open one with new_tab."


async def test_strict_unowned_tab_is_blocked(strict):
    with pytest.raises(server.ToolError) as e:
        await server.navigate(url="https://ok.com/x", tab_id="t1")
    assert UNOWNED in str(e.value)


async def test_strict_active_tab_without_tab_id_is_blocked(strict):
    with pytest.raises(server.ToolError) as e:
        await server.navigate(url="https://ok.com/x")
    assert UNOWNED in str(e.value)


@pytest.mark.parametrize("mode", ["strict", "sessions"])
async def test_tab_of_another_live_session_is_blocked(mode, tmp_path, monkeypatch):
    make_env(tmp_path, monkeypatch, mode)
    other = os.getppid()
    set_owner("t1", other)
    with pytest.raises(server.ToolError) as e:
        await server.navigate(url="https://ok.com/x", tab_id="t1")
    assert f"Tab t1 belongs to another Claude session (zenpilot pid {other}). Use your own tabs (new_tab)." in str(
        e.value
    )


async def test_sessions_unowned_tab_passes(sessions):
    assert await server.navigate(url="https://ok.com/x", tab_id="t1")


async def test_own_tab_passes_in_strict(strict):
    set_owner("t1", os.getpid())
    assert await server.navigate(url="https://ok.com/x", tab_id="t1")


async def test_dead_owner_counts_as_unowned(strict, monkeypatch):
    monkeypatch.setattr(safety, "alive", lambda pid: False)
    set_owner("t1", 999999)
    with pytest.raises(server.ToolError, match="isn't Claude's"):
        await server.navigate(url="https://ok.com/x", tab_id="t1")


async def test_off_skips_the_check(off):
    set_owner("t1", os.getppid())
    assert await server.navigate(url="https://ok.com/x", tab_id="t1")


async def test_new_tab_claims_and_does_not_check(strict):
    await server.new_tab()
    assert safety.owner_of(PORT, "t9") == os.getpid()


async def test_close_tab_releases(strict):
    safety.claim(PORT, "t9")
    await server.close_tab(tab_id="t9")
    assert safety.owner_of(PORT, "t9") is None
    assert server.browser.closed == "t9"


async def test_list_and_switch_tab_do_not_check(strict):
    assert "t1" in await server.list_tabs()
    assert "Switched to t1." == await server.switch_tab(tab_id="t1")


REF_CALLS = [
    lambda: server.click(ref="r1"),
    lambda: server.type(ref="r1", text="x"),
    lambda: server.form_input(ref="r1", value="x"),
]


@pytest.mark.parametrize("call", REF_CALLS)
async def test_ref_tools_block_an_unowned_tab_in_strict(call, strict):
    with pytest.raises(server.ToolError, match="Tab t1 isn't Claude's"):
        await call()


@pytest.mark.parametrize("call", REF_CALLS)
async def test_ref_tools_block_another_sessions_tab(call, strict):
    set_owner("t1", os.getppid())
    with pytest.raises(server.ToolError, match="belongs to another Claude session"):
        await call()


@pytest.mark.parametrize("call", REF_CALLS)
async def test_ref_tools_pass_on_an_own_tab(call, strict):
    set_owner("t1", os.getpid())
    assert await call()


THREE_TABS = [
    {"id": "t1", "context": "c1", "url": "https://ok.com/a", "title": "Mine", "active": True},
    {"id": "t2", "context": "c2", "url": "https://ok.com/b", "title": "Theirs", "active": False},
    {"id": "t3", "context": "c3", "url": "https://ok.com/c", "title": "Loose", "active": False},
]


def set_owners(owners):
    safety.save_state(f"owners-{PORT}", {t: {"pid": p, "since": 1.0} for t, p in owners.items()})


@pytest.mark.parametrize("mode", ["strict", "sessions"])
async def test_list_tabs_tags_each_owner_state(mode, tmp_path, monkeypatch):
    make_env(tmp_path, monkeypatch, mode)
    server.browser.tabs_list = THREE_TABS
    set_owners({"t1": os.getpid(), "t2": os.getppid()})
    out = await server.list_tabs()
    assert "*t1 [yours] https://ok.com/a | Mine" in out
    assert " t2 [other session] https://ok.com/b | Theirs" in out
    assert " t3 [not attached] https://ok.com/c | Loose" in out


@pytest.mark.parametrize("mode", ["strict", "sessions"])
async def test_list_tabs_tags_a_blocked_line_after_the_id(mode, tmp_path, monkeypatch):
    make_env(tmp_path, monkeypatch, mode)
    server.browser.tabs_list = [{"id": "t4", "context": "c4", "url": "https://mail.example.com/", "title": "M", "active": False}]
    set_owners({"t4": os.getppid()})
    out = await server.list_tabs()
    assert " t4 [other session] [not allowlisted: mail.example.com" in out


async def test_list_tabs_off_output_is_unchanged(tmp_path, monkeypatch):
    make_env(tmp_path, monkeypatch, "off")
    server.browser.tabs_list = THREE_TABS
    set_owners({"t1": os.getpid(), "t2": os.getppid()})
    out = await server.list_tabs()
    assert "[yours]" not in out and "[other session]" not in out and "[not attached]" not in out
    assert "*t1 https://ok.com/a | Mine" in out
    assert " t2 https://ok.com/b | Theirs" in out
    assert " t3 https://ok.com/c | Loose" in out
