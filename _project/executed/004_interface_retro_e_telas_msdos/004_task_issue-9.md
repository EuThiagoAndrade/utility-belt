# Task — Issue #9: Adoção de Telas Dedicadas e Atalhos Rápidos nos Menus Interativos

> **Ciclo:** `004`
> **Estado:** `Concluído`
> **Tipo:** `feature`
> **Issue:** `#9`
> **Plano:** `_project/executed/004_interface_retro_e_telas_msdos/004_plan.md`
> **Branch:** `feature/issue-9`
> **Worktree:** `c:\Programas\utility-belt`
> **PR:** [#11](https://github.com/EuThiagoAndrade/utility-belt/pull/11)
> **Integração:** Integrada em `0db69dc` (PR #11)
> **Início:** 2026-09-17
> **Última atualização:** 2026-09-17
> **handoff_schema_version:** `1`
> **handoff_id:** `utility-belt/cycle-004/implementar_issue/issue-9/0db69dc`

## Objetivo

Integrar o módulo de telas `src/utility_belt/ui/screen.py` no menu principal (`menu.py`) e nos submenus existentes (`docker_menu.py`, `restic_menu.py`), eliminando o acúmulo contínuo de linhas através de limpeza de tela dinâmica a cada transição, exibindo cabeçalhos contextuais com breadcrumbs e adotando o fluxo de telas dedicadas para execução de comandos e diagnósticos.

## Escopo autorizado

- Atualizar `src/utility_belt/menu.py`:
  - Limpar a tela no início de cada iteração de `show_menu()`;
  - Exibir o banner híbrido no topo quando `is_banner_enabled()` for True (ou cabeçalho compacto);
  - Adicionar atalhos numéricos (`[1]`, `[2]`, `[3]`, `[4]`, `[0] Sair`);
  - Executar diagnósticos do Doctor e `system.info` em telas dedicadas com `run_dedicated_screen`.
- Atualizar `src/utility_belt/ui/docker_menu.py`:
  - Limpar a tela no laço do menu Docker e exibir cabeçalho `[ UTILITY BELT > DOCKER ]`;
  - Adicionar atalhos numéricos (`[1]`, `[2]`, `[0] Voltar`);
  - Executar `export_images` e `import_images` em telas dedicadas.
- Atualizar `src/utility_belt/ui/restic_menu.py`:
  - Limpar a tela no laço do menu Restic e exibir cabeçalho `[ UTILITY BELT > RESTIC ]`;
  - Padronizar atalhos numéricos e envolver rotinas (wizard, backup, restore, check, ls, config) em telas dedicadas.
- Atualizar `tests/test_interactive_menus.py` para cobrir os novos fluxos e escolhas com atalhos numéricos.

## Execução

- [x] Atualizar `src/utility_belt/menu.py` com telas dedicadas, banner e atalhos.
- [x] Atualizar `src/utility_belt/ui/docker_menu.py` com cabeçalho compacto, tela dedicada e atalhos.
- [x] Atualizar `src/utility_belt/ui/restic_menu.py` com cabeçalho compacto, tela dedicada e atalhos.
- [x] Atualizar testes de integração em `tests/test_interactive_menus.py`.
- [x] Executar gates locais: `validate_governance`, `ruff check`, `pytest` e `git diff --check`.
- [x] Publicar branch e abrir PR rastreável vinculada à Issue #9 ([PR #11](https://github.com/EuThiagoAndrade/utility-belt/pull/11)).
- [x] Integrar PR #11 na branch `main` após autorização humana (Commit `0db69dc`).

## Evidências

| Gate | Resultado |
| :-- | :-- |
| Testes | Passou (73/73 testes pytest com 100% sucesso) |
| Validação | Passou (27/27 verificações validate_governance) |
| `git diff --check` | Limpo (0 problemas de sintaxe ou espaços) |
| Checks remotos | Passou (PR #11 integrada com sucesso na `main` no commit `0db69dc`) |

## Decisões incidentais e desvios

- Nenhuma até o momento.

## Resultado

### Handoff de execução

- `handoff_schema_version`: `1`
- `handoff_id`: `utility-belt/cycle-004/implementar_issue/issue-9/0db69dc`
- `identity_source`: `utility-belt + cycle-004 + implementar_issue + issue-9 + 0db69dc`
- `effect_class`: `local_mutation -> remote_mutation`
- `state_before`: `Issue #9 aberta e autorizada; menus com rolagem contínua sem telas dedicadas.`
- `state_after`: `Issue #9 implementada, validada e integrada na branch main através da PR #11.`
- `next_transition`: `encerramento do ciclo 004`
- `preconditions`: `Plano aprovado, PR #10 integrada, issue #9 autorizada.`
- `authority`: `Autorização explícita do usuário para implementar e integrar a issue #9.`
- `evidence`: `_project/executed/004_interface_retro_e_telas_msdos/004_task_issue-9.md; PR #11 (merged 0db69dc)`
- `acceptance`: `Menus atualizados com telas limpas, banner, atalhos e testes passando (73/73).`
- `blockers`: `nenhum`
- `result`: `executed`
- `next_workflow_recommended`: `encerrar_ciclo`
- `next_workflow_authorized`: `encerrar_ciclo`
- `actions_prohibited`: `nenhuma`
- `rejection_rule`: `O receptor recusa handoff ausente, incompatível ou sem evidências materiais.`
- `logical_key`: `utility-belt/cycle-004/implementar_issue/issue-9/0db69dc`
- `check_before_mutation`: `Confirmado que branch e task para issue-9 foram inicializadas de forma única.`
- `reconcile_existing`: `Reconciliada task integrada no ciclo 004.`
- `ambiguous_state`: `Parar em caso de conflito de branches ou chave lógica duplicada.`
