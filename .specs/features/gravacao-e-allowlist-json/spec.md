---
status: TODO
progress: 0/2
updated: 2026-10-29
---
# Spec — zenpilot (fork): `allow --json`, gravação da sessão e posse de abas

> Build this with **spec-implement** on the user's literal `executar`. Every criterion becomes a check
> with a proof, referenced by its number. Nothing under `Unresolved` gets settled while building.
> Bundle companheiro (consumidor): `~/Projects/zen-devtools/.specs/features/melhorias-referencias-browser/`.

## Intent

O plugin zen-devtools precisa aplicar a allowlist do zenpilot às chamadas do zen-devtools-mcp. Hoje
`zenpilot allow` só imprime texto para humanos ("Allowlist: a, b / For now: x (until 12:00)") e não
diz `dangerously_allow_all_sites`, então outro programa não consegue ler a lista de forma confiável.
Também não há como rever depois o que o Claude fez no Zen: o `audit.jsonl` guarda as ações, mas
nenhuma imagem. As referências claude-for-firefox (gif.js) e Claude in Chrome (assistir e intervir)
mostram o que falta. O PRD não traz número de impacto.

Com a mudança, `zenpilot allow --json` imprime a allowlist, as grants e `allow_all_sites` numa linha
JSON. `zenpilot record start|stop` grava um frame depois de cada ação e de cada screenshot. No stop,
gera um `recording.html` (sempre) e um `recording.gif` (só se o Pillow estiver instalado, extra
`zenpilot[gif]`), guardando as 20 gravações mais recentes, nenhuma com mais de 7 dias. As dependências
base não mudam. Posse de abas (claudezilla, claude-code-bridge): por padrão (`tab_ownership = "strict"`)
o Claude só age nas abas que abriu ou que o usuário entregou via `attach_tab`, e nunca nas de outra
sessão viva. Hoje duas sessões Claude podem clicar na mesma aba sem saber uma da outra.

**22 criteria in 3 slices · 5 one-way doors · 0 open**

| File | Content |
| --- | --- |
| [spec/01-criteria.md](spec/01-criteria.md) | Criteria · States · Out of scope · Observable · Swept |
| [spec/02-technical.md](spec/02-technical.md) | Impact · Decided · Surface · contratos · RCG · Sources · gap · BDD flow |
| [tasks/README.md](tasks/README.md) · [tests.md](tests.md) · [acceptance/](acceptance/) | DAG · test design · Gherkin |

## Unresolved

| # | Kind | Question | Until answered |
| --- | --- | --- | --- |
| — | — | None (retenção = 20 últimas e ≤ 7 dias; PRs só no fork: respostas do usuário em 2026-10-29) | — |

## Skills

| Skill | Verdict |
| --- | --- |
| security-engineer | applies — frames só de abas já liberadas pela allowlist (o screenshot passa por `_tab`); texto digitado nunca entra em `frames.jsonl` (usa `redact`); HTML escapa a legenda (`html.escape`). Aplicado a mão. |
| domain-expert-erp · mysql | not applicable — sem regra de ERP, sem banco. |
| code-quality | applies — reusa `load_state`/`save_state` (`safety.py:173`), o `redact` do decorator (`server.py:118`) e `browser.screenshot` (`browser.py:632`). |
| performance | applies — um screenshot JPEG extra por ação **só com a gravação ativa**; sem gravação, uma leitura de `recording.json` por chamada (~µs). |
| frontend-architect | OFF — o `recording.html` é um artefato estático gerado, sem Bootstrap/AdminLTE. |
| laya | LAYA_UNAVAILABLE; o usuário escolheu seguir sem. |

## §0 Pre-flight

- [x] `git log --diff-filter=D -- '.specs/features/*'` → nenhum.
- [x] `git log -S record` em `main` @ `8f155ec`: nenhuma gravação. O `runs/` em `~/.local/state/zenpilot` vem da branch `feat/devtools` (HAR + report), não de `main`.
- [x] posse de abas: `git log -S owner` em `main` → nada; os ids de aba já são compartilhados entre processos em `tabs-<port>.json` (`browser.py:336`).
- [x] baseline: `uv run pytest -q` → 99 passed, 14 skipped.
