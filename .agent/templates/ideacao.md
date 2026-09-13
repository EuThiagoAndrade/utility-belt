# Ideação — NNN: assunto

> **Ciclo:** `NNN`
> **Estado:** `Ideação`
> **Criado em:** AAAA-MM-DD
> **Última atualização:** AAAA-MM-DD

## Problema

## Contexto e evidências

## Resultado desejado

## Hipóteses

## Alternativas

## Riscos e restrições

## Perguntas em aberto

## Fora do escopo

## Critérios para iniciar o planejamento

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: derivado de repositório, ciclo, workflow, alvo lógico e revisão de origem.
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`; timestamp e UUID não definem a identidade.
- `effect_class`: `local_mutation`
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
- `check_before_mutation`: verificar artefato e reserva de ciclo existentes antes de criar.
- `reconcile_existing`: atualizar a ideação compatível sem duplicar ciclo ou arquivo.
- `ambiguous_state`: parar quando identidade, ciclo ou revisão estiverem em conflito.
