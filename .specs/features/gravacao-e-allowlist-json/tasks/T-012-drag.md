---
id: T-012
status: TODO
progress: 0/2
updated: 2026-10-29
depends_on: [T-011]
---
# T-012 — Tool `drag`

1. `browser.drag(from_key, to_key)`: centros via `RECT_JS`; uma sequência `pointerMove`(from) → `pointerDown` → 10 `pointerMove` (`duration` 30 ms cada) até `to` → `pointerUp`; `_show(kind="drag")`; retorno = diff de página como em `click`. `server.py` `@tool(mutates=True)` `drag(from_ref, to_ref)`: `_check_ref` nos dois; contextos diferentes → ToolError do 31. Manifest + batch.
2. RED: a sequência exata de ações no fake; abas diferentes → erro; ref sem posse em strict → Blocked (marker `ownership`).
