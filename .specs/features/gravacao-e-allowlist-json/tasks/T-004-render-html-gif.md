---
id: T-004
status: DONE
progress: 3/3
updated: 2026-10-29
depends_on: []
---
# T-004 — `zenpilot gif` + GIF no `run_report`

1. Novo `src/zenpilot/gif.py`: `write_gif(run_dir) -> Path` (import do PIL dentro da função; `ImportError` → exceção própria `NoPillow`; sem `step-*.jpg` → `NoSteps`), frames por seq, 800 ms, `loop=0`, redimensionados ao primeiro (4).
2. `cli.py`: subcomando `gif [run]` (default: `max()` dos nomes válidos em `RUNS_DIR`); mensagens e exit codes 4-6. `server.py` `run_report`: depois de `write_report`, tenta `write_gif`; sucesso → acrescenta ` GIF: <path>.`; `NoPillow`/`NoSteps` → retorno igual (7).
3. `pyproject.toml` extra `gif = ["Pillow>=10"]` (9); README seção "GIF". RED: `pytest.importorskip("PIL")` para os testes que geram o GIF; teste sem PIL via monkeypatch de `builtins.__import__`; `run_report` com e sem steps.
