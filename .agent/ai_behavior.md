# Comportamento canônico de agentes

## Finalidade

Este arquivo é a autoridade para comportamento, limites e autorizações de agentes no `utility-belt`. Organização documental e ciclo de vida pertencem a `_project/README.md`; estado e numeração correntes pertencem a `_project/cycles.md`; o escopo executável pertence ao plano aprovado e à issue correspondente.

## Ordem de leitura

1. Este arquivo por inteiro.
2. `_project/README.md` e `_project/cycles.md`.
3. O plano, a issue e a task persistente relacionados ao trabalho.
4. ADRs, KBs, workflows, templates e skills relevantes.

Em conflito, preserve a instrução humana mais recente e explícita, não amplie escopo e registre a divergência antes de prosseguir.

## Matriz de autoridade

| Responsabilidade | Autoridade |
| :-- | :-- |
| Comportamento e autorização | `.agent/ai_behavior.md` |
| Ciclo de vida, nomes e estados válidos | `_project/README.md` |
| Ciclos e próxima numeração | `_project/cycles.md` |
| Escopo da implementação | Plano aprovado |
| Unidade de entrega | Issue |
| Histórico operacional local | Task persistente do ciclo |
| Estado global de issue, PR, revisão e checks | GitHub |
| Decisões duradouras | `_project/decisions/` |
| Conhecimento reutilizável | `_project/knowledge/` |

Adapters, workflows, templates, skills, validadores e CI consomem essas autoridades; não criam políticas concorrentes.

## Contrato canônico de handoff

Todo workflow que produza uma transição ou mutação deve terminar com um handoff completo, salvo os workflows somente leitura explicitamente classificados como saída reduzida. O contrato normativo vive neste arquivo; workflows, templates, skills e validadores apenas o instanciam.

Um handoff completo deve declarar, nesta ordem:

1. `handoff_schema_version: 1` — versão local do contrato, sem consulta a `latest` ou a estado remoto.
2. `handoff_id` — identidade derivada de repositório, ciclo, workflow, alvo lógico e revisão de origem quando aplicável.
3. `identity_source` — deve explicitar `repository + cycle + workflow + logical_target + source_revision`; timestamp e UUID eventual são metadados, nunca a identidade lógica.
4. `effect_class` — `read_only`, `local_mutation` ou `remote_mutation`.
5. `state_before` e `state_after` — estados observados e produzidos, sem inferir transições ausentes.
6. `next_transition` — próxima transição recomendada, separada de sua autorização.
7. `preconditions` — condições obrigatórias antes do próximo efeito.
8. `authority` — pessoa, artefato ou sistema autorizado a satisfazer cada precondição.
9. `evidence` — evidência verificável esperada para cada precondição e para o resultado.
10. `acceptance` — critério explícito de aceite pelo receptor.
11. `blockers` — bloqueios atuais, inclusive `nenhum` quando verificado.
12. `result` — `executed`, `already_executed_and_reconciled`, `ambiguous_human_intervention_required` ou `not_executed`.
13. `next_workflow_recommended` e `next_workflow_authorized` — recomendação não concede autorização.
14. `actions_prohibited` — efeitos que o receptor ou o agente não podem executar enquanto o aceite estiver pendente.
15. `rejection_rule` — o receptor recusa handoff ausente, incompatível, contraditório ou sem evidência material suficiente.

Workflows mutantes devem declarar ainda `logical_key`, `check_before_mutation`, `reconcile_existing` e `ambiguous_state`. A chave lógica deve permanecer estável quando o contexto material não mudar; reexecução compatível deve ser reconciliada, e conflito, concorrência ou execução parcial sem estado comprovável devem produzir `ambiguous_human_intervention_required` e parar sem mutação destrutiva.

O handoff nunca aciona automaticamente o workflow seguinte. O receptor deve executar seu preflight, aceitar ou recusar explicitamente a transição e preservar a parada quando faltar autorização material.

Workflows somente leitura podem usar saída estruturada reduzida com `context`, `findings`, `blockers`, `next_step_likely` e `mutation: none`; eles não devem simular autorização, aceite remoto ou mutação inexistente.

## Autorizações e gates

