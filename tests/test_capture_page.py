"""capture_page: four files per call (HAR, console, DOM, storage + cookies), against fakes."""

import contextlib
import json
import types

import pytest
from mcp.server.mcpserver.exceptions import ToolError
from test_devtools_tools import FakeBiDi, console_event, fake_bidi, seed_request  # noqa: F401

from zenpilot import server
from zenpilot.bidi import BiDiError
from zenpilot.browser import Browser, BrowserError
from zenpilot.devtools import Devtools
from zenpilot.history import History
from zenpilot.safety import Config


class FakePageBrowser:
    stopped = False
    connected = True

    def __init__(self):
        self.devtools = Devtools()
        self.devtools_error = None
        self.url = "http://localhost:8000/"
        self.cookie_error = None
        self.storage_error = None
        self.cookie_list = [{"name": "sid", "value": "secret", "httpOnly": True}]
        self.storage_data = {"localStorage": {"a": "1"}, "sessionStorage": {"b": "2"}}

    def ref_key(self, key):
        return None

    async def mark(self, context, action=None):
        pass

    @contextlib.asynccontextmanager
    async def session(self, port):
        yield

    async def tab(self, tab_id):
        return {"id": "t1", "context": "c1", "url": self.url, "active": True, "title": ""}

    async def read_page(self, tab, frame_allowed):
        return "button r1 Go"

    def dialog_note(self, context):
        return None

    async def response_body(self, request_id):
        return "<html>hi</html>", False

    async def cookies(self, context):
        if self.cookie_error:
            raise self.cookie_error
        return list(self.cookie_list)

    async def storage(self, tab):
        if self.storage_error:
            raise self.storage_error
        return self.storage_data


@pytest.fixture
def cap(monkeypatch, tmp_path):
    cfg = Config(
        allowlist=["localhost"],
        read_only=False,
        allow_all_sites=False,
        port=9222,
        audit_log=tmp_path / "audit.jsonl",
        auto_launch=False,
        prompts=False,
    )
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    hist = History()
    hist.run_dir = lambda base=None: run_dir
    fb = FakePageBrowser()
    monkeypatch.setattr(server, "load_config", lambda *a, **k: cfg)
    monkeypatch.setattr(server, "browser", fb)
    monkeypatch.setattr(server, "HISTORY", hist)
    seed_request(fb.devtools, "r1", "http://localhost:8000/", 200)
    fb.devtools.on_log(console_event("boom", "error"))
    return types.SimpleNamespace(browser=fb, run_dir=run_dir, cfg=cfg)


async def test_capture_writes_four_files_and_summary(cap):
    out = await server.capture_page()
    d = cap.run_dir
    assert out == f"Captured t1: 1 requests, 1 console, 1 cookies → {d}/capture-1*"
    har = json.loads((d / "capture-1.har").read_text())
    assert len(har["log"]["entries"]) == 1
    assert har["log"]["entries"][0]["response"]["content"]["text"] == "<html>hi</html>"
    console = json.loads((d / "capture-1-console.json").read_text())
    assert [e["text"] for e in console] == ["boom"]
    dom = (d / "capture-1-dom.txt").read_text()
    assert "button r1 Go" in dom
    st = json.loads((d / "capture-1-storage.json").read_text())
    assert st == {
        "url": "http://localhost:8000/",
        "localStorage": {"a": "1"},
        "sessionStorage": {"b": "2"},
        "cookies": [{"name": "sid", "value": "[redacted]", "httpOnly": True}],
    }


async def test_second_call_is_n2_and_never_overwrites(cap):
    await server.capture_page()
    out = await server.capture_page()
    assert out.endswith("capture-2*")
    assert (cap.run_dir / "capture-1.har").exists() and (cap.run_dir / "capture-2.har").exists()


async def test_outside_allowlist_blocks_and_writes_nothing(cap):
    cap.browser.url = "http://evil.example/"
    with pytest.raises(ToolError, match="not on the zenpilot allowlist"):
        await server.capture_page()
    assert list(cap.run_dir.iterdir()) == []


async def test_cookies_failure_gives_empty_list_and_note(cap):
    cap.browser.cookie_error = BiDiError("unknown command", "no storage")
    out = await server.capture_page()
    assert "0 cookies" in out
    assert "(cookies failed: " in out
    st = json.loads((cap.run_dir / "capture-1-storage.json").read_text())
    assert st["cookies"] == []
    assert st["localStorage"] == {"a": "1"}


