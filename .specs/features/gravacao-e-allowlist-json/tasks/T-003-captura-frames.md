---
id: T-003
status: TODO
progress: 0/2
updated: 2026-10-29
depends_on: [T-002]
---
# T-003 — Captura de frames no decorator `tool()`

1. `server.py:153`, depois de `browser.mark(context, _action(done=True))`: se `recording.active()` e `fn.__name__` está em `{"new_tab","navigate","click","type","select","upload","screenshot"}` (5, 10) e `context`, então `await browser.screenshot({"context": context})`, grava `NNNN.jpg` e uma linha em `frames.jsonl` com os `params` redigidos (mesma expressão de `server.py:170`). Em `try/except`: falha → `audit(..., error="record_error: …")` sem mudar o resultado (6). Com `n >= 500` → `audit` `record_cap` (9).
2. RED em `tests/test_server.py` com o `browser` falso (padrão de `conftest.py`): frame gravado; `type` → `{"chars": N}`; captura lança → a tool devolve ok; 500 → para; `get_text` → nenhum frame.
