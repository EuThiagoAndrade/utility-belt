# Plano de Implementação — Demonstração dos menus em GIF

> **Ciclo:** `012`
> **Status:** `Concluído` (proposta documental, efetiva após integração da PR de closure)
> **Versão:** `v1`
> **Data de criação:** 2026-10-21
> **Última atualização:** 2026-10-21
> **Tipo:** `chore`
> **Prioridade:** `P2`
> **Revisão formal:** `Concluída`
> **Veredito da revisão:** `APTO COM RESSALVAS`
> **Aprovação humana pós-revisão:** `Aprovada em 2026-10-21`

## Objetivo

Produzir um GIF de 25–35 segundos que percorra os menus Restic, Docker, Markdown, Desenvolvimento e Sistema, retornando ao menu principal entre eles e sem executar suas operações. Exibir a demonstração diretamente no README do GitHub.

## Contexto e baseline

- Repositório `EuThiagoAndrade/utility-belt`, baseline `main` em `5b0cb559ebf2d67b9f30f793a6484f201e0723e5`, árvore inicialmente limpa; ciclo disponível `012`.
- Contexto equivalente à ideação: conversa de 2026-10-21 e solicitação humana “Gostei da sua sugestão, vamos implementar isso.” O pedido direto permite iniciar o planejamento sem ideação separada, conforme `_project/README.md`; não substitui revisão e aprovação humana pós-revisão.
- `tests/ui_smoke.py` já captura navegação Questionary com teclado controlado, saída VT100, emulação por pyte e renderização com Pillow. É uma referência técnica, não evidência de execução do novo roteiro.
- FFmpeg e Consolas estão disponíveis neste Windows. Questionary está na `.venv`; pyte e Pillow não estão instalados nela e serão opcionais para geração.
- `src/utility_belt/menu.py` verifica dependências antes de Restic e Docker; o guard de Docker consulta seu executável. O gerador deverá isolar esse preflight para apresentar os menus sem consultas a serviços externos.
- Nenhum menu foi executado e nenhuma mídia foi gerada nesta etapa.
- Verificação documental do rascunho: `uv run python scripts/validate_governance.py` retornou 43 OK, 1 aviso e 0 falhas; `git diff --check` passou. O aviso decorre de o validador calcular o próximo ciclo apenas a partir dos concluídos (012), enquanto 012 está reservado em Planejamento e o próximo disponível é 013. Nenhuma regra do validador foi alterada. Estas verificações não constituem revisão formal do plano.

## Escopo

### Dentro do escopo

- Gerador reproduzível `scripts/generate_demo.py`, arquivo `docs/assets/demo.gif` e referência no README com texto alternativo.
- Captura dos menus reais em terminal VT controlado, usando setas, Enter e retorno, sem duplicar seus textos manualmente.
- Evidências de cobertura das telas, duração, dimensões, tamanho, inspeção visual e ausência de execução de operações.

### Fora do escopo

- MP4, áudio, Instagram/Reels, site e Playwright.
- Mudanças em `src/`, dependências obrigatórias do produto, comportamento dos menus ou refatoração de `tests/ui_smoke.py`.
- Instalar ou iniciar Docker/Restic, executar backups, conversões, diagnósticos, limpeza ou alterações de perfis reais.
- Publicação, merge ou encerramento automático sem os gates próprios.

## Decisões e autoridades

- Autoridades e template lidos: `.agent/ai_behavior.md`, `_project/README.md`, `_project/cycles.md` e `.agent/templates/plano_implementacao.md`.
- O plano foi redigido em `Rascunho` e passou a `Em Revisão` após autorização humana explícita “Pode revisar.”, em 2026-10-21. O pedido anterior ao parecer não será tratado como aprovação pós-revisão.
- O GIF será a renderização da saída de uma sessão VT dos menus reais, não uma gravação da janela nativa do Windows. As adaptações de teclado, limpeza ANSI, tamanho e ambiente ficarão restritas ao processo do gerador.
- Simular somente a disponibilidade de dependências no harness de captura e documentar essa adaptação. Não simular resultados de operações nem modificar o guard do produto.
- Bloquear despacho de operações, subprocessos e persistência real durante a captura, abortando se algum deles for alcançado. Usar configuração temporária e restaurar adaptações inclusive em falhas.
- Preservar a restrição humana do ciclo 011: não incluir badge de CI.

