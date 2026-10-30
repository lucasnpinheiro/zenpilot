import dataclasses

import pytest

from zenpilot import safety, server


class _OwnershipOff:
    """Wraps server._cfg so tool tests act on unowned fake tabs; `ownership`-marked tests keep the real mode."""

    def __init__(self, cfg):
        self._cfg = cfg

    def set(self, value):
        return self._cfg.set(value)

    def get(self):
        return dataclasses.replace(self._cfg.get(), tab_ownership="off")


@pytest.fixture(autouse=True)
def state_dir(tmp_path, monkeypatch):
    """Tab ids and site grants go to a temp folder, never the user's."""
    monkeypatch.setattr(safety, "STATE_DIR", tmp_path / "state")
    return tmp_path / "state"


@pytest.fixture(autouse=True)
def ownership_off(request, monkeypatch):
    """Existing tool tests predate tab ownership (default strict): run them with tab_ownership = "off"."""
    if request.node.get_closest_marker("ownership") is None:
        monkeypatch.setattr(server, "_cfg", _OwnershipOff(server._cfg))
