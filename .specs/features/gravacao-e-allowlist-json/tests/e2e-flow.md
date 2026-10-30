---
status: TODO
progress: 0/2
updated: 2026-10-29
---
# e2e-flow — Zen real (manual)
1. Claude navega e clica na fixture `localhost:8000`, depois chama `run_report` → o retorno cita `recording.gif`; abrir o GIF: um frame por ação, sem o badge. Critérios 4, 7.
2. Posse (2 sessões Claude Code): A abre `new_tab`; B tenta `click` nela → Blocked 17; B chama `read_page` na aba ativa do usuário → Blocked 16; `attach_tab` → diálogo → Allow → B lê. Critérios 16, 17, 19.