## Estratégia de testes

- Executar o gerador e validar a sequência de estados, cada submenu e seu retorno. Usar espera por renderização/estado com timeout, sem depender apenas de pausas fixas.
- Verificar que os bloqueios de operações não foram acionados, que nenhuma configuração real foi escrita e que não houve subprocessos externos na captura.
- Decodificar o GIF com Pillow: integridade, duração acumulada de 25–35 segundos, loop, dimensões constantes e tamanho máximo de 5 MB.
- Inspecionar quadros de todas as telas e a sequência animada, incluindo cores, destaque, acentos, cortes e tempo de leitura.
- Na entrega, executar os cinco gates: `uv run python scripts/validate_governance.py`, `uv run ruff check`, `uv run pytest`, `git diff --check` e `git status --short`.
- Não adicionar testes que apenas espelhem textos dos menus. O roteiro verificável e as barreiras do gerador validam esta mudança documental.

## Itens de implementação

### Item 1 — Gerador de captura dos menus

**Contexto:** A referência existente captura um estado; esta entrega precisa cobrir os cinco módulos sem atingir operações.

**Ação técnica:** Criar gerador isolado com as funções reais dos menus, Questionary/prompt_toolkit, pyte e Pillow. Capturar a saída VT com teclado controlado e produzir GIF com paleta estável e quadros diferenciais. Documentar no script o comando `uv run --with pyte --with pillow python scripts/generate_demo.py`. FFmpeg poderá otimizar a mídia, sem se tornar dependência do produto.

**Critérios de aceite:**

- [x] Roteiro: principal → Restic → principal → Docker → principal → Markdown → principal → Desenvolvimento → principal → Sistema → principal.
- [x] Abertura de cerca de 3 segundos e cada submenu visível por pelo menos 3 segundos; retornos e transições completam 25–35 segundos.
- [x] Enter somente abre submenus ou confirma Voltar; nenhuma operação é confirmada.
- [x] Rótulos e opções vêm do código atual, sem cópias dos textos de menus no gerador.
- [x] Desvio, timeout, exceção ou tentativa de operação abortam a geração; uma captura parcial não é publicada como válida.
- [x] Configuração, arquivos pessoais, branches e serviços não são alterados pela captura; adaptações estão documentadas e limitadas ao harness.
- [x] Não alterar `src/` nem `pyproject.toml`.

### Item 2 — GIF e inclusão no README

**Contexto:** A prévia deve ser legível diretamente na apresentação do repositório.

**Ação técnica:** Gerar `docs/assets/demo.gif` e referenciá-lo no README com texto alternativo e indicação de navegação demonstrativa. Usar resolução constante e terminal com altura suficiente para todas as telas.

**Critérios de aceite:**

- [x] GIF íntegro, em loop, com 25–35 segundos e até 5 MB.
- [x] Largura alvo entre 960 e 1280 pixels, altura constante, sem cortes e com textos e destaque legíveis.
- [x] Sem caminhos pessoais, credenciais, dados do computador ou perfis reais.
- [x] README referencia o arquivo existente e descreve o alcance da demonstração.
- [x] Quadros e animação inspecionados; task registra comando de regeneração, propriedades da mídia e verificações.

## Arquivos afetados

- Planejamento: este plano e `_project/cycles.md`.
- Entrega futura: `scripts/generate_demo.py`, `docs/assets/demo.gif`, `README.md` e task da issue neste diretório.
- Closure futura: task de encerramento, estados e movimentação do ciclo somente após integração verificada e autorização.

