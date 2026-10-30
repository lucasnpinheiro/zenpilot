---
id: T-002
status: TODO
progress: 0/2
updated: 2026-10-29
depends_on: []
---
# T-002 — Retenção de `runs/`

1. `history.py`: `prune_runs(base, keep=20, max_days=7, now)` — só subdiretórios reais (`is_dir()` e não `is_symlink()`) com nome `^\d{8}T\d{6}Z-[0-9a-f]{4}$`; apaga os com data do nome > 7 dias e depois os mais antigos além de 20; `shutil.rmtree(ignore_errors=True)`. `History.run_dir()` chama na primeira criação do diretório do run (`not path.exists()` antes do `mkdir`) (8).
2. RED em `tests/test_history.py`: 25 dirs (3 com mais de 7 dias), 1 symlink, 1 nome estranho → sobram 20 + symlink + estranho; a segunda chamada de `run_dir()` não apaga nada.
