---
status: TODO
progress: 0/1
updated: 2026-10-29
---
# integration — decorator `tool()` com browser falso
| # | Caso | Esperado | Crit. |
| --- | --- | --- | --- |
| I1 | gravando + `click` ok | `0001.jpg` + linha em frames.jsonl | 5 |
| I2 | gravando + screenshot lança | a tool ok; audit `record_error` | 6 |
| I3 | gravando + `get_text`, `scroll`, `close_tab` | nenhum frame | 10 |
| I4 | strict: aba sem dono · aba ativa sem `tab_id` | Blocked 16 | 16 |
| I5 | aba de pid vivo alheio (strict e sessions) | Blocked 17; `attach_tab` também | 17 |
| I6 | `attach_tab` Allow/Don't/None/prompts off/já minha | textos 19, 20 | 19, 20 |
| I7 | `list_tabs` strict · off | marcas · saída atual | 21, 22 |