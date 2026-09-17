# Task — Issue #8: Módulo de Telas Retrô e Identidade Visual com Banner Híbrido

> **Ciclo:** `004`
> **Estado:** `Concluído`
> **Tipo:** `feature`
> **Issue:** `#8`
> **Plano:** `_project/drafts/004_interface_retro_e_telas_msdos/004_plan.md`
> **Branch:** `feature/issue-8`
> **Worktree:** `c:\Programas\utility-belt`
> **PR:** [#10](https://github.com/EuThiagoAndrade/utility-belt/pull/10)
> **Integração:** Integrada em `76a8367` (PR #10)
> **Início:** 2026-09-17
> **Última atualização:** 2026-09-17
> **handoff_schema_version:** `1`
> **handoff_id:** `utility-belt/cycle-004/implementar_issue/issue-8/5195480`

## Objetivo

Implementar o módulo centralizado de interface e telas `src/utility_belt/ui/screen.py`, provendo limpeza de tela, cabeçalhos de navegação com breadcrumbs em molduras MS-DOS, banner de abertura híbrido com canivete suíço em ASCII art e tipografia 3D em blocos isométricos, suporte a fallback compacto para terminais estreitos, helper para execução em tela dedicada e configuração `show_banner`.

## Escopo autorizado

- Criação de `src/utility_belt/ui/screen.py` com:
  - `clear_screen()` com chamada a `typer.clear()`;
  - `render_banner(compact: bool = False)` com arte híbrida (canivete ASCII + título em blocos 3D em até 78 colunas) e cores âmbar/laranja e ciano;
  - `render_header(breadcrumbs: list[str])` formatado em moldura MS-DOS de linhas duplas;
  - `run_dedicated_screen(title: str, func, *args, wait_for_key: bool = True, **kwargs)` para execução isolada em tela dedicada com suporte a bypass da pausa em testes;
  - Detecção defensiva de dimensões via `shutil.get_terminal_size(fallback=(80, 24))`.
- Atualização de `src/utility_belt/config.py` para incluir a chave de configuração `show_banner` (default: `True`).
- Criação de testes unitários abrangentes em `tests/test_screen.py`.

## Execução

- [x] Criar `src/utility_belt/ui/screen.py` com todas as funções de tela, molduras e banner.
- [x] Atualizar `src/utility_belt/config.py` com a chave `show_banner`.
- [x] Criar testes unitários em `tests/test_screen.py`.
- [x] Executar gates locais: `validate_governance`, `ruff check`, `pytest` e `git diff --check`.
- [x] Publicar branch e abrir PR rastreável vinculada à Issue #8.

## Evidências

| Gate | Resultado |
| :-- | :-- |
| Testes | Passou (67/67 testes pytest com 100% sucesso) |
| Validação | Passou (27/27 verificações validate_governance) |
| `git diff --check` | Limpo (0 problemas de sintaxe ou espaços) |
| Checks remotos | Passou (PR #10 aberta com sucesso no GitHub) |

## Decisões incidentais e desvios

- Nenhuma até o momento.

## Resultado

### Handoff de execução

- `handoff_schema_version`: `1`
- `handoff_id`: `utility-belt/cycle-004/implementar_issue/issue-8/e0c8fc9`
- `identity_source`: `utility-belt + cycle-004 + implementar_issue + issue-8 + e0c8fc9`
- `effect_class`: `local_mutation`
- `state_before`: `Issue #8 aberta e autorizada; módulo ui/screen.py inexistente.`
- `state_after`: `Em andamento.`
- `next_transition`: `implementação -> validação de gates -> abertura de PR`
- `preconditions`: `Plano aprovado, issue #8 existente e autorização explícita concedida.`
- `authority`: `Autorização explícita do usuário para implementar a issue.`
- `evidence`: `_project/drafts/004_interface_retro_e_telas_msdos/004_task_issue-8.md`
- `acceptance`: `Módulo screen.py implementado, testes unitários passando e gates validados.`
- `blockers`: `nenhum`
- `result`: `executed`
- `next_workflow_recommended`: `abrir_pr`
- `next_workflow_authorized`: `nenhum`
- `actions_prohibited`: `Integrar PR ou alterar escopo fora da Issue #8 sem autorização.`
- `rejection_rule`: `O receptor recusa handoff ausente, incompatível ou sem evidências materiais.`
- `logical_key`: `utility-belt/cycle-004/implementar_issue/issue-8/e0c8fc9`
- `check_before_mutation`: `Confirmado que branch e task para issue-8 foram inicializadas de forma única.`
- `reconcile_existing`: `Reconciliada task inicializada no ciclo 004.`
- `ambiguous_state`: `Parar em caso de conflito de branches ou chave lógica duplicada.`
