---
id: T-011
status: TODO
progress: 0/2
updated: 2026-10-29
depends_on: []
---
# T-011 — `click` com `button` e `count`

1. `server.py` `click(ref, button="left", count=1)` valida (texto do 30). `browser.click`/`_click` recebem `button`/`count` e montam os pares `pointerDown`/`pointerUp` (0/2/1). O overlay recebe `kind` `right`/`double`. `mcpb/manifest.json` e docstring atualizados. `browser_batch` repassa os args.
2. RED: performActions gravado pelo fake → direito = button 2; duplo = 2 pares; padrão idêntico ao atual (o teste existente continua); inválidos → ToolError.
