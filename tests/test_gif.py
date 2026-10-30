"""zenpilot gif: recording.gif from a run's step screenshots, the CLI command and the run_report tail."""

import builtins
import tomllib
import types
from pathlib import Path

import pytest

from zenpilot import cli, gif, history


def _jpg(path: Path, size: tuple[int, int], color) -> None:
    Image = pytest.importorskip("PIL.Image")
    Image.new("RGB", size, color).save(path, "JPEG")


@pytest.fixture
def no_pillow(monkeypatch):
    real = builtins.__import__

    def fake(name, *a, **k):
        if name == "PIL" or name.startswith("PIL."):
            raise ImportError("no PIL")
        return real(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake)


def _run(monkeypatch, tmp_path, name="20260101T000000Z-abcd"):
    monkeypatch.setattr(history, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(cli, "RUNS_DIR", tmp_path / "runs", raising=False)
    d = tmp_path / "runs" / name
    d.mkdir(parents=True)
    return d


def _args(run=None):
    return types.SimpleNamespace(run=run)


# -- U2 -----------------------------------------------------------------------


def test_write_gif_three_steps_first_size_800ms_loop_forever(tmp_path):
    Image = pytest.importorskip("PIL.Image")
    _jpg(tmp_path / "step-0002.jpg", (40, 30), "green")
    _jpg(tmp_path / "step-0001.jpg", (20, 10), "red")
    _jpg(tmp_path / "step-0003.jpg", (60, 60), "blue")
    out = gif.write_gif(tmp_path)
    assert out == tmp_path / "recording.gif"
    with Image.open(out) as im:
        assert im.n_frames == 3
        assert im.size == (20, 10)
        assert im.info["duration"] == 800
        assert im.info["loop"] == 0


def test_write_gif_no_steps(tmp_path):
    with pytest.raises(gif.NoSteps, match="No step screenshots in"):
        gif.write_gif(tmp_path)


def test_write_gif_without_pillow(tmp_path, no_pillow):
    (tmp_path / "step-0001.jpg").write_bytes(b"x")
    with pytest.raises(gif.NoPillow):
        gif.write_gif(tmp_path)


# -- CLI (U2-U4, V2) ----------------------------------------------------------


def test_cli_gif_default_is_newest_run(tmp_path, monkeypatch, capsys):
    pytest.importorskip("PIL")
    old = _run(monkeypatch, tmp_path, "20250101T000000Z-aaaa")
    new = _run(monkeypatch, tmp_path, "20260101T000000Z-bbbb")
    (tmp_path / "runs" / "junk").mkdir()
    _jpg(old / "step-0001.jpg", (8, 8), "red")
    _jpg(new / "step-0001.jpg", (8, 8), "red")
    assert cli.gif_cmd(_args()) == 0
    assert capsys.readouterr().out == f"GIF: {new / 'recording.gif'}\n"
    assert (new / "recording.gif").exists() and not (old / "recording.gif").exists()


def test_cli_gif_without_pillow(tmp_path, monkeypatch, capsys, no_pillow):
    d = _run(monkeypatch, tmp_path)
    (d / "step-0001.jpg").write_bytes(b"x")
    assert cli.gif_cmd(_args()) == 1
    assert capsys.readouterr().err.strip() == "GIF: pip install 'zenpilot[gif]'"


def test_cli_gif_without_steps(tmp_path, monkeypatch, capsys):
    d = _run(monkeypatch, tmp_path)
    assert cli.gif_cmd(_args()) == 1
    assert f"No step screenshots in {d}" in capsys.readouterr().err


def test_cli_gif_no_runs_at_all(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "RUNS_DIR", tmp_path / "none", raising=False)
    assert cli.gif_cmd(_args()) == 1
    assert "No step screenshots in" in capsys.readouterr().err


def test_cli_gif_missing_path(tmp_path, capsys):
    missing = tmp_path / "inexistente"
    assert cli.gif_cmd(_args(str(missing))) == 1
    assert f"No step screenshots in {missing}" in capsys.readouterr().err


# -- U6 -----------------------------------------------------------------------


def test_pyproject_gif_extra_and_unchanged_dependencies():
    data = tomllib.loads((Path(__file__).parent.parent / "pyproject.toml").read_text())
    assert data["project"]["optional-dependencies"]["gif"] == ["Pillow>=10"]
    assert data["project"]["dependencies"] == ["mcp>=2.3,<3", "websockets>=15,<18"]
