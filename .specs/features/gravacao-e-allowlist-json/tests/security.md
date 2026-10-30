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
