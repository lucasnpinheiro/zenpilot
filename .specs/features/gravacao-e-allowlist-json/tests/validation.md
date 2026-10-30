---
status: TODO
progress: 0/2
updated: 2026-10-29
---
# validation
| # | Entrada | Esperado | Crit. |
| --- | --- | --- | --- |
| V1 | `allow --json gerfin.test` · `allow --json --remove x` | exit 2, stderr com a mensagem | 2 |
| V2 | `gif /caminho/inexistente` | `No step screenshots in`, exit 1 | 6 |
