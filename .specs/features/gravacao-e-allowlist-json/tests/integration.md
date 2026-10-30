---
status: TODO
progress: 0/6
updated: 2026-10-29
---
# integration — tools com browser falso
| # | Caso | Esperado | Crit. |
| --- | --- | --- | --- |
| I1 | `run_report` com steps + PIL · sem PIL | ` GIF: <path>.` · retorno igual | 7 |
| I2 | strict: aba sem dono · aba ativa sem `tab_id` | Blocked 16 | 16 |
| I3 | aba de pid vivo alheio (strict e sessions) | Blocked 17; `attach_tab` também | 17 |
| I4 | `attach_tab` Allow/Don't/None/prompts off/já minha | textos 19, 20 | 19, 20 |
| I5 | `list_tabs` strict · off | marcas · saída atual | 21, 22 |
| I6 | `capture_page` ok · fora da allowlist · getCookies falha · storage longo · 2ª chamada | 4 arquivos + retorno · nada · nota · corte · `n=2` | 23-27 |
