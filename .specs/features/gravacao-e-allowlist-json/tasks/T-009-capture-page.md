---
id: T-009
status: TODO
progress: 0/3
updated: 2026-10-29
depends_on: [T-006]
---
# T-009 — Tool `capture_page`

1. `browser.py`: `cookies(context)` via BiDi `storage.getCookies` com partition de contexto; `storage(tab)` via `evaluate` de um script fixo que devolve JSON de `localStorage`/`sessionStorage` (valores cortados em 10 000) (24, 25).
2. `server.py`: `@tool()` `capture_page(tab_id=None)` — `tab = await _tab(tab_id)` (allowlist + posse, 26); reusa `har()`/`_har_bodies()`, `browser.devtools.console(context)` e o mesmo texto do `read_page` (extrair o miolo do `read_page` para uma função interna, sem mudar a saída dele); grava os 4 arquivos com `n` sequencial; pedaço que falha vira nota no retorno (Swept).
3. RED com browser falso (`tests/test_devtools_tools.py` como modelo): 4 arquivos e o texto do retorno; aba fora da allowlist → nada gravado; `getCookies` falha → `cookies: []` + nota; valor de storage com 10 001 caracteres → cortado; `n` = 2 na 2ª chamada.
