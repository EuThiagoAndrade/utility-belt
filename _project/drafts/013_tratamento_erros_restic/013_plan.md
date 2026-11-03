# Plano de Implementação — Tratamento orientado de erros no Restic

> **Ciclo:** `013`
> **Status:** `Em Execução`
> **Versão:** `v1`
> **Data de criação:** 2026-11-03
> **Última atualização:** 2026-11-03
> **Tipo:** `feature`
> **Prioridade:** `P2`
> **Revisão formal:** `Concluída`
> **Veredito da revisão:** `APTO COM RESSALVAS`
> **Aprovação humana pós-revisão:** `Aprovada em 2026-11-03`

## Objetivo

Explicar erros e resultados incompletos do Restic em linguagem acionável, preservar o diagnóstico e código de saída originais, e oferecer `unlock` assistido quando houver falha de lock, sem iniciar recuperação ou repetição de operação sem decisão explícita do usuário.

## Contexto e baseline

- Repositório `EuThiagoAndrade/utility-belt`; revisão de código inspecionada: `c5a679a3e6a2`; ciclo `013` reservado após aceite da ideação em 2026-11-03.
- Decisões aceitas na ideação: escopo inicial somente Restic; no código 11, opções de aguardar/tentar novamente com lock retry, executar `unlock` ou voltar; confirmação antes do desbloqueio; saída do Restic preservada com resumo final em `stderr`; desbloqueio bem-sucedido não repete a operação que falhou e não altera seu código de saída.
- `src/utility_belt/ui/restic_menu.py` usa `subprocess.run(..., check=True)`. A exceção pode reduzir a falha a `CalledProcessError`; a maioria das ações não captura `stderr` nem mantém o código de retorno disponível para orientar recuperação.
- `src/utility_belt/tools/restic_backup/main.py` devolve códigos de retorno do Restic e já distingue o código 3 de backup incompleto, mas não declara `unlock` nem apresenta orientação dedicada para código 11 ou erro parcial de restauração.
- `src/utility_belt/adapters/restic.py` encaminha subcomandos ao motor e não declara `belt restic unlock`.
- `tests/test_restic_adapter.py` já simula subprocessos e valida códigos de retorno; `tests/test_interactive_menus.py` cobre abertura e roteamento básico dos menus. A interação de erros e unlock ainda não tem cobertura dedicada.
- O exemplo do responsável relata progresso de restauração, uma falha ao ajustar `creation time` para caminho ausente e saída final 1. A causa da ausência do caminho e a integridade completa do destino permanecem desconhecidas.
- `restic_excludes.txt` já estava sem rastreamento antes deste plano; é externo ao ciclo e deve ser preservado.

## Escopo

### Dentro do escopo

- Expor `unlock` no motor Restic, no adaptador CLI e no menu interativo.
- Interpretar o código 11 como falha ao obter lock e orientar o usuário nos canais CLI e menu.
- No menu, oferecer aguardar e tentar novamente com `--retry-lock 1m` (espera limitada a um minuto), executar `unlock` após confirmação ou voltar. O item de menu para desbloqueio manual reutiliza a mesma confirmação.
- Exibir a mensagem/path original do Restic e orientação de conferência quando uma restauração terminar com erro; nunca rotular resultado com código diferente de zero como restauração completa.
- Preservar a saída original e o código de retorno. No CLI, acrescentar orientação em `stderr` ao fim da operação, sem abrir prompt de recuperação.
- Documentar o novo comando e o significado do fluxo no README.
- Testar os resultados por mocks; não executar operações contra repositórios reais.

### Fora do escopo

- Remover locks com `--remove-all`, executar `unlock` automaticamente ou repetir automaticamente a operação original.
- Detectar ou reparar a causa do caminho ausente no sistema de arquivos.
- Garantir integridade do conteúdo restaurado somente com base no resumo, percentual ou contagem informados pelo Restic.
- Criar framework genérico de erros para Docker, Markdown ou outras ferramentas.
- Alterar semântica dos códigos de saída já existentes, inclusive código 3 do backup incompleto.
- Reparar, podar, esquecer snapshots, alterar dados do repositório ou executar validação contra o repositório real do responsável.

## Decisões e autoridades

