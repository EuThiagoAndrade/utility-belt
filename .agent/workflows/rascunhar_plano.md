---
description: "Transformar uma ideia em plano rastreável, ainda sem revisão ou aprovação automática."
---

# Workflow: Rascunhar plano

## Entradas

- Handoff de `idear` ou contexto equivalente identificado.
- Regras canônicas em `.agent/ai_behavior.md`, `_project/README.md` e `_project/cycles.md`.
- Ideação do ciclo e template local `.agent/templates/plano_implementacao.md`.
- Escopo, critérios de aceite, riscos, dependências e decisões pendentes.

## Barreira

- Confirmar identidade do repositório, ciclo, alvo lógico e revisão de origem.
- Ler o template local e recusar a mutação quando ele estiver ausente ou incompatível com as autoridades.
- Não tratar o rascunho como revisão, aprovação ou autorização de implementação.
- Se o handoff anterior estiver ausente, incompatível ou contraditório, recusar e registrar o bloqueio.

## Execução

1. Ler `.agent/templates/plano_implementacao.md` e instanciar integralmente suas seções no rascunho do diretório de ciclo definido por `_project/README.md`.
2. Reconciliar a ideação e `_project/cycles.md` com o mesmo número e alvo lógico, sem criar um segundo plano canônico.
3. Descrever objetivo, não-objetivos, entregáveis, sequência, gates, riscos e evidências nos campos do template.
4. Manter `Status: Rascunho` até a revisão formal; nunca escrever `Aprovado` neste workflow; não marque o plano como `Aprovado`.
5. Encaminhar explicitamente o artefato para `.agent/workflows/revisar_plano.md`, sem executar a revisão automaticamente; não inicie a revisão automaticamente.

## Saída

- Mutação prevista: `local_mutation` no rascunho do plano.
- Resultado permitido: `executed`, `already_executed_and_reconciled`, `ambiguous_human_intervention_required` ou `not_executed`.
- A recomendação para revisão não é autorização para criar issue ou implementar.

## Handoff

- `handoff_schema_version`: `1`
- `handoff_id`: `repository + cycle + workflow + logical_target + source_revision`
- `identity_source`: repositório, ciclo, workflow, alvo lógico e revisão de origem; identidade estável, sem timestamp/UUID.
- `effect_class`: `local_mutation`
- `state_before`: ideia ou contexto documental recebido.
- `state_after`: plano rastreável em estado `Rascunho`.
- `next_transition`: `rascunho -> revisão formal`.
- `preconditions`: ciclo identificado, objetivo delimitado e autoridade para rascunhar.
- `authority`: solicitação explícita para produzir ou atualizar o rascunho.
- `evidence`: arquivos, decisões, links e revisões consultados.
- `acceptance`: plano completo, estado correto, não-objetivos e gates explícitos.
- `blockers`: decisões, evidências ou dependências ainda ausentes.
- `result`: `executed` | `already_executed_and_reconciled` | `ambiguous_human_intervention_required` | `not_executed`.
- `next_workflow_recommended`: `revisar_plano`.
- `next_workflow_authorized`: somente revisão explicitamente autorizada; não inclui aprovação ou implementação.
- `actions_prohibited`: escrever `Aprovado`, criar issue, implementar, publicar PR ou integrar PR.
- `rejection_rule`: o receptor recusa handoff ausente, incompatível, sem revisão ou com status promovido indevidamente.
- `logical_key`: `repository + cycle + workflow + logical_target + source_revision`.
- `check_before_mutation`: verificar se já existe rascunho para o mesmo ciclo, alvo e revisão.
- `reconcile_existing`: atualizar o rascunho existente preservando histórico e evitando duplicidade.
- `ambiguous_state`: parar quando houver mais de um rascunho canônico ou conflito de revisão.
