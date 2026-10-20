# Task — Issue #33: fix: compatibilidade de opcoes em checkbox e padronizacao visual de menus (ciclo 010)

> **Ciclo:** `010`
> **Estado:** `Em andamento`
> **Tipo:** `fix`
> **Issue:** `#33`
> **Plano:** `_project/drafts/010_correcoes_e_padronizacao_menus/010_plan.md`
> **Branch:** `fix/issue-33`
> **Worktree:** `C:\Programas\utility-belt`
> **PR:** [#34](https://github.com/EuThiagoAndrade/utility-belt/pull/34)
> **Integração:** `Pendente`
> **Início:** 2026-10-20
> **Última atualização:** 2026-10-20
> **handoff_schema_version:** `1`
> **handoff_id:** `EuThiagoAndrade/utility-belt+010+implementar_issue+fix-issue-33+b8a408d`

## Objetivo

Corrigir a incompatibilidade de opções em `questionary.checkbox` via `menu_options()`, eliminando o erro `TypeError: PromptSession.__init__() got an unexpected keyword argument 'use_shortcuts'` em fluxos interativos de seleção múltipla do `dev_menu`, e padronizar visualmente os submenus de Markdown e Desenvolvimento inserindo a linha divisória (`menu_separator()`) antes da opção `[0] Voltar ao menu principal`.

## Escopo autorizado

1. **Item 1 — Saneamento de `menu_options()` e guarda defensiva em `prompt()`** (`src/utility_belt/ui/screen.py`):
   - Remover `"use_shortcuts": False` de `menu_options()`.
   - Adicionar guarda defensiva determinística em `prompt()`: descartar `use_shortcuts` quando o parâmetro não for declarado na assinatura da fábrica.
2. **Item 2 — Verificação dos fluxos de checklist em Desenvolvimento** (`src/utility_belt/ui/dev_menu.py`):
   - Verificar que `run_janitor_flow`, `run_git_tidy_local_flow`, `run_git_tidy_remote_flow` e `run_git_tidy_all_flow` funcionam sem `use_shortcuts`.
3. **Item 3 — Padronização de linha separadora antes de `[0]`** (`src/utility_belt/ui/markdown_menu.py` e `src/utility_belt/ui/dev_menu.py`):
   - Inserir `menu_separator()` antes de `[0] Voltar ao menu principal` em `show_markdown_menu()`.
   - Inserir `menu_separator()` antes de `[0] Voltar ao menu principal` em `show_dev_menu()`.
4. **Item 4 — Testes automatizados em `tests/test_ui_experience.py`**:
   - Teste de `menu_options()` sem `use_shortcuts`.
   - Teste de `prompt()` real com `questionary.checkbox` e `DummyOutput()` / pipe.
   - Teste de guarda defensiva em `prompt(questionary.checkbox, ..., use_shortcuts=False)`.
   - Teste de não regressão em `prompt(questionary.select, ..., **menu_options())`.
   - Testes dos fluxos do `dev_menu` com itens simulados e `create_app_session`.
   - Teste estrutural de `menu_separator()` antes do item `exit` em Markdown e Desenvolvimento.

## Execução

- [x] Item 1: Sanear `menu_options()` e implementar guarda defensiva em `prompt()` em `screen.py`.
- [x] Item 2: Padronizar `menu_separator()` antes de `[0]` em `markdown_menu.py` e `dev_menu.py`.
- [x] Item 3: Adicionar testes automatizados em `tests/test_ui_experience.py` cobrindo prompts reais e separadores.
- [x] Item 4: Executar e validar todos os gates locais mínimos (`validate_governance.py`, `ruff check`, `pytest`, `git diff --check`, `git status --short`).
- [x] Item 5: Fazer commit semântico `fix(issue-33): ...`, publicar branch `fix/issue-33` e abrir PR vinculada à issue #33.

## Evidências

| Gate | Resultado |
| :-- | :-- |
| `uv run python scripts/validate_governance.py` | 39 OK | 0 Avisos | 0 Falhas |
| `uv run ruff check` | All checks passed! |
| `uv run pytest` | 250 passed, 36 skipped, 1 warning in 48.83s |
| `git diff --check` | Limpo |
| Checks remotos | 100% sucesso (ubuntu-latest: pass, windows-latest: pass) |

## Decisões incidentais e desvios

- Observadas as ressalvas RV2-1 (uso de `create_app_session` para injeção de pipes nos testes de fluxo) e RV2-2 (teste de select tratado como não regressão).

## Resultado

### Handoff de execução

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+010+implementar_issue+fix-issue-33+b8a408d`
- `identity_source`: `EuThiagoAndrade/utility-belt + 010 + implementar_issue + fix-issue-33 + b8a408d`
- `effect_class`: `local_mutation -> remote_mutation`
- `state_before`: issue #33 aberta, erro em tempo de execução ao exibir checklist no dev_menu e separadores ausentes em Markdown e Desenvolvimento.
- `state_after`: escopo técnico implementado, 9 novos testes unitários e de integração adicionados, gates 100% validados localmente.
- `next_transition`: `abertura de PR -> checks remotos de CI -> aprovação humana de merge`.
- `preconditions`: implementação concluída, todos os gates atendidos.
- `authority`: usuário, autorização em 2026-10-20.
- `evidence`: `_project/drafts/010_correcoes_e_padronizacao_menus/010_task_issue-33.md`, commit na branch `fix/issue-33`.
- `acceptance`: itens implementados cirurgicamente, suite de testes passando e PR vinculada à issue #33.
- `blockers`: nenhum.
- `result`: `executed`
- `next_workflow_recommended`: aguardar checks remotos e aprovação de merge.
- `next_workflow_authorized`: nenhum (merge requer aprovação explícita separada).
- `actions_prohibited`: fazer merge sem autorização humana.
- `rejection_rule`: recusar handoff com gates pendentes ou sem evidência verificável.
- `logical_key`: `EuThiagoAndrade/utility-belt+010+implementar_issue+fix-issue-33+b8a408d`
- `check_before_mutation`: verificar branch `fix/issue-33` limpa antes de codificar.
- `reconcile_existing`: atualizar esta task a cada progresso real.
- `ambiguous_state`: parar se houver divergência entre plano e código.
