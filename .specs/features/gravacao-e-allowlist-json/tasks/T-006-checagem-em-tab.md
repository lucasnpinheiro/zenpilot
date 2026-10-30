---
id: T-006
status: TODO
progress: 0/2
updated: 2026-10-29
depends_on: [T-005]
---
# T-006 — Checagem de posse em `_tab()`

1. `server.py:277` `_tab()`: depois de `browser.tab(tab_id)`, aplica 16/17 conforme `cfg.tab_ownership`, com os textos literais. `new_tab` chama `claim` e `close_tab` chama `release` (15).
2. RED em `tests/test_server.py` com browser falso: strict + aba sem dono → Blocked 16; aba de outro pid vivo (`os.getppid()`) → Blocked 17; `sessions` + sem dono → passa; `off` → passa; a suíte antiga roda com `tab_ownership="off"` no fixture de config, para não mudar asserts (e2e-regression).
