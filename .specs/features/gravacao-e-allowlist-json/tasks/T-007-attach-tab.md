---
id: T-007
status: DONE
progress: 2/2
updated: 2026-10-29
depends_on: [T-005]
---
# T-007 — Tool `attach_tab`

1. `server.py`: `@tool()` `attach_tab(tab_id)`; diálogo via `dialogs.ask` em thread (padrão de `_grant`, `server.py:249`); respostas e textos dos critérios 19 e 20; `attach_tab` numa aba de outra sessão viva → texto 17.
2. RED: Allow/Don't Allow/None (`dialogs.ask` falso); `prompts=false`; já minha.
