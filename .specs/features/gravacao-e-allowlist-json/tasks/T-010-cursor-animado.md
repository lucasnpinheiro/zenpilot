---
id: T-010
status: TODO
progress: 0/2
updated: 2026-10-29
depends_on: []
---
# T-010 — Cursor em seta deslizando no overlay

1. `src/zenpilot/overlay.js`: a parte `cursor` vira uma seta SVG de 20 px (cor `COLOR`, contorno branco, ponta em (x, y)) com `transition: left 250ms, top 250ms`. Na criação do root, começa no centro da viewport. Como o root é reaproveitado entre chamadas, o cursor desliza da posição anterior. `browser._show` espera a transição (`SHOW_PAUSE` ≥ 0.25 s). `kind` novos: `drag`, `move`, `right`, `double` (rótulo do chip).
2. RED em `tests/test_overlay.py` (o mesmo estilo que roda o JS): cursor com `<svg`, a `transition` presente e `left`/`top` iguais a (x, y) depois da chamada; a segunda chamada parte da posição anterior (o estilo inicial lido antes da mudança).
