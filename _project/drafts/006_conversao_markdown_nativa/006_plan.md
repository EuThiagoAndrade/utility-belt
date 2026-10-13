# Plano de Implementação — Conversão Markdown Nativa no Utility Belt

> **Ciclo:** `006`
> **Status:** `Em Execução`
> **Versão:** `v4`
> **Data de criação:** 2026-10-12
> **Última atualização:** 2026-10-12
> **Tipo:** `feature`
> **Prioridade:** `P2`
> **Revisão formal:** `Concluída`
> **Veredito da revisão:** `APTO COM RESSALVAS`
> **Aprovação humana pós-revisão:** `Aprovada em 2026-10-12`

## Objetivo

Incorporar ao Utility Belt as cinco capacidades selecionadas do File2MD: conversão individual de arquivo ou URL, lote, monitoramento de novos arquivos, leitura de caminho ou URL do clipboard e configuração persistente de uma pasta central de saída. Todos os arquivos suportados pela versão instalada do MarkItDown devem poder ser submetidos à conversão, sem lista restritiva de formatos criada pelo Belt. Lote e monitoramento percorrem subpastas por padrão. Cada operação deve produzir resultados em uma subpasta exclusiva, preservando arquivos existentes, a extensão original dos arquivos locais e a estrutura relativa das entradas de pasta.

Este documento define o escopo e as entregas aprovados da `v4`; iniciar implementação exige issue vinculada e autorização explícita própria. A descontinuação do File2MD continua fora desses efeitos. Prioridade `P2`, sem prazo assumido.

## Contexto e baseline

