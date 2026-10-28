"""The dialogs zenpilot shows: site access and the first-run profile choice (dialogs faked)."""

from dataclasses import replace

import pytest

from zenpilot import server
from zenpilot.safety import Config, load_config, set_config_value


@pytest.fixture
def env(tmp_path, monkeypatch):
    path = tmp_path / "config.toml"
    monkeypatch.setattr(server, "load_config", lambda: load_config(path))
    monkeypatch.setattr(server, "set_config_value", lambda k, v: set_config_value(k, v, path))
    monkeypatch.setattr(server, "_allowed_for_session", set())
    monkeypatch.setattr(server, "_declined", set())
    answers, asked = [], []

    def ask(message, buttons, default):
        asked.append((message, buttons, default))
        return answers.pop(0)

    monkeypatch.setattr(server.dialogs, "ask", ask)
    return path, answers, asked


def cfg():
    return Config(["localhost"], False, False, 9222, None, profile="Default (release)")


def test_always_allow_saves_to_the_allowlist(env):
    path, answers, asked = env
    answers.append("Always Allow")
    c = cfg()
    assert server._grant("github.com", c) is True
    assert "github.com" in c.allowlist and "github.com" in load_config(path).allowlist
    message, buttons, default = asked[0]
    assert "github.com" in message and "Default (release)" in message
    assert default == "Don't Allow"  # a stray Enter must not grant access


def test_allow_this_session_is_not_saved(env):
    path, answers, _ = env
    answers.append("Allow This Session")
    assert server._grant("github.com", cfg()) is True
    assert server._allowed_for_session == {"github.com"}
    assert "github.com" not in load_config(path).allowlist


@pytest.mark.parametrize("answer", ["Don't Allow", None])  # None: timed out
def test_declined_sites_are_not_asked_again(env, answer):
    _, answers, asked = env
    answers.append(answer)
    assert server._grant("evil.com", cfg()) is False
    assert server._grant("evil.com", cfg()) is False
    assert len(asked) == 1


def test_start_zen_uses_the_default_profile_without_asking(monkeypatch):
    monkeypatch.setattr(server, "port_open", lambda port: False)
    monkeypatch.setattr(server.dialogs, "choose", lambda *a: pytest.fail("asked which profile"))
    launched = []
    monkeypatch.setattr(server, "launch", lambda name, port, confirm: launched.append((name, port)) or True)
    server._start_zen(replace(cfg(), profile=None))
    assert launched == [(server.ZEN_DEFAULT, 9222)]
