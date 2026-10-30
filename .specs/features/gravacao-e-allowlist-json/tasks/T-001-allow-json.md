---
id: T-001
status: TODO
progress: 0/2
updated: 2026-10-29
depends_on: []
---
# T-001 — `allow --json`

1. `cli.py:324`: `p.add_argument("--json", action="store_true")`. Em `allow()` (`cli.py:205`), com `args.json`: domínios ou `--remove` → stderr + `return 2` (2); senão `print(json.dumps({"allowlist": cfg.allowlist, "grants": grants(), "allow_all_sites": cfg.allow_all_sites}))` e `return 0` (1).
2. RED em `tests/test_cli.py`: saída valida contra o schema de 02; grant vencida fora; `--json x` → 2; sem `--json`, o texto fica idêntico (3).
