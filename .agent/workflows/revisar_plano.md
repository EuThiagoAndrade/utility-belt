---
description: "Revisar formalmente um plano e emitir parecer, sem aprová-lo ou implementá-lo automaticamente."
---

# Workflow: Revisar plano

## Entradas

- Plano em estado `Rascunho` ou `Em Revisão`.
- Handoff de `rascunhar_plano` ou evidência equivalente.
- Autoridades `.agent/ai_behavior.md`, `_project/README.md` e `_project/cycles.md`.
- Estrutura canônica em `.agent/templates/plano_implementacao.md`.

## Barreira

- Confirmar que o plano existe, está no ciclo correto, encontra-se em `Rascunho` ou `Em Revisão` e ainda não foi aprovado.
- Ler o template local; plano incompatível ou template ausente é achado bloqueador, não uma estrutura a ser improvisada.
- Separar parecer técnico de aprovação humana; `APTO PARA APROVAÇÃO` não equivale a `Aprovado`.
- Manter `Aprovação humana pós-revisão: Pendente`; aprovação anterior do rascunho não satisfaz este gate.
- Recusar handoff anterior ausente, incompatível ou contraditório.

## Execução

1. Comparar o plano com todas as seções e estados exigidos por `.agent/templates/plano_implementacao.md`.
2. Ao iniciar a revisão de um `Rascunho`, alterar o status para `Em Revisão` antes de emitir qualquer parecer; em reexecução, reconciliar o parecer da mesma revisão sem duplicá-lo.
3. Verificar objetivo, escopo, não-escopo, sequência, dependências, riscos, gates e critérios de aceite.
4. Verificar compatibilidade com `.agent/ai_behavior.md`, `_project/README.md` e `_project/cycles.md`.
5. Registrar achados classificados como bloqueadores, ressalvas ou itens atendidos.
6. Emitir um dos vereditos canônicos: `APTO PARA APROVAÇÃO`, `APTO COM RESSALVAS` ou `REQUER NOVA RODADA`.
7. Manter `Aprovação humana pós-revisão: Pendente`, apresentar o parecer e parar; somente uma manifestação humana posterior pode autorizar o registro de `Aprovado`.

## Saída

- Mutação prevista: `local_mutation` no parecer e na rastreabilidade do plano.
- Resultado permitido: `executed`, `already_executed_and_reconciled`, `ambiguous_human_intervention_required` ou `not_executed`.
- Nenhuma issue, implementação, PR ou integração é criada por este workflow.

## Handoff

- `handoff_schema_version`: `1`
- `handoff_id`: `repository + cycle + workflow + logical_target + source_revision`
- `identity_source`: repositório, ciclo, workflow, alvo lógico e revisão de origem; identidade estável, sem timestamp/UUID.
- `effect_class`: `local_mutation`
- `state_before`: plano em `Rascunho` ou `Em Revisão`, com decisão humana pendente.
- `state_after`: plano em `Em Revisão`, parecer canônico registrado e aprovação humana ainda `Pendente`.
- `next_transition`: `parecer -> aprovação humana`.
- `preconditions`: plano completo e revisão formal autorizada.
- `authority`: solicitação explícita para revisar; não inclui aprovação.
- `evidence`: checklist, arquivos, comandos, revisão e achados.
- `acceptance`: parecer explícito, ressalvas classificadas e decisão humana não inferida.
- `blockers`: falhas de completude, incoerências ou evidências insuficientes.
- `result`: `executed` | `already_executed_and_reconciled` | `ambiguous_human_intervention_required` | `not_executed`.
- `next_workflow_recommended`: `criar_issues` apenas após parecer apto e aprovação humana registrada.
- `next_workflow_authorized`: somente o próximo workflow explicitamente autorizado.
- `actions_prohibited`: marcar `Aprovado`, criar issue, implementar, publicar PR ou integrar PR sem gates próprios.
- `rejection_rule`: o receptor recusa handoff ausente, incompatível, sem parecer formal ou que trate aptidão como aprovação.
- `logical_key`: `repository + cycle + workflow + logical_target + source_revision`.
- `check_before_mutation`: verificar se já existe parecer para a mesma revisão do plano.
- `reconcile_existing`: atualizar o parecer apenas com nova evidência/revisão, preservando o parecer anterior.
- `ambiguous_state`: parar quando o plano mudar durante a revisão ou houver decisões conflitantes.
