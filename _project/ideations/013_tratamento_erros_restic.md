# Ideação — 013: Tratamento orientado de erros no Restic

> **Ciclo:** `013`
> **Estado:** `Ideação`
> **Criado em:** 2026-11-03
> **Última atualização:** 2026-11-03

## Problema

Quando uma operação Restic falha, a interface atual pode deixar o usuário com uma exceção Python, um código de saída ou uma mensagem fatal da ferramenta sem explicar, em linguagem direta, o que falhou, o que se sabe sobre a causa e qual próximo passo é seguro. O usuário precisa conseguir responder na própria tela: **qual foi o erro, qual foi o impacto da operação e o que posso fazer agora?**

Dois casos concretos motivam esta ideação:

1. O menu interativo (`ui/restic_menu.py`), o adaptador Typer (`adapters/restic.py`) e o motor (`tools/restic_backup/main.py`) não expõem `unlock`. Também não há tratamento dedicado para o código 11 do Restic, que indica falha ao obter o lock do repositório. O desbloqueio pode ajudar quando há lock obsoleto, mas não se deve presumir que todo lock é obsoleto nem remover um lock enquanto outra operação estiver ativa.
2. Uma restauração relatou 164.889 arquivos e diretórios restaurados, mas também falhou ao ajustar o horário de criação de `node_modules`, pois o caminho de destino indicado não existia, e terminou com `Fatal: There were 1 errors`. A saída capturada pelo usuário termina em uma exceção Python com o código 1. Ela não explica claramente que houve progresso substancial, qual item teve problema nem o que conferir antes de considerar a restauração utilizável.

## Contexto e evidências