- Inspeção, análise ou diagnóstico autorizam somente ações de leitura e registros pedidos explicitamente.
- Redigir ou revisar plano não autoriza implementação.
- `Rascunho` é a primeira passagem e deve terminar com handoff explícito para `.agent/workflows/revisar_plano.md`; aprovação do rascunho autoriza a revisão, não permite saltá-la.
- Todo plano deve passar por `Em Revisão`, receber veredito formal sem bloqueios e somente depois obter aprovação humana específica para mudar para `Aprovado`.
- Uma manifestação humana anterior ao veredito não vale como aprovação pós-revisão. O agente deve apresentar o resultado da revisão e aguardar a decisão subsequente.
- Implementação exige plano aprovado, issue vinculada e autorização humana explícita para execução.
- Publicar branch ou PR exige que o escopo solicitado esteja validado e rastreável.
- Integrar ou fechar uma entrega exige autorização explícita quando o plano estabelecer esse gate.
- Encerramento documental ocorre depois da integração verificada e não cria issue recursiva.

Quando faltar uma autorização material, pare no gate e peça decisão; não trate silêncio como aprovação.

## Conduta de execução

- Inspecione o estado real antes de alterar arquivos.
- Todo workflow que crie ou atualize um artefato estruturado deve nomear e ler, no ponto de uso, o template e as autoridades locais aplicáveis; template ausente ou incompatível bloqueia a execução.
- A nomenclatura de branch e commit deve ser consumida de `_project/README.md` no momento da criação ou reconciliação, sem ser reinventada pelo workflow.
- Preserve mudanças alheias e mantenha cada entrega dentro do plano aprovado.
- Crie a task persistente no início da implementação e atualize evidências reais durante o trabalho.
- Use uma branch por issue; mantenha commits intencionais e PR revisável.
- Prefira o conector GitHub disponível para issues, PRs e checks; use Git local para branch, diff, stage, commit e push.
- Execute os gates locais definidos no plano antes de publicar.
- Não publique PR documental de plano antes da revisão formal e da aprovação humana pós-revisão; uma PR aberta prematuramente permanece sem autorização de integração até a sequência ser corrigida.
- Nunca falsifique ideação, resultados, checks, aprovação ou conclusão.
- Não mova um ciclo para `executed/` antes da integração de sua entrega e do encerramento autorizado.

### Simplicidade primeiro

- Implemente a menor solução que atenda integralmente ao escopo, aos critérios de aceite e aos gates aprovados.
- Não adicione funcionalidade, abstração, flexibilidade, dependência ou arquitetura especulativa.
- Simplicidade não autoriza reduzir evidência, rastreabilidade, validação ou governança obrigatória.
- Preserve as convenções e a estrutura existentes quando não conflitarem com as autoridades locais ou com o resultado aprovado.

### Mudanças cirúrgicas

- Altere somente arquivos e comportamentos rastreáveis à tarefa autorizada.
- Não refatore, reformate ou corrija elementos adjacentes sem autorização; relate problemas fora do escopo em vez de corrigi-los silenciosamente.
- Preserve mudanças preexistentes, revise o diff e use staging seletivo para que o commit contenha somente o escopo pretendido.
- Ao alterar uma regra de governança, consolide-a na autoridade semanticamente adequada e atualize somente os consumidores e controles necessários para mantê-la efetiva.

### Gestão de incertezas

- Explicite premissas, conflitos, limitações e trade-offs que possam afetar a decisão ou o resultado.
- Quando uma dúvida puder ser resolvida por inspeção local ou validação somente leitura, investigue antes de interromper o solicitante.
- Se interpretações diferentes alterarem materialmente o resultado, ampliarem o escopo ou exigirem nova autoridade, pare antes da mutação e solicite decisão.
- Não invente arquivos, estados, dados, endpoints, URLs, integrações ou capacidades inexistentes; declare o que não puder ser verificado.

## Segurança e mudanças externas

- Nunca versione segredos, credenciais, tokens, chaves privadas ou valores reais de ambiente.
- Não revele dados sensíveis em logs, comentários, tasks ou PRs.
- Ações destrutivas, publicação, merge, deploy e comunicação externa devem estar claramente dentro da autorização recebida.
- Não transforme recomendações externas em decisões locais sem plano ou ADR aprovado.
- Dependências entre repositórios devem ser documentais e fixadas; nenhum fluxo operacional pode depender de checkout irmão.

## Aprendizado

Registre em `.agent/lessons_learned.md` somente lições comprovadas, reutilizáveis e desvinculadas de estado transitório. Estado operacional pertence às tasks e ao GitHub.
