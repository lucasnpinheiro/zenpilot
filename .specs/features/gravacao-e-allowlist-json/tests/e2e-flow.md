---
status: TODO
progress: 0/1
updated: 2026-10-29
---
# e2e-flow — Zen real (manual)
1. `zenpilot record start` → 2. Claude navega na fixture `localhost:8000`, clica, digita → 3. `zenpilot record stop` → abrir `recording.html` no Zen: N frames, ←/→ funciona, o badge não aparece nos frames; com Pillow, o GIF anima. Critérios 4, 5, 7.

Posse (2 sessões Claude Code): A abre `new_tab` na fixture; B tenta `click` nessa aba → Blocked 17; B chama `read_page` na aba ativa do usuário → Blocked 16; `attach_tab` → diálogo → Allow → B lê. Critérios 16, 17, 19.