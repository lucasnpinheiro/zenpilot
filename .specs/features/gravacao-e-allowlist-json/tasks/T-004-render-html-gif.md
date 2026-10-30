---
id: T-004
status: TODO
progress: 0/3
updated: 2026-10-29
depends_on: [T-002, T-003]
---
# T-004 — `recording.html` + GIF opcional

1. `recording.render(dir)`: HTML único com os frames em `data:image/jpeg;base64`, legendas via `html.escape`, ←/→ e play em JS inline; 0 frames → "No frames recorded" (7, 12).
2. GIF: `try: from PIL import Image` → `save(..., save_all=True, duration=800, loop=0)`; `ImportError` → a mensagem do critério 7.
3. `pyproject.toml`: `[project.optional-dependencies] gif = ["Pillow>=10"]` (11). README: seção "Recording". RED: o HTML contém N `<img>` e escapa `<script>` vindo da url; GIF via `pytest.importorskip("PIL")`.
