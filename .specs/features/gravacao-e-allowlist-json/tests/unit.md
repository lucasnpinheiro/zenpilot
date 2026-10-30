---
status: DONE
progress: 9/9
updated: 2026-10-29
---
# unit
| # | Caso | Esperado | Crit. |
| --- | --- | --- | --- |
| U1 | `allow --json` com allowlist + grant vigente + vencida | JSON válido no schema; só a vigente | 1 |
| U2 | `gif` com 3 steps de tamanhos diferentes (PIL) | GIF com 3 frames, tamanho do 1º, 800 ms, loop 0 | 4 |
| U3 | `gif` sem PIL | stderr `pip install 'zenpilot[gif]'`, exit 1 | 5 |
| U4 | `gif` sem steps / sem run | `No step screenshots in`, exit 1 | 6 |
| U5 | `prune_runs` | 25 dirs (3 > 7 dias, symlink, nome estranho) → 20 + symlink + estranho | 8 |
| U6 | pyproject | extra `gif`; `dependencies` iguais | 9 |
| U7 | config `tab_ownership="x"` | erro de config com o texto | 14 |
| U8 | claim/release/pid morto | arquivo correto; morto = sem dono | 15, 18 |
| U9 | `allow --json x` | exit 2 | 2 |
