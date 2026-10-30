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