- Autoridades e template lidos: `.agent/ai_behavior.md`, `_project/README.md`, `_project/cycles.md`, `.agent/workflows/rascunhar_plano.md`, `.agent/workflows/revisar_plano.md` e `.agent/templates/plano_implementacao.md`.
- A ideação 013 foi validada pelo responsável, que aceitou todas as sugestões e pediu o próximo passo em 2026-11-03. O plano foi redigido em `Rascunho` e transitou para `Em Revisão` após autorização explícita (“Pode iniciar a revisão formal do rascunho 013 do ciclo.”) em 2026-11-03.
- A primeira entrega fica restrita ao Restic. A interpretação compartilhada deve ficar em um helper pequeno e específico do Restic, sem criar uma infraestrutura universal.
- A opção de aguardar inicia a operação uma vez com `--retry-lock 1m`, que limita a espera por lock a um minuto. Ao atingir o limite, mostrar o erro e as opções de recuperação novamente; não iniciar outro comando sem nova escolha do usuário.
- A opção `unlock` usa o comportamento padrão do Restic, com confirmação explícita e sem `--remove-all`. Uma operação desbloqueada não dispara novamente o comando anterior. Se o próprio `unlock` falhar com código 11, não oferecer `unlock` recursivamente.
- O item visível no menu será `Desbloquear locks obsoletos`; após código 11, a ação também aparece nas opções contextuais `Aguardar e tentar novamente`, `Executar unlock` e `Voltar`.
- A saída bruta do Restic deve permanecer visível. O motor poderá capturar `stderr` e reapresentá-lo após o processo para adicionar o resumo orientativo, mantendo `stdout` e o progresso da operação fluindo durante a execução.
- Código 11 é falha ao obter lock, não prova isolada de que o lock está obsoleto. Saída desconhecida continua sendo falha e mantém o diagnóstico original.
- A revisão formal foi concluída com veredito `APTO COM RESSALVAS` (R1–R3) e o responsável aprovou o plano v1 com as ressalvas vinculantes R1–R3 em 2026-11-03. O próximo gate requer autorização explícita para publicação documental e/ou criação da issue no GitHub (`criar_issues`).

## Estratégia de testes

- Criar testes focados para o helper de diagnóstico, cobrindo código 11, falha de restauração com detalhe/path, retorno desconhecido e ausência de recomendação indevida de sucesso.
- Atualizar `tests/test_restic_adapter.py` para verificar exposição de `unlock`, seleção por `--repo` ou `--profile`, uso do engine e preservação do retorno real de `unlock` e da operação original.
- Adicionar cobertura do menu interativo para a ação explícita de desbloqueio, confirmação/cancelamento, escolhas contextuais após código 11, aplicação única de `--retry-lock 1m` e ausência de execução automática do unlock ou repetição.
- Verificar que stdout/progresso original permanece visível, o stderr do Restic é preservado e o resumo orientativo vem depois, sem prompt no fluxo CLI.
- Simular erro de restauração com caminho e metadado, confirmar que o resultado é descrito como incompleto e que o código de saída 1 permanece inalterado.
- Executar na implementação os gates do projeto: `uv run python scripts/validate_governance.py`, `uv run ruff check`, `uv run pytest`, `git diff --check` e `git status --short`.
- Não rodar operações Restic reais; testes usam subprocessos simulados ou executável falso controlado.

## Itens de implementação

### Item 1 — Diagnóstico acionável e preservação dos resultados

**Contexto:** A mensagem original do Restic pode indicar o item e a causa técnica, mas o fluxo atual não conecta o código de retorno ao impacto da operação e ao próximo passo.

**Ação técnica:** Criar um helper pequeno e específico do Restic (proposto: `src/utility_belt/restic_diagnostics.py`) que traduza os casos reconhecidos sem substituir saída bruta. Integrá-lo ao `ResticController` no motor e ao `run_restic()` do menu. Manter a saída padrão e o código de retorno originais; no CLI, capturar/reapresentar `stderr` depois do processo para anexar uma orientação em `stderr`. Na restauração com erro, informar que houve falha, manter visíveis mensagem e caminho do Restic, recomendar conferir o destino e evitar declarar a restauração completa.

**Critérios de aceite:**

- [ ] Código 11 em backup, restore, check ou snapshots informa falha ao obter o lock, sugere verificar operação em andamento e aponta `belt restic unlock` como ação deliberada.
- [ ] Falha de restauração com retorno não zero apresenta o detalhe e o item/path reportado pelo Restic, informa que o resultado não está confirmado como completo e orienta conferir o destino.
- [ ] O diagnóstico suplementar não apaga, substitui ou reescreve a saída original do Restic.
- [ ] `stdout` e progresso continuam visíveis durante operações longas; orientação suplementar aparece ao final em `stderr`.
- [ ] Códigos de saída do Restic são preservados; código 3 existente continua reportando backup incompleto.
- [ ] Falhas desconhecidas mantêm a saída bruta e recebem mensagem genérica, sem causa ou recuperação inventada.
- [ ] Nenhum fluxo CLI inicia pergunta interativa de recuperação.

### Item 2 — Subcomando unlock e recuperação assistida

**Contexto:** `unlock` não está exposto nos três pontos de entrada citados na ideação, e a falha ao obter lock não oferece um fluxo seguro de decisão.