- Repositório: `C:/Programas/utility-belt`; origem `https://github.com/EuThiagoAndrade/utility-belt.git`; branch observada `main`; revisão de origem `b36d04396ca0bb7af3dab79e5781b092df06ef12`.
- Entrada: [ideação 006](../../ideations/006_conversao_markdown_nativa.md), ainda não versionada no baseline observado; hash de conteúdo Git `66433b2bfeecfef9b583bf002dffcf243351fbb7`. Seu handoff `utility-belt/006/idear/conversao_markdown_nativa/b36d04396ca0bb7af3dab79e5781b092df06ef12` foi aceito para este rascunho: ciclo e alvo são únicos, escolhas e pendências estão delimitadas e a solicitação humana atual autoriza `rascunhar_plano`. A ausência de autorização para planejar no registro histórico foi suprida pelo pedido atual; o registro de ideação é preservado.
- Estado anterior: `_project/cycles.md` modificado e ideação 006 não rastreada, ambos preexistentes a este workflow. Ciclo `006` em `Ideação`, próximo ciclo `007`, nenhum plano canônico para o alvo encontrado. Este workflow acrescenta o plano e reconcilia somente a linha e a descrição do ciclo 006.
- Atualização `v2`: após a entrega de `v1`, o responsável confirmou em 2026-10-12 que todos os arquivos suportados pelo MarkItDown podem ser utilizados e que lote/monitoramento devem percorrer subpastas. Esta resposta resolve as escolhas de produto `P01` e `P02` e autoriza sua incorporação ao rascunho; não autoriza revisão ou implementação. O plano `v1` tinha hash de conteúdo Git `2908b39690a4fb03eb7df3f3eb6c753f98080035`, usado como revisão de origem deste handoff de atualização. O baseline Git permanece o mesmo; ideação e registro de ciclos são preservados nesta atualização.
- Atualização `v3`: em 2026-10-12 o responsável escolheu dependências de formatos instaladas conforme a necessidade, com informação e confirmação antes do download. Isso resolve o modelo de aquisição em `P04`; versões, mapeamento por conversor, ambiente de destino e mecanismo compatível com a distribuição continuam como definição técnica para revisão. O plano `v2` de entrada tinha hash Git de conteúdo `91e488c1b4c7661595aa6451f9f93b5c3199fb10`, origem do handoff desta atualização. Nenhuma dependência é baixada nesta etapa documental.
- Início da revisão `v4` em 2026-10-12: responsável aceitou preservar Markdown/front matter e monitorar arquivos novos criados ou movidos, com estabilidade, sem estoque inicial ou reconversão de edições posteriores, e autorizou a revisão do rascunho. Handoff de `v3` aceito após preflight de identidade, template, estados e autorização atual. Conteúdo de entrada `v3` identificado pelo hash Git `a0bec469414905e3dfbef6fa0b5ce44b0ef49e3d`. Status alterado para `Em Revisão` antes de qualquer parecer; aprovação humana pós-revisão permanece pendente.
- Aprovação pós-revisão de `v4` em 2026-10-12: após apresentação do parecer `APTO COM RESSALVAS` e esclarecimento da sequência de workflows, o responsável declarou nesta conversa: “Ok, então está aprovado a V4.” Esta manifestação autoriza registrar `Em Revisão -> Aprovado`, preservando a versão, escopo, parecer e ressalvas. Conteúdo da `v4` antes desse registro: hash Git `55d97a2ef9c959e65119775ac2532eab3dea148f`. Não há autorização adicional para publicação, criação de issues ou implementação.
- Arquitetura observada: Python `>=3.11`, Hatchling, Typer, Questionary, `platformdirs` e `tomli-w`. `cli.py` registra adaptadores Docker/Restic; `menu.py` integra submenus dedicados; `catalog.py` descobre `tool.toml` no pacote instalado; `runner.py` usa subprocesso Python, `cwd` do usuário e códigos `0`, `1`, `2`, `130`.
- `config.py` mantém `schema_version`, `default_profile`, `show_banner` e `profiles`, com gravação TOML por arquivo temporário e substituição. A nova preferência não deve substituir o documento inteiro nem exigir migração das configurações existentes.
- `doctor.py` verifica executáveis externos; ainda não diagnostica o motor Markdown ou clipboard. MarkItDown, monitoramento e clipboard não estão declarados em `pyproject.toml` nem em `uv.lock`. Nenhuma conversão foi executada neste planejamento.
- A [documentação oficial do MarkItDown](https://github.com/microsoft/markitdown#python-api), consultada em 2026-10-12, apresenta API Python, dependências opcionais por formato e plugins desativados por padrão. A [orientação de I/O](https://github.com/microsoft/markitdown#security-considerations) permite escolher métodos específicos para arquivos locais e respostas HTTP. Isso fundamenta a proposta de integração; não comprova qualidade dos documentos do usuário nem fixa uma versão do motor.
- A análise do File2MD e sua revisão `ad13d85f53f2b8911583d6f08df3c57e96615655` são evidências herdadas da ideação. Não houve nova inspeção ou modificação desse repositório nesta etapa. Nenhuma dependência de execução poderá apontar para seu checkout.

## Escopo

### Dentro do escopo

1. Núcleo compartilhado de conversão, validação das entradas e gravação segura dos resultados.
2. Destino central persistido em TOML; operação individual/URL/clipboard com uma pasta por conversão, lote com uma pasta compartilhada e monitoramento com uma pasta por arquivo convertido.
3. Todos os formatos de arquivo suportados pelo MarkItDown, com a mesma política de aceitação em individual/lote/monitoramento; lote e monitoramento recursivos, preservando caminhos relativos.
4. Adaptador CLI, catálogo e submenu seguindo as telas existentes do Belt; sem prompts em automação, com oferta específica de instalação de dependência apenas quando a interação é permitida.
5. Dependências de formatos adquiridas sob demanda, após informação e confirmação do usuário; diagnóstico local, testes do consentimento/instalação, validação do pacote instalado e documentação dos limites reais de conversão.
6. Evidências dos usos selecionados suficientes para uma decisão futura sobre o File2MD, sem executar sua descontinuação.

### Fora do escopo

- Opções excluídas do File2MD: tela própria de formatos, preview, configuração geral de IA/nuvem, alternância de limpeza YAML e troca de idioma. Exceção autorizada nesta revisão: transcrição de áudio pelo serviço nativo do MarkItDown, com consentimento por operação.
- Implementar motores/conversores próprios, autenticação de sites ou plataforma de plugins. Permanecem abrangidos todos os conversores nativos disponíveis, com seus limites reais; admitem-se somente adaptações necessárias ao consentimento, dependências e diagnóstico. Descrições de imagens por LLM, OCR por IA e serviços Azure ficam excluídos. Áudio pode usar o serviço externo autorizado; imagens sem IA produzem metadados locais, quando disponíveis.
- Migração automática da configuração JSON do File2MD, cópia integral do script legado, fallback para seu executável ou descoberta de seu ambiente virtual.
- Plataforma genérica de plugins, UI web/gráfica, serviço hospedado, daemon persistente, monitor em segundo plano ou paralelismo configurável.
- Refatoração geral de catálogo, runner, configuração, Docker/Restic, banners ou governança; correções adjacentes devem ser relatadas separadamente.
- Alterar, excluir, publicar aviso ou arquivar o File2MD; criar issues, branch, commit ou PR durante o rascunho.

## Decisões e autoridades

As autoridades [ai_behavior](../../../.agent/ai_behavior.md), [governança](../../README.md) e [cycles](../../cycles.md) regem autorizações, estados e numeração. ADR-001 e ADR-002 permanecem vigentes. O template [plano_implementacao](../../../.agent/templates/plano_implementacao.md) foi lido no ponto de uso e instanciado integralmente. Não se cria ADR nesta passagem.

### Escolhas já confirmadas na ideação

- Incorporar somente as cinco capacidades selecionadas, com experiência nativa do Belt.
- Pasta central configurável; subpastas exclusivas pelo início da operação, não pela criação da origem.
- Nome local `<nome-com-extensão>.md`, preservação da estrutura relativa em pastas e sufixo para colisão entre pastas de operação.
- Descontinuação do File2MD condicionada à adaptação validada e a autorização separada.

### Escolhas e contratos consolidados na revisão

As escolhas humanas adicionais em `v2` são: aceitar todos os arquivos suportados pelo MarkItDown (`P01` resolvida quanto ao escopo de formatos) e percorrer subpastas em lote e monitoramento (`P02` resolvida). A recursividade passa a ser comportamento padrão, sem exigir `--recursive`. Exemplo: entrada `financeiro/relatorio.pdf` gera `<pasta-da-operacao>/financeiro/relatorio.pdf.md` tanto no lote quanto na conversão automática pelo monitor.

Na revisão `v4`, o responsável confirmou `P03` (preservar Markdown/front matter) e `P05` (novos arquivos criados/movidos, com estabilidade, sem estoque inicial ou edições posteriores). Também autorizou transcrição externa de áudio, com aviso e consentimento por operação, como exceção específica à exclusão de IA/nuvem. A confirmação para instalar dependências permanece separada. `P04` é definido tecnicamente abaixo; nenhum download ou teste funcional é realizado por esta revisão.

| Tema | Contrato proposto | Autoridade / situação |
| :-- | :-- | :-- |
| Organização | Núcleo em `utility_belt.markdown`, adaptador `adapters/markdown.py`, menu `ui/markdown_menu.py` e uma ferramenta `tools/markdown_convert/` de ID `markdown.convert`. A entrada do catálogo delega ao mesmo núcleo em subprocesso, sem duplicar regras. | ADR-002; proposta para revisão. |
| CLI | Grupo `belt markdown`: `convert <arquivo-ou-url>`, `batch <pasta>`, `watch <pasta>`, `clipboard`, `config --output-dir <pasta>` e `menu`. `--output-dir` altera somente a execução; somente `config` persiste. `belt run markdown.convert <subcomando> ...` oferece o mesmo contrato. Comandos diretos não pedem argumentos/destino ausentes; em TTY podem oferecer confirmação específica de dependência, salvo modo `--non-interactive`. | Nomes propostos; interação de instalação derivada da escolha humana em `v3`. |
| Motor | MarkItDown `0.1.8`, API Python em worker do pacote executado em ambiente de conversão próprio no diretório de dados do usuário. Sem File2MD, LLM ou Azure. Processos do motor são novos após instalações, impedindo reaproveitamento de imports que falharam antes da aquisição. | `P04` definido tecnicamente nesta revisão; evidência funcional exigida nas entregas. |
| Formatos | Submeter arquivos ao motor sem allowlist restritiva própria nem rejeição apenas pela extensão; mesma política em individual/lote/monitor. O inventário da versão fixada relaciona conversores, dependências e fixtures e serve para diagnóstico/evidência. Diferenciar formato não suportado, dependência ausente e falha de conversão; conteúdo vazio nunca é sucesso. | `P01` resolvida pelo responsável: todos os arquivos suportados pelo MarkItDown. Inventário e instalação em `P04`. |
| Configuração | Chave global `[markdown].output_dir` em `config.toml`, independente de perfis Restic; caminho absoluto resolvido no `cwd`, preservando chaves existentes. Antes de gravar, ler TOML estritamente: configuração inválida não pode virar defaults e ser sobrescrita. Sem migração legada. | Correção da revisão para preservar configuração; erro deve retornar `2` sem gravar. |
| Destino ausente | No menu, solicitar configuração quando necessária e permitir cancelar. CLI direta sem destino persistido ou explícito encerra com `2`, sem prompt. Criar destino configurado inexistente ao executar; arquivo no lugar de pasta ou erro de acesso impede conversão e informa o caminho. | Proposta para revisão. |
| Pasta de operação | Horário local `AAAA-MM-DD_HH-MM-SS`, capturado imediatamente antes da primeira conversão, após preflight de entrada/destino/dependências. Primeira colisão recebe `_2`, depois `_3`; criação exclusiva, repetindo somente em colisão. Nunca reutilizar pasta existente. Lote captura um único horário. | Exclusividade confirmada; precisão/sufixo e momento de captura consolidados na revisão. |
| Gravação | UTF-8; nome local preserva extensão e caminhos relativos; saída URL fixa `web_content.md` dentro da pasta exclusiva. Escrita final exclusiva, sem sobrescrever; falha/interrupção não publica resultado incompleto como sucesso. Não deixar caminho de destino escapar da pasta reservada. | Proposta para proteção de saídas; não adicionar manifesto persistente sem necessidade. |
| Markdown | Preservar conteúdo emitido pelo motor, inclusive front matter; sem limpeza YAML, pós-processamento semântico ou opção correspondente. | `P03` resolvida pelo aceite humano em 2026-10-12. |
| Lote | Sequencial, enumeração recursiva, determinística e finita antes de converter; continuar após falha individual e apresentar resumo de sucessos, falhas e ignorados. Submeter arquivos regulares ao motor; formato não suportado é ignorado com contagem, dependência ausente/falha de conversão não é ocultada como ignorado. Pasta sem arquivos elegíveis retorna `2`; sem sucesso após tentativas retorna `1`. | Recursividade confirmada em `P02`; demais regras propostas. |
| Recursividade | Percorrer subpastas por padrão em lote e monitoramento, preservando estrutura relativa à raiz de entrada. Não exigir flag para atender essa escolha. Não seguir links simbólicos/junctions para fora da árvore nem ciclos de diretórios. | `P02` resolvida pelo responsável; proteção de caminhos proposta para revisão. |
| Monitor | Primeiro plano e recursivo; acompanha novos arquivos criados ou movidos para a árvore após o início, sem converter estoque inicial ou reconverter edições posteriores. Movimentação de pasta para dentro da árvore deve alcançar seus arquivos; diretórios criados depois do início também são observados. Um trabalhador e deduplicação de eventos por caminho/ciclo de vida; exclusão encerra o ciclo, permitindo futura criação nova. | `P05` confirmada pelo responsável; detalhes de observação consolidados pela revisão. |
| Estabilidade | Duas observações consecutivas de tamanho e mtime iguais, separadas por 1 segundo, leitura possível e limite de espera de 30 segundos desde o evento elegível. Revalidar identidade/tamanho/mtime antes e após converter; mudança descarta o resultado e exige nova estabilização dentro do limite. Timeout informa falha, sem loop automático; conversão manual posterior continua possível. Estabilidade é aproximação, sem garantia para gravações pausadas. | `P05` resolvida quanto ao comportamento; limitação técnica deve constar na documentação e smoke. |
| Exclusão da saída | Lote e monitor excluem toda a raiz de saída resolvida e seus descendentes quando internos à origem. Raízes de entrada e saída iguais são rejeitadas. Nenhum resultado pode alimentar novas conversões. | Derivado do risco explícito da ideação; obrigatório em todas as modalidades de pasta. |
| Clipboard | Ler uma entrada textual, aparar espaços e um par de aspas externas de caminho; aceitar somente arquivo existente ou URL HTTP(S). Delegar ao fluxo individual; clipboard vazio, texto livre, pasta ou backend ausente retorna `2` com diagnóstico. | Capacidade confirmada; tratamento proposto. |
| Rede | Aceitar somente HTTP/HTTPS com host; métodos distintos para arquivo e URL. Tempo limite HTTP de 30 segundos e redirects restritos a HTTP(S); tratar HTTP inválido, indisponibilidade e corpo não conversível. Não registrar credenciais/query sensível nas mensagens. Conteúdos remotos seguem os conversores disponíveis; requisitos específicos de URL são inventariados em `P04`. | Proposta de transporte; escolha sobre arquivos não promete autenticação ou processamento de JavaScript. |
| Falhas | `0`: execução finita com resultado e nenhuma falha; `1`: conversão falha/vazia, instalação falha ou lote parcial; `2`: entrada/configuração/dependência ausente, inclusive instalação recusada/indisponível antes de qualquer sucesso; `130`: interrupção. Sucessos e destinos são preservados. Monitor continua após falha individual e encerra com `130` em Ctrl+C. | Códigos alinhados ao runner; sem falha de instalação mascarada como sucesso. |
| Retenção | Manter pastas já reservadas mesmo após falha ou cancelamento; relatar ausência de resultados e preservar sucessos parciais. Erro em preflight não reserva pasta. Sem limpeza automática ou exclusão de arquivos da origem. | Proposta para revisão. |
| Dependências | Instalação inicial com o necessário ao módulo/motor; dependências opcionais de formatos não são todas baixadas antecipadamente. Ao detectar ausência de requisito conhecido do conversor, informar formato, pacote/extra necessário e finalidade e perguntar se deseja baixar e instalar. Instalar somente o grupo necessário com confirmação explícita; depois revalidar disponibilidade e tentar a conversão novamente. Dependência já disponível não gera pergunta ou download. | Escolha humana em `v3`; detalhes técnicos em `P04`. |
| Consentimento e automação | Menu e comandos em TTY oferecem instalação com resposta padrão negativa; recusa, cancelamento ou falta de TTY/`--non-interactive` não baixa nada e informa a dependência e como instalar para repetir a operação. Autorização vale para o grupo identificado e suas dependências transitivas necessárias, sem consentimento permanente ou instalação de todos os extras. | Escolha humana de confirmação; comportamento não interativo proposto conforme ADR-002. |
| Instalação e retomada | Receitas fixas abaixo e `uv >=0.12.13`; criar venv com intérprete explícito e sem download de Python. Usar `uv pip install --python <python-da-venv> --constraints <constraints-do-pacote>` somente após consentimento. Sem pip global, autodetecção de `.venv` do usuário ou instalação em ambiente do Belt em uso. Timeout de aquisição de 300 segundos, cancelamento e validação de imports; repetir conversão uma vez após sucesso, preservando resultados. | Contrato fechado em `P04`; aquisição real é gate de execução, não evidência já produzida. |
| Lote e monitor sem dependência | No lote interativo, agrupar pedidos quando identificáveis e não repetir pergunta sobre grupo recusado na mesma operação; processar arquivos independentes e reportar os pendentes. Monitor interativo pausa o processamento para confirmação por grupo, sem prompts concorrentes, e mantém arquivos pendentes deduplicados. Modo não interativo informa falha e segue a política de falhas do lote/monitor, sem instalar. Instalações bem-sucedidas são reutilizadas por operações posteriores. | Regras propostas para as modalidades confirmadas, sem bloqueio por instalação ilimitada. |


### Definição técnica de dependências (`P04`)

- **Ambientes:** `get_data_dir()/markdown/engines/markitdown-0.1.8/py<major.minor>/core` e `audio`. Criar com `uv venv --python <sys.executable> --no-python-downloads <destino>`; usar somente Python 3.11–3.14 para este motor. Python posterior mantém o restante do Belt disponível, mas o módulo informa incompatibilidade sem baixar intérprete. Matriz de aceite inicial: Windows x64 e Linux x64, Python 3.11 e 3.13; demais combinações reconhecidas pelo motor permanecem sujeitas a diagnóstico e não são anunciadas como testadas.
- **Isolamento de áudio:** `core` contém MarkItDown e grupos locais, sem `speech_recognition`/`pydub`; o worker verifica esse invariante e usa modo isolado do Python. O ambiente `audio` tem transcrição e somente é usado para os arquivos abrangidos por consentimento externo da operação. Depois de instalado ele não implica consentimento futuro. Isso evita o envio automático que o conversor nativo faria se a biblioteca estivesse disponível no ambiente comum.
- **Distribuição:** manter `watchdog==6.0.0` e `pyperclip==1.11.0` nas dependências do módulo distribuído com o Belt; requisitos de formato/motor são receitas empacotadas, adquiridas no primeiro uso confirmado. Worker independente em `markdown_runtime/worker.py` usa a API do motor, recebe entrada/consentimento em argumentos estruturados e retorna status, Markdown e diagnóstico em JSON; o núcleo do Belt organiza e publica saídas. Não instalar uma segunda cópia do Belt na venv nem depender de checkout.
- **Receitas:** base e extras fixam `markitdown==0.1.8`, com requisitos transitivos declarados nessa release. Na entrega A, resolver e empacotar constraints transitivas de base e de cada grupo, com hashes/versões registradas e validação nas duas plataformas; o instalador em produção consome essas constraints, nunca `latest` ou nomes extraídos de exceções arbitrárias. Essa geração e o smoke são gates de entrega. Não alterar versão/receita incompatível silenciosamente; revisão material exige atualização do plano.
- **Aquisição:** fonte Python padrão PyPI; subprocessos com argumentos em lista e `shell=False`, intérprete e constraints explícitos, `--no-config` para não consumir configuração do diretório corrente. Serializar criação/instalação por ambiente; processos do motor precisam estar encerrados antes da mutação. Registrar grupo como disponível somente após validar versão/imports. Falha parcial não vira disponibilidade nem provoca remoção de aquisições anteriores; próxima tentativa exige novo consentimento para o que ainda falta. Ambientes são reutilizados em upgrades compatíveis do Belt; mudança de intérprete/receita usa outro diretório, preservando o anterior.
- **Binários locais:** ExifTool `13.59` existente compatível pode ser reutilizado; se ausente, oferecer aquisição portátil da distribuição oficial para dados do usuário, com confirmação, artefato/versão/hash fixados no manifesto de receitas antes da publicação. Windows x64 usa arquivo `exiftool-13.59_64.zip` completo, inclusive runtime; Linux usa `Image-ExifTool-13.59.tar.gz` e exige Perl local. Sem Perl, informar requisito/instrução com código `2`, sem instalar pacotes do sistema ou obter privilégio administrativo. FFmpeg já disponível pode ser usado; aquisição portátil para áudio comprimido usa wheel compatível de `imageio-ffmpeg==0.6.0`, sem mudança global de PATH. No worker, normalizar áudio comprimido em WAV temporário com esse executável e chamar o fluxo nativo de transcrição WAV; preservar o nome de saída original e remover somente temporários próprios.
- **Consentimento externo:** antes de usar o ambiente `audio`, informar que conteúdo de áudio será enviado ao serviço Google usado pelo motor, identificar os arquivos e pedir consentimento com padrão negativo. Individual/clipboard: um arquivo; lote: conjunto finito de arquivos de áudio desta execução, incluindo membros de ZIP identificados; monitor: uma nova conversão por vez. Mudança no conjunto exige nova confirmação; nunca persistir autorização geral. Sem TTY ou com `--non-interactive`, não enviar áudio e limitar a metadados locais disponíveis; se não houver conteúdo, diagnosticar ausência de resultado/requisito. Recusa permite somente esse mesmo fallback local e deve ser informada no resumo. Autorização de download não autoriza envio de conteúdo, e vice-versa.

| Família nativa / origem | Receita sob demanda / limite |
| :-- | :-- |
| Texto, JSON/JSONL, Markdown, CSV, HTML, RSS, páginas Wikipedia/Bing, IPYNB e EPUB | Base `markitdown==0.1.8`; formatos genéricos dependem de detecção do motor, não de allowlist do Belt. |
| PDF | `markitdown[pdf]==0.1.8`; extração textual, sem prometer OCR de documento digitalizado. |
| DOCX / PPTX | `markitdown[docx]==0.1.8` / `markitdown[pptx]==0.1.8`. |
| XLSX / XLS | `markitdown[xlsx]==0.1.8` / `markitdown[xls]==0.1.8`. |
| Outlook MSG | `markitdown[outlook]==0.1.8`. |
| ZIP | Base mais grupos necessários aos membros; a saída continua um `<arquivo>.zip.md`. Instrumentar chamadas do motor aos membros para registrar erros que o ZIP nativo suprime; conteúdo parcial é publicado como parcial com código `1`, nunca sucesso integral silencioso. |
| Imagens JPEG/PNG | Base e ExifTool para metadados locais. Sem OCR ou descrição por LLM; arquivo sem metadados úteis não gera sucesso vazio. |
| WAV/MP3/M4A/MP4 | Metadados locais com base/ExifTool; com consentimento externo, `markitdown[audio-transcription]==0.1.8` no ambiente `audio` e FFmpeg quando necessário. MP4 refere-se ao áudio, não a análise visual de vídeo. |
| URLs YouTube | `markitdown[youtube-transcription]==0.1.8` para obtenção de legendas pela URL informada; não é autorização de envio de áudio local. Disponibilidade das legendas é limitação do serviço. |
| Azure / plugins de IA | Não habilitados; `[all]` não é receita utilizada, pois inclui recursos fora do escopo. |

O inventário acima corresponde ao registro de conversores e metadados da release fixada; entradas reconhecidas por conteúdo também são aceitas. Aquisição real e qualidade não foram demonstradas nesta revisão e precisam passar pelos critérios das entregas. Mudança que retire uma família abrangida ou introduza novo serviço exige decisão explícita.

## Estratégia de testes

### Evidências da futura implementação

- **Núcleo e integridade:** inventariar os formatos/conversores nativos da versão fixada e suas dependências; usar fixtures pequenas e redistribuíveis com assertivas sobre texto ou metadados conhecidos, título/tabela quando pertinente e conteúdo não vazio. Pelo menos uma conversão real por formato/conversor do inventário confirma a integração; nenhum formato é excluído por não pertencer à lista inicial de candidatos de `v1`. Cobrir um formato fora dessa lista, arquivo sem extensão/extensão não reconhecida e dependência ausente. Limitações do motor são documentadas; divergência de cobertura exige resolução explícita antes do aceite. Nenhum documento pessoal é versionado.
- **Destinos:** arquivo único, homônimos `relatorio.pdf`/`relatorio.docx`, subpastas com mesmo basename, nomes Unicode/espaços e caminhos relativos ao `cwd`. Relógio controlado e duas reservas concorrentes no mesmo segundo devem produzir pastas distintas; conferir bytes intactos de saídas existentes. Exercitar erro de escrita e interrupção sem resultado final parcial.
- **Lote:** lote misto, falha parcial, pasta vazia ou composta apenas por entradas não suportadas, arquivos em dois ou mais níveis de subpastas sem flag adicional, links/junctions e saída interna à origem. O resumo distingue não suportados de dependências ausentes/falhas; o código reflete o estado real, mantendo os arquivos de sucesso.
- **Monitor:** criação/movimento de arquivos e pastas com conteúdo em dois ou mais níveis, diretórios criados após início, eventos duplicados, cópia lenta, timeout, remoção e mudança durante conversão. Estoque inicial/edições não convertem; excluir e recriar inicia um novo ciclo de vida. Relógio/observador controlados; smoke real Windows/Linux comprova recursão, caminho relativo, uma conversão por arquivo, ausência de reconversão da saída e encerramento limpo.
- **CLI e menu:** testar ajuda fora de TTY, argumento/destino ausente, códigos e paridade entre `belt markdown` e `belt run markdown.convert`. Prompts de instalação somente em interação permitida, nunca em não-TTY ou `--non-interactive`, inclusive quando repassado pelo catálogo. Menu oferece as cinco ações e voltar usando telas existentes. Clipboard usa backend mockado e smoke em sessão suportada; ausência do backend também é demonstrada.
- **Áudio e ZIP:** mocks de rede comprovam nenhum envio sem consentimento, mesmo com ambiente `audio` já instalado, na CLI, clipboard, lote, monitor e membros de ZIP. Consentimento de instalação e envio testados separadamente, com conjunto de entradas definido. Smoke real de áudio usa fixture não pessoal e autorização explícita daquela operação; indisponibilidade do serviço não entra como dependência da suíte automatizada. Áudio comprimido valida aquisição/execução do FFmpeg e limpeza de temporários; imagens/áudio sem consentimento validam somente metadados. ZIP com membro corrompido ou dependência ausente precisa relatar parcialidade, pois o motor nativo pode suprimir essas exceções.
- **URL:** servidor HTTP local de teste com HTML conhecido, erro HTTP, atraso e redirect com esquema inválido; sem depender de disponibilidade da internet na suíte. Validação manual de URL pública escolhida pelo responsável fica registrada, sem promessa de autenticação ou JavaScript.
- **Configuração e dependências:** preservar perfis/chaves e rejeitar TOML inválido sem gravar. Exercitar requisito disponível/ausente, confirmação/recusa/cancelamento, não-TTY/`--non-interactive`, falha de aquisição/import e concorrência de instalações. Antes de consentimento, zero chamada de instalador/download de dependência. Instalar somente receita necessária; recusa preserva outros formatos. Verificar ambiente correto, timeout e ausência de mutação do Python global, ambiente do Belt, PATH e outros diretórios.
- **Distribuição:** construir wheel/sdist e instalar fora do checkout em ambientes descartáveis Windows/Linux, com configuração temporária. Demonstrar catálogo/manifesto, comandos e instalação mínima sem extras de formato. Após confirmação interativa, adquirir dependência de um formato e converter; uma segunda operação deve reutilizá-la sem download. Simular recusa e modo não interativo sem mutações, testar falha de aquisição e repetição posterior com preservação dos resultados. Validar Python 3.11 e uma versão posterior compatível; registrar versões, ambiente de conversão, mecanismo e persistência após atualização do Belt. Parte dos testes usa instalador simulado, mas ao menos uma aquisição real por estratégia suportada deve ser comprovada.

### Gates e evidência exigida

Antes da publicação de cada entrega, executar os gates canônicos: `uv run python scripts/validate_governance.py`, `uv run ruff check`, `uv run pytest`, `git diff --check` e `git status --short`. Registrar comandos, resultados, ambiente, SHA, PR e checks reais na task da issue; revisar staging seletivo. Na entrega final acrescentar build, instalação e smoke do pacote conforme a matriz acima. Falha ou plataforma não verificada não conta como aceite e deve permanecer explícita até ser resolvida.

Para este rascunho local, a validação é documental: auditoria de governança, conferência manual das seções do template, rastreabilidade ciclo/ideação/plano e diff. Testes de conversão, lint de código, build e instalação são futuros; nenhum resultado funcional é assumido.

## Itens de implementação

### Item 1 — Núcleo, destino persistente e conversão individual

**Contexto:** Todas as modalidades precisam da mesma política de nomes, formatos, dependências, erros e gravação. O legado não protege colisões e não pode ser dependência operacional.

**Ação técnica:**

- Criar `src/utility_belt/markdown.py` com integração estreita ao motor, classificação de entrada, política comum de formatos, reserva de pasta e publicação segura do Markdown.
- Integrar leitura/gravação de `[markdown].output_dir` ao mecanismo TOML existente preservando configurações anteriores; permitir destino explícito sem persistência incidental.
- Declarar as dependências leves do módulo e receitas/constraints empacotadas de motor/formato conforme `P04`. Criar gerência restrita dos ambientes e worker do motor, com aquisição consentida, revalidação, isolamento de transcrição, diagnóstico de ZIP parcial e retomada; sem gerenciador genérico de plugins/dependências.
- Implementar arquivo e URL preservando Markdown/front matter conforme `P03` confirmada; aplicar contratos de nomes, códigos, consentimento de áudio e publicação segura. Criar testes e fixtures desse núcleo.

**Critérios de aceite:**

- [ ] Todos os conversores/formatos nativos inventariados em `P04` têm evidência de integração e dependências identificadas; não há allowlist restritiva do Belt e entradas vazias não retornam sucesso. Limites do motor ou requisitos externos são explicitados e resolvidos antes do aceite, sem redução silenciosa do escopo.
- [ ] Duas operações no mesmo segundo, inclusive concorrentes, reservam diretórios distintos sem alterar arquivos existentes.
- [ ] Arquivos locais resultam em `<nome-com-extensão>.md`; URL resulta no nome aprovado; paths não escapam do diretório reservado.
- [ ] Configuração existente mantém perfis e preferências; destino ausente/inválido e falhas de escrita produzem diagnóstico e código definidos.
- [ ] Falha de motor/rede/interrupção não deixa Markdown incompleto anunciado como concluído; dependência de formato ausente não quebra comandos alheios.
- [ ] Requisito ausente produz explicação e confirmação antes de qualquer download/instalação; recusa/cancelamento ou modo não interativo não chama o instalador nem modifica o ambiente.
- [ ] Confirmação instala somente receita necessária no ambiente próprio e valida versões/imports antes de repetir a conversão; falhas/cancelamento não provocam loop, sobrescrita ou disponibilidade falsa; aquisições são reutilizadas.
- [ ] Com bibliotecas de transcrição previamente instaladas, nenhuma modalidade envia áudio sem consentimento específico da operação; recusa/não-TTY mantém somente extração local de metadados e informa a limitação.
- [ ] ZIP com erro em membro produz diagnóstico/código de parcialidade em vez de ocultar a falha; aquisição necessária a um membro passa pelo mesmo consentimento.

### Item 2 — Lote, monitoramento e clipboard

**Contexto:** As modalidades selecionadas devem reutilizar o núcleo, com contagem de falhas e proteção contra a própria saída. O comportamento do monitor não pode ser deduzido da espera fixa do legado.

**Ação técnica:**

- Acrescentar processamento sequencial de lote recursivo por padrão, preservação de caminhos relativos e resumo, conforme decisão confirmada em `P02`.
- Integrar observador em primeiro plano com política de novos arquivos, fila/trabalhador único, deduplicação e estabilização conforme `P05`; liberar observador e recursos ao cancelar.
- Tratar grupos de dependência ausentes no lote e monitoramento conforme o contrato de confirmação: sem perguntas repetidas/concorrentes, preservando entradas pendentes e sucessos independentes.
- Resolver e excluir saída e descendentes antes de enumerar/observar; rejeitar raízes iguais e evitar fuga por links.
- Integrar leitura de clipboard com diagnóstico de backend e reutilização da conversão individual; sem interpretar texto livre como documento.

**Critérios de aceite:**

- [ ] Um lote inteiro compartilha uma pasta; arquivos com extensões ou caminhos relativos distintos têm resultados separados.
- [ ] Falha de uma entrada não elimina sucessos nem interrompe as demais; resumo e códigos cobrem falha parcial, ignorados e ausência de candidatos.
- [ ] Lote e monitor percorrem subpastas sem flag adicional, inclusive múltiplos níveis; monitor alcança subpastas criadas depois do início, mantendo os caminhos relativos.
- [ ] Cada arquivo novo estável gera uma pasta; eventos duplicados não geram conversões repetidas e a política de edição/estoque inicial é comprovada.
- [ ] Cópia lenta, falha de leitura, timeout e Ctrl+C são exercitados; encerramento libera o observador e informa resultados já concluídos.
- [ ] Saída interna à origem não é enumerada nem observada; links/ciclos não permitem recursão indevida.
- [ ] Clipboard de arquivo/URL segue o mesmo contrato individual; vazio, inválido e indisponível geram erro útil sem traceback como única explicação.

### Item 3 — CLI, catálogo, menus, diagnóstico e distribuição

**Contexto:** A adaptação somente está completa quando pode ser usada a partir do pacote instalado e da experiência existente do Utility Belt, com todas as capacidades acessíveis.

**Ação técnica:**

- Criar adaptador Typer `adapters/markdown.py`, registrar grupo em `cli.py` e ferramenta `markdown.convert` com manifesto Python para Windows/Linux, risco `write`, `interactive = false` e sem dry-run prometido.
- Criar `tools/markdown_convert/main.py` como entrada fina para operações e configuração. Garantir propagação explícita de `--non-interactive` do runner ao processo filho para suprimir ofertas de instalação mesmo em TTY; limitar o ajuste no runner a esse contrato, sem refatoração geral.
- Criar `ui/markdown_menu.py`, integrar nova opção no menu principal e reutilizar cabeçalhos/telas existentes. Seleções: individual, lote, monitor, clipboard, saída e voltar; não reproduzir números legados como contrato do Belt.
- Estender `doctor.py` estritamente para disponibilidade do motor/dependências adquiridas e limites do clipboard; diagnóstico informa ausências sem instalar ou pedir consentimento.
- Documentar instalação inicial mínima, aquisição de dependências por formato, confirmação, recusa, automações, ambiente de destino, retomada, comandos, configuração, formatos validados, saídas, erros e monitor. Não corrigir seções adjacentes não relacionadas.
- Validar artefatos distribuíveis, experiência TTY e modos diretos nas duas plataformas; consolidar evidências na task final.

**Critérios de aceite:**

- [ ] As cinco capacidades podem ser usadas no menu e CLI; `belt markdown` abre menu somente em TTY e exibe ajuda fora dele.
- [ ] Execuções diretas e via catálogo mantêm `cwd`, configuração, resultados e códigos equivalentes; não-TTY/`--non-interactive` não pergunta nem instala, e ofertas em TTY obedecem ao consentimento específico.
- [ ] O menu retorna corretamente após sucesso, erro ou cancelamento, preservando as telas e opções existentes.
- [ ] Wheel/sdist incluem ferramenta e manifesto; instalação mínima fora do checkout funciona e aquisição de dependência após consentimento torna o formato utilizável, sem downloads antecipados de extras não necessários.
- [ ] Conversões e monitoramento têm evidência real em Windows/Linux e versões Python da matriz; fixtures não dependem de File2MD, documentos privados ou serviços de IA.
- [ ] Gates canônicos passam; README corresponde ao comportamento instalado e distingue formatos validados de conteúdo não atendido.
- [ ] Responsável recebe destinos e resultados dos cinco usos reais para aceite da adaptação; essa evidência não autoriza descontinuar o File2MD.

## Arquivos afetados

Lista prevista para implementação futura; revisão e registro de aprovação alteram somente este plano e a descrição do ciclo 006 em `_project/cycles.md`. Nenhum código ou dependência é alterado nesses registros.

| Arquivo / grupo | Alteração prevista |
| :-- | :-- |
| `src/utility_belt/markdown.py` (novo) | Núcleo, saídas e modalidades; coordenação de dependências/consentimentos e configuração. |
| `src/utility_belt/markdown_runtime/worker.py`, `recipes.toml`, constraints por grupo (novos) | Worker do motor, receitas fixas e isolamento dos ambientes, incluídos no wheel/sdist. Organização pode ajustar nomes sem mudar os contratos. |
| `src/utility_belt/config.py` | Persistência da preferência global de saída preservando esquema e demais dados. |
| `pyproject.toml`, `uv.lock` | Dependências leves do módulo e resolução de constraints para receitas; sem instalação inicial de todos os extras. |
| `src/utility_belt/adapters/markdown.py` (novo), `src/utility_belt/cli.py` | Grupo de comandos e registro. |
| `src/utility_belt/tools/markdown_convert/main.py`, `tool.toml` (novos) | Entrada de catálogo distribuível e metadados. |
| `src/utility_belt/ui/markdown_menu.py` (novo), `src/utility_belt/menu.py` | Cinco ações e retorno no padrão de telas existente. |
| `src/utility_belt/doctor.py` | Diagnóstico de requisitos disponíveis/ausentes, sem instalação incidental. |
| `src/utility_belt/runner.py`, `tests/test_runner.py` | Ajuste cirúrgico para propagar modo não interativo ao processo filho e verificar supressão de ofertas de instalação. |
| `tests/test_markdown.py`, `tests/test_markdown_adapter.py`, `tests/test_markdown_watch.py`, `tests/fixtures/markdown/` (novos) | Integridade, motor, modalidades e interfaces. Divisão de testes pode ser ajustada sem ampliar cobertura funcional. |
| `tests/test_config.py`, `tests/test_catalog.py`, `tests/test_cli.py`, `tests/test_interactive_menus.py` | Integração e regressão dos pontos modificados. |
| `README.md` | Documentação da ferramenta e do fluxo de dependências sob demanda. |
| `_project/drafts/006_conversao_markdown_nativa/006_plan.md`, `_project/cycles.md` e futuras tasks/evidências `006_*` | Rastreabilidade e estados conforme cada workflow autorizado. |

## Decomposição em issues e PRs

Issues [#16](https://github.com/EuThiagoAndrade/utility-belt/issues/16), [#17](https://github.com/EuThiagoAndrade/utility-belt/issues/17) e [#18](https://github.com/EuThiagoAndrade/utility-belt/issues/18) foram criadas conforme esta decomposição. A entrega A foi integrada na [PR #19](https://github.com/EuThiagoAndrade/utility-belt/pull/19), merge `13b4719af643747b679e87602ac5ff414b35d716`, após autorização humana. B (#17) está em implementação autorizada; C não iniciada. A sequência aprovada contém três entregas, normalmente uma issue e uma PR por entrega:

| Entrega proposta | Escopo | Dependência | Evidência de saída |
| :-- | :-- | :-- | :-- |
| A — Núcleo de conversão Markdown e destino seguro | Item 1; worker/receitas, aquisição, consentimento externo, testes do motor, formatos e integridade. | Plano aprovado e autorização própria para a issue. | Task com constraints/hashes, fixtures, versões, aquisições/consentimentos e gates locais. |
| B — Lote, monitoramento e clipboard | Item 2; eventos, exclusões, caminhos, falhas e consentimentos por operação. | A integrada e execução autorizada. | Task com testes e smoke do monitor/clipboard. |
| C — Integração da experiência e distribuição | Item 3; CLI, catálogo, menu, diagnóstico e README. | B integrada. | Task com gates completos, instalação fora do checkout e aceite dos usos. |

Cada issue exige plano aprovado, vínculo e autorização humana explícita para executar; criar task no início da implementação. Consumir novamente `_project/README.md` ao criar branches `feature/issue-N` e commits `feat(issue-N):`, sem inventar números. A publicação documental do plano só ocorre após revisão formal e aprovação humana posterior, em branch canônica `chore/cycle-006-plan` se autorizada. Nenhuma publicação está autorizada agora.

Encerramento posterior: task `006_task_closure.md` e PR documental sem issue recursiva, somente após entregas integradas e encerramento autorizado. A task registra integração das entregas; o próprio merge da closure é comprovado no GitHub. Não mover o ciclo para `executed/` antecipadamente.

## Dependências e blockers

As escolhas `P01`–`P05` foram resolvidas no planejamento; revisão concluída com `APTO COM RESSALVAS`, sem bloqueios remanescentes. Ressalvas permanecem riscos/gates concretos das entregas, sem evidência funcional presumida. Aprovação humana pós-revisão da `v4` registrada em 2026-10-12.

| ID | Pendência | Quem resolve | Evidência necessária antes da aprovação |
| :-- | :-- | :-- | :-- |
| `P01` — resolvida | Todos os arquivos suportados pelo MarkItDown podem ser utilizados; sem seleção restritiva de formatos do Belt. | Responsável, resposta em 2026-10-12. | Escolha registrada neste `v2`; inventário técnico, requisitos de URL e dependências tratados em `P04`, com conversões reais como gates de entrega. |
| `P02` — resolvida | Lote e monitoramento percorrem subpastas; comportamento recursivo por padrão. | Responsável, resposta em 2026-10-12. | Escolha registrada neste `v2`, exemplo `financeiro/relatorio.pdf` e critérios de teste em múltiplos níveis sem flag adicional. |
| `P03` — resolvida | Preservar Markdown/front matter sem limpeza YAML. | Responsável, aceite em 2026-10-12. | Escolha incorporada à tabela e aos critérios. |
| `P04` — resolvida no planejamento | Aquisição por necessidade e consentimento; ambientes, receitas/versões, binários, transcrição externa, retomada e distribuição definidos acima. | Responsável define consentimentos; revisão técnica fixa estratégia baseada em fontes primárias. | Receitas fixadas em MarkItDown 0.1.8, watchdog 6.0.0, pyperclip 1.11.0, imageio-ffmpeg 0.6.0 e ExifTool 13.59; uv mínimo 0.12.13. Constraints transitivas/hashes e prova de aquisição são gates da entrega A, não resultados já executados. |
| `P05` — resolvida | Novos arquivos criados/movidos, estabilização, sem estoque inicial ou reconversão de edições. | Responsável, aceite em 2026-10-12; revisão delimita tempos e ciclo de vida. | Contrato e testes para 1 segundo entre observações/30 segundos de espera, novos subdiretórios, movimentos de pasta, duplicados e cancelamento. |

Os contratos da `v4` receberam aprovação humana posterior ao veredito em 2026-10-12. Mudança material exige atualização e nova avaliação; a aprovação atual não cobre ampliação de escopo.

A `.venv` local aponta em `pyvenv.cfg` para um Python de outro caminho de usuário; a ideação registra falha anterior desse ambiente. Reparar ambiente não faz parte deste registro de aprovação. Antes de gates de implementação, confirmar ambiente funcional sem alterar artefatos alheios. O plano aprovado delimita escopo, mas a execução depende de issue e autorização própria; nenhuma evidência funcional futura está declarada como realizada.

## Riscos, suposições e rollback

| Risco / suposição | Tratamento proposto |
| :-- | :-- |
| Motor pode extrair mal tabelas, conteúdo digitalizado ou documentos reais. | Abrangência confirmada em `P01`; inventariar capacidades/limites em `P04` e validar fixtures/usos reais. Se requisito essencial falhar, revisar abordagem antes de declarar adaptação concluída. Recursos nativos ficam contemplados; serviços de IA/nuvem não são habilitados por inferência. |
| Dependências podem falhar ou conflitar durante aquisição. | Receitas/versões explícitas, constraints testadas, dois ambientes e exclusão de downloads de Python. Validar instalação mínima, aquisições e reutilização nas plataformas da matriz; falhas preservam resultados e não autorizam aquisições adicionais. |
| Tamanho/mtime estáveis não garantem término de escrita. | Revalidar identidade e estado, testar cópia lenta e documentar a aproximação. Timeout não declara resultado concluído; conversão manual posterior permanece disponível. |
| Colisões, concorrência, diferenças de caixa e links podem ameaçar saídas. | Reserva e gravação exclusivas, validação de contenção, testes concorrentes e exclusão da raiz de saída. Pastas existentes jamais reutilizadas. |
| Transcrição envia conteúdo ao Google e depende de disponibilidade externa. | Consentimento independente por operação, ambiente de transcrição separado e testes de ausência de envio após recusa/não-TTY. Nenhum consentimento geral persistido. |
| ZIP nativo pode ocultar erros dos membros. | Instrumentar chamadas de conversão e relatar parcialidade sem alterar semanticamente o Markdown; testes com membros inválidos/dependências ausentes. |
| Clipboard depende da sessão e pode estar ausente no Linux sem interface gráfica. | Diagnóstico concreto e código `2`; demais modalidades permanecem utilizáveis. Não instalar utilitários do sistema automaticamente. |
| URL pode retornar erro, conteúdo dinâmico ou formato não contratado. | HTTP(S) delimitado, timeout, fixtures HTTP locais e erros explícitos; não prometer navegador/autenticação. |
| Pastas vazias/saídas parciais e monitor encerrado podem causar dúvida sobre sucesso. | Resumos com destino e contagem, códigos consistentes, retenção informada e cancelamento sem exclusão dos sucessos. |
| Aceite do rascunho pode ser confundido com aprovação/execução. | Handoff explícito para revisão; manter estados e autorização separados em todas as transições. |

Rollback futuro: reverter as PRs específicas em ordem inversa de dependências, após decisão do responsável e preservando arquivos convertidos e configuração do usuário. Não remover automaticamente o destino central, resultados ou chave persistida. O File2MD continua disponível durante a adaptação; sua permanência é alternativa operacional do usuário, nunca dependência do Belt. Para corrigir este rascunho, atualizar o mesmo artefato e a linha do ciclo sem criar plano paralelo.

## Sequência recomendada

1. Revisão formal da `v4` concluída com `APTO COM RESSALVAS` e aprovação humana posterior registrada em 2026-10-12; gate documental satisfeito.
2. Solicitar/receber autorização própria para os próximos efeitos; mudança material no plano exige nova avaliação antes de execução.
3. Após aprovação registrada, publicar documentação do plano/criar issues somente conforme autorização e workflows próprios.
4. Ao receber autorização explícita para execução, criar task persistente e branch da issue; não executar automaticamente a partir do parecer.
5. Entregar A, B e C na ordem definida, verificando baseline e integração anterior, com gates e evidências de cada issue; publicação e integração seguem os gates aplicáveis, sem merge automático presumido.
6. Demonstrar as cinco capacidades na instalação distribuída, receber aceite da adaptação e registrar falhas/limites reais. Eventual descontinuação do File2MD exige decisão e autorização próprias, fora deste ciclo executável.
7. Com integrações verificadas e encerramento autorizado, produzir closure e PR documental, mover para `executed/` e marcar `Concluído` apenas quando a integração do encerramento for verificável.

## Referências

- [Ideação 006](../../ideations/006_conversao_markdown_nativa.md) e [registro de ciclos](../../cycles.md).
- [Comportamento canônico](../../../.agent/ai_behavior.md), [governança](../../README.md), [workflow rascunhar_plano](../../../.agent/workflows/rascunhar_plano.md) e [template de plano](../../../.agent/templates/plano_implementacao.md).
- [ADR-001](../../decisions/ADR-001_governanca_agnostica_adapters.md) e [ADR-002](../../decisions/ADR-002_arquitetura_cli_distribuivel.md).
- Baseline local: [pyproject.toml](../../../pyproject.toml), [CLI](../../../src/utility_belt/cli.py), [menu](../../../src/utility_belt/menu.py), [catálogo](../../../src/utility_belt/catalog.py), [runner](../../../src/utility_belt/runner.py), [configuração](../../../src/utility_belt/config.py) e [doctor](../../../src/utility_belt/doctor.py).
- Fontes do File2MD fixadas e herdadas da ideação: [script](https://github.com/EuThiagoAndrade/File2MD/blob/ad13d85f53f2b8911583d6f08df3c57e96615655/Scripts/File2MD.py), [README](https://github.com/EuThiagoAndrade/File2MD/blob/ad13d85f53f2b8911583d6f08df3c57e96615655/README.md) e [dependências](https://github.com/EuThiagoAndrade/File2MD/blob/ad13d85f53f2b8911583d6f08df3c57e96615655/requirements.txt). Referências documentais, sem requisito de checkout irmão.
- [Documentação oficial do MarkItDown](https://github.com/microsoft/markitdown#optional-dependencies), consultada em 2026-10-12; dependências opcionais podem ser selecionadas por formato; versão e constraints dependem de `P04`.
- [Documentação oficial de ferramentas do uv](https://docs.astral.sh/uv/guides/tools/), consultada em 2026-10-12: ferramentas usam ambientes isolados e podem declarar dependências adicionais. Essa documentação fundamenta a necessidade de definir o ambiente de aquisição em `P04`; não comprova instalação dinâmica nesta aplicação.

- Revisão: [workflow revisar_plano](../../../.agent/workflows/revisar_plano.md); [release MarkItDown 0.1.8](https://pypi.org/project/markitdown/0.1.8/) e [metadados](https://pypi.org/pypi/markitdown/0.1.8/json); [registro de conversores](https://github.com/microsoft/markitdown/blob/b8f79c57ebc0044be41323d89b2a45d3fda8460e/packages/markitdown/src/markitdown/_markitdown.py), [transcrição](https://github.com/microsoft/markitdown/blob/b8f79c57ebc0044be41323d89b2a45d3fda8460e/packages/markitdown/src/markitdown/converters/_transcribe_audio.py), [imagens](https://github.com/microsoft/markitdown/blob/b8f79c57ebc0044be41323d89b2a45d3fda8460e/packages/markitdown/src/markitdown/converters/_image_converter.py) e [ZIP](https://github.com/microsoft/markitdown/blob/b8f79c57ebc0044be41323d89b2a45d3fda8460e/packages/markitdown/src/markitdown/converters/_zip_converter.py), revisão fixa `b8f79c57ebc0044be41323d89b2a45d3fda8460e`.
- [uv: ambientes explícitos](https://docs.astral.sh/uv/pip/environments/), opções verificadas em `uv 0.12.13 --help`; [watchdog 6.0.0](https://pypi.org/project/watchdog/6.0.0/), [pyperclip 1.11.0](https://pypi.org/project/pyperclip/1.11.0/), [imageio-ffmpeg 0.6.0](https://pypi.org/project/imageio-ffmpeg/0.6.0/), [ExifTool: instalação](https://exiftool.org/install.html), [arquivo Windows 13.59](https://sourceforge.net/projects/exiftool/files/exiftool-13.59_64.zip/download) e [arquivo Perl 13.59](https://sourceforge.net/projects/exiftool/files/Image-ExifTool-13.59.tar.gz/download). Somente metadados/documentação consultados, sem aquisição ou execução desses pacotes.

## Rastreabilidade

| Campo | Valor |
| :-- | :-- |
| Issue(s) | [#16 — A: Núcleo de conversão Markdown e destino seguro](https://github.com/EuThiagoAndrade/utility-belt/issues/16), [#17 — B: Lote, monitoramento e clipboard](https://github.com/EuThiagoAndrade/utility-belt/issues/17), [#18 — C: CLI, menus, diagnóstico e distribuição](https://github.com/EuThiagoAndrade/utility-belt/issues/18) |
| PR(s) | [#19](https://github.com/EuThiagoAndrade/utility-belt/pull/19) — entrega A (#16), integrada em `13b4719af643747b679e87602ac5ff414b35d716`; PR de B ainda não publicada. |
| Branch(es) | `feature/issue-16` — A integrada; `feature/issue-17` — B em execução; tasks por issue neste diretório. |
| Ideação | `_project/ideations/006_conversao_markdown_nativa.md` |
| Revisão de origem | Registro de aprovação: conteúdo da `v4` revisada, hash Git `55d97a2ef9c959e65119775ac2532eab3dea148f`; baseline do repositório `b36d04396ca0bb7af3dab79e5781b092df06ef12`. |
| `handoff_schema_version` | `1` |
| `handoff_id` | `utility-belt/006/implementar_issue/issue-17/13b4719af643747b679e87602ac5ff414b35d716` (vigente; históricos preservados abaixo) |
| Destino após conclusão | `_project/executed/006_conversao_markdown_nativa/006_plan.md` |

### Validação documental e histórico do rascunho

As evidências das passagens de rascunho foram preservadas. A revisão `v4` acrescenta seus comandos/resultados abaixo.

- `python scripts/validate_governance.py`: código `0`, 32 verificações, 31 OK, um aviso e nenhuma falha. O aviso compara próximo ciclo `007` ao sucessor do maior concluído (`005`), sem considerar a reserva de `006`; a numeração permanece conforme `cycles.md`. O validador não foi alterado.
- `git diff --check`: código `0`, sem erros nos arquivos rastreados. Como o plano ainda é não rastreado, seu texto foi conferido separadamente quanto a espaços residuais, com resultado sem ocorrências.
- Conferência documental inicial por leitura e verificação pontual em memória: 16 seções de nível 2 do template presentes, status `Rascunho`, plano único `006_plan.md`, links locais existentes e caminho canônico vinculado em `cycles.md`. Isso não representa revisão crítica formal.
- `git status --short`: `_project/cycles.md` modificado, `_project/drafts/` novo e ideação 006 não rastreada. O hash da ideação permaneceu `66433b2bfeecfef9b583bf002dffcf243351fbb7`; mudanças anteriores no registro foram preservadas. Nenhum código, dependência ou configuração de ambiente alterado.
- Auditoria executada com o Python do sistema, preservando a `.venv` cujo caminho de origem não corresponde ao ambiente atual. `uv run`, lint, testes funcionais, build e instalação não executados nesta entrega documental local; serão exigidos antes das publicações aplicáveis. Nenhuma issue, branch, commit, PR ou mutação do File2MD realizada.
- Revalidação de `v2` em 2026-10-12: auditoria de governança novamente com 31 OK, um aviso conhecido e nenhuma falha; `git diff --check` sem erros. Conferência pontual da versão, 16 seções canônicas, plano único, links locais, espaços residuais e remoção dos contratos antigos de formatos/recursividade concluída com código `0`. `P01`/`P02` constam como resolvidas; `P03`–`P05` permanecem pendentes. A atualização altera somente este plano e preserva o hash da ideação; não houve teste funcional, mudança de código ou promoção de status.
- Revalidação de `v3` em 2026-10-12: `python scripts/validate_governance.py` com código `0`, 31 OK, um aviso conhecido e nenhuma falha; `git diff --check` sem erros. Conferência em memória das 16 seções, plano único, links locais, tabela, espaços residuais, consentimento, instalação sob demanda e comportamento não interativo com código `0`. Ideação mantém o mesmo hash; esta atualização altera somente o plano, em `Rascunho`. Testes funcionais e aquisição real continuam futuros; nenhuma dependência ou ambiente foi instalado/alterado.

- Validação de `v4` em 2026-10-12: `python scripts/validate_governance.py` com código `0`, 32 verificações (31 OK, um aviso conhecido e nenhuma falha); `git diff --check` sem erros. Conferência em memória com código `0`: 16 seções canônicas, plano único, links locais, estados do plano/ciclo, escolhas resolvidas e espaços residuais. Revisão manual adicional confrontou API/conversores fixados, metadados de pacotes, opções de `uv 0.12.13`, runner/configuração e critérios de instalação/consentimento.
- Limites da evidência: consultas HTTP de metadados/código e ajuda de comandos são somente leitura; não constituem aquisição de bibliotecas, prova de resolução transitiva, conversão ou instalação. Algumas URLs do ExifTool retornaram 403 no navegador de pesquisa; a documentação original e os nomes das distribuições foram obtidos via HTTP pelo Python, sem baixar arquivos de distribuição. Nenhum smoke funcional, build, lint ou suite de código executado nesta revisão documental.
- Escopo local observado: plano e descrição do ciclo 006 atualizados; próximo ciclo 007 e ideação/hash `66433b2bfeecfef9b583bf002dffcf243351fbb7` preservados. Nenhuma issue, branch, commit, PR, publicação, instalação ou mudança no File2MD.
- Validação do registro de aprovação em 2026-10-12: auditoria de governança com código `0`, 31 OK, um aviso conhecido e nenhuma falha; `git diff --check` sem erros. Conferência em memória com código `0` de status `Aprovado`, versão `v4`, parecer concluído, data/aprovação posterior, 16 seções, plano único, links, handoff integral e ciclo 006 ainda em `Planejamento`/próximo 007. Comparação com o conteúdo revisado confirmou preservação integral de escopo, decisões/contratos, estratégia de testes, itens de implementação e riscos. Ideação mantém o hash; somente registros documentais do plano/ciclo foram atualizados, sem publicação ou execução.

## Handoff de saída

### Registro histórico: aprovação da v4

O handoff abaixo registra somente a aprovação. A autorização humana posterior para implementar as issues em sequência é registrada no handoff vigente e na task #16, sem mudar o escopo aprovado.

- `handoff_schema_version`: `1`.
- `handoff_id`: `utility-belt/006/registrar_aprovacao/conversao_markdown_nativa/55d97a2ef9c959e65119775ac2532eab3dea148f`.
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`; valores `utility-belt` + `006` + `registrar_aprovacao` + `conversao_markdown_nativa` + `55d97a2ef9c959e65119775ac2532eab3dea148f` (hash Git da `v4` revisada antes do registro, sem representar commit). `registrar_aprovacao` identifica esta transição canônica local, sem criar um arquivo de workflow. Baseline Git identificado separadamente; data é metadado.
- `effect_class`: `local_mutation`.
- `state_before`: plano único `v4` em `Em Revisão`, revisão formal `Concluída`, parecer `APTO COM RESSALVAS` sem bloqueios, aprovação humana pós-revisão pendente; ciclo 006 em `Planejamento`, próximo ciclo 007 e mudanças documentais preexistentes.
- `state_after`: mesmo plano `v4` em `Aprovado`, aprovação humana pós-revisão registrada em 2026-10-12; revisão/veredito/escopo técnico/ressalvas preservados. Ciclo 006 continua em `Planejamento`, próximo ciclo 007; nenhuma issue, publicação ou implementação iniciada por este registro.
- `next_transition`: `plano aprovado -> criação de issues` e publicação documental conforme solicitação/gates próprios; implementação é transição posterior com issue vinculada e autorização explícita.
- `preconditions`: antes de criar issues, autorização específica, plano/versão aprovada íntegros, aceite deste handoff, autoridades/template do workflow lidos e preflight de reconciliação no GitHub. Publicação documental exige autorização e gates aplicáveis. Implementação exige issue válida vinculada ao plano, autorização explícita e task persistente ao iniciar.
- `authority`: responsável humano desta conversa aprovou explicitamente a `v4` após o parecer; agente registra a transição definida em `_project/README.md` e `.agent/ai_behavior.md`. Autoridades locais regem próximos gates; GitHub comprovará estados remotos quando workflows remotos forem autorizados.
- `evidence`: parecer formal e ressalvas da `v4` apresentados antes da decisão; mensagem humana “Ok, então está aprovado a V4.”; hash Git da entrada revisada, campos de aprovação/status e `cycles.md` reconciliados, autoridades/template e validação documental. Rastreabilidade de issues/PRs e provas funcionais continuam futuras, sem resultados presumidos.
- `acceptance`: receptor confere plano único `v4`/`Aprovado`, revisão concluída com parecer apto sem bloqueios, aprovação humana posterior registrada, escopo técnico e ressalvas preservados, ciclo 006/007 coerente e handoff integral. Próximo efeito exige sua própria autorização e preflight.
- `blockers`: nenhum para registrar aprovação; falta autorização específica para criação de issues/publicação/implementação, que não é concedida por este registro. Ressalvas técnicas continuam gates das entregas.
- `result`: `executed`.
- `next_workflow_recommended`: `.agent/workflows/criar_issues.md`, quando explicitamente solicitado, com publicação documental conforme autorização/gates próprios.
- `next_workflow_authorized`: `nenhum`; autorização atual cobre somente registro da aprovação pós-revisão da `v4` e reconciliação documental.
- `actions_prohibited`: criar issues, iniciar implementação, instalar dependências, criar/publicar branch ou PR, integrar entregas ou descontinuar/arquivar File2MD sem autorização/gates próprios; alterar materialmente a `v4` e reutilizar esta aprovação sem nova avaliação.
- `rejection_rule`: receptor recusa handoff ausente, incompatível, contraditório, sem evidência material ou sem aprovação posterior ao veredito; recusa também escopo alterado ou uso da aprovação como autorização automática do workflow seguinte.
- `logical_key`: `utility-belt/006/registrar_aprovacao/conversao_markdown_nativa/55d97a2ef9c959e65119775ac2532eab3dea148f`.
- `check_before_mutation`: lidos autoridades/template e plano; confirmados versão `v4`, status `Em Revisão`, revisão concluída/parecer apto, ausência de bloqueios e aprovação anterior ainda pendente. Verificados hash da entrada, baseline Git, ciclo/numeração e manifestação humana posterior ao parecer; nenhum conflito observado.
- `reconcile_existing`: reexecução compatível preserva a mesma aprovação/data e plano canônico, sem duplicar registro, alterar escopo ou conceder efeitos adicionais. Nova revisão material não reutiliza esta aprovação.
- `ambiguous_state`: parar em alteração concorrente/material da versão aprovada, divergência entre decisão humana e parecer/status ou evidência insuficiente; não sobrescrever registro conflitante nem inferir nova aprovação.

### Registro histórico: publicação da entrega A

- `handoff_schema_version`: `1`.
- `handoff_id`: `utility-belt/006/implementar_issue/issue-16/b36d04396ca0bb7af3dab79e5781b092df06ef12`.
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`; origem Git `b36d04396ca0bb7af3dab79e5781b092df06ef12`, escopo aprovado da v4 e alvo #16.
- `effect_class`: `remote_mutation`; branch/PR publicadas após gates autorizados.
- `state_before`: v4 aprovada, ciclo em Planejamento, issues #16/#17/#18 abertas, documentos locais preexistentes.
- `state_after`: plano em Em Execução, ciclo Em execução, #16 implementada/validada em `feature/issue-16` publicada, PR #19 aberta/draft e task persistente com evidências; B/C não iniciadas e nenhuma integração.
- `next_transition`: PR #19 -> revisão/checks -> integração autorizada -> implementar B.
- `preconditions`: gates A e staging seletivo antes de publicar; revisão e autorização de integração antes do merge; A integrada antes de B, B integrada antes de C.
- `authority`: pedido humano atual “Pode implentar as issues com implementar_issue.md a partir do plano 006_plan.md em sequencia da ordem de prioridade proposta no plano”; GitHub comprova estados remotos, responsável autoriza integração.
- `evidence`: [task #16](006_task_issue-16.md), [PR #19](https://github.com/EuThiagoAndrade/utility-belt/pull/19), commit `438647eb401e2f37e16fa615e30a3993d50767a8`, 138 testes, matriz Windows/Linux Python 3.11/3.13, constraints/hashes, smokes consentidos e gates locais registrados na task; zero statuses/runs remotos na consulta, sem inferir sucesso de CI.
- `acceptance`: cumprir Item 1 e aceitar evidências reais/limites, PR rastreável sem ampliar escopo; receptor verifica novamente o estado remoto.
- `blockers`: revisão e autorização de integração pendentes; nenhum bloqueio local de testes/lint/governança e nenhum check remoto disponível na consulta.
- `result`: `executed`.
- `next_workflow_recommended`: revisão da PR de A; integração somente após autorização, depois entrega B.
- `next_workflow_authorized`: implementar_issue para #16 (inclui publicação validada); #17/#18 depois das integrações exigidas; merge não autorizado.
- `actions_prohibited`: merge automático, iniciar B/C antes das dependências integradas, encerrar ciclo ou descontinuar File2MD; repetir envio de áudio usando o consentimento específico já consumido.
- `rejection_rule`: recusar handoff contraditório, sem evidência ou autorização material; não promover próximos efeitos por recomendação.
- `logical_key`: `utility-belt/006/implementar_issue/issue-16/b36d04396ca0bb7af3dab79e5781b092df06ef12`.
- `check_before_mutation`: autoridades/templates lidos, v4 aprovada/issue/autorização confirmadas, main reconciliada; task/branch/PR duplicadas não encontradas.
- `reconcile_existing`: retomar branch/task/PR canônicas compatíveis, sem duplicar artefatos ou alterar escopo técnico.
- `ambiguous_state`: parar em concorrência ou divergência entre plano, issue, task, branch e PR.

### Handoff vigente: implementação da entrega B

- `handoff_schema_version`: `1`.
- `handoff_id`: `utility-belt/006/implementar_issue/issue-17/13b4719af643747b679e87602ac5ff414b35d716`.
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`.
- `effect_class`: `local_mutation`.
- `state_before`: A publicada/não integrada e autorização humana para integrar PR #19 e continuar #17.
- `state_after`: PR #19 integrada em `13b4719af643747b679e87602ac5ff414b35d716`, issue #16 fechada; B implementada na branch `feature/issue-17`, em validação; C não iniciada.
- `next_transition`: gates/smokes B -> publicação de PR -> revisão -> integração autorizada -> C.
- `preconditions`: Item 2 completo e gates/smokes reais para publicar; autorização própria para integrar B; B integrada antes de C.
- `authority`: solicitação humana atual autorizou integração da PR #19 e implementação de #17; GitHub comprova merge/issue; autoridades locais regem próximos gates.
- `evidence`: [task A](006_task_issue-16.md), [task B](006_task_issue-17.md), merge `13b4719`, issue #17 aberta e arquivos/testes/gates B registrados na task.
- `acceptance`: receptor confere escopo B, evidências, PR canônica e dependência integrada, sem ampliar v4.
- `blockers`: gates/publicação B em conclusão; integração de B sem autorização.
- `result`: `executed`.
- `next_workflow_recommended`: concluir implementar_issue #17 e encaminhar à revisão.
- `next_workflow_authorized`: implementar_issue #17; #18 somente após B integrada; merge de B não autorizado.
- `actions_prohibited`: integrar B automaticamente, iniciar C antes da dependência, encerrar ciclo/descontinuar File2MD ou reutilizar consentimento externo de A.
- `rejection_rule`: recusar divergência de escopo, evidência, estado ou autorização.
- `logical_key`: `utility-belt/006/implementar_issue/issue-17/13b4719af643747b679e87602ac5ff414b35d716`.
- `check_before_mutation`: autoridades/templates/plano/issue/autorização lidos; merge de A/base confirmados; duplicações de task/branch/PR não encontradas.
- `reconcile_existing`: retomar a unidade B compatível e preservar registros históricos.
- `ambiguous_state`: parar em concorrência/divergência material.

## Revisão crítica

- **Data:** 2026-10-12
- **Versão revisada:** `v4`, após incorporar aceites e correções técnicas; origem `v3` com hash Git de conteúdo `a0bec469414905e3dfbef6fa0b5ce44b0ef49e3d`.
- **Veredito:** `APTO COM RESSALVAS`
- **Bloqueios remanescentes:** Nenhum de planejamento; aprovação humana posterior ao parecer registrada em 2026-10-12.
- **Aprovação humana pós-revisão:** `Aprovada em 2026-10-12`; manifestação nesta conversa: “Ok, então está aprovado a V4.”, posterior à apresentação do parecer.
- **Correções materiais:** `P03`/`P05` confirmadas; `P04` fechado com receitas e ambientes próprios; transcrição externa delimitada por consentimento; requisitos de binários explicitados; proteção de TOML inválido e detecção de ZIP parcial acrescentadas.
- **Ressalvas:** `R01`–`R05` abaixo; não dispensam testes nem autorizam reduzir o escopo.

### Checklist e achados classificados

| ID | Classe / situação | Achado e evidência |
| :-- | :-- | :-- |
| `A01` | Atendido | As 16 seções do template estão presentes; plano/ciclo/numeração são únicos e coerentes. Status entrou em `Em Revisão` antes do parecer; aprovação posterior da `v4` registrada em 2026-10-12, sem autorização automática de execução. |
| `A02` | Atendido | Cinco capacidades, nomes, pastas exclusivas, extensão original, estrutura relativa e recursividade rastreiam ideação e respostas humanas. Nenhuma cópia/execução do File2MD é requisito. |
| `A03` | Atendido | Entregas A/B/C têm dependências, critérios, tasks, gates, distribuição instalada e fechamento sem issue recursiva; nenhuma issue ou execução iniciada aqui. |
| `C01` | Bloqueador corrigido | Tratamento de Markdown e política do monitor estavam pendentes em `v3`; aceite humano atual e contratos/testes de `v4` resolvem ambos. |
| `C02` | Bloqueador corrigido | `v3` não definia alvo/mecanismo/versões de instalação. `P04` agora fixa motor/grupos, uv, ambientes de dados do usuário, worker, constraints e binários, com aquisição real como gate da entrega A. Não se presume alteração do ambiente global ou do Belt. |
| `C03` | Bloqueador corrigido | Código fixado do motor chama Google em transcrição quando dependências estão disponíveis. Responsável autorizou esse recurso com consentimento por operação. Separação `core`/`audio` e testes garantem que instalar biblioteca não autoriza envio e que ausência de TTY não ativa serviço. |
| `C04` | Bloqueador corrigido | MarkItDown sem LLM usa metadados para imagens; áudio também pode produzir apenas metadados, com ExifTool externo. Limites e aquisição/pré-requisitos estão explícitos, sem promessa de OCR, interpretação de vídeo ou extração universal. |
| `C05` | Bloqueador corrigido | ZIP nativo suprime erros de conversão de membros. Worker precisa registrar essas falhas e reportar saída parcial/código `1`; teste dedicado evita sucesso silencioso com conteúdo omitido. |
| `C06` | Correção de integridade | `load_config()` pode devolver defaults após TOML inválido; preferência nova exige leitura estrita antes da escrita, preservando dados em erro. Teste exige nenhuma gravação nessa situação. |
| `A04` | Atendido | Runner atual não propaga modo não interativo ao subprocesso de ferramenta não interativa; ajuste cirúrgico foi incluído em arquivos/escopo/testes. Não se promete supressão de prompts sem esse ajuste. |

### Ressalvas e gates de entrega

| ID | Ressalva | Evidência que resolve na execução |
| :-- | :-- | :-- |
| `R01` | Compatibilidade é baseada em metadados, ainda sem instalação/uso real. Python do motor é 3.11–3.14; não restringir o restante do Belt silenciosamente. | A deve gerar constraints/hashes e validar aquisições, binários e famílias nas plataformas/Python definidos. C deve demonstrar wheel/sdist fora do checkout, execução mínima, aquisição posterior e reutilização/upgrade. |
| `R02` | Transcrição depende de serviço externo e pode falhar ou produzir texto inadequado. | Testes automatizados isolam rede e provam consentimento por operação; smoke real usa fixture não pessoal com consentimento próprio e registra qualidade/limites. Nenhum serviço externo pode ser acessado para áudio após recusa ou em automação. |
| `R03` | Estabilidade por tamanho/mtime é uma aproximação; eventos variam entre sistemas. | B deve validar cópia lenta, timeout, movimentos de pastas, novos subdiretórios, duplicados, ciclos de vida e cancelamento com observador real nas duas plataformas, além de documentar a limitação. |
| `R04` | Binários podem não existir ou não suportar a plataforma; ExifTool Perl exige Perl local. | A deve confirmar fonte/versão/hash e extração portátil, diagnóstico de pré-requisito ausente, ausência de instalação privilegiada/mudança global e preservação após falha/cancelamento. Sem pré-requisito, informar `2` e manter demais formatos disponíveis. |
| `R05` | Validador emite aviso conhecido para 007 por considerar somente ciclos concluídos. | Numeração 006/007 conferida manualmente; preservar a autoridade `cycles.md`. O aviso não indica falha desta revisão nem autoriza alterar o validador neste ciclo. |

As ressalvas são critérios de verificação das entregas, não bloqueios abertos de escolha ou arquitetura. Se a execução comprovar que algum contrato não pode ser atendido, interromper a entrega e revisar o plano; não reduzir cobertura, consentimento ou proteção das saídas silenciosamente. Este parecer avalia o plano, não certifica código inexistente.

## Pós-mortem

- **Data de conclusão:** —
- **Desvios:** —
- **Lições comprovadas:** —
