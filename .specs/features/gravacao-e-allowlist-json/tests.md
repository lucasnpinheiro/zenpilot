---
status: TODO
progress: 0/9
updated: 2026-10-29
---
# Tests — design (zenpilot)

Runner: `uv run pytest -q` (um exit code). Coverage plan: 12/12 critérios com teste (100%); `recording.py` com teste direto em todas as funções; meta ≥93% de linha via `pytest --cov=zenpilot.recording` (pytest-cov já usado? não verificado → instalar só no dev se faltar).

| Tipo | Arquivo | Critérios |
| --- | --- | --- |
| unit | [tests/unit.md](tests/unit.md) | 1-4, 7-9, 11, 12 |
| integration | [tests/integration.md](tests/integration.md) | 5, 6, 10 |
| e2e-flow | [tests/e2e-flow.md](tests/e2e-flow.md) | 4, 5, 7 |
| validation | [tests/validation.md](tests/validation.md) | 2 |
| business-rules | [tests/business-rules.md](tests/business-rules.md) | 3, 9 |
| ui-design | [tests/ui-design.md](tests/ui-design.md) | 7, 12 |
| load-k6 | [tests/load-k6.md](tests/load-k6.md) | N/A |
| security | [tests/security.md](tests/security.md) | 5, 7 |
| e2e-regression | [tests/e2e-regression.md](tests/e2e-regression.md) | suíte atual |
