# Handoffs complementares — ciclo 007

Contrato consumido de `.agent/ai_behavior.md` e seção Handoff de `.agent/templates/task.md`, lidos no ponto de registro. Ideação e rascunho têm os próprios handoffs integrais em seus artefatos. O handoff corrente de implementação/publicação está em `007_task_issue-23.md`. As entradas abaixo preservam o histórico das transições; não concedem autorização de merge.

## Revisão formal

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+007+revisar_plano+interface-cli-versionamento+e9f375f`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`
- `effect_class`: `local_mutation`
- `state_before`: rascunho v1, revisão pendente; handoff do rascunho aceito por completude e autoridade explícita.
- `state_after`: Em Revisão, parecer APTO COM RESSALVAS sem bloqueios para entregar até a PR; aprovação humana pós-revisão pendente.
- `next_transition`: registrar decisão sobre prosseguimento.
- `preconditions`: parecer formal, escopo delimitado e autoridade humana verificável.
- `authority`: responsável autorizou workflow completo autoaprovado até a PR; gate normal exige aprovação pós-revisão, dispensável aqui somente pela instrução humana mais recente.
- `evidence`: revisão crítica no plano; validator 33 OK/1 aviso/0 falhas; templates e baseline consultados.
- `acceptance`: receptor aceita parecer apto, ressalvas explícitas e ausência de aprovação humana fictícia.
- `blockers`: nenhum para registrar exceção já solicitada; merge sem autorização.
- `result`: `executed`
- `next_workflow_recommended`: decisão humana sobre prosseguimento.
- `next_workflow_authorized`: registro da exceção expressamente solicitada na conversa.
- `actions_prohibited`: registrar aprovação humana posterior inexistente; merge; release nesta sessão.
- `rejection_rule`: recusar parecer sem evidência ou aptidão tratada como aprovação humana.
- `logical_key`: `EuThiagoAndrade/utility-belt+007+revisar_plano+interface-cli-versionamento+e9f375f`
- `check_before_mutation`: plano entrou em Em Revisão antes do parecer; sem parecer concorrente.
- `reconcile_existing`: retomar este parecer por revisão, sem duplicar aprovação.
- `ambiguous_state`: divergência de escopo/identidade impede prosseguimento.

## Autorização excepcional

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+007+autorizacao_excepcional+prosseguimento-ate-pr+e9f375f`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`
- `effect_class`: `local_mutation`
- `state_before`: revisão apta; aprovação humana posterior não realizada.
- `state_after`: plano Aprovado por exceção explícita do responsável para este ciclo; aprovação humana pós-revisão não foi fabricada.
- `next_transition`: criar a issue única planejada.
- `preconditions`: revisão apta e conjunto completo delimitado.
- `authority`: conversa de 2026-10-13: pedido de workflow "autoaprovado" até a PR; resposta "Conjunto completo".
- `evidence`: transcrição da autorização no plano; precedência da instrução humana em ai_behavior.
- `acceptance`: receptor aceita autorização excepcional restrita; política permanente preservada.
- `blockers`: nenhum para issue/implementação/publicação dentro do plano.
- `result`: `executed`
- `next_workflow_recommended`: `criar_issues`
- `next_workflow_authorized`: `criar_issues`, depois `implementar_issue` até PR, pela autorização explícita.
- `actions_prohibited`: merge, release remoto nesta sessão e mudança permanente da governança.
- `rejection_rule`: recusar exceção sem manifestação explícita ou que amplie o conjunto confirmado.
- `logical_key`: `EuThiagoAndrade/utility-belt+007+autorizacao_excepcional+prosseguimento-ate-pr+e9f375f`
- `check_before_mutation`: parecer apto registrado antes da transição.
- `reconcile_existing`: manter uma única autorização contextual no plano.
- `ambiguous_state`: instrução humana conflitante exige nova decisão antes de efeitos.

## Criar issue

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+007+criar_issues+feature-interface-cli-versionamento+e9f375f`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`
- `effect_class`: `remote_mutation`
- `state_before`: plano apto/autorizado; busca por ciclo 007 sem issue/PR correspondente.
- `state_after`: issue [#23](https://github.com/EuThiagoAndrade/utility-belt/issues/23) criada e consultada, aberta com label enhancement.
- `next_transition`: issue -> implementação.
- `preconditions`: issue canônica, base atualizada, escopo e autorização de execução.
- `authority`: responsável autorizou todos os workflows até a PR; payload deriva do plano e Issue Form feature.
- `evidence`: resposta do conector create_issue e fetch_issue; plano, baseline e issue URL.
- `acceptance`: receptor aceita issue única com três itens e critérios verificáveis; base igual a origin/main e branch correspondente.
- `blockers`: nenhum para implementar.
- `result`: `executed`
- `next_workflow_recommended`: `implementar_issue`
- `next_workflow_authorized`: `implementar_issue`, validar e publicar PR; sem merge.
- `actions_prohibited`: ampliar escopo, duplicar issue, integrar PR ou executar release remoto nesta sessão.
- `rejection_rule`: recusar issue sem plano/autoridade/evidência ou com identidade ambígua.
- `logical_key`: `EuThiagoAndrade/utility-belt+007+criar_issues+feature-interface-cli-versionamento+e9f375f`
- `check_before_mutation`: conector search_issues/search_prs não encontrou unidade equivalente.
- `reconcile_existing`: issue 23 é canônica; atualizar somente evidências/estado dentro do plano.
- `ambiguous_state`: conflito entre issue, plano, branch e PR impede mutação.
