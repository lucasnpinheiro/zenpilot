---
id: T-002
status: TODO
progress: 0/2
updated: 2026-10-29
depends_on: []
---
# T-002 — Estado da gravação + `record start|stop`

1. Novo módulo `src/zenpilot/recording.py`: `start() -> (dir, already)`, `active() -> dict | None`, `stop() -> dict | None`, sobre `load_state`/`save_state("recording")` (Decided 2); diretório `STATE_DIR/recordings/<UTC>`.
2. `cli.py`: subparser `record` com `action` em `{start, stop}`; mensagens e exit codes dos critérios 4 e 8 (o render do stop vem em T-004; aqui o stop só fecha o estado). RED em `tests/test_recording.py` com `ZENPILOT_STATE` em `tmp_path`.