**Ação técnica:** Adicionar `cmd_unlock` e parsing de `unlock` em `tools/restic_backup/main.py`, aceitando repositório explícito ou perfil e preservando verificação de identidade configurada. Expor `belt restic unlock` em `adapters/restic.py`. No `restic_menu.py`, incluir `Desbloquear locks obsoletos` com confirmação e, quando uma operação terminar com código 11, oferecer aguardar/repetir com limite de um minuto, executar `unlock` após confirmação ou voltar. Mostrar o resultado do desbloqueio separadamente e deixar a operação original com seu retorno original; não repetí-la automaticamente.

**Critérios de aceite:**

- [ ] `belt restic unlock --repo CAMINHO` e `belt restic unlock --profile NOME` chegam ao motor com o repositório correto e retornam o código do Restic.
- [ ] O parser interno aceita `unlock` sem origem ou destino e segue o padrão de senha, auditoria e verificação de `repo_id` aplicável aos demais comandos.
- [ ] O menu oferece a ação explícita `Desbloquear locks obsoletos`, informa a ação e só executa após confirmação.
- [ ] No código 11 em backup, restore, check ou snapshots, o menu apresenta `Aguardar e tentar novamente`, `Executar unlock` e `Voltar`.
- [ ] Se o próprio comando `unlock` falhar, o menu apresenta o diagnóstico e retorno sem oferecer outro `unlock` recursivo.
- [ ] A espera reapresenta a mesma operação com `--retry-lock 1m`; excedido o limite, não há outra execução automática nem retry ilimitado.
- [ ] A opção `Executar unlock` pede confirmação, usa somente `unlock` padrão e nunca adiciona `--remove-all`.
- [ ] Cancelar a confirmação ou escolher voltar não executa `unlock`.
- [ ] Mesmo quando `unlock` termina com sucesso, o comando que falhou não é repetido e seu código 11 continua reportado; resultado do desbloqueio aparece separadamente.

### Item 3 — Documentação e cobertura do fluxo

**Contexto:** O novo comando e as consequências de um erro parcial precisam ser entendidos sem depender da ideação interna.

**Ação técnica:** Atualizar a seção Restic do `README.md` com o comando `unlock`, o comportamento seguro para locks obsoletos e a interpretação de uma restauração que terminou com erro. Atualizar testes existentes e criar testes específicos do helper e da recuperação no menu.

**Critérios de aceite:**

- [ ] README documenta `belt restic unlock` com `--repo` e `--profile`, confirmação no menu e ausência de desbloqueio forçado.
- [ ] README explica que um resultado de restauração com erro deve ser conferido antes de ser considerado cópia completa.
- [ ] Testes cobrem resultados de sucesso, cancelamento, código 11, código 1 na restauração, códigos desconhecidos e preservação dos códigos.
- [ ] Todos os gates previstos neste plano passam na entrega de implementação, com resultados reais registrados na task.

## Arquivos afetados

- Planejamento: `_project/ideations/013_tratamento_erros_restic.md`, `_project/drafts/013_tratamento_erros_restic/013_plan.md` e `_project/cycles.md`.
- Implementação futura: `src/utility_belt/restic_diagnostics.py` (novo), `src/utility_belt/tools/restic_backup/main.py`, `src/utility_belt/adapters/restic.py`, `src/utility_belt/ui/restic_menu.py` e `README.md`.
- Testes futuros: `tests/test_restic_diagnostics.py` (novo), `tests/test_restic_adapter.py` e cobertura dedicada ao menu (novo `tests/test_restic_menu.py` ou ampliação de `tests/test_interactive_menus.py`, a definir na revisão conforme fixture disponível).
- Execução futura: task da issue neste diretório e evidências reais de gates.

## Decomposição em issues e PRs

