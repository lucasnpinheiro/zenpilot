---
status: TODO
progress: 0/4
updated: 2026-10-29
---
# e2e-flow — Zen real (manual)
1. Claude navega e clica na fixture `localhost:8000`, depois chama `run_report` → o retorno cita `recording.gif`; abrir o GIF: um frame por ação, sem o badge. Critérios 4, 7.
2. Posse (2 sessões Claude Code): A abre `new_tab`; B tenta `click` nela → Blocked 17; B chama `read_page` na aba ativa do usuário → Blocked 16; `attach_tab` → diálogo → Allow → B lê. Critérios 16, 17, 19.
3. Na fixture com `fetch` + `localStorage.setItem` + cookie httpOnly do servidor: `capture_page` → o HAR tem request e response com corpo; o storage.json tem a chave e o cookie httpOnly. Critérios 23-25.
4. Mouse (fixture local + gerfin.test/admin só com cliques de navegação): `hover` num item de menu (o cursor desliza), `click` num link do menu lateral, `click(button="right")` num texto (menu de contexto) e depois `press_key Escape`, `click(count=2)` num texto (seleção), `select` num filtro sem enviar, `scroll`, `mouse_move`/`click_at` num ponto de gráfico (tooltip), `drag` na fixture (lista arrastável). Screenshots provam o cursor. Critérios 29-35.
