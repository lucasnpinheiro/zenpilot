---
status: TODO
progress: 0/1
updated: 2026-10-29
---
# unit
| # | Caso | Esperado | Crit. |
| --- | --- | --- | --- |
| U1 | `allow --json` com allowlist+grant vigente+vencida | JSON válido no schema; só a vigente | 1 |
| U2 | `record start` 2x | 2ª: `Already recording to` exit 0 | 4 |
| U3 | `record stop` sem start | `Not recording` exit 1 | 8 |
| U4 | stop com 0 frames | HTML "No frames recorded", sem GIF | 12 |
| U5 | stop sem PIL (monkeypatch import) | mensagem `pip install 'zenpilot[gif]'` | 7 |
| U6 | pyproject | `gif` extra; `dependencies` = mcp, websockets | 11 |
| U7 | cap | frame 501 não grava; audit `record_cap` | 9 |
| U8 | retenção | 25 dirs (3 > 7 dias, 1 symlink, 1 nome estranho) → sobram 20 + symlink + estranho | 13 |
| U9 | config `tab_ownership="x"` | erro de config com o texto | 14 |
| U10 | claim/release/pid morto | arquivo de donos correto; morto = sem dono | 15, 18 |