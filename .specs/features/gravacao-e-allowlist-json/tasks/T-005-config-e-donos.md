---
id: T-005
status: DONE
progress: 2/2
updated: 2026-10-29
depends_on: []
---
# T-005 — Config `tab_ownership` + arquivo de donos

1. `safety.py`: chave no `DEFAULT_CONFIG` com comentário, campo em `Config`, validação em `load_config` (14). Novo `owners.py` (ou funções em `safety.py`): `owner_of(port, tab)`, `claim(port, tab)`, `release(port, tab)`, `alive(pid)` sobre `load_state`/`save_state("owners-<port>")`, relendo antes de gravar (15, 18). `off` → nada roda (22).
2. RED em `tests/test_safety.py`: valor inválido; claim/release; pid morto (pid de um processo encerrado) = sem dono.
