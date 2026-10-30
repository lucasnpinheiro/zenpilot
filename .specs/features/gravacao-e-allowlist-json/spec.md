---
status: DONE
progress: 4/4
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
JSON. A gravação reusa o que o fork já tem (`daa3d32`): o screenshot por ação (`_step_shot` → `runs/<run>/step-NNNN.jpg`) e a tool `run_report` (HTML com linha do tempo). Falta só o GIF desses frames (`zenpilot gif [run]` e `run_report`, com o Pillow do extra `zenpilot[gif]`) e a retenção de `runs/`: as 20 mais recentes, nenhuma com mais de 7 dias. As dependências
base não mudam. Posse de abas (claudezilla, claude-code-bridge): por padrão (`tab_ownership = "strict"`)
o Claude só age nas abas que abriu ou que o usuário entregou via `attach_tab`, e nunca nas de outra
sessão viva. Hoje duas sessões Claude podem clicar na mesma aba sem saber uma da outra.

**24 criteria in 4 slices (3 removidos) · 7 one-way doors · 0 open**

| File | Content |
| --- | --- |
| [spec/01-criteria.md](spec/01-criteria.md) | Criteria · States · Out of scope · Observable · Swept |
| [spec/02-technical.md](spec/02-technical.md) | Impact · Decided · Surface · contratos · RCG · Sources · gap · BDD flow |
| [spec/03-captura.md](spec/03-captura.md) | `capture_page` (23-28) |
| [spec/04-mouse.md](spec/04-mouse.md) | Ações de mouse: cursor, botões, drag, coordenadas (29-35) |
| [tasks/README.md](tasks/README.md) · [tests.md](tests.md) · [acceptance/](acceptance/) | DAG · test design · Gherkin |

## Unresolved

| # | Kind | Question | Until answered |
| --- | --- | --- | --- |
| — | — | None (retenção = 20 últimas e ≤ 7 dias; PRs só no fork: respostas do usuário em 2026-10-29) | — |

## Skills

| Skill | Verdict |
| --- | --- |
| security-engineer | applies — retenção nunca segue symlink nem sai de `runs/` (8); o GIF não desenha args (10); posse estrita (16-19). Aplicado a mão. |
| domain-expert-erp · mysql | not applicable — sem regra de ERP, sem banco. |
| code-quality | applies — reusa `load_state`/`save_state` (`safety.py:173`), o `redact` do decorator (`server.py:118`) e `browser.screenshot` (`browser.py:632`). |
| performance | applies — um screenshot JPEG extra por ação **só com a gravação ativa**; sem gravação, uma leitura de `recording.json` por chamada (~µs). |
| frontend-architect | OFF — o único artefato visual é o `recording.gif`; o `report.html` já existe no fork. |
| laya | LAYA_UNAVAILABLE; o usuário escolheu seguir sem. |

## §0 Pre-flight

- [x] `git log --diff-filter=D -- '.specs/features/*'` → nenhum.
- [x] `git log -S record` no `main` do fork: já existe o screenshot por ação + `run_report` (`daa3d32`). Na 1ª rodada a investigação olhou `8f155ec` e não viu isso (corrigido abaixo).
- [x] posse de abas: `git log -S owner` em `main` → nada; os ids de aba já são compartilhados entre processos em `tabs-<port>.json` (`browser.py:336`).
- [x] re-verificação (2026-10-29): o `main` do fork (`2e871c7`) ≠ upstream `8f155ec`. Tem `history.py`, `run_report.py`, `_step_shot` e `file_upload`. O slice de gravação foi refeito para reusar `runs/` (decisão do usuário). Âncoras = nomes de função, não linhas. O `main` estava quebrado pelo merge `4234797` → PR `fix/merge-4234797` antes das tasks.
- [x] baseline: `4bc4366` (fork antes do merge) → 305 passed; o `main` quebrado não importa. A baseline válida é a do fix.
