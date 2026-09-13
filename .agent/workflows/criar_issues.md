---
description: "Criar ou reconciliar issues do GitHub a partir de um plano aprovado, sem iniciar a implementação."
---

# Workflow: Criar issues

## Entradas

- Plano no ciclo correto, com parecer formal apto e aprovação humana registrada.
- Decomposição aprovada, escopo, critérios de aceite e dependências.
- Repositório remoto e evidências de identidade da revisão do plano.
- Autoridades locais `.agent/ai_behavior.md`, `_project/README.md` e `_project/cycles.md`.
- Issue Forms locais: `.github/ISSUE_TEMPLATE/feature_request.yml`, `.github/ISSUE_TEMPLATE/bug_report.yml` e `.github/ISSUE_TEMPLATE/chore.yml`.

## Barreira

- Verificar os gates de revisão e aprovação antes de qualquer mutação remota.
- Classificar cada unidade como `feature`, `fix` ou `chore`, ler o Issue Form correspondente e bloquear se o arquivo estiver ausente ou incompatível.
- Confirmar que a autorização cobre o payload remoto exato; caso contrário, apresentar o rascunho e parar antes da mutação.
- Não criar issue por inferência, duplicidade ou plano apenas `Rascunho`.
- Consultar previamente issues existentes pela chave lógica; handoff ausente, incompatível ou contraditório é recusado.

## Execução

1. Ler `.agent/ai_behavior.md`, `_project/README.md` e `_project/cycles.md`; derivar somente as issues previstas no plano aprovado e selecionar o template local: `feature` usa `.github/ISSUE_TEMPLATE/feature_request.yml`, `fix` usa `.github/ISSUE_TEMPLATE/bug_report.yml` e `chore` usa `.github/ISSUE_TEMPLATE/chore.yml`.
2. Montar título e corpo na ordem dos campos obrigatórios do Issue Form selecionado, preenchendo-os com evidências do plano sem inventar conteúdo.
3. Para cada `logical_key`, consultar a issue existente antes de criar.
4. Criar ou reconciliar título, corpo, labels e rastreabilidade apenas dentro do payload autorizado; não duplicar.
5. Consultar novamente a issue no GitHub e registrar número, URL, estado e payload efetivo como evidência.
6. Não implementar, abrir PR ou integrar PR como efeito colateral.

## Saída

- Mutação prevista: `remote_mutation` no GitHub, limitada às issues autorizadas.
- Resultado permitido: `executed`, `already_executed_and_reconciled`, `ambiguous_human_intervention_required` ou `not_executed`.
- A criação da issue não autoriza implementação; a autorização deve ser explícita e separada.

## Handoff

- `handoff_schema_version`: `1`
- `handoff_id`: `repository + cycle + workflow + logical_target + source_revision`
- `identity_source`: repositório, ciclo, workflow, alvo lógico e revisão de origem; identidade estável, sem timestamp/UUID.
- `effect_class`: `remote_mutation`
- `state_before`: plano aprovado e issue ainda ausente, existente ou não reconciliada.
- `state_after`: issue criada ou reconciliada, com número, URL e estado remoto registrados.
- `next_transition`: `issue -> implementação autorizada`.
- `preconditions`: aprovação humana, decomposição aprovada e acesso ao repositório remoto.
- `authority`: autorização explícita para criar/reconciliar as issues do plano.
- `evidence`: plano, revisão, issue URL/number, payload efetivo e resposta do GitHub.
- `acceptance`: uma issue canônica por chave lógica, rastreável e sem implementação incidental.
- `blockers`: gate ausente, acesso remoto, conflito de identidade ou estado remoto ambíguo.
- `result`: `executed` | `already_executed_and_reconciled` | `ambiguous_human_intervention_required` | `not_executed`.
- `next_workflow_recommended`: `implementar_issue` após autorização própria.
- `next_workflow_authorized`: somente a implementação explicitamente autorizada pelo solicitante.
- `actions_prohibited`: implementar, alterar código, abrir PR de implementação ou integrar PR.
- `rejection_rule`: o receptor recusa handoff ausente, incompatível, sem aprovação, sem issue canônica ou sem evidência remota.
- `logical_key`: `repository + cycle + workflow + logical_target(issue_kind + planned_scope) + source_revision`.
- `check_before_mutation`: buscar issue por URL, número, título/ciclo e chave lógica antes da criação.
- `reconcile_existing`: atualizar a issue canônica ou registrar `already_executed_and_reconciled`; nunca criar duplicata.
- `ambiguous_state`: não criar nem editar quando duas issues podem representar a mesma chave lógica.
