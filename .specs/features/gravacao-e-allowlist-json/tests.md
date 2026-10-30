---
status: TODO
progress: 0/9
updated: 2026-10-29
---
# Tests — design (zenpilot)

Runner: `uv run pytest -q` (um exit code). Coverage plan: 24/24 critérios ativos com teste (100%); `recording.py` com teste direto em todas as funções; meta ≥93% de linha via `pytest --cov=zenpilot.recording` (pytest-cov já usado? não verificado → instalar só no dev se faltar).

| Tipo | Arquivo | Critérios |
| --- | --- | --- |
| unit | [tests/unit.md](tests/unit.md) | 1-6, 8, 9, 14, 15, 18 |
| integration | [tests/integration.md](tests/integration.md) | 7, 16, 17, 19-27 |
| e2e-flow | [tests/e2e-flow.md](tests/e2e-flow.md) | 4, 7, 16, 17, 19 |
| validation | [tests/validation.md](tests/validation.md) | 2 |
| business-rules | [tests/business-rules.md](tests/business-rules.md) | 3, 10 |
| ui-design | [tests/ui-design.md](tests/ui-design.md) | 4 |
| load-k6 | [tests/load-k6.md](tests/load-k6.md) | N/A |
| security | [tests/security.md](tests/security.md) | 8, 10, 17, 19, 24, 26 |
| e2e-regression | [tests/e2e-regression.md](tests/e2e-regression.md) | suíte atual |
