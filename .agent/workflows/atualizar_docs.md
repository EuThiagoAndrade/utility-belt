---
description: "Atualizar a documentação canônica após uma transição autorizada, preservando histórico e rastreabilidade."
---

# Workflow: Atualizar documentação

## Entradas

- Transição autorizada e handoff do workflow anterior.
- Estado atual do ciclo, plano, issue, task, branch, PR e evidências.
- Arquivos canônicos indicados em `_project/README.md`.
- Skill local `.agent/skills/doc-updater/doc-updater.md` e, quando houver decisão arquitetural duradoura, `.agent/templates/adr.md`.

## Barreira

- Confirmar que a transição ocorreu de fato antes de alterar o estado documental.
- Ler `.agent/skills/doc-updater/doc-updater.md`; arquivo ausente ou incompatível bloqueia a atualização.
- Não registrar conclusão, aprovação ou integração com base em intenção futura.
- Recusar handoff ausente, incompatível ou contraditório e preservar o último estado comprovado.

## Execução

1. Aplicar a sequência de inspeção e atualização de `.agent/skills/doc-updater/doc-updater.md` às autoridades indicadas em `_project/README.md`.
2. Reconciliar o estado observado com `_project/cycles.md`, plano, task e lições reutilizáveis.
3. Atualizar apenas os documentos canônicos necessários, preservando datas e evidências.
4. Usar `.agent/templates/adr.md` somente quando uma decisão arquitetural duradoura exigir ADR; não criar ADR para estado operacional.
5. Não apagar histórico nem duplicar links, decisões ou registros.
6. Registrar bloqueios e o próximo passo provável quando a transição não estiver completa.

## Saída

- Mutação prevista: `local_mutation` documental.
- Resultado permitido: `executed`, `already_executed_and_reconciled`, `ambiguous_human_intervention_required` ou `not_executed`.
- A atualização documental não cria autorização para a próxima mutação.

## Handoff

- `handoff_schema_version`: `1`
- `handoff_id`: `repository + cycle + workflow + logical_target + source_revision`
- `identity_source`: repositório, ciclo, workflow, alvo lógico e revisão de origem; identidade estável, sem timestamp/UUID.
- `effect_class`: `local_mutation`
- `state_before`: estado canônico anterior e evidência da transição.
- `state_after`: documentos reconciliados com a transição comprovada.
- `next_transition`: próxima transição prevista pelo ciclo, sem autorização implícita.
- `preconditions`: evidência verificável e autoridade para atualizar os documentos.
- `authority`: autorização explícita para registrar a transição documental.
- `evidence`: comandos, links, commits, PR/checks, issue e arquivos atualizados.
- `acceptance`: estado coerente, histórico preservado, links resolvíveis e bloqueios explícitos.
- `blockers`: evidência ausente, conflito de estado ou autorização insuficiente.
- `result`: `executed` | `already_executed_and_reconciled` | `ambiguous_human_intervention_required` | `not_executed`.
- `next_workflow_recommended`: workflow correspondente à próxima transição.
- `next_workflow_authorized`: somente o workflow explicitamente autorizado.
- `actions_prohibited`: inventar evidência, promover estado, apagar histórico ou executar a próxima mutação.
- `rejection_rule`: o receptor recusa handoff ausente, incompatível, sem evidência ou que promova estado não comprovado.
- `logical_key`: `repository + cycle + workflow + logical_target(document_set + transition) + source_revision`.
- `check_before_mutation`: comparar o estado documental e a revisão antes de editar.
- `reconcile_existing`: preservar registros existentes e aplicar somente a diferença comprovada.
- `ambiguous_state`: não escolher entre estados conflitantes sem intervenção humana.