async def test_storage_failure_skips_storage_keeps_the_rest(cap):
    cap.browser.storage_error = BrowserError("JavaScript error: boom")
    out = await server.capture_page()
    assert "(storage failed: " in out
    assert not (cap.run_dir / "capture-1-storage.json").exists()
    assert (cap.run_dir / "capture-1.har").exists()
    assert (cap.run_dir / "capture-1-console.json").exists()
    assert (cap.run_dir / "capture-1-dom.txt").exists()


async def test_read_page_output_unchanged(cap):
    out = await server.read_page()
    assert out.startswith("Tab t1\n")
    assert "button r1 Go" in out


async def test_browser_storage_cuts_values_over_10000(fake_bidi):  # noqa: F811
    b = Browser()
    await b.connect(9222)
    big = "x" * 10_001
    payload = json.dumps({"localStorage": {"k": big, "ok": "y" * 10_000}, "sessionStorage": {}})
    fake_bidi.replies["script.evaluate"] = {"type": "success", "result": {"type": "string", "value": payload}}
    data = await b.storage({"context": "c1"})
    assert data["localStorage"]["k"] == "x" * 10_000 + "…"
    assert data["localStorage"]["ok"] == "y" * 10_000
    assert data["sessionStorage"] == {}


async def test_browser_cookies_shape_and_partition(fake_bidi):  # noqa: F811
    b = Browser()
    await b.connect(9222)
    fake_bidi.replies["storage.getCookies"] = {
        "cookies": [
            {
                "name": "sid",
                "value": {"type": "string", "value": "abc"},
                "domain": "localhost",
                "path": "/",
                "httpOnly": True,
                "secure": False,
                "sameSite": "lax",
                "expiry": 99,
                "size": 6,
            },
            {"name": "bin", "value": {"type": "base64", "value": "aGk="}, "domain": "localhost", "path": "/"},
        ]
    }
    cookies = await b.cookies("c1")
    sent = [p for m, p in fake_bidi.instances[0].sent if m == "storage.getCookies"][-1]
    assert sent == {"partition": {"type": "context", "context": "c1"}}
    assert cookies[0] == {
        "name": "sid",
        "value": "abc",
        "domain": "localhost",
        "path": "/",
        "httpOnly": True,
        "secure": False,
        "sameSite": "lax",
        "expiry": 99,
    }
    assert cookies[1]["value"] == "aGk=" and cookies[1]["encoding"] == "base64"


async def test_default_mode_masks_httponly_value_only(cap):
    cap.browser.cookie_list = [
        {"name": "sid", "value": "secret", "httpOnly": True},
        {"name": "theme", "value": "dark", "httpOnly": False},
    ]
    out = await server.capture_page()
    assert out.endswith("2 cookies → " + str(cap.run_dir) + "/capture-1*")
    st = json.loads((cap.run_dir / "capture-1-storage.json").read_text())
    assert st["cookies"] == [
        {"name": "sid", "value": "[redacted]", "httpOnly": True},
        {"name": "theme", "value": "dark", "httpOnly": False},
    ]


async def test_page_mode_keeps_only_non_httponly_names_in_document_cookie(cap):
    cap.cfg.capture_cookies = "page"
    cap.browser.cookie_list = [
        {"name": "sid", "value": "secret", "httpOnly": True},
        {"name": "theme", "value": "dark", "httpOnly": False},
        {"name": "lang", "value": "pt", "httpOnly": False},
        {"name": "other", "value": "x", "httpOnly": False},
    ]
    cap.browser.storage_data = {
        "localStorage": {},
        "sessionStorage": {},
        "cookie": "theme=dark; lang=pt; sid=page-view",
    }
    out = await server.capture_page()
    assert "2 cookies" in out
    st = json.loads((cap.run_dir / "capture-1-storage.json").read_text())
    assert st["cookies"] == [
        {"name": "theme", "value": "dark", "httpOnly": False},
        {"name": "lang", "value": "pt", "httpOnly": False},
    ]
    assert "cookie" not in st


async def test_all_mode_keeps_every_cookie_value(cap):
    cap.cfg.capture_cookies = "all"
    cap.browser.cookie_list = [
        {"name": "sid", "value": "secret", "httpOnly": True},
        {"name": "theme", "value": "dark", "httpOnly": False},
    ]
    await server.capture_page()
    st = json.loads((cap.run_dir / "capture-1-storage.json").read_text())
    assert st["cookies"] == [
        {"name": "sid", "value": "secret", "httpOnly": True},
        {"name": "theme", "value": "dark", "httpOnly": False},
    ]
