"""Action overlay: show_actions config, what each action draws, and walker skipping it."""

import contextlib
import json
import shutil
import socket
import subprocess

import pytest
from test_interact_tools import FakeBiDi, connected_browser, sent
from zen_port import zen_port

from zenpilot import browser as browser_mod
from zenpilot import server, tree
from zenpilot.browser import MAX_ITEMS, Browser, BrowserError
from zenpilot.safety import DEFAULT_CONFIG, Config, load_config
from zenpilot.tree import Ref

OVERLAY_ID = "__zenpilot_overlay"


@pytest.fixture
def fake_bidi(monkeypatch):
    FakeBiDi.instances = []
    FakeBiDi.fail = None
    FakeBiDi.replies = {}
    monkeypatch.setattr(browser_mod, "BiDi", FakeBiDi)
    return FakeBiDi


async def shown_browser(fake_bidi):
    """Connected browser with the overlay on, as server.py sets it from config."""
    b, bidi = await connected_browser(fake_bidi)
    b.show_actions = True
    return b, bidi


@pytest.fixture
def calls(monkeypatch):
    """Record page-script calls with how many BiDi commands had been sent by then."""
    log = []
    replies = {
        "PREPARE": ["ok", "BUTTON", "", ""],
        "FORM": ["ok", "x"],
        "FILE": True,
        "RECT": [10.0, 20.0, 100.0, 40.0],
    }

    async def fake_run(self, context, fn, *args, timeout=15):
        bidi = FakeBiDi.instances[0]
        performed = len(sent(bidi, "input.performActions"))
        log.append({"fn": fn, "args": args, "timeout": timeout, "performed": performed})
        if fn is browser_mod.PREPARE_JS:
            return replies["PREPARE"]
        if fn is browser_mod.FORM_INPUT_JS:
            return replies["FORM"]
        if fn is browser_mod.IS_FILE_INPUT_JS:
            return replies["FILE"]
        if fn is browser_mod.RECT_JS:
            return replies["RECT"]
        return None

    monkeypatch.setattr(Browser, "run", fake_run)
    return log


def overlay_calls(log):
    return [c for c in log if c["fn"] is browser_mod.OVERLAY_JS]


# -- config -------------------------------------------------------------------


def test_show_actions_defaults_on(tmp_path):
    assert load_config(tmp_path / "config.toml").show_actions is True


