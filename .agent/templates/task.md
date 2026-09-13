# Task — Issue #N: título

> **Ciclo:** `NNN`
> **Estado:** `Em andamento`
> **Tipo:** `feature | fix | chore`
> **Issue:** `#N`
> **Plano:** `_project/drafts/NNN_assunto/NNN_plan.md`
> **Branch:** `tipo/issue-N`
> **Worktree:** caminho local
> **PR:** —
> **Integração:** `Pendente`
> **Início:** AAAA-MM-DD
> **Última atualização:** AAAA-MM-DD
> **handoff_schema_version:** `1`
> **handoff_id:** repository + cycle + workflow + logical_target + source_revision

## Objetivo

## Escopo autorizado

## Execução

- [ ] Passo ou critério real.

## Evidências

| Gate | Resultado |
| :-- | :-- |
| Testes | Pendente |
| Validação | Pendente |
| `git diff --check` | Pendente |
| Checks remotos | Pendente |

## Decisões incidentais e desvios

## Resultado

### Handoff de execução

- `handoff_schema_version`: `1`
- `handoff_id`: derivado de repositório, ciclo, workflow, alvo lógico e revisão de origem.
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`; timestamp e UUID não definem a identidade.
- `effect_class`: `local_mutation | remote_mutation`
- `state_before` / `state_after`: estados observados e produzidos.
- `next_transition`: próxima transição recomendada.
- `preconditions`: precondições obrigatórias.
- `authority`: autoridade capaz de satisfazê-las.
- `evidence`: evidências esperadas.
- `acceptance`: critério de aceite do receptor.
- `blockers`: bloqueios atuais.
- `result`: `executed | already_executed_and_reconciled | ambiguous_human_intervention_required | not_executed`
- `next_workflow_recommended` / `next_workflow_authorized`: recomendação separada de autorização.
- `actions_prohibited`: ações não automáticas enquanto o aceite estiver pendente.
- `rejection_rule`: o receptor recusa handoff ausente, incompatível, contraditório ou sem evidência material.
- `logical_key`: `repository + cycle + workflow + logical_target + source_revision`.
- `check_before_mutation`: verificar task, branch e PR existentes antes de criar ou publicar.
- `reconcile_existing`: atualizar a unidade compatível sem duplicar task, branch ou PR.
- `ambiguous_state`: parar quando issue, task, branch, PR ou revisão estiverem em conflito.
