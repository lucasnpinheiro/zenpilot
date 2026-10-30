---
id: T-013
status: DONE
progress: 2/2
updated: 2026-10-29
depends_on: [T-011]
---
# T-013 — `mouse_move` e `click_at`

1. `browser.viewport(tab)` (`window.innerWidth/innerHeight` via `run`); `browser.move_to(tab, x, y)` e `browser.click_at(tab, x, y, button, count)` com `origin: "viewport"`; overlay com o rect 1x1 em (x, y). `server.py`: `@tool(mutates=True)` `mouse_move(x, y, tab_id=None)` → "Moved to x, y."; `click_at(...)` → diff de página. Os dois via `_tab()` e com a checagem de viewport (texto do 32). Manifest + batch.
2. RED: performActions com `origin` viewport; fora da viewport → erro; aba sem posse → Blocked; botões/contagem como no 30.
