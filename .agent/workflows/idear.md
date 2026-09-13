---
description: "Explorar uma ideia sem convertê-la automaticamente em plano, issue ou implementação."
---

# Workflow: Idear

## Entradas

- Contexto do repositório e do ciclo, quando houver.
- Objetivo, problema ou hipótese trazida pelo solicitante.
- Evidências disponíveis; ausência de evidência deve ser declarada.
- Autoridades locais `.agent/ai_behavior.md`, `_project/README.md` e `_project/cycles.md`.
- Template local `.agent/templates/ideacao.md`.

## Barreira

- Confirmar a identidade do repositório, ciclo e alvo lógico antes de registrar qualquer saída.
- Ler as autoridades e o template locais; arquivo ausente ou estrutura incompatível bloqueia a mutação.
- Não inferir aprovação, autorização de implementação ou autorização de mutação remota.
- Quando a ideação retomar uma transição anterior, recusar handoff ausente, incompatível ou contraditório; uma solicitação humana inicial identificada não exige predecessor artificial.

## Execução

1. Ler `.agent/templates/ideacao.md` e instanciar suas seções no artefato do ciclo, sem remover campos canônicos.
2. Separar fatos, hipóteses, perguntas em aberto e alternativas.
3. Identificar impacto, dependências, riscos e critérios de descarte.
4. Criar ou reconciliar `_project/ideations/NNN_assunto.md` e, quando aplicável, reservar o mesmo ciclo em `_project/cycles.md` conforme `_project/README.md`.
5. Registrar a exploração sem promover a ideia a plano aprovado.
6. Indicar qual workflow pode receber a ideia e quais decisões humanas continuam pendentes.

## Saída

- Mutação prevista: `local_mutation` somente nos artefatos de ideação autorizados.
- Resultado permitido: `executed`, `already_executed_and_reconciled`, `ambiguous_human_intervention_required` ou `not_executed`.
- A saída é recomendação; não autoriza automaticamente o próximo workflow.

## Handoff

- `handoff_schema_version`: `1`
- `handoff_id`: `repository + cycle + workflow + logical_target + source_revision`
- `identity_source`: repositório, ciclo, workflow, alvo lógico e revisão de origem; identidade estável, sem timestamp/UUID.
- `effect_class`: `local_mutation`
- `state_before`: contexto e estado documental observados antes da ideação.
- `state_after`: perguntas, hipóteses, riscos e decisão pendente registrados.
- `next_transition`: `ideia -> rascunho de plano`, somente após decisão humana.
- `preconditions`: contexto identificado e objetivo compreensível.
- `authority`: solicitação explícita para idear; nenhuma autorização implícita para implementar.
- `evidence`: links, arquivos, comandos e revisões que sustentam a saída.
- `acceptance`: fatos e hipóteses separados, riscos explícitos e próximo workflow indicado.
- `blockers`: evidências ou decisões ausentes.
- `result`: `executed` | `already_executed_and_reconciled` | `ambiguous_human_intervention_required` | `not_executed`.
- `next_workflow_recommended`: `rascunhar_plano` ou `nenhum`.
- `next_workflow_authorized`: somente o workflow explicitamente autorizado pelo solicitante.
- `actions_prohibited`: aprovar plano, criar issue, implementar, publicar PR ou integrar PR sem autorização própria.
- `rejection_rule`: o receptor recusa handoff ausente, incompatível, sem evidência ou sem autoridade explícita.
- `logical_key`: `repository + cycle + workflow + logical_target + source_revision`.
- `check_before_mutation`: verificar se a mesma revisão e alvo já possuem saída registrada.
- `reconcile_existing`: reutilizar ou atualizar a saída existente sem duplicar o artefato.
- `ambiguous_state`: interromper a mutação e solicitar intervenção humana quando houver conflito de identidade ou estado.
