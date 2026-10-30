---
status: TODO
progress: 0/4
updated: 2026-10-29
---
# Tasks — zenpilot (DAG)

TDD com `uv run pytest -q` (baseline 99 passed / 14 skipped). PR só no fork `lucasnpinheiro/zenpilot` (`gh pr create --repo lucasnpinheiro/zenpilot --base main`).

| ID | Título | depends_on | security-sensitive | Critérios |
| --- | --- | --- | --- | --- |
| [T-001](T-001-allow-json.md) | `allow --json` | — | sim (allowlist) | 1-3 |
| [T-002](T-002-record-cli.md) | estado + `record start\|stop` (sem render) | — | não | 4, 8 |
| [T-003](T-003-captura-frames.md) | captura no decorator `tool()` | T-002 | sim (redação) | 5, 6, 9, 10 |
| [T-004](T-004-render-html-gif.md) | `recording.html` + GIF opcional + extra | T-002, T-003 | não | 7, 11, 12 |
