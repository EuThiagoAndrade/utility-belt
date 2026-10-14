# Task — Issue #26: Validação prévia de dependências externas (preflight guard)

> **Ciclo:** `008`
> **Estado:** `Em andamento`
> **Tipo:** `feature`
> **Issue:** `#26`
> **Plano:** `_project/drafts/008_validacao_preflight_dependencias/008_plan.md`
> **Branch:** `feature/issue-26`
> **Worktree:** `c:\Programas\utility-belt`
> **PR:** [PR #27](https://github.com/EuThiagoAndrade/utility-belt/pull/27)
> **Integração:** `Pendente`
> **Início:** 2026-10-14
> **Última atualização:** 2026-10-14
> **handoff_schema_version:** `1`
> **handoff_id:** `EuThiagoAndrade/utility-belt+008+implementar_issue+issue-26+cf44c90`

## Objetivo

Implementar validação prévia de dependências externas (Restic e Docker) com onboarding amigável, orientações de instalação contextualizadas para Windows/Linux, abertura assistida de links no navegador e enriquecimento do diagnóstico do doctor.

## Escopo autorizado

- Criação de `src/utility_belt/ui/guard.py` com o componente visual canônico baseado em `screen.py`.
- Integração prévia em `src/utility_belt/menu.py` antes de acionar os menus de Restic e Docker.
- Tratamento de ausência de executável e Docker daemon inativo.
- Enriquecimento de `doctor.py`, `cli.py` e `menu.py` com dicas de instalação.
- Testes automatizados em `tests/test_guard.py` e atualização de testes existentes.

## Execução

- [x] Criar módulo `src/utility_belt/ui/guard.py` com metadados e tela de onboarding.
- [x] Integrar guard em `src/utility_belt/menu.py` nas opções Restic e Docker.
- [x] Enriquecer `src/utility_belt/doctor.py` e comandos de diagnóstico com `install_guide` e URLs.
- [x] Criar suíte de testes `tests/test_guard.py` com cobertura completa.
- [x] Validar gates: `validate_governance.py`, `ruff check`, `pytest` e `git diff --check`.
- [x] Publicar branch `feature/issue-26` e abrir Pull Request com rastreabilidade completa.

## Evidências

| Gate | Resultado |
| :-- | :-- |
| Testes (`pytest`) | 216 passed, 36 skipped em 47.65s (100% de sucesso) |
| Linter (`ruff check`) | All checks passed! |
| Governança (`validate_governance.py`) | 35 verificações OK, 0 Avisos, 0 Falhas |
| `git diff --check` | Limpo (sem problemas de espaço em branco) |
| Checks remotos | Pendente (a executar no GitHub Actions após PR) |

## Decisões incidentais e desvios

- Nenhuma dependência externa adicional adicionada; utilização da biblioteca padrão `webbrowser` e `shutil`.
- Estrita observância de `screen.py` para fidelidade gráfica e consistência visual retrô.

## Resultado

### Handoff de execução

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+008+implementar_issue+issue-26+cf44c90`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`
- `effect_class`: `local_mutation -> remote_mutation`
- `state_before`: ausência de preflight guard; issue #26 aberta e autorizada.
- `state_after`: em andamento na branch feature/issue-26.
- `next_transition`: `PR -> revisão/checks -> integração autorizada`.
- `preconditions`: issue #26 aberta, plano aprovado, branch e task criadas.
- `authority`: autorização explícita do responsável em 2026-10-14.
- `evidence`: task persistente e código implementado.
- `acceptance`: todos os critérios de aceite da issue #26 atendidos e gates validados.
- `blockers`: nenhum.
- `result`: `executed`
- `next_workflow_recommended`: abertura de PR e solicitação de autorização humana para merge.
- `next_workflow_authorized`: abertura de PR; merge bloqueado aguardando autorização.
- `actions_prohibited`: merge automático sem autorização prévia.
- `rejection_rule`: recusar handoff ausente, incompatível ou sem validação completa.
- `logical_key`: `EuThiagoAndrade/utility-belt+008+implementar_issue+issue-26+cf44c90`
- `check_before_mutation`: verificar task e branch existentes.
- `reconcile_existing`: retomar a branch e task canônicas sem duplicidade.
- `ambiguous_state`: parar se houver conflito.
