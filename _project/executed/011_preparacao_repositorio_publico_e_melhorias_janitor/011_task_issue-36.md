# Task — Issue #36: feat: pre-selecionar caches no janitor e padronizar legendas de checklist (ciclo 011)

> **Ciclo:** `011`
> **Estado:** `Concluído`
> **Tipo:** `feature`
> **Issue:** `#36`
> **Plano:** `_project/executed/011_preparacao_repositorio_publico_e_melhorias_janitor/011_plan.md`
> **Branch:** `feature/issue-36`
> **Worktree:** `C:\Programas\utility-belt`
> **PR:** [#38](https://github.com/EuThiagoAndrade/utility-belt/pull/38)
> **Integração:** `Integrada na main via PR #38 (release v0.5.0)`
> **Início:** 2026-10-21
> **Última atualização:** 2026-10-21
> **handoff_schema_version:** `1`
> **handoff_id:** `EuThiagoAndrade/utility-belt+011+implementar_issue+feature-issue-36+cb13947`

## Objetivo

Aperfeiçoar a experiência do Janitor (`belt dev janitor`) pré-selecionando todos os caches descobertos por padrão (`checked=True`) em `src/utility_belt/ui/dev_menu.py:run_janitor_flow()`, preservando a confirmação de segurança com valor padrão negativo (`default=False`), e padronizando as mensagens de prompt de todos os checklists do menu Desenvolvimento (`run_janitor_flow`, `run_git_tidy_local_flow` e `run_git_tidy_remote_flow`) com a legenda canônica `"([Espaço] Marcar/Desmarcar · [a] Todos · [Enter] Confirmar):"`.

## Escopo autorizado

1. **Item 1 — Pré-seleção e legendas nos prompts de checklist** (`src/utility_belt/ui/dev_menu.py`):
   - Atribuir `checked=True` a todos os `choices` em `run_janitor_flow()`, independentemente de atividade recente (`is_active`).
   - Manter a confirmação final de segurança (`questionary.confirm`) com `default=False`.
   - Atualizar a mensagem do prompt em `run_janitor_flow`:
     `"Selecione as pastas para exclusão ([Espaço] Marcar/Desmarcar · [a] Todos · [Enter] Confirmar):"`
   - Atualizar a mensagem do prompt em `run_git_tidy_local_flow`:
     `"Selecione as branches locais para remoção ([Espaço] Marcar/Desmarcar · [a] Todos · [Enter] Confirmar):"`
   - Atualizar a mensagem do prompt em `run_git_tidy_remote_flow`:
     `"Selecione as branches remotas a excluir no origin ([Espaço] Marcar/Desmarcar · [a] Todos · [Enter] Confirmar):"`
2. **Item 2 — Cobertura de testes automatizados** (`tests/test_ui_experience.py`):
   - Teste validando que `run_janitor_flow()` inicializa `checked=True` para caches ativos e inativos.
   - Teste validando que os prompts dos fluxos de checklist contêm a legenda canônica `"([Espaço] Marcar/Desmarcar · [a] Todos · [Enter] Confirmar):"`.
   - Garantir preservação dos testes existentes sem regressão.
3. **Item 3 — Gates mínimos de governança e qualidade**:
   - `uv run python scripts/validate_governance.py`
   - `uv run ruff check`
   - `uv run pytest`
   - `git diff --check`
   - `git status --short`

## Execução

- [x] Item 1: Atualizar `run_janitor_flow()`, `run_git_tidy_local_flow()` e `run_git_tidy_remote_flow()` em `src/utility_belt/ui/dev_menu.py`.
- [x] Item 2: Implementar testes automatizados em `tests/test_ui_experience.py`.
- [x] Item 3: Executar e validar todos os gates locais mínimos.
- [x] Item 4: Fazer commit semântico `feat(issue-36): pre-selecionar caches no janitor e padronizar legendas de checklist` via staging seletivo (`1aa9cf9`).
- [x] Item 5: Publicar branch `feature/issue-36` e abrir PR vinculada à issue #36 ([PR #38](https://github.com/EuThiagoAndrade/utility-belt/pull/38)).

## Evidências

| Gate | Resultado |
| :-- | :-- |
| `uv run python scripts/validate_governance.py` | 41 OK \| 0 Avisos \| 0 Falhas |
| `uv run ruff check` | All checks passed! |
| `uv run pytest` | 253 passed, 36 skipped, 1 warning in 76.88s |
| `git diff --check` | Limpo |
| `git status --short` | Staging seletivo isolado |
| `uv build` | Sucesso (tar.gz e whl) |
| Checks remotos | 100% sucesso (ubuntu-latest: pass, windows-latest: pass) |

## Decisões incidentais e desvios

- Ressalva R4: Sufixo canônico da legenda `"([Espaço] Marcar/Desmarcar · [a] Todos · [Enter] Confirmar):"` aplicado estritamente aos três prompts de checklist.
- Ressalva R5: Execução completa dos 5 gates mínimos registrada com comandos e resultados reais.

## Resultado

### Handoff de execução

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+011+implementar_issue+feature-issue-36+1aa9cf9`
- `identity_source`: `EuThiagoAndrade/utility-belt + 011 + implementar_issue + feature-issue-36 + 1aa9cf9`
- `effect_class`: `local_mutation -> remote_mutation`
- `state_before`: issue #36 aberta, caches do Janitor desmarcados quando ativos e ausência de legendas padronizadas nos prompts.
- `state_after`: escopo técnico implementado, 3 novos testes adicionados em tests/test_ui_experience.py, 5 gates locais aprovados, commit 1aa9cf9 e PR #38 aberta.
- `next_transition`: `checks remotos de CI -> revisão -> autorização de merge`.
- `preconditions`: implementação concluída, todos os gates locais atendidos, PR #38 aberta.
- `authority`: responsável humano do repositório.
- `evidence`: `_project/drafts/011_preparacao_repositorio_publico_e_melhorias_janitor/011_task_issue-36.md`, PR #38.
- `acceptance`: itens de escopo implementados, 100% dos testes passando e PR vinculada à issue #36.
- `blockers`: aguardando checks de CI e autorização humana de merge.
- `result`: `executed`
- `next_workflow_recommended`: aguardar aprovação de checks remotos e autorização humana de merge.
- `next_workflow_authorized`: nenhum (merge requer aprovação explícita separada).
- `actions_prohibited`: fazer merge na main sem aprovação do responsável.
- `rejection_rule`: recusar handoff com gates incompletos ou testes falhando.
- `logical_key`: `EuThiagoAndrade/utility-belt+011+implementar_issue+feature-issue-36+cb13947`
- `check_before_mutation`: verificar branch limpa e issue #36 aberta.
- `reconcile_existing`: atualizar esta task a cada avanço real.
- `ambiguous_state`: parar se houver divergência de escopo.
