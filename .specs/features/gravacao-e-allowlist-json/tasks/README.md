---
status: DONE
progress: 9/9
updated: 2026-10-29
---
# Tasks — zenpilot (DAG)

TDD com `uv run pytest -q` (baseline = suíte verde depois do PR `fix/merge-4234797`). Âncoras por nome de função. PR só no fork `lucasnpinheiro/zenpilot` (`gh pr create --repo lucasnpinheiro/zenpilot --base main`).

| ID | Título | depends_on | security-sensitive | Critérios |
| --- | --- | --- | --- | --- |
| [T-001](T-001-allow-json.md) | `allow --json` | — | sim (allowlist) | 1-3 |
| [T-002](T-002-record-cli.md) | retenção de `runs/` em `History.run_dir()` | — | sim (apaga dirs) | 8 |
| [T-003](T-003-captura-frames.md) | (descartada — o fork já captura por ação) | — | — | — |
| [T-004](T-004-render-html-gif.md) | `zenpilot gif` + GIF no `run_report` + extra `gif` | — | não | 4-7, 9, 10 |
| [T-005](T-005-config-e-donos.md) | `tab_ownership` + `owners-<port>.json` | — | sim | 14, 15, 18, 22 |
| [T-006](T-006-checagem-em-tab.md) | checagem de posse em `_tab()` | T-005 | sim (**breaking**: default strict) | 16, 17 |
| [T-007](T-007-attach-tab.md) | tool `attach_tab` + diálogo | T-005 | sim | 19, 20 |
| [T-008](T-008-list-tabs-dono.md) | `list_tabs` com o dono | T-005 | não | 21 |
| [T-009](T-009-capture-page.md) | tool `capture_page` | T-006 | sim (cookies) | 23-27 |