## Decomposição em issues e PRs

- Issue `chore` [#42](https://github.com/EuThiagoAndrade/utility-belt/issues/42) criada após os gates para os itens 1 e 2, incluindo R1–R3.
- Branch documental local: `chore/cycle-012-plan`; publicação somente depois de revisão e aprovação humana pós-revisão.
- Branch da implementação: `chore/issue-N`, após issue real e vinculada; commit `chore(issue-N): adicionar demonstracao dos menus em gif`.
- Uma PR de implementação com gerador, mídia, README e evidências; merge mediante autorização humana específica. Closure documental posterior conforme fluxo canônico.

## Dependências e blockers

- pyte e Pillow opcionais, resolvidos via `uv` no ambiente de geração, sem adicioná-los às dependências do produto. FFmpeg disponível como alternativa de otimização.
- Consolas disponível; outro ambiente poderá usar fonte monoespaçada equivalente, sem exigir equivalência binária do GIF.
- Revisão, aprovação humana pós-revisão e issue #42 confirmadas em 2026-10-21. Implementação integrada na main pela PR #44 após revisão e autorização humana; closure documental em PR própria.
- Captura e tamanho final validados na implementação: 33,5 segundos, 1104 × 776 px, 431.643 bytes, zero tentativas de operação. Evidências completas na task `012_task_issue-42.md`; integração verificada em `98a735e`, encerramento documental na task de closure.

## Riscos, suposições e rollback

- Teclado acionar operação: roteiro limitado, validação de estados e bloqueio dos pontos de despacho/subprocessos.
- Guards impedirem a demonstração: adaptar apenas o harness e documentar isso, sem alterar o produto ou consultar/iniciar serviços.
- Artefatos ANSI, cortes ou texto ilegível: emulação VT, resolução fixa e inspeção de todas as telas.
- GIF pesado: quadros diferenciais, paleta constante e pausas estáticas, preservando o tempo mínimo de leitura.
- Configuração exposta ou alterada: ambiente temporário e bloqueio de persistência real.
- Rollback: reverter somente o commit da issue, removendo GIF, gerador e referência; preservar mudanças alheias e não executar limpeza genérica.

## Sequência recomendada

1. Apresentar o rascunho e obter autorização para revisão formal.
2. Executar `revisar_plano`, emitir parecer e aguardar decisão humana posterior.
3. Após gates e autorização aplicável, publicar documentação e criar issue; vincular número real, criar branch e task.
4. Implementar gerador, produzir GIF e adicionar sua referência ao README.
5. Inspecionar mídia, executar gates, apresentar o GIF e publicar PR conforme autorização.
6. Aguardar autorização de merge e, após integração, realizar closure autorizada.

## Referências

- Conversa humana de 2026-10-21: GIF curto no README, cinco módulos, navegação sem operações e pedido de implementação.
- `.agent/ai_behavior.md`; `_project/README.md`; `_project/cycles.md`; `.agent/templates/plano_implementacao.md`.
- `.agent/workflows/rascunhar_plano.md`; `.agent/workflows/revisar_plano.md`.
- `tests/ui_smoke.py`; `src/utility_belt/menu.py`; `src/utility_belt/ui/screen.py`; `src/utility_belt/ui/guard.py`; `src/utility_belt/config.py`.
- `src/utility_belt/ui/restic_menu.py`; `src/utility_belt/ui/docker_menu.py`; `src/utility_belt/ui/markdown_menu.py`; `src/utility_belt/ui/dev_menu.py`.

## Rastreabilidade

| Campo | Valor |
| :-- | :-- |
| Issue(s) | [#42](https://github.com/EuThiagoAndrade/utility-belt/issues/42), fechada; itens 1–2 e R1–R3 atendidos |
| PR(s) | [#43](https://github.com/EuThiagoAndrade/utility-belt/pull/43), documental integrada; [#44](https://github.com/EuThiagoAndrade/utility-belt/pull/44), entrega integrada; [#45](https://github.com/EuThiagoAndrade/utility-belt/pull/45), closure |
| Branch(es) | `chore/cycle-012-plan`; `chore/issue-42`; `chore/cycle-012-closure` |
| `handoff_schema_version` | `1` |
| `handoff_id` | `EuThiagoAndrade/utility-belt+012+atualizar_docs+closure+98a735e` |
| Destino após conclusão | `_project/executed/012_demonstracao_gif_menus/012_plan.md` |

## Handoff de saída

Encerramento documental em `012_task_closure.md`, que contém o contrato completo atual. A entrega foi integrada em `98a735e`, com autorização humana “Revisado pode seguir o fluxo”. O handoff abaixo permanece como histórico da revisão do plano, sem substituir o estado atual de integração.

### Handoff da revisão v1 (histórico)

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+012+revisar_plano+demonstracao-gif-menus+5b0cb559/v1`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision` = `EuThiagoAndrade/utility-belt + 012 + revisar_plano + demonstracao-gif-menus + 5b0cb559ebf2d67b9f30f793a6484f201e0723e5/v1`.
- `effect_class`: `local_mutation`
- `state_before`: plano v1 em `Rascunho`, handoff de redação identificado e revisão autorizada em chat; baseline `5b0cb559`, ciclo 012 em `Planejamento` e árvore com apenas os artefatos de planejamento.
- `state_after`: plano v1 em `Em Revisão`, parecer `APTO COM RESSALVAS` (R1–R3), aprovação humana pós-revisão `Pendente`; sem implementação ou mutação remota.
- `next_transition`: `parecer -> aprovação humana pós-revisão`.
- `preconditions`: decisão humana explícita, posterior ao parecer, aprovando v1 com R1–R3; depois, issue vinculada e autorização aplicável antes de implementar.
- `authority`: responsável humano aprova ou pede ajustes após conhecer o parecer; agente registra a decisão e executa somente os workflows autorizados.
- `evidence`: este plano (Revisão crítica), `_project/cycles.md`, baseline Git, template, código inspecionado e verificações registradas no parecer.
- `acceptance`: parecer apto, ressalvas vinculantes identificadas, bloqueadores técnicos ausentes e aprovação humana não inferida.
- `blockers`: nenhum bloqueador técnico de planejamento; aprovação humana pós-revisão e issue pendentes para implementar.
- `result`: `executed`
- `next_workflow_recommended`: após aprovação humana pós-revisão, registrar `Aprovado` e seguir com publicação documental e `criar_issues` conforme autorização aplicável.
- `next_workflow_authorized`: nenhum novo workflow por este parecer; aguarda decisão humana pós-revisão, preservando as autorizações já dadas sem antecipar seus gates.
- `actions_prohibited`: aprovar plano, implementar, gerar GIF, criar issue, publicar PR ou integrar sem os gates correspondentes.
- `rejection_rule`: recusar handoff ausente, incompatível, contraditório, sem evidência ou que trate a solicitação anterior ao parecer como aprovação pós-revisão.
- `logical_key`: `EuThiagoAndrade/utility-belt+012+revisar_plano+demonstracao-gif-menus+5b0cb559/v1`.
- `check_before_mutation`: plano v1 em `Rascunho` sem parecer anterior, baseline inalterada e autorização “Pode revisar.” verificadas antes da transição para `Em Revisão`.
- `reconcile_existing`: atualizar este parecer apenas com nova evidência ou revisão, preservando histórico e sem duplicar artefatos.
- `ambiguous_state`: parar em conflito de baseline, ciclo, plano, revisão ou decisão humana.

## Revisão crítica

- **Data:** 2026-10-21
- **Versão revisada:** `v1`, baseline `5b0cb559ebf2d67b9f30f793a6484f201e0723e5`.
- **Veredito:** `APTO COM RESSALVAS`
- **Bloqueios remanescentes:** nenhum bloqueador técnico de planejamento; aprovação humana posterior registrada abaixo.
- **Aprovação humana pós-revisão:** `Aprovada em 2026-10-21`
- **Correções materiais:** rastreabilidade atualizada para a revisão autorizada, sem ampliar o escopo. R1–R3 são condições de execução da v1, dispensando nova rodada se aceitas integralmente.
- **Ressalvas:** R1–R3 abaixo, vinculantes para issue e implementação.

### Parecer v1

#### Autorização e aceite do predecessor

- Solicitação humana de revisão: “Pode revisar.”, em 2026-10-21, posterior à apresentação do rascunho.
- Handoff recebido: `EuThiagoAndrade/utility-belt+012+rascunhar_plano+demonstracao-gif-menus+5b0cb559/v1`. Aceito: identidade, baseline, ciclo, escopo, template e solicitação humana compatíveis; nenhum predecessor ou parecer concorrente identificado.
- Transição de entrada: `Rascunho` → `Em Revisão`, antes da emissão deste parecer. O handoff atual consta em `## Handoff de saída`.

#### Evidências e itens atendidos

- Template conferido por leitura e comparação programática: 16 seções de nível 2 e 10 campos do cabeçalho presentes; estado `Em Revisão` e aprovação humana `Pendente` verificados.
- `git rev-parse HEAD` confirmou a baseline e `git branch --show-current` confirmou `chore/cycle-012-plan`. `git status --short` mostrou apenas `_project/cycles.md` e o diretório do novo plano.
- `tests/ui_smoke.py` confirma a abordagem local com `create_pipe_input`, `Vt100_Output`, pyte e Pillow. O capturador anterior contém pausas fixas e captura estática; o plano exige validação de estados e duração própria em vez de presumir sua cobertura.
- `src/utility_belt/menu.py` confirma cinco módulos, preflight antes de Restic/Docker, submenu Sistema e retorno. Os quatro arquivos de submenu confirmam que abrir a tela apenas apresenta escolhas e que as operações passam por `run_dedicated_screen`.
- `src/utility_belt/ui/guard.py` confirma consulta Docker no preflight; `screen.py` usa `os.system` para limpar a tela e os módulos importam referências locais dessas funções. `config.py` confirma que até `is_banner_enabled()` lê configuração e pode criar diretório.
- FFmpeg, uv e Consolas continuam disponíveis. Não foi instalado pacote opcional nem executado o gerador ou o aplicativo para esta revisão.
- Escopo coerente com a solicitação: GIF curto, cinco submenus, navegação sem operações, README e gerador; MP4 e alterações do produto excluídos. Tamanho, duração, cobertura e legibilidade têm critérios verificáveis.
- Branch/commit seguem as convenções canônicas; uma issue e uma PR de entrega, com publicação documental e closure separadas, preservam rastreabilidade e gates humanos.
- O aviso de próximo ciclo é compatível com `_project/README.md`: o valor declarado em `cycles.md` é a autoridade. O validador calcula a sugestão apenas pelo maior concluído e não considera a reserva ativa de 012; não se deve alterar o validador nem reutilizar 012 para eliminar esse aviso.

#### Bloqueadores

- Nenhum bloqueador técnico de planejamento. O parecer não confirma ainda captura, aparência ou tamanho de um GIF inexistente; essas evidências pertencem à entrega autorizada.

#### Ressalvas vinculantes

- **R1 — Isolamento antes de abrir o menu e no ponto de uso.** Importar previamente os módulos necessários e aplicar as adaptações em cada referência local de `clear_screen` e `run_dedicated_screen`, incluindo menu principal/Sistema e quatro submenus. Substituir a limpeza por sequências VT, não por um no-op que acumule telas. Isolar a configuração antes de `show_menu()`/`is_banner_enabled()`, redirecionando leituras e diretórios para ambiente temporário. Aplicar o preflight demonstrativo e as barreiras de subprocessos antes da captura; remover/restaurar tudo ao sair. Isso concretiza o isolamento já exigido no plano sem mudar `src/`.
- **R2 — Falha observável mesmo quando a interface captura exceções.** Restic e Docker capturam `Exception`; lançar uma exceção no bloqueio não basta como prova de aborto. Registrar tentativas de operação/erros em estado independente e rejeitar a captura ao final mesmo se a interface absorver a exceção. Exigir a sequência completa de cinco entradas e cinco retornos, timeout finito, término do controlador de teclado e ausência de worker vivo após a captura. Na validação do gerador, provocar bloqueio e timeout de forma controlada e comprovar que falham sem chamar ações reais nem produzir GIF válido parcial.
- **R3 — Validação e publicação do arquivo final.** Interpretar 5 MB como máximo de `5_000_000` bytes. Gerar em arquivo temporário, validar duração acumulada de todos os quadros, resolução e loop e somente depois substituir o destino, preservando eventual GIF válido anterior se houver falha. O primeiro quadro deve identificar o programa e os retornos devem ser visíveis; inspecionar legibilidade também na largura efetiva de apresentação no README. Registrar versões opcionais efetivamente usadas e comando de regeneração na task, sem exigir equivalência binária entre fontes/plataformas.

#### Verificações executadas

- `uv run python scripts/validate_governance.py`: 43 OK, 1 aviso conhecido sobre a reserva do ciclo 013, 0 falhas.
- `uv run ruff check`: `All checks passed!`.
- `uv run pytest -q`: `253 passed, 36 skipped, 1 warning in 52.09s`. O único aviso foi `PytestCacheWarning` por acesso negado ao tentar gravar `.pytest_cache/v/cache/nodeids`; não houve falha de teste e não foram alteradas permissões nem executada limpeza fora do escopo.
- `git diff --check`: passou. O plano ainda não rastreado também foi conferido programaticamente para ausência de espaços finais.
- `git status --short`: somente artefatos documentais de planejamento; sem alterações de implementação ou publicação remota.

### Aprovação humana pós-revisão

- Em 2026-10-21, após apresentação do parecer `APTO COM RESSALVAS`, o responsável respondeu “Aprovado” à pergunta sobre a v1 com R1–R3 e continuidade da entrega.
- Transição registrada: `Em Revisão` → `Aprovado`. R1–R3 aceitas integralmente. Preservado o pedido anterior de implementação; a aprovação autoriza seguir com a entrega planejada, incluindo a issue e as PRs rastreáveis, sem merge ou closure automáticos.
- O handoff da revisão acima é histórico e foi aceito. Seus gates de decisão humana estão satisfeitos por esta manifestação posterior.
- Preflight da entrega: remoto avançou de `5b0cb559` para `69c8b786ad45db0dbc1fc154b491f77756706b01` somente com remoção de badge de release no README. A branch documental foi atualizada por fast-forward, preservando essa alteração; nenhuma mudança de escopo ou código exige nova revisão.

## Pós-mortem

- **Data de conclusão:** 2026-10-21 (entrega integrada; encerramento documental efetivo após merge da closure).
- **Desvios:** nenhum desvio material. A entrega foi publicada inicialmente sobre a branch documental e redirecionada à main após integração de #43, preservando o mesmo head revisado. Captura VT e dependências opcionais evitaram alterações do produto ou execução das operações.
- **Lições comprovadas:** menus Questionary podem ser apresentados a partir da saída VT real com teclado controlado; barreiras no harness e validação de falhas permitem gerar uma demonstração curta sem executar ações dos módulos. Evidências e versões na task #42; nenhum novo registro transitório em lessons_learned.
