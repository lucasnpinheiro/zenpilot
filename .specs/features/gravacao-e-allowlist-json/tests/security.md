---
status: DONE
progress: 5/5
updated: 2026-10-29
---
# security
| # | Risco | Esperado | Crit. |
| --- | --- | --- | --- |
| S1 | symlink em `runs/` apontando para ~ | não é seguido nem apagado | 8 |
| S2 | sessão B tenta clicar na aba da sessão A | Blocked 17, inclusive via attach | 17 |
| S3 | página fora da allowlist numa aba anexada | a allowlist continua valendo (`_tab`) | 19 |
| S4 | `type` com senha | o GIF não desenha args; `report.json` já redige (existente) | 10 |
| S5 | `capture_page` numa aba de outra sessão / fora da allowlist | Blocked; nenhum arquivo com cookies | 24, 26 |