- Revisão local inspecionada: `c5a679a3e6a2`; ciclo `013` estava livre e é o próximo ciclo declarado em `_project/cycles.md`.
- `src/utility_belt/ui/restic_menu.py` executa Restic via `subprocess.run(..., check=True)`. Em `CalledProcessError`, exibe a exceção e, quando disponível, `stderr`; a maioria das operações não captura a saída. O menu não oferece `unlock`.
- `src/utility_belt/adapters/restic.py` encaminha subcomandos para `restic_backup.main` e não declara o comando `unlock`.
- `src/utility_belt/tools/restic_backup/main.py` usa `ResticController.run_restic()` e devolve `proc.returncode` nos comandos; seu parser não declara `unlock`. Assim, a mensagem útil do Restic pode existir no terminal, mas o motor não a converte em uma orientação compreensível e consistente.
- A documentação oficial de scripting do Restic define o código 11 como “Failed to lock repository” e recomenda tratar códigos desconhecidos como falha: [Exit codes — Restic 0.19.0](https://restic.readthedocs.io/en/v0.19.0/075_scripting.html).
- A documentação oficial informa que operações interrompidas podem exigir `unlock` manual e descreve procedimentos de recuperação para repositórios: [Troubleshooting — Restic](https://restic.readthedocs.io/en/stable/077_troubleshooting.html).
- No exemplo de restauração apresentado pelo solicitante, a ferramenta informa progresso de 100%, 164.889 itens e 4,577 GiB, seguido de um erro ao restaurar a data de criação de um caminho. A causa da ausência do caminho, os itens afetados além desse erro e a integridade final do destino não foram verificados; a ideação não deve presumir esses fatos.
- A mensagem de erro na CLI deve preservar detalhes técnicos úteis e o código real de saída, sem exigir interação ou esconder a saída original da ferramenta.

## Resultado desejado

Para cada erro que o Utility Belt reconheça, apresentar uma explicação orientada à ação, no canal apropriado, com os elementos que se aplicarem:

1. **O que aconteceu:** operação e erro em termos claros, mantendo código e mensagem originais disponíveis para diagnóstico.
2. **Impacto conhecido:** falha total, cancelamento ou resultado parcial; distinguir fatos observados de informação indisponível.
3. **O que fazer agora:** próximo passo seguro e específico, incluindo quando aguardar, conferir caminhos ou consultar o diagnóstico detalhado.
4. **Ação assistida opcional:** quando houver recuperação segura e consentida, explicar o que será executado antes de pedir confirmação.

Aplicado aos exemplos:

- **Código 11:** identificar falha ao obter o lock. Explicar que pode existir outra operação ativa ou um lock abandonado. Orientar a verificar se há backup/restauração em andamento; no menu, oferecer executar `unlock` somente após confirmação explícita do usuário. Na CLI não interativa, explicar a causa provável e instruir como verificar e invocar `belt restic unlock`, preservando código de saída 11 da operação que falhou.
- **Restauração com erro de metadados:** informar que Restic reportou restauração de 164.889 itens e apontou falha ao definir a data de criação do caminho indicado. Classificar o resultado como incompleto ou parcial quando o retorno e a saída indicarem erro; não declarar a restauração integralmente concluída. Orientar a conferir o destino e o item afetado antes de usar o conteúdo como cópia completa. Não executar automaticamente outra restauração nem sugerir excluir ou sobrescrever dados sem diagnóstico.

## Hipóteses

- Um formato comum de diagnóstico (operação, código, mensagem original, impacto conhecido e próximo passo) pode manter coerência entre menu e CLI sem forçar prompts interativos em automações.
- A apresentação pode variar por interface: explicação curta e confirmação no menu; orientação objetiva em `stderr` e código de saída preservado na CLI.
- Para o erro de restauração, a saída estruturada do Restic, quando disponível, pode ajudar a identificar o item e o tipo de falha; mensagens em texto e versões antigas ainda exigirão fallback que preserve a saída original.
- A primeira entrega deve provavelmente se concentrar nos fluxos Restic apresentados. Expandir uma taxonomia compartilhada para Docker, Markdown ou todas as ferramentas pode aumentar o ciclo e precisa de validação própria.
- A ação `unlock` deve ser deliberada. O código 11 identifica falha de lock, mas sozinho não demonstra que o processo que o mantém terminou.

## Alternativas

1. **Manter saída técnica atual:** preserva o comportamento e não resolve a dúvida do usuário sobre causa e recuperação.
2. **Adicionar mensagens específicas apenas no menu:** ajuda no uso interativo, mas deixa o adaptador CLI e o motor com resultados desiguais e não atende scripts.
3. **Criar tratamento contextual para Restic nos canais existentes:** interpretar códigos e resultados conhecidos, preservar o diagnóstico original e exibir orientação distinta para menu e CLI. É a direção recomendada para planejamento, mantendo o escopo inicial nos dois exemplos e evitando uma arquitetura genérica antes de haver evidência.
4. **Construir uma camada universal de erros para todos os adaptadores:** pode uniformizar o produto, mas é prematura sem casos concretos e critérios para cada ferramenta.

## Riscos e restrições

- **Lock ainda ativo:** código 11 não prova que o lock está abandonado. Explicar que `unlock` se destina a locks obsoletos e pedir confirmação; não executar automaticamente ao receber código 11.
- **Limites de `unlock`:** a ação padrão remove locks obsoletos; não incluir `--remove-all` nesta proposta. Mostrar a saída do Restic caso o lock não seja considerado obsoleto.
- **Erro parcial interpretado como sucesso:** código 1 junto com progresso não comprova que os arquivos restaurados estejam completos ou utilizáveis. Comunicar progresso e erro separadamente, sem garantia indevida.
- **Diagnóstico frágil por texto:** mensagens podem mudar entre versões ou localização. Preferir código de saída e saída JSON estruturada quando aplicável; manter fallback legível e detalhe bruto.
- **Compatibilidade de saída:** não suprimir os logs úteis do Restic, nem substituir um código de erro por sucesso após uma ação assistida sem verificar o resultado.
- **Segredos e dados locais:** não registrar senha, conteúdo sensível ou despejo excessivo de saída em logs de auditoria.
- **CLI automatizada:** não iniciar prompts, abrir UI ou aguardar interação em modo não interativo.
- **Escopo:** a implementação, se aprovada mais tarde, deve seguir o plano e a issue do ciclo. Esta ideação não autoriza mudanças de código.

## Decisões aceitas

Em 2026-11-03, o responsável aceitou as sugestões de resposta e autorizou avançar ao rascunho do plano:

- **Escopo:** começar com os dois exemplos Restic; outros adaptadores ficam fora desta entrega.
- **Código 11 no menu:** oferecer aguardar/tentar novamente com `--retry-lock`, executar `unlock` após confirmação explícita ou voltar. Explicar que `unlock` trata locks obsoletos e não executar `--remove-all`.
- **Diagnóstico da restauração:** exibir a mensagem e o caminho apontado pelo Restic, informar progresso/resultado reportado e orientar a conferir o destino antes de considerá-lo uma cópia completa; não repetir nem sobrescrever automaticamente.
- **CLI:** preservar a saída original do Restic e acrescentar um resumo orientativo em `stderr` ao final, sem prompt interativo.
- **Resultado após `unlock`:** registrar o resultado do desbloqueio separadamente; a operação original continua com seu código de saída 11 e não é repetida automaticamente.
- **Opções do menu:** apresentar `Aguardar e tentar novamente`, `Executar unlock` e `Voltar`, com confirmação para o desbloqueio.

## Fora do escopo

- Executar `unlock` automaticamente ou remover locks sem confirmação explícita.
- Prometer que uma restauração com código diferente de zero está completa com base apenas no percentual ou na contagem apresentada.
- Corrigir a causa de sistema de arquivos do erro de `creation time` sem diagnóstico adicional.
- Recuperar, reparar ou modificar repositórios automaticamente; comandos como `repair`, `prune` ou `forget` não são propostos nesta ideação.
- Criar uma estrutura universal de erros para todas as ferramentas sem decisão de escopo.
- Implementar código, criar issue ou abrir PR antes dos gates de planejamento e autorização previstos pela governança.

## Critérios para iniciar o planejamento

- [x] Responsável aceitou as decisões acima e autorizou preparar o próximo artefato em 2026-11-03.
- [x] Escopo delimitado aos fluxos Restic.
- [x] Comportamento de código 11, orientação para restauração parcial e saída da CLI definidos para o rascunho.
- [ ] Revisão formal e aprovação humana posterior do plano, exigidas antes de publicação, issues ou implementação conforme aplicável.

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+013+idear+tratamento-erros-restic+c5a679a3e6a2`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`
- `effect_class`: `local_mutation`
- `state_before`: ciclo `013` livre conforme `_project/cycles.md`; ausência de ideação para este alvo; exemplo do solicitante e código atual inspecionados na revisão `c5a679a3e6a2`.
- `state_after`: ideação registrada e decisões aceitas pelo responsável; autorização explícita recebida para redigir o rascunho do plano.
- `next_transition`: `ideia -> rascunho de plano`, somente após decisão humana.
- `preconditions`: objetivo compreensível; autoridades e template locais lidos; ciclo e alvo lógico conferidos.
- `authority`: solicitação explícita do responsável para idear e aceite de todas as sugestões com pedido para avançar ao próximo passo, em 2026-11-03; autorização limitada a `rascunhar_plano`.
- `evidence`: `_project/ideations/013_tratamento_erros_restic.md`; `_project/cycles.md`; `.agent/templates/ideacao.md`; `src/utility_belt/ui/restic_menu.py`; `src/utility_belt/adapters/restic.py`; `src/utility_belt/tools/restic_backup/main.py`; documentação oficial Restic ligada em “Contexto e evidências”.
- `acceptance`: perguntas “qual foi o erro?”, “qual foi o impacto?” e “o que fazer agora?” estão contempladas para ambos os exemplos; incertezas e ações inseguras estão explícitas; nenhuma implementação foi autorizada.
- `blockers`: nenhum para redigir o rascunho; revisão formal e decisão humana pós-revisão permanecem pendentes.
- `result`: `executed`
- `next_workflow_recommended`: `rascunhar_plano`, autorizado pelo responsável após aceitar as decisões em 2026-11-03.
- `next_workflow_authorized`: `rascunhar_plano`
- `actions_prohibited`: aprovar ou executar plano, criar issue, alterar código de produção, publicar branch ou PR, executar `unlock` em repositório real.
- `rejection_rule`: o receptor recusa handoff ausente, incompatível, contraditório ou sem evidência material suficiente; aprovação da ideação não substitui revisão formal nem autorização posterior.
- `logical_key`: `EuThiagoAndrade/utility-belt+013+idear+tratamento-erros-restic+c5a679a3e6a2`
- `check_before_mutation`: confirmar repositório `EuThiagoAndrade/utility-belt`, revisão de origem, ciclo `013` livre e ausência de ideação conflitante.
- `reconcile_existing`: não duplicar o artefato; incorporar refinamentos compatíveis nesta ideação, atualizando data, evidências e identidade se a revisão de origem mudar.
- `ambiguous_state`: interromper atualização se ciclo, identidade do repositório, revisão ou escopo da ideação divergirem.