def test_show_actions_false_turns_it_off(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("show_actions = false\n")
    assert load_config(path).show_actions is False


def test_default_config_documents_show_actions():
    assert (
        "# true draws a cursor, click ripple and highlight in the page before each click/type/hover\n"
        "# so you can watch what Claude does. Hidden from what Claude reads.\n" in DEFAULT_CONFIG
    )
    assert "show_actions = true" in DEFAULT_CONFIG


# -- what each action draws ---------------------------------------------------


async def test_click_draws_overlay_before_the_click(fake_bidi, calls):
    b, bidi = await shown_browser(fake_bidi)
    b.refs.add(Ref("t1", "c1", "s1", session=b._session))
    await b.click("r1")
    (call,) = overlay_calls(calls)
    assert call["args"][2:4] == ("click", "click")
    assert call["performed"] == 0  # drawn before the input action went out
    assert len(sent(bidi, "input.performActions")) == 1


async def test_click_overlay_gets_point_and_rect(fake_bidi, calls):
    b, _ = await shown_browser(fake_bidi)
    b.refs.add(Ref("t1", "c1", "s1", session=b._session))
    await b.click("r1")
    x, y, kind, label, rect = overlay_calls(calls)[0]["args"]
    assert (x, y) == (60.0, 40.0)  # center of the RECT reply
    assert rect == {"x": 10.0, "y": 20.0, "w": 100.0, "h": 40.0}


async def test_type_label_counts_chars_and_never_shows_text(fake_bidi, calls):
    b, _ = await shown_browser(fake_bidi)
    b.refs.add(Ref("t1", "c1", "s1", session=b._session))
    await b.type("r1", "hunter2", False)
    (call,) = overlay_calls(calls)
    assert call["args"][2:4] == ("type", "type 7 chars")
    assert "hunter2" not in call["args"][3]


async def test_hover_draws_hover_overlay(fake_bidi, calls):
    b, _ = await shown_browser(fake_bidi)
    b.refs.add(Ref("t1", "c1", "s1", session=b._session))
    await b.hover("r1")
    assert overlay_calls(calls)[0]["args"][2:4] == ("hover", "hover")


async def test_form_input_draws_type_overlay(fake_bidi, calls):
    b, _ = await shown_browser(fake_bidi)
    b.refs.add(Ref("t1", "c1", "s1", session=b._session))
    await b.form_input("r1", "Brasil")
    assert overlay_calls(calls)[0]["args"][2:4] == ("type", "set value")


async def test_file_upload_draws_click_overlay_with_file_count(fake_bidi, calls, tmp_path):
    b, _ = await shown_browser(fake_bidi)
    b.refs.add(Ref("t1", "c1", "s1", session=b._session))
    files = [str(tmp_path / "a"), str(tmp_path / "b")]
    await b.file_upload("r1", files)
    assert overlay_calls(calls)[0]["args"][2:4] == ("click", "upload 2 file(s)")


async def test_show_actions_off_draws_nothing(fake_bidi, calls):
    b, bidi = await shown_browser(fake_bidi)
    b.show_actions = False
    b.refs.add(Ref("t1", "c1", "s1", session=b._session))
    await b.click("r1")
    assert not overlay_calls(calls)
    assert not [c for c in calls if c["fn"] is browser_mod.RECT_JS]
    assert sent(bidi, "input.performActions")


async def test_overlay_failure_never_fails_the_click(fake_bidi, monkeypatch):
    b, bidi = await shown_browser(fake_bidi)
    b.refs.add(Ref("t1", "c1", "s1", session=b._session))
    real_run = Browser.run

    async def broken_overlay(self, context, fn, *args, timeout=15):
        if fn in (browser_mod.OVERLAY_JS, browser_mod.RECT_JS):
            raise BrowserError("Script error in page: boom")
        return await real_run(self, context, fn, *args, timeout=timeout)

    monkeypatch.setattr(Browser, "run", broken_overlay)
    fake_bidi.replies["script.callFunction"] = {
        "type": "success",
        "result": {"type": "array", "value": [{"type": "string", "value": v} for v in ("ok", "BUTTON", "", "")]},
    }
    assert await b.click("r1") == "Clicked r1."
    assert sent(bidi, "input.performActions")


async def test_overlay_is_short_timeout(fake_bidi, calls):
    b, _ = await shown_browser(fake_bidi)
    b.refs.add(Ref("t1", "c1", "s1", session=b._session))
    await b.hover("r1")
    assert overlay_calls(calls)[0]["timeout"] == 2


# -- overlay.js and walker ----------------------------------------------------


def test_overlay_js_is_a_bare_function_expression():
    src = browser_mod.OVERLAY_JS.strip()
    assert src.endswith("}")
    assert "(x, y, kind, label, rect) =>" in src


def test_overlay_js_is_hidden_and_builds_label_with_textcontent():
    src = browser_mod.OVERLAY_JS
    assert OVERLAY_ID in src
    assert 'aria-hidden", "true"' in src
    assert "pointer-events:none" in src
    assert "2147483647" in src
    assert "textContent" in src
    assert "innerHTML" not in src


def test_walker_skips_overlay_subtree():
    src = tree.WALKER_JS
    assert f'el.id === "{OVERLAY_ID}"' in src
    assert f'el.id === "{OVERLAY_ID}") continue' in src


@pytest.mark.integration
@pytest.mark.skipif(
    socket.socket().connect_ex(("127.0.0.1", zen_port())) != 0,
    reason="Zen is not listening on 127.0.0.1 at the configured port",
)
async def test_read_page_omits_overlay_live():
    b = Browser()
    await b.connect(zen_port())
    tid = await b.new_tab()
    try:
        tab = await b.tab(tid)
        await b.navigate(tab, "data:text/html," + "<main><button>Save</button></main>")
        rect = {"x": 40, "y": 40, "w": 20, "h": 20}
        await b.run(tab["context"], browser_mod.OVERLAY_JS, 50.0, 50.0, "click", "zzprobe", rect)
        out, _ = await b.run(tab["context"], tree.WALKER_JS, MAX_ITEMS, timeout=20)
        assert "zzprobe" not in json.dumps(out)
        assert "Save" in json.dumps(out)
    finally:
        await b.close_tab(await b.tab(tid))
        await b.close()


# -- config wiring in server.py -------------------------------------------------


class ProbeBrowser:
    stopped = False  # the badge's Stop button, read by every tool call

    def ref_key(self, key):
        return None

    async def mark(self, context, action=None):
        pass

    connected = True
    devtools_error = None

    def __init__(self, show_actions):
        self.show_actions = show_actions
        self.seen = []

    @contextlib.asynccontextmanager
    async def session(self, port):
        yield

    async def tabs(self):
        self.seen.append(self.show_actions)
        return []


@pytest.mark.parametrize("on", [True, False])
async def test_tool_call_sets_browser_show_actions_from_config(monkeypatch, tmp_path, on):
    cfg = Config(
        allowlist=["localhost"],
        read_only=False,
        allow_all_sites=False,
        port=9222,
        audit_log=tmp_path / "audit.jsonl",
        auto_launch=False,
        show_actions=on,
    )
    probe = ProbeBrowser(show_actions=not on)  # starts opposite, so only the tool wrapper can match config
    monkeypatch.setattr(server, "load_config", lambda *a, **k: cfg)
    monkeypatch.setattr(server, "browser", probe)
    await server.list_tabs()
    assert probe.seen == [on]


# -- cursor arrow and slide (T-010) -------------------------------------------

NODE = shutil.which("node")

# Minimal DOM stand-in: enough for overlay.js. Records every style write on each element.
OVERLAY_HARNESS = r"""
const src = process.argv[1];
const calls = JSON.parse(process.argv[2]);
const byId = {};
function mkStyle(el) {
  return new Proxy({}, {
    set(t, k, v) {
      el.writes.push([k, String(v)]);
      if (k === "cssText") {
        for (const decl of String(v).split(";")) {
          const i = decl.indexOf(":");
          if (i > 0) t[decl.slice(0, i).trim()] = decl.slice(i + 1).trim();
        }
      } else {
        t[k] = v;
      }
      return true;
    },
  });
}
function mk(tag, ns) {
  const el = { tag, ns, children: [], writes: [], attrs: {}, dataset: {}, isConnected: false, textContent: "" };
  el.style = mkStyle(el);
  el.setAttribute = (k, v) => { el.attrs[k] = String(v); };
  el.append = (...n) => n.forEach((c) => el.appendChild(c));
  el.appendChild = (c) => { el.children.push(c); c.parent = el; mark(c, true); return c; };
  el.remove = () => { mark(el, false); };
  el.querySelector = (sel) => find(el, sel.match(/data-part="(\w+)"/)[1]);
  return el;
}
function mark(el, on) { el.isConnected = on; if (el.id) byId[el.id] = on ? el : undefined; el.children.forEach((c) => mark(c, on)); }
function find(el, part) {
  if (el.dataset.part === part) return el;
  for (const c of el.children) { const f = find(c, part); if (f) return f; }
  return null;
}
const docEl = mk("html");
docEl.isConnected = true;
global.window = { innerWidth: 1000, innerHeight: 800 };
global.setTimeout = () => 0;
global.clearTimeout = () => {};
global.document = {
  documentElement: docEl,
  getElementById: (id) => byId[id] || null,
  createElement: (tag) => mk(tag, "html"),
  createElementNS: (ns, tag) => mk(tag, ns),
};
const overlay = eval("(" + src + ")");
const out = { calls: [] };
let root = null;
for (const c of calls) {
  const before = document.getElementById("__zenpilot_overlay");
  const startLeft = before ? find(before, "cursor").style.left : undefined;
  const startTop = before ? find(before, "cursor").style.top : undefined;
  const writesBefore = before ? find(before, "cursor").writes.length : 0;
  overlay(c.x, c.y, c.kind, "lbl", c.rect);
  root = document.getElementById("__zenpilot_overlay");
  const cursor = find(root, "cursor");
  const ripples = root.children.filter((e) => String(e.style.animation || "").includes("__zp_ripple")).length;
  out.calls.push({
    sameRoot: before === null ? null : before === root,
    startLeft, startTop,
    writes: cursor.writes.slice(writesBefore),
    left: cursor.style.left, top: cursor.style.top,
    transition: cursor.style.transition,
    svgTag: cursor.children[0] ? cursor.children[0].tag : null,
    svgNs: cursor.children[0] ? cursor.children[0].ns : null,
    svgAttrs: cursor.children[0] ? cursor.children[0].attrs : null,
    ripples,
  });
}
console.log(JSON.stringify(out));
"""


def run_overlay(calls):
    """Run overlay.js in node against the stand-in DOM; calls = [{x, y, kind, rect}, ...]."""
    out = subprocess.run(
        [NODE, "-e", OVERLAY_HARNESS, browser_mod.OVERLAY_JS, json.dumps(calls)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(out.stdout)["calls"]


RECT = {"x": 10, "y": 20, "w": 100, "h": 40}
needs_node = pytest.mark.skipif(NODE is None, reason="node not installed")


@needs_node
def test_cursor_is_svg_arrow_20px_with_fill_and_white_stroke():
    (c,) = run_overlay([{"x": 60, "y": 40, "kind": "click", "rect": RECT}])
    assert c["svgTag"] == "svg"
    assert c["svgNs"] == "http://www.w3.org/2000/svg"
    assert c["svgAttrs"]["width"] == "20" and c["svgAttrs"]["height"] == "20"
    assert "#e8590c" in browser_mod.OVERLAY_JS
    assert 'stroke", "#fff"' in browser_mod.OVERLAY_JS or "#fff" in browser_mod.OVERLAY_JS


@needs_node
def test_cursor_transition_slides_left_and_top_250ms():
    (c,) = run_overlay([{"x": 60, "y": 40, "kind": "click", "rect": RECT}])
    assert "left 250ms" in c["transition"]
    assert "top 250ms" in c["transition"]


@needs_node
def test_cursor_ends_on_the_point_tip_top_left():
    (c,) = run_overlay([{"x": 60, "y": 40, "kind": "click", "rect": RECT}])
    assert (c["left"], c["top"]) == ("60px", "40px")


@needs_node
def test_first_call_cursor_starts_at_viewport_center():
    (c,) = run_overlay([{"x": 60, "y": 40, "kind": "click", "rect": RECT}])
    lefts = [v for k, v in c["writes"] if k == "left"]
    tops = [v for k, v in c["writes"] if k == "top"]
    assert lefts[0] == "500px" and tops[0] == "400px"  # center first, then the target
    assert lefts[-1] == "60px" and tops[-1] == "40px"


@needs_node
def test_second_call_slides_from_previous_position():
    first, second = run_overlay(
        [
            {"x": 60, "y": 40, "kind": "click", "rect": RECT},
            {"x": 300, "y": 200, "kind": "hover", "rect": RECT},
        ]
    )
    assert second["sameRoot"] is True  # root reused, not rebuilt
    assert (second["startLeft"], second["startTop"]) == ("60px", "40px")
    assert (second["left"], second["top"]) == ("300px", "200px")
    assert ["left", "500px"] not in second["writes"]  # no re-centering on later calls


@needs_node
@pytest.mark.parametrize(
    ("kind", "ripples"),
    [("drag", 0), ("move", 0), ("right", 1), ("double", 2), ("click", 1)],
)
def test_new_kinds_and_ripples(kind, ripples):
    (c,) = run_overlay([{"x": 60, "y": 40, "kind": kind, "rect": RECT}])
    assert c["ripples"] == ripples


def test_show_pause_waits_for_the_slide():
    assert browser_mod.SHOW_PAUSE >= 0.25