- Issue de implementação: [#46](https://github.com/EuThiagoAndrade/utility-belt/issues/46) (`feature`), cobrindo os três itens deste plano (diagnóstico acionável, subcomando unlock e recuperação assistida, documentação e testes) e as ressalvas vinculantes R1–R3.
- Uma PR de implementação correspondente à issue #46, com alterações de engine, adaptador, menu, testes e README.
- Branch planejada para a issue: `feature/issue-46`; commit semântico: `feat(issue-46): orientar erros e desbloqueio do Restic`.

## Dependências e blockers

- Nenhuma dependência Python nova proposta.
- O binário Restic deve suportar `--retry-lock`; validar a compatibilidade na implementação e, se a versão instalada não suportar o parâmetro, exibir erro original e orientação para atualizar/retentar manualmente, sem fallback de repetição ilimitada.
- A implementação requer que os testes possam simular `stdout`, `stderr`, códigos de retorno, confirmações Questionary e argumentos enviados ao Restic.
- Nenhum bloqueio impede a revisão deste rascunho. Aprovação formal, issue e autorização de implementação seguem pendentes.

## Riscos, suposições e rollback

- **Lock ativo:** explicar que código 11 não prova abandono; `unlock` padrão só é oferecido com ação explícita e confirmação. Não adicionar `--remove-all`.
- **Retry indefinido:** limitar a espera do Restic a um minuto por escolha do usuário; interrupção e novo erro devem encerrar a espera claramente, sem relançar o comando automaticamente.
- **Perda de progresso no terminal:** capturar apenas o necessário para o diagnóstico e manter `stdout`/progresso visíveis; verificar o comportamento em TTY e não-TTY nos testes.
- **Saída de Restic muda por versão:** preservar sempre o texto original; códigos conhecidos fornecem orientação estável, e desconhecidos recebem resumo genérico.
- **Restauração considerada completa por engano:** qualquer código não zero é sinalizado como erro, sem afirmar que conteúdo foi integralmente restaurado.
- **Senha ou conteúdo sensível:** o helper não persiste credenciais nem registra conteúdo de arquivos; a auditoria atual deve continuar sem senha.
- **Rollback:** reverter somente a issue/PR aprovada; remover o subcomando e as mensagens de interface adicionados, sem alterar locks, repositórios, destinos de restauração, perfis ou arquivos pessoais.
- **Prioridade P2 proposta:** melhora a segurança operacional e entendimento em backup/restauração, mas não há evidência de perda de dados que justifique classificar como P1 neste rascunho.

## Sequência recomendada

1. Apresentar este `Rascunho` e obter autorização explícita para iniciar `revisar_plano`.
2. Executar revisão crítica formal, registrar veredito e corrigir bloqueios materiais.
3. Aguardar aprovação humana posterior ao veredito; somente então seguir os gates de aprovação/publicação documental e criação de issue descritos pela governança.
4. Com plano aprovado, issue válida e autorização explícita de implementação, criar branch, task persistente e implementar os três itens.
5. Executar os gates mínimos e critérios desta entrega, registrar evidências reais na task e preparar uma PR revisável.
6. Aguardar as autorizações de publicação/integração aplicáveis; não executar `unlock` em um repositório real como parte de desenvolvimento ou teste.

## Referências

- Decisões aceitas pelo responsável na conversa de 2026-11-03; ideação `_project/ideations/013_tratamento_erros_restic.md`.
- `.agent/ai_behavior.md`; `_project/README.md`; `_project/cycles.md`; `.agent/workflows/rascunhar_plano.md`; `.agent/workflows/revisar_plano.md`; `.agent/templates/plano_implementacao.md`.
- `src/utility_belt/ui/restic_menu.py`; `src/utility_belt/adapters/restic.py`; `src/utility_belt/tools/restic_backup/main.py`; `tests/test_restic_adapter.py`; `tests/test_interactive_menus.py`; seção Restic do `README.md`.
- [Restic exit codes and JSON output](https://restic.readthedocs.io/en/v0.19.0/075_scripting.html); [Restic manual](https://restic.readthedocs.io/en/stable/manual_rest.html); [Restic troubleshooting](https://restic.readthedocs.io/en/stable/077_troubleshooting.html).

## Rastreabilidade

| Campo | Valor |
| :-- | :-- |
| Issue(s) | [#46](https://github.com/EuThiagoAndrade/utility-belt/issues/46) |
| PR(s) | [#47](https://github.com/EuThiagoAndrade/utility-belt/pull/47) |
| Branch(es) | `feature/issue-46` |
| `handoff_schema_version` | `1` |
| `handoff_id` | `EuThiagoAndrade/utility-belt+013+implementar_issue+issue-46+c5a679a3e6a2/pr-47` |
| Destino após conclusão | `_project/executed/013_tratamento_erros_restic/013_plan.md` |

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+013+criar_issues+tratamento-erros-restic+c5a679a3e6a2/issue-46`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision` = `EuThiagoAndrade/utility-belt + 013 + criar_issues + tratamento-erros-restic + c5a679a3e6a2068fc28b3bb63fd2794d6c671cdf/issue-46`
- `effect_class`: `remote_mutation`
- `state_before`: plano v1 `Aprovado` com ressalvas vinculantes R1–R3; issue no GitHub pendente de criação.
- `state_after`: issue [#46](https://github.com/EuThiagoAndrade/utility-belt/issues/46) criada no GitHub como `OPEN`, rótulo `enhancement`, com rastreabilidade ao plano e critérios de aceite vinculantes; sem branch ou código de implementação criado.
- `next_transition`: `issue -> implementação autorizada`.
- `preconditions`: autorização explícita do responsável para iniciar o workflow de implementação (`implementar_issue`) na branch `feature/issue-46`.
- `authority`: responsável humano autoriza a implementação da issue #46.
- `evidence`: issue [#46](https://github.com/EuThiagoAndrade/utility-belt/issues/46) registrada no GitHub (`gh issue view 46`); payload correspondente ao plano aprovado; `_project/cycles.md` e plano atualizados.
- `acceptance`: issue única criada no GitHub, rastreável ao ciclo 013 e ao plano, sem implementação incidental ou alterações fora de escopo.
- `blockers`: nenhum bloqueador técnico; aguardando autorização explícita para iniciar a implementação (`implementar_issue`).
- `result`: `executed`
- `next_workflow_recommended`: `implementar_issue` (para a issue #46 na branch `feature/issue-46`).
- `next_workflow_authorized`: `nenhum` (aguardando autorização humana explícita para implementar).
- `actions_prohibited`: alterar código-fonte, criar arquivos de implementação, abrir branch/PR de implementação sem autorização explícita.
- `rejection_rule`: o receptor recusa handoff ausente, incompatível, contraditório, sem issue canônica remota comprovada ou que inicie implementação sem autorização.
- `logical_key`: `EuThiagoAndrade/utility-belt+013+criar_issues+tratamento-erros-restic+c5a679a3e6a2/issue-46`
- `check_before_mutation`: conferido previamente via `gh issue list` a ausência de duplicidade para o ciclo 013 e plano aprovado antes da criação remota.
- `reconcile_existing`: issue #46 registrada canonicamente em `cycles.md` e no plano v1.
- `ambiguous_state`: parar se houver conflito de issue ou divergência com o plano aprovado.

### Handoff do plano aprovado (histórico)

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+013+revisar_plano+tratamento-erros-restic+c5a679a3e6a2/v1-aprovado`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision` = `EuThiagoAndrade/utility-belt + 013 + revisar_plano + tratamento-erros-restic + c5a679a3e6a2068fc28b3bb63fd2794d6c671cdf/v1-aprovado`
- `effect_class`: `local_mutation`
- `state_before`: plano v1 em `Em Revisão`, parecer `APTO COM RESSALVAS` (R1–R3) emitido e aguardando manifestação humana pós-revisão.
- `state_after`: plano v1 em `Aprovado`, com `Aprovação humana pós-revisão: Aprovada em 2026-11-03` e ressalvas vinculantes R1–R3 incorporadas; sem mutação remota, sem issue criada e sem implementação iniciada.
- `next_transition`: `plano aprovado -> criação de issue (e publicação documental conforme autorização)`.
- `preconditions`: plano em `Aprovado` com R1–R3 aceitas; autorização explícita do responsável para o payload remoto da issue (`criar_issues`) e para eventual publicação documental; posteriormente, autorização explícita antes de `implementar_issue`.
- `authority`: manifestação humana em 2026-11-03 (“Aprovo o plano v1 com as ressalvas vinculantes R1–R3”), que satisfaz o gate de aprovação pós-revisão do plano; mutações remotas (issue/PR) e implementação requerem autorização explícita.
- `evidence`: este plano (seção `Revisão crítica` e `Aprovação humana pós-revisão`); `_project/ideations/013_tratamento_erros_restic.md`; `_project/cycles.md`; `.github/ISSUE_TEMPLATE/feature_request.yml`.
- `acceptance`: status `Aprovado` registrado após veredito formal e decisão humana posterior; rascunho do payload da issue preparado conforme `.github/ISSUE_TEMPLATE/feature_request.yml` sem execução remota não autorizada.
- `blockers`: nenhum bloqueador técnico; aguarda autorização explícita para criar a issue no GitHub (e/ou publicar a branch documental) antes de iniciar a implementação.
- `result`: `executed`
- `next_workflow_recommended`: `criar_issues` (com o payload `feature` abaixo, incluindo os itens 1–3 e R1–R3).
- `next_workflow_authorized`: `nenhum` (aguardando autorização explícita para criar a issue e/ou iniciar implementação).
- `actions_prohibited`: criar issue no GitHub sem confirmação do payload; implementar código; publicar branch/PR; integrar PR; executar operações em repositório Restic real.
- `rejection_rule`: o receptor recusa handoff ausente, incompatível, contraditório ou que inicie mutação remota/implementação sem autorização explícita.
- `logical_key`: `EuThiagoAndrade/utility-belt+013+revisar_plano+tratamento-erros-restic+c5a679a3e6a2/v1-aprovado`
- `check_before_mutation`: confirmar parecer `APTO COM RESSALVAS` previamente emitido e manifestação humana posterior aprovando v1 com R1–R3.
- `reconcile_existing`: preservar parecer v1 e histórico de handoffs sem duplicar artefatos.
- `ambiguous_state`: parar em caso de divergência entre o plano aprovado e o escopo da issue proposta.

### Handoff da revisão v1 (histórico)

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+013+revisar_plano+tratamento-erros-restic+c5a679a3e6a2/v1`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision` = `EuThiagoAndrade/utility-belt + 013 + revisar_plano + tratamento-erros-restic + c5a679a3e6a2068fc28b3bb63fd2794d6c671cdf/v1`
- `effect_class`: `local_mutation`
- `state_before`: plano v1 em `Rascunho`, handoff de `rascunhar_plano` íntegro e revisão formal autorizada pelo responsável; baseline `c5a679a3e6a2` e ciclo `013` em `Planejamento`.
- `state_after`: plano v1 em `Em Revisão`, parecer formal `APTO COM RESSALVAS` (R1–R3) registrado e `Aprovação humana pós-revisão: Pendente`; sem criação de issue, branch de implementação ou mutação remota.
- `next_transition`: `parecer -> aprovação humana pós-revisão`.
- `preconditions`: decisão humana explícita, posterior a este parecer, aprovando o plano v1 com as ressalvas vinculantes R1–R3; posteriormente, issue vinculada e autorização explícita antes de implementar.
- `authority`: responsável humano aprova ou solicita ajustes após conhecer este parecer; a solicitação de revisão recebida em 2026-11-03 autorizou exclusivamente `revisar_plano`.
- `evidence`: este plano (seção `Revisão crítica`); `_project/ideations/013_tratamento_erros_restic.md`; `_project/cycles.md`; `.agent/templates/plano_implementacao.md`; `.agent/workflows/revisar_plano.md`; arquivos inspecionados (`src/utility_belt/ui/restic_menu.py`, `src/utility_belt/adapters/restic.py`, `src/utility_belt/tools/restic_backup/main.py`, `tests/test_restic_adapter.py`, `tests/test_interactive_menus.py`, `README.md`) e resultados reais dos gates locais.
- `acceptance`: parecer explícito (`APTO COM RESSALVAS`), ressalvas vinculantes R1–R3 classificadas, bloqueadores técnicos de planejamento ausentes e aprovação humana pós-revisão não inferida (`Pendente`).
- `blockers`: nenhum bloqueador técnico de planejamento; aprovação humana pós-revisão, criação de issue e autorização de implementação permanecem pendentes.
- `result`: `executed`
- `next_workflow_recommended`: após aprovação humana pós-revisão, registrar `Aprovado` e seguir com publicação documental e `criar_issues` conforme autorização aplicável.
- `next_workflow_authorized`: `nenhum` (aguardando manifestação humana pós-revisão).
- `actions_prohibited`: marcar `Aprovado`, criar issue, implementar, publicar branch/PR ou integrar PR sem os gates próprios; executar operações em repositório Restic real.
- `rejection_rule`: o receptor recusa handoff ausente, incompatível, contraditório, sem parecer formal ou que trate aptidão técnica ou pedido de revisão como aprovação humana pós-revisão.
- `logical_key`: `EuThiagoAndrade/utility-belt+013+revisar_plano+tratamento-erros-restic+c5a679a3e6a2/v1`
- `check_before_mutation`: plano v1 em `Rascunho` sem parecer anterior para a revisão `c5a679a3e6a2/v1`, handoff predecessor íntegro e autorização explícita de revisão verificados antes da transição para `Em Revisão`.
- `reconcile_existing`: atualizar este parecer apenas com nova evidência ou revisão, preservando o histórico e sem duplicar artefatos.
- `ambiguous_state`: parar quando o plano mudar durante a revisão, a baseline divergir ou houver decisões humanas conflitantes.

### Handoff da redação v1 (histórico)

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+013+rascunhar_plano+tratamento-erros-restic+c5a679a3e6a2/v1`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision` = `EuThiagoAndrade/utility-belt + 013 + rascunhar_plano + tratamento-erros-restic + c5a679a3e6a2/v1`
- `effect_class`: `local_mutation`
- `state_before`: ciclo 013 com ideação aceita; plano ainda não existia; usuário autorizou o próximo passo como rascunho; código inspecionado em `c5a679a3e6a2`.
- `state_after`: plano v1 em `Rascunho`, com escopo, itens, critérios, testes, riscos e decisões aceitas rastreáveis; sem revisão formal, aprovação, issue ou implementação.
- `next_transition`: `rascunho -> revisão formal`.
- `preconditions`: autoridades e template lidos; identidade do repositório e ciclo confirmados; decisões de ideação aceitas; autorização explícita para redigir plano.
- `authority`: responsável autorizou avançar ao próximo passo em 2026-11-03; autorização limitada ao rascunho.
- `evidence`: este plano; `_project/ideations/013_tratamento_erros_restic.md`; `_project/cycles.md`; `.agent/workflows/rascunhar_plano.md`; `.agent/templates/plano_implementacao.md`; arquivos e testes listados em “Contexto e baseline”.
- `acceptance`: todas as seções do template foram instanciadas; status permanece `Rascunho`; decisões aceitas estão materializadas; revisão e implementação não foram executadas.
- `blockers`: nenhum para o rascunho; revisão formal e decisão humana posterior permanecem gates.
- `result`: `executed`
- `next_workflow_recommended`: `revisar_plano`.
- `next_workflow_authorized`: `nenhum` (aguardando autorização explícita para a revisão formal).
- `actions_prohibited`: marcar o plano como `Aprovado`; criar issue; implementar; criar branch de issue; abrir PR; executar operações em repositório Restic real.
- `rejection_rule`: o receptor recusa handoff ausente, incompatível, contraditório, com status promovido sem revisão ou sem evidência material.
- `logical_key`: `EuThiagoAndrade/utility-belt+013+rascunhar_plano+tratamento-erros-restic+c5a679a3e6a2/v1`
- `check_before_mutation`: verificar plano existente, estado `Planejamento` do ciclo, identidade `EuThiagoAndrade/utility-belt` e ausência de artefato canônico concorrente.
- `reconcile_existing`: atualizar este rascunho v1 sem duplicar plano ou ciclo e registrar alterações de escopo por nova revisão.
- `ambiguous_state`: parar se houver segundo plano canônico, ciclo ou identidade divergente, ou se o usuário alterar decisões materiais da ideação.

## Revisão crítica

- **Data:** 2026-11-03
- **Versão revisada:** `v1`, baseline `c5a679a3e6a2068fc28b3bb63fd2794d6c671cdf`.
- **Veredito:** `APTO COM RESSALVAS`
- **Bloqueios remanescentes:** nenhum bloqueador técnico de planejamento; aprovação humana posterior registrada abaixo.
- **Aprovação humana pós-revisão:** `Aprovada em 2026-11-03`
- **Correções materiais:** status promovido de `Rascunho` para `Em Revisão` e, após decisão humana posterior ao parecer, para `Aprovado`, incorporando as ressalvas vinculantes R1–R3 sem ampliar o escopo.
- **Ressalvas:** R1–R3 abaixo, vinculantes para a issue e para a implementação.

### Parecer v1

#### Autorização e aceite do predecessor

- Solicitação humana de revisão: “Pode iniciar a revisão formal do rascunho 013 do ciclo.”, em 2026-11-03.
- Handoff recebido: `EuThiagoAndrade/utility-belt+013+rascunhar_plano+tratamento-erros-restic+c5a679a3e6a2/v1`. Aceito: identidade, revisão de origem (`c5a679a3e6a2`), ciclo `013`, template e decisões da ideação são compatíveis e sem conflitos.
- Transição de entrada: `Rascunho` → `Em Revisão` aplicada antes da emissão deste parecer, mantendo `Aprovação humana pós-revisão: Pendente`.

#### Evidências e itens atendidos

- Estrutura canônica conferida contra `.agent/templates/plano_implementacao.md`: todas as 16 seções de nível 2 e os 10 metadados de cabeçalho estão presentes e preenchidos.
- Alinhamento com a ideação `_project/ideations/013_tratamento_erros_restic.md`: escopo restrito ao Restic, código 11 com `Aguardar e tentar novamente` (`--retry-lock 1m`), `Executar unlock` mediante confirmação explícita (sem `--remove-all`) e `Voltar`, preservação do código 11 original sem repetição automática pós-unlock, e diagnóstico de restauração parcial preservando caminho/erro original sem declarar conclusão integral.
- Inspeção do código-fonte real (`src/utility_belt/ui/restic_menu.py`, `src/utility_belt/adapters/restic.py`, `src/utility_belt/tools/restic_backup/main.py` e `src/utility_belt/runner.py`) confirmou os pontos de entrada, a ausência atual de `unlock` e a arquitetura de execução e auditoria.
- Decomposição em uma única issue `feature` é proporcional e coerente, pois helper de diagnóstico, subcomando `unlock`, menu interativo, testes e README compõem a mesma unidade funcional.

#### Bloqueadores

- Nenhum bloqueador técnico ou de governança no plano.

#### Ressalvas vinculantes

- **R1 — Isolamento de testes e proteção contra `getpass.getpass()` fora de TTY (`tests/test_interactive_menus.py`, `tools/restic_backup/main.py` e `adapters/restic.py`).** Durante a auditoria desta revisão, verificou-se que `tests/test_interactive_menus.py::TestCLICallbackBehavior::test_belt_restic_with_subcommand_does_not_open_menu` invoca `runner.invoke(app, ["restic", "snapshots"])` sem simular `run_tool` nem isolar a configuração do host. Quando a máquina possui perfil Restic real em `%APPDATA%\utility-belt\config.toml` e binário `restic` instalado, o teste dispara o subprocesso real `tools/restic_backup/main.py`, encontra o repositório configurado e chama `getpass.getpass()`, que no Windows lê diretamente do console (`CONIN$` via `msvcrt.getwch()`), bloqueando indefinidamente `uv run pytest` (ou acessando o repositório real caso `RESTIC_PASSWORD` esteja definida). Na implementação: (a) isolar `test_belt_restic_with_subcommand_does_not_open_menu` (e o teste análogo de Docker) com mock de `run_tool` para garantir que a suíte jamais acesse configuração ou repositório real do host; (b) suportar `--non-interactive` também em `unlock` (além de `check` e `snapshots`) e tratar `self.non_interactive or not sys.stdin.isatty()` em `ResticController.get_password()`, recusando abrir `getpass.getpass()` quando `stdin` não for TTY.
- **R2 — Streaming de `stdout`/progresso em tempo real e verificação de identidade sob lock (`tools/restic_backup/main.py`).** Para atender simultaneamente aos critérios de manter `stdout`/progresso visíveis durante operações longas e anexar o diagnóstico em `stderr` ao final, `ResticController.run_restic()` (quando `capture_output=False`) não deve tamponar `stdout`: deve manter `stdout` herdado do terminal e capturar apenas `stderr` (`stderr=subprocess.PIPE`), reemitindo `stderr` integralmente em `sys.stderr` logo após o término do processo antes do resumo suplementar. Além disso, em `verify_repo_id()`, `restic cat config` deve ser invocado com `--no-lock` (`["cat", "config", "--no-lock"]`) ou propagar o código `11` caso falhe por lock exclusivo, evitando que um lock ativo/obsoleto faça `verify_repo_id()` abortar precocemente com código `2` e impeça a execução de `belt restic unlock` ou o diagnóstico do código `11`.
- **R3 — Semântica de retorno em `ui/restic_menu.py` e bloqueio de falso sucesso em `do_restore()`.** Atualmente, `do_restore()` verifica apenas `if result is not None:` antes de perguntar `"Restauração concluída. Deseja abrir a pasta no Windows Explorer?"`. Ao remover `check=True` (ou ao tratar erros dentro de `run_restic()`), `do_restore()` somente pode exibir mensagem de conclusão ou oferecer abrir a pasta quando `result is not None and result.returncode == 0`. Se a operação terminar com código diferente de zero (incluindo código `1` com arquivos restaurados parcialmente, ou código `11` mesmo após `Executar unlock` concluir o desbloqueio com sucesso), `run_restic()` deve preservar o resultado da operação original como não concluído, sem anunciar restauração completa.

#### Verificações executadas

- `uv run python scripts/validate_governance.py`: `46 verificações | 45 OK | 1 Avisos | 0 Falhas` (o único aviso refere-se ao cálculo do próximo ciclo `014` sobre o último concluído `012` enquanto `013` está em `Planejamento`).
- `uv run ruff check`: `All checks passed!`.
- `uv run pytest tests/test_restic_adapter.py -v`: `7 passed in 0.58s`.
- `uv run pytest -q -k "not test_belt_restic_with_subcommand_does_not_open_menu and not test_belt_docker_with_subcommand_does_not_open_menu"`: `251 passed, 36 skipped, 2 deselected in 54.43s`, e `uv run pytest tests/test_interactive_menus.py -k "not test_belt_restic_with_subcommand_does_not_open_menu" -q`: `28 passed, 1 deselected in 0.84s` (confirmando que o bloqueio em `pytest` decorre exclusivamente da chamada sem mock em `test_belt_restic_with_subcommand_does_not_open_menu`, endereçada na ressalva R1).
- `git diff --check`: passou sem erros de formatação ou espaços finais.
- `git status --short`: apenas artefatos documentais do ciclo `013` (`_project/cycles.md`, `_project/ideations/013_tratamento_erros_restic.md`, `_project/drafts/013_tratamento_erros_restic/013_plan.md`) e `restic_excludes.txt` preexistente preservado.

### Aprovação humana pós-revisão

- Em 2026-11-03, após apresentação do parecer `APTO COM RESSALVAS`, o responsável declarou: “Aprovo o plano v1 com as ressalvas vinculantes R1–R3”.
- Transição registrada: `Em Revisão` → `Aprovado`, com `Aprovação humana pós-revisão: Aprovada em 2026-11-03` e incorporação integral de R1–R3.
- O próximo passo requer autorização explícita para o payload remoto da issue (`criar_issues`) e eventual publicação documental antes da implementação.

## Pós-mortem

- **Data de conclusão:** —
- **Desvios:** —
- **Lições comprovadas:** —
