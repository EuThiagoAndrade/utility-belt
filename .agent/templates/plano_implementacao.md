# Plano de Implementação — assunto

> **Ciclo:** `NNN`
> **Status:** `Rascunho`
> **Versão:** `v1`
> **Data de criação:** AAAA-MM-DD
> **Última atualização:** AAAA-MM-DD
> **Tipo:** `feature | fix | chore`
> **Prioridade:** `P0 | P1 | P2 | P3`
> **Revisão formal:** `Pendente | Em andamento | Concluída`
> **Veredito da revisão:** `Pendente | APTO PARA APROVAÇÃO | APTO COM RESSALVAS | REQUER NOVA RODADA`
> **Aprovação humana pós-revisão:** `Pendente | Aprovada em AAAA-MM-DD`

## Objetivo

## Contexto e baseline

## Escopo

### Dentro do escopo

### Fora do escopo

## Decisões e autoridades

## Estratégia de testes

## Itens de implementação

### Item 1 — título

**Contexto:**

**Ação técnica:**

**Critérios de aceite:**

- [ ] Critério verificável.

## Arquivos afetados

## Decomposição em issues e PRs

## Dependências e blockers

## Riscos, suposições e rollback

## Sequência recomendada

## Referências

## Rastreabilidade

| Campo | Valor |
| :-- | :-- |
| Issue(s) | — |
| PR(s) | — |
| Branch(es) | — |
| `handoff_schema_version` | `1` |
| `handoff_id` | repository + cycle + workflow + logical_target + source_revision |
| Destino após conclusão | `_project/executed/NNN_assunto/NNN_plan.md` |

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: derivado de repositório, ciclo, workflow, alvo lógico e revisão de origem.
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`; timestamp e UUID não definem a identidade.
- `effect_class`: `read_only | local_mutation | remote_mutation`
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
- `check_before_mutation`: verificar plano e revisão existentes antes de criar ou atualizar.
- `reconcile_existing`: atualizar o plano compatível sem duplicar o artefato ou o parecer.
- `ambiguous_state`: parar quando ciclo, alvo, status ou revisão estiverem em conflito.

## Revisão crítica

- **Data:** —
- **Versão revisada:** —
- **Veredito:** `Pendente`
- **Bloqueios remanescentes:** —
- **Aprovação humana pós-revisão:** `Pendente`
- **Correções materiais:** —
- **Ressalvas:** —

## Pós-mortem

- **Data de conclusão:** —
- **Desvios:** —
- **Lições comprovadas:** —
