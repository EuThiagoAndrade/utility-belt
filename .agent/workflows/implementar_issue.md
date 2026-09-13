---
description: "Implementar uma issue autorizada, validar o resultado e publicar uma PR rastreável sem integrar automaticamente."
---

# Workflow: Implementar issue

## Entradas

- Plano aprovado/em execução e issue remota aberta, identificada por número e URL.
- Autorização humana explícita para implementar a issue.
- Base atualizada, branch de implementação compatível e task persistente.
- Critérios de aceite, escopo, não-escopo e gates do plano.
- Autoridades locais `.agent/ai_behavior.md`, `_project/README.md`, `_project/cycles.md` e `.agent/lessons_learned.md`.
- Templates locais `.agent/templates/task.md` e `.github/PULL_REQUEST_TEMPLATE/pull_request_template.md`.
- Gate local `.agent/skills/governance-check/governance-check.md`.

## Barreira

- Não criar task, branch de entrega ou código antes de confirmar issue, autorização e base.
- Ler autoridades, templates e gate locais; item ausente ou incompatível bloqueia a operação correspondente.
- Não expandir o escopo para endpoints, API funcional, persistência, autenticação, deploy ou outro repositório sem autorização própria.
- Verificar PR/branch existentes pela chave lógica; recusar handoff ausente, incompatível ou contraditório.

## Execução

1. Confirmar a issue, o plano, a autorização e a revisão da base; ler também `.agent/lessons_learned.md` sem promover estado transitório a lição.
2. Classificar a issue e aplicar a taxonomia de `_project/README.md`: `feature/issue-N`, `fix/issue-N` ou `chore/issue-N`; um prefixo operacional externo `codex/` pode anteceder o nome sem substituir o tipo semântico.
3. Criar ou reconciliar a branch canônica sem apagar trabalho existente e sem criar uma segunda branch para a mesma chave lógica.
4. Ler `.agent/templates/task.md` e instanciar ou reconciliar a task persistente com intenção, estado e handoff.
5. Implementar somente os itens autorizados, incluindo testes e fixtures necessários.
6. Executar os gates do plano e a inspeção somente leitura de `.agent/skills/governance-check/governance-check.md`; registrar evidências reais na task.
7. Inspecionar o diff e fazer staging seletivo; usar no commit o prefixo de `_project/README.md`: `feat(issue-N):`, `fix(issue-N):` ou `chore(issue-N):`.
8. Ler `.github/PULL_REQUEST_TEMPLATE/pull_request_template.md`, preencher todas as seções aplicáveis, publicar a branch e criar ou reconciliar a PR rastreável, preferencialmente em rascunho.
9. Aguardar revisão, checks e autorização de integração; não fazer merge automaticamente.

## Saída

- Mutação prevista: `local_mutation` e, após validação, `remote_mutation` para branch/PR.
- Resultado permitido: `executed`, `already_executed_and_reconciled`, `ambiguous_human_intervention_required` ou `not_executed`.
- A PR publicada é a unidade de entrega; merge permanece sujeito ao gate humano próprio.

## Handoff

- `handoff_schema_version`: `1`
- `handoff_id`: `repository + cycle + workflow + logical_target + source_revision`
- `identity_source`: repositório, ciclo, workflow, alvo lógico e revisão de origem; identidade estável, sem timestamp/UUID.
- `effect_class`: `local_mutation -> remote_mutation`
- `state_before`: issue autorizada, base, branch e task observadas antes da implementação.
- `state_after`: escopo implementado, evidências registradas, branch publicada e PR vinculada, ou bloqueio explícito.
- `next_transition`: `PR -> revisão/checks -> integração autorizada`.
- `preconditions`: issue, autorização, base atualizada, task persistente e critérios de aceite.
- `authority`: autorização humana explícita para implementar a issue; não inclui merge.
- `evidence`: issue/PR URLs, commits, arquivos, testes, validator, checks e revisão da base.
- `acceptance`: itens da issue atendidos, escopo preservado, gates registrados e PR rastreável.
- `blockers`: falhas de teste, conflito de branch, check pendente, revisão ou autorização de integração ausente.
- `result`: `executed` | `already_executed_and_reconciled` | `ambiguous_human_intervention_required` | `not_executed`.
- `next_workflow_recommended`: revisão da PR e, somente após aprovação, integração.
- `next_workflow_authorized`: apenas as ações explicitamente autorizadas; merge exige autorização separada.
- `actions_prohibited`: ampliar escopo, integrar PR, alterar outro repositório ou declarar concluído sem evidência.
- `rejection_rule`: o receptor recusa handoff ausente, incompatível, sem autorização, sem issue/PR canônica ou sem evidências de validação.
- `logical_key`: `repository + cycle + workflow + logical_target(issue_number + planned_scope) + source_revision`.
- `check_before_mutation`: localizar task, branch e PR existentes para a chave lógica antes de criar ou publicar.
- `reconcile_existing`: retomar a branch/task/PR canônica e registrar `already_executed_and_reconciled` quando o trabalho já estiver feito.
- `ambiguous_state`: parar e pedir intervenção humana quando houver múltiplas branches/PRs ou divergência entre issue, task e plano.
