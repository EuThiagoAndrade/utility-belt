# Ideação — 006: Conversão Markdown Nativa no Utility Belt

> **Ciclo:** `006`
> **Estado:** `Ideação`
> **Criado em:** 2026-10-12
> **Última atualização:** 2026-10-12

## Problema

A conversão de documentos para Markdown está disponível em um projeto separado, File2MD, enquanto o Utility Belt pretende concentrar ferramentas pessoais de terminal em uma experiência única. Manter o conversor separado exige instalação, configuração e interface próprias.

O responsável deseja incorporar ao Utility Belt somente as funcionalidades do File2MD que utiliza ou considera importantes, adaptando-as à filosofia do Belt. O File2MD será descontinuado depois que a adaptação estiver validada. Este documento registra a exploração e as escolhas da conversa; não constitui plano executável ou autorização de implementação.

## Contexto e evidências

### Fatos observados

- Repositório de destino: `C:/Programas/utility-belt`, origem `https://github.com/EuThiagoAndrade/utility-belt.git`, revisão inspecionada `b36d04396ca0bb7af3dab79e5781b092df06ef12`; árvore de trabalho limpa antes deste registro.
- O [README](../../README.md), o [pyproject.toml](../../pyproject.toml) e a [ADR-002](../decisions/ADR-002_arquitetura_cli_distribuivel.md) descrevem distribuição como pacote Python, CLI, menus interativos e catálogo por `tool.toml`. A configuração existente usa TOML e diretórios do usuário.
- As autoridades [.agent/ai_behavior.md](../../.agent/ai_behavior.md) e [_project/README.md](../README.md) foram lidas. A governança proíbe dependência operacional de checkout irmão.
- [_project/cycles.md](../cycles.md) declarava `006` como próximo ciclo; não havia ideação, plano ou reserva conflitante para esse número e assunto.
- O File2MD foi inspecionado apenas em leitura em `C:/Programas/File2MD`, revisão `ad13d85f53f2b8911583d6f08df3c57e96615655`, sem alterações locais observadas. Referências documentais fixadas: [script principal](https://github.com/EuThiagoAndrade/File2MD/blob/ad13d85f53f2b8911583d6f08df3c57e96615655/Scripts/File2MD.py), [README](https://github.com/EuThiagoAndrade/File2MD/blob/ad13d85f53f2b8911583d6f08df3c57e96615655/README.md) e [dependências](https://github.com/EuThiagoAndrade/File2MD/blob/ad13d85f53f2b8911583d6f08df3c57e96615655/requirements.txt). Esses links identificam a fonte estudada; não são dependências de execução.
- O script usa a API Python do MarkItDown quando disponível, com alternativa por subprocesso. Reúne conversão, interface, configuração JSON e recursos opcionais no mesmo arquivo.
- O lote atual percorre somente o nível imediato da pasta; o monitoramento atual observa criação de arquivos, sem recursividade, e espera um segundo antes da conversão. As listas de extensões de lote e monitoramento diferem.
- A saída local atual substitui a extensão por `.md`; URLs usam `web_content.md`. A escrita usa modo `w`, permitindo colisões e sobrescritas. A organização por operação discutida aqui ainda não existe.
- Não foram executadas conversões, testes funcionais ou medições de qualidade do MarkItDown nesta ideação. Suporte real por formato e dependências necessárias continuam sujeitos a validação posterior; não se assume conversão de qualquer arquivo.

### Escolhas confirmadas na conversa

- Incorporar as funcionalidades ao Utility Belt e adaptar sua experiência às convenções do projeto, em vez de manter duas aplicações ou depender da pasta local do File2MD.
- Manter somente as opções atuais `2`, `3`, `4`, `5` e `9`: conversão individual de arquivo ou URL, lote, monitoramento, clipboard e configuração da pasta de saída.
- Concentrar os resultados em uma pasta de saída configurável.
- Criar uma subpasta exclusiva por operação, identificada pela data e hora de início da conversão, e não pela data de criação do arquivo original.
- Arquivo único, URL e clipboard: uma subpasta por conversão. Lote: uma subpasta compartilhada por todos os resultados da execução. Monitoramento: uma subpasta por conversão automática de arquivo.
- Preservar a extensão original no nome, como `relatorio.pdf.md`, e a estrutura relativa de subpastas nas conversões de pastas.
- Acrescentar um sufixo quando houver coincidência de nomes de pastas de operação, sem reutilizar uma pasta existente.
- Descontinuar o File2MD somente depois da adaptação validada. A forma concreta e o momento da descontinuação serão definidos posteriormente.
- O pedido atual autoriza o workflow [idear](../../.agent/workflows/idear.md) para documentar esta discussão. O usuário mantém a restrição de não codificar ou implementar; o plano será uma etapa posterior.

### Validação deste registro

- `python scripts/validate_governance.py`: concluído com código `0`, 31 verificações OK, um aviso e nenhuma falha. O aviso compara `007` ao sucessor do maior ciclo concluído (`005`), sem considerar a reserva de `006` em Ideação; a numeração foi mantida conforme a autoridade `cycles.md`. Nenhuma alteração no validador faz parte desta etapa.
- `git diff --check`: concluído sem erros; o novo arquivo também foi inspecionado quanto a espaços residuais e presença das seções canônicas do template.
- `git status --short`: somente `_project/cycles.md` modificado e este arquivo novo; nenhum código ou artefato de plano alterado ou criado.
- A tentativa inicial de usar `.venv/Scripts/python.exe` não executou o validador porque o ambiente existente referencia um Python ausente. A validação foi realizada com o Python do sistema, sem reparar ou modificar o ambiente. Testes funcionais e lint de código não foram executados, pois a entrega é somente documental e não será publicada nesta etapa.

## Resultado desejado

Uma ferramenta nativa de conversão Markdown acessível pela experiência do Utility Belt, com as cinco funcionalidades selecionadas e regras comuns de destino e organização.

| Funcionalidade | Resultado esperado |
| :-- | :-- |
| Conversão individual | Converter um arquivo local ou URL e salvar o Markdown em uma pasta exclusiva da operação. |
| Conversão em lote | Converter arquivos compatíveis da pasta de entrada e reunir as saídas na pasta exclusiva do lote. |
| Monitoramento | Converter novos arquivos compatíveis da pasta acompanhada, com uma pasta de saída por conversão automática. |
| Clipboard | Ler um caminho de arquivo ou URL da área de transferência e aplicar o comportamento da conversão individual. |
| Pasta de saída | Definir e persistir o destino central utilizado pelas modalidades de conversão. |

Exemplos ilustrativos da organização acordada, sem definir ainda nomes de comandos ou detalhes de implementação:

- Individual: `Conversoes/2026-10-12_14-30-05/relatorio.pdf.md`.
- Lote: `Conversoes/2026-10-12_14-35-20/relatorio.pdf.md` e `Conversoes/2026-10-12_14-35-20/relatorio.docx.md`.
- Subpastas: quando a entrada incluir `financeiro/relatorio.pdf`, preservar `financeiro/relatorio.pdf.md` dentro da pasta da operação.
- Coincidência entre operações: uma segunda pasta pode receber um sufixo, como `2026-10-12_14-35-20_2`; o formato exato do sufixo será definido no planejamento.

## Hipóteses

- **H1 — Encaixe arquitetural:** o MarkItDown pode ser o motor de um adaptador nativo, enquanto o Belt oferece catálogo, CLI, menus e configuração, sem necessidade de criar uma plataforma genérica de plugins.
- **H2 — Aproveitamento:** regras e experiência do File2MD podem orientar a adaptação; copiar integralmente seu script carregaria interface, configuração e recursos excluídos. A parcela reutilizável será avaliada no planejamento.
- **H3 — Dependências:** uma combinação delimitada de dependências de conversão, clipboard e monitoramento pode atender ao escopo sem trazer configuração de IA. Instalação obrigatória ou opcional ainda não foi decidida.
- **H4 — Integridade:** pastas exclusivas por operação, extensão original no nome e preservação de subpastas podem evitar as colisões comuns, desde que a reserva das pastas trate concorrência e diferenças entre plataformas.
- **H5 — Experiência:** uma pasta de saída persistida e regras compartilhadas entre modalidades podem reduzir decisões repetidas e facilitar localizar resultados.

## Alternativas

| Alternativa | Avaliação |
| :-- | :-- |
| Funcionalidades incorporadas ao Utility Belt | Caminho selecionado pelo responsável. Concentra manutenção, experiência e distribuição; exige adaptar o legado e validar os usos essenciais. |
| Belt chama File2MD instalado separadamente | Não selecionada. Preserva duas instalações e configurações; depender diretamente do checkout irmão também contraria a governança. |
| File2MD como pacote independente consumido pelo Belt | Não selecionada. Permite dois produtos com núcleo compartilhado, mas acrescenta manutenção de distribuição e versões sem necessidade confirmada. |

Para implementação futura, API Python do MarkItDown é uma hipótese inicial; o mecanismo concreto, empacotamento e versões ainda precisam de avaliação. Nenhuma alternativa técnica passa a ser decisão arquitetural aprovada apenas por este registro.

## Riscos e restrições

- **Escopo:** transportar toda a aplicação antiga reintroduziria funcionalidades que o usuário excluiu. A adaptação deve atender às cinco capacidades escolhidas.
- **Qualidade e formatos:** extração de texto, tabelas e documentos digitalizados pode variar. Listas exibidas pelo legado não comprovam suporte efetivo. Definir um conjunto de formatos verificável antes de prometer compatibilidade.
- **Instalação:** avaliar peso, versões e compatibilidade de MarkItDown e seus conversores com o Python e as plataformas do Belt. Não usar descoberta de ambientes virtuais do File2MD como requisito operacional.
- **Nomes e concorrência:** operações podem começar no mesmo segundo; nomes devem permanecer válidos em Windows e Linux e pastas existentes devem ser preservadas. URLs ainda precisam de uma regra de nomeação.
- **Monitoramento:** a espera fixa do legado não comprova que uma cópia terminou. Discutir estabilidade do arquivo, eventos repetidos, cancelamento e tratamento de falhas. Impedir que a própria saída seja reconvertida se estiver dentro da árvore monitorada.
- **Lotes e falhas:** o código atual inicia threads por arquivo; a posição do semáforo não impõe limite por trabalhador. O planejamento deve avaliar necessidade e limite de concorrência, resumo de falhas e códigos de saída, sem presumir desempenho já validado.
- **Clipboard:** disponibilidade do mecanismo varia por sistema e sessão. Definir mensagem e comportamento para clipboard vazio, conteúdo inválido e ambiente sem suporte.
- **Rede:** URLs implicam acesso remoto; delimitar entradas aceitas e comportamento de erro, sem incluir processamento por IA ou serviços de nuvem por inferência.
- **Governança:** registro de escolhas de produto não aprova plano, issues ou execução. Descontinuação remota, arquivamento do File2MD e publicação exigem autorização própria.

Critérios para descartar ou rever uma abordagem durante o planejamento: dependência operacional do checkout File2MD; inclusão de recursos excluídos; impossibilidade de proteger resultados existentes; conversão incompatível com os formatos prioritários; ou complexidade de instalação sem justificativa para os usos selecionados. Esses critérios não cancelam automaticamente o ciclo.

## Perguntas em aberto

1. Qual será o nome do módulo e dos comandos, e como as cinco funcionalidades se encaixarão no menu e no catálogo existentes?
2. Quais formatos precisam ser atendidos primeiro? Como manter critérios coerentes entre conversão individual, lote e monitoramento?
3. O lote e o monitoramento serão recursivos? A preservação da estrutura relativa já foi acordada, mas não define por si só quais subpastas serão percorridas.
4. Qual comportamento fixo substituirá a opção de limpeza YAML removida? Preservar o Markdown do motor foi sugerido, mas não recebeu confirmação específica e permanece proposta.
5. Como agir quando a pasta de saída não estiver configurada, não existir ou não puder ser escrita? Solicitar o destino no menu foi sugerido; a regra da CLI não interativa ainda precisa ser definida.
6. Como nomear saídas de URLs? Qual precisão e referência de horário usar nos nomes das pastas, e qual regra de sufixo adotar?
7. Quais eventos o monitoramento deve considerar: somente novos arquivos ou também alterações e movimentações? Como detectar que estão prontos e lidar com duplicidade de eventos?
8. Como comunicar conversões vazias, falhas parciais, cancelamentos e resultados para automações? Manter pastas de operações que falharam ou removê-las?
9. Quais dependências serão obrigatórias ou opcionais, com quais versões e mecanismos de diagnóstico? Haverá necessidade de migrar alguma preferência legada?
10. Quais evidências e usos reais confirmarão que o File2MD pode ser descontinuado? Aviso no README e eventual arquivamento do repositório serão decisões separadas, sem mutação remota nesta etapa.

## Fora do escopo

- Tela específica de formatos suportados, preview integrado, configuração/integração de IA, alternância de limpeza YAML e troca de idioma do File2MD. Mensagens normais de compatibilidade e erros continuam pertinentes ao uso das cinco funcionalidades.
- Construir ou manter o File2MD como um segundo produto ou pacote compartilhado independente.
- Criar interface web, API hospedada, aplicação gráfica ou mecanismo genérico de plugins.
- Prometer conversão universal ou fidelidade visual irrestrita.
- Escrever código, alterar dependências, criar plano, issue, branch, commit, PR ou realizar integração neste workflow.
- Alterar, excluir ou arquivar o repositório File2MD, seus arquivos ou sua configuração.

## Critérios para iniciar o planejamento

- O responsável autoriza explicitamente o workflow [rascunhar_plano](../../.agent/workflows/rascunhar_plano.md), após receber esta ideação. O pedido de preparar a discussão para um plano posterior não inicia esse workflow automaticamente.
- O receptor confirma a identidade do ciclo `006`, o registro em `cycles.md`, as escolhas confirmadas e o handoff abaixo, e lê as autoridades e o template de plano no ponto de uso.
- Formatos prioritários, recursividade, tratamento fixo do Markdown, instalação das dependências e requisitos de monitoramento são decididos com o responsável ou identificados no rascunho como pendências que precisam ser resolvidas antes da aprovação.
- O futuro rascunho delimita critérios verificáveis para as cinco capacidades, proteção das saídas, comportamento interativo e não interativo, falhas e validação da distribuição instalada.
- A futura descontinuação do File2MD é condicionada à validação da adaptação e tem ações e autorizações próprias. Não é efeito automático desta ideação.

## Handoff de saída

- `handoff_schema_version`: `1`.
- `handoff_id`: `utility-belt/006/idear/conversao_markdown_nativa/b36d04396ca0bb7af3dab79e5781b092df06ef12`.
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`; valores: `utility-belt` + `006` + `idear` + `conversao_markdown_nativa` + `b36d04396ca0bb7af3dab79e5781b092df06ef12`. Data é metadado e não define identidade.
- `effect_class`: `local_mutation`.
- `state_before`: próximo ciclo declarado `006`; árvore limpa; nenhum artefato ou reserva para este ciclo e alvo; discussão humana identificada, sem plano, issue ou autorização de implementação.
- `state_after`: esta ideação registra fatos, escolhas, hipóteses, alternativas, riscos e perguntas; ciclo `006` reservado em estado `Ideação`; próximo ciclo `007`; nenhum plano criado ou aprovado.
- `next_transition`: `Ideação -> Planejamento`, com criação de plano em `Rascunho`, somente após decisão humana e aceite do receptor.
- `preconditions`: autorização explícita para rascunhar; identidade e reserva do ciclo coerentes; leitura das autoridades e do template de plano; decisões pendentes resolvidas ou delimitadas no rascunho sem inventar aprovação.
- `authority`: responsável humano autoriza o próximo workflow e decide preferências; autoridades canônicas definem estados e gates; agente receptor verifica consistência e instancia o template sem ampliar o escopo.
- `evidence`: solicitação humana deste workflow e escolhas confirmadas nesta conversa; autoridades, template `.agent/templates/ideacao.md`, workflow `.agent/workflows/idear.md`, arquivos e revisões identificados em Contexto e evidências; este artefato e a reserva em `cycles.md`; resultados reais registrados em Validação deste registro. Antes do aceite, verificar consistência documental e ausência de mudanças fora dos dois artefatos autorizados.
- `acceptance`: receptor verifica todas as seções do template, separação entre fatos e hipóteses, rastreabilidade das escolhas, ciclo único, riscos e pendências explícitos e autorização própria antes de criar o rascunho. Não há aceite do próximo workflow declarado nesta saída.
- `blockers`: nenhum para registrar a ideação. Para o próximo efeito, autorização de rascunho ainda não recebida; perguntas em aberto precisam de tratamento no planejamento antes da aprovação.
- `result`: `executed`.
- `next_workflow_recommended`: `.agent/workflows/rascunhar_plano.md`.
- `next_workflow_authorized`: `nenhum`; a autorização atual cobre somente `idear` e os registros locais associados.
- `actions_prohibited`: iniciar rascunho ou revisão sem autorização própria, aprovar plano, criar issue, implementar, alterar dependências, publicar branch/PR, integrar entrega ou descontinuar/arquivar File2MD nesta etapa.
- `rejection_rule`: receptor recusa handoff ausente, incompatível, contraditório ou sem evidência suficiente; recomendação não satisfaz autorização humana e nenhum workflow seguinte é acionado automaticamente.
- `logical_key`: `utility-belt/006/idear/conversao_markdown_nativa/b36d04396ca0bb7af3dab79e5781b092df06ef12`.
- `check_before_mutation`: autoridades, template, identidade Git, estado local, lista de artefatos e referências a `006` foram inspecionados; nenhuma saída compatível ou reserva conflitante foi encontrada antes da criação.
- `reconcile_existing`: reexecução compatível reutiliza este arquivo e a linha do ciclo `006`, sem reservar `007` novamente; diferenças materiais devem ser reconciliadas preservando escolhas e evidências.
- `ambiguous_state`: interromper mutação se houver reserva concorrente, mais de uma ideação canônica para o alvo, divergência de revisão não reconciliada ou estado parcial sem evidência; solicitar intervenção humana sem sobrescrever artefatos conflitantes.
