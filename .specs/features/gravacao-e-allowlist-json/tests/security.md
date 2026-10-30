---
status: TODO
progress: 0/1
updated: 2026-10-29
---
# security
| # | Risco | Esperado | Crit. |
| --- | --- | --- | --- |
| S1 | `type` com senha | frames.jsonl tem `{"chars": N}`, nunca o texto | 5 |
| S2 | url com `<script>` na legenda | escapada no HTML | 7 |
| S3 | aba fora da allowlist | `screenshot` já falha em `_tab`; nenhum frame | 5 |
| S4 | symlink em recordings/ apontando para ~ | não é seguido nem apagado | 13 |
| S5 | sessão B tenta clicar na aba da sessão A | Blocked 17, inclusive via attach | 17 |
| S6 | página fora da allowlist numa aba anexada | a allowlist continua valendo (`_tab`) | 19 |