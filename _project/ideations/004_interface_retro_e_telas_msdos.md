# Ideação — 004: Interface Retrô MS-DOS e Identidade Visual

> **Ciclo:** `004`
> **Estado:** `Ideação`
> **Criado em:** 2026-09-17
> **Última atualização:** 2026-09-17

## Problema

A interface interativa atual do Utility Belt (`belt menu`) opera em fluxo contínuo de terminal (scrolling linear tradicional). Conforme o usuário escolhe opções de navegação ou dispara a execução de ferramentas (como exportação/importação do Docker, rotinas do Restic ou diagnóstico do Doctor), as saídas são impressas nas linhas subsequentes e os menus anteriores continuam visíveis e empilhados para cima.

Esse comportamento gera dois atritos principais:
1. **Perda de foco e poluição visual:** O terminal "anda" verticalmente a cada clique, acumulando menus passados, prompts respondidos e logs de comandos, em vez de oferecer a experiência imersiva e limpa de "telas/visões dedicadas" típica de sistemas clássicos como MS-DOS, Norton Utilities ou BIOS.
2. **Ausência de identidade visual marcante de abertura:** Ao inicializar a CLI, falta um elemento de boas-vindas com forte identidade retrô que represente o conceito do projeto: o canivete suíço de utilitários para terminal com tipografia marcante em blocos 3D.

## Contexto e evidências

- **Base de código atual:** O projeto utiliza Python 3.11+, Typer para a CLI, Questionary para navegação por setas (`questionary.select`, `checkbox`, `path`, etc.) e Platformdirs para persistência de configurações locais.
- **Estrutura dos menus atuais:** Em `src/utility_belt/menu.py`, `src/utility_belt/ui/docker_menu.py` e `src/utility_belt/ui/restic_menu.py`, os laços de menu utilizam `while True:` sem chamadas a limpeza de tela (`typer.clear()`).
- **Alinhamento via `/grill-me` (2026-09-17):** Durante a rodada de alinhamento com o usuário, foram acordados os seguintes direcionamentos de design:
  1. *Transições de tela:* Adoção de limpeza dinâmica de tela (`typer.clear()`) a cada transição de submenu ou comando, exibindo um cabeçalho fixo com breadcrumbs de navegação (ex: `BELT > DOCKER > EXPORTAR`), mantendo a leveza e simplicidade do Questionary sem frameworks pesados de TUI (como Curses ou Textual).
  2. *Tela dedicada de execução:* Para cada ferramenta acionada, limpar a tela antes da execução, exibir o cabeçalho contextual da tarefa, imprimir a saída e aguardar confirmação ("Pressione qualquer tecla para voltar..."), limpando novamente a tela ao retornar ao menu de origem.
  3. *Identidade visual híbrida (Banner de Abertura):* Composição combinando arte ASCII de um canivete suíço detalhado à esquerda e o título "UTILITY BELT" em tipografia de blocos isométricos/3D à direita (inspirada na imagem de referência do Claude Code em tons quentes/laranja), tudo envolvido por uma moldura retrô de linhas duplas (`╔═╗`) formatada para terminais de 80 colunas.
  4. *Frequência e hierarquia:* Banner de abertura completo exibido no Menu Principal; submenus utilizam barra de navegação/breadcrumbs compacta no topo para preservar espaço vertical útil.
  5. *Paleta de cores retrô:* Tons quentes/alaranjados (âmbar/terracota) nos blocos 3D do título, combinados com ciano e branco brilhante para bordas, separadores e realces de seleção.
  6. *Navegação híbrida por teclado:* Preservação da navegação clássica por setas (↑↓) e Enter, somada a atalhos numéricos e letras rápidas (ex: `[1]`, `[2]`, `[0]`, `[ESC]`) para retorno e seleção ágil.
  7. *Escopo exclusivo:* A experiência visual de telas e banner atua estritamente no modo interativo (`belt menu`); comandos diretos de linha de comando (`belt doctor`, `belt catalog list`) permanecem limpos e adequados para automações e pipes.
  8. *Configurabilidade:* Suporte a desativar ou reduzir o banner via configuração do usuário (`belt config`) e tolerância a terminais de dimensões reduzidas ou sem suporte UTF-8.

## Resultado desejado

1. Um módulo centralizado de interface e telas (ex: `src/utility_belt/ui/screen.py` ou layout equivalente) que encapsule:
   - Limpeza segura de tela (`clear_screen`);
   - Renderização do banner híbrido retrô com canivete ASCII + tipografia 3D em blocos;
   - Renderização de cabeçalhos de navegação com breadcrumbs (ex: `╔═ UTILITY BELT ═ DOCKER ═ EXPORTAR ═╗`);
   - Helper de execução de tela dedicada (`screen_view` ou wrapper similar) para envolver diagnósticos, execuções do Docker e do Restic.
2. Menu principal (`menu.py`) modernizado com exibição limpa do banner, navegação rápida por atalhos e saída graciosa.
3. Submenus (`docker_menu.py` e `restic_menu.py`) integrados ao mesmo padrão de transição e cabeçalhos compactos.
4. Experiência de execução de comandos isolada em tela própria com pausa antes do retorno, eliminando a rolagem acumulada de menus passados.
5. Opção de configuração `show_banner` no arquivo de configuração do Utility Belt para flexibilidade do usuário.

## Hipóteses

- **H1:** A orquestração de `typer.clear()` combinada com cabeçalhos padronizados e Questionary entrega a sensação nostálgica e limpa de "telas MS-DOS" sem o overhead, instabilidade de terminal ou complexidade arquitetural de frameworks TUI completos (como Textual ou Blessed).
- **H2:** Um layout de banner híbrido de ~78 colunas (canivete ~24 colunas + título 3D em blocos ~50 colunas) oferece alta legibilidade e é compatível com os terminais padrão do Windows (Windows Terminal, PowerShell, CMD) e Linux.
- **H3:** A adição de atalhos numéricos (`[1]`, `[2]`, etc.) reduz a fricção de navegação para usuários avançados sem interferir na facilidade de uso via setas para novos usuários.

## Alternativas

- **Alternativa A — Migração para Framework TUI Completo (Textual / Curses):**
  - *Prós:* Controle absoluto de buffer alternativo de tela, widgets avançados, suporte nativo a janelas e eventos de mouse.
  - *Contras:* Aumentaria drasticamente as dependências do projeto, reescreveria todo o trabalho feito no Ciclo 001 com Questionary e exigiria refatoração profunda dos menus e testes.
  - *Veredito:* Descartada em favor da abordagem leve acordada com o usuário.
- **Alternativa B — Limpeza de tela pontual sem módulo unificado:**
  - *Prós:* Rápida de implementar diretamente nos arquivos existentes com `typer.clear()`.
  - *Contras:* Código duplicado em cada menu, cabeçalhos inconsistentes, risco de formatação divergente e ausência de uma identidade visual consolidada.
  - *Veredito:* Descartada.
- **Alternativa C (Selecionada) — Módulo centralizado de telas retrô com Questionary e Banner Híbrido:**
  - *Prós:* Mantém as dependências atuais, padroniza todos os menus e submenus, garante consistência em transições e cria uma assinatura visual marcante para o projeto.

## Riscos e restrições

- **Compatibilidade de caracteres e fontes (Windows CMD legados):** Alguns ambientes legados podem apresentar problemas ao renderizar caracteres de caixa UTF-8 (`╔`, `═`, `║`).
  - *Mitigação:* Usar codificação UTF-8 explícita e prever fallback seguro com caracteres ASCII padrão (`+`, `-`, `|`) se a codificação falhar.
- **Redimensionamento ou terminais com menos de 80 colunas:** Telas menores que 80 colunas podem quebrar linhas da arte ASCII.
  - *Mitigação:* O banner deve ser projetado com no máximo 76-78 colunas e detectar a largura do terminal via `shutil.get_terminal_size()` para exibir uma versão simplificada de 1 linha caso o terminal seja muito estreito.
- **Subprocessos interativos e stdin/stdout:** Comandos externos (ex: `docker save`, `restic backup`) precisam preservar a visibilidade de logs e interações.
  - *Mitigação:* O wrapper de tela dedicada deve apenas limpar a tela antes e aguardar após a conclusão, sem interceptar destrutivamente os streams de dados dos utilitários.

## Perguntas em aberto

- Nenhuma pergunta bloqueante em aberto. Todos os ramos fundamentais de design (estilo de transição, modelo de execução, arte do banner, frequência de exibição, paleta de cores e atalhos de teclado) foram esclarecidos e alinhados na entrevista `/grill-me`.

## Fora do escopo

- Reescrever a lógica interna de comandos de negócio (Restic, Docker ou Catálogo).
- Modificar o comportamento ou adicionar banners nas chamadas diretas de CLI (`belt doctor`, `belt catalog list`, etc.).
- Suporte a cliques de mouse ou janelas gráficas flutuantes estilo mouse DOS.

## Critérios para iniciar o planejamento

- Registro e reserva formal do Ciclo `004` no arquivo de governança `_project/cycles.md`.
- Handoff de saída da ideação aceito e autorização explícita do solicitante para executar o workflow `.agent/workflows/rascunhar_plano.md`.

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: `utility-belt/cycle-004/idear/004_interface_retro_e_telas_msdos/2c3be55`
- `identity_source`: `utility-belt + cycle-004 + idear + 004_interface_retro_e_telas_msdos + 2c3be55`
- `effect_class`: `local_mutation`
- `state_before`: `Ciclo 003 concluído; menus interativos em fluxo contínuo sem transição limpa de telas e sem banner temático de inicialização.`
- `state_after`: `Ideação 004 registrada com problemas, requisitos visuais retrô, decisões da entrevista /grill-me e arquitetura leve de telas documentadas.`
- `next_transition`: `ideia -> rascunho de plano (após decisão e autorização humana)`
- `preconditions`: `Alinhamento completo dos requisitos de telas e identidade visual do Ciclo 004 obtido via entrevista.`
- `authority`: `Solicitação explícita do usuário para entrevistar e registrar a ideação.`
- `evidence`: `_project/ideations/004_interface_retro_e_telas_msdos.md e branch chore/cycle-004-ideation.`
- `acceptance`: `Ideação instanciando integralmente o template canônico sem omissão de seções, critérios de descarte explícitos e handoff estruturado.`
- `blockers`: `nenhum`
- `result`: `executed`
- `next_workflow_recommended`: `rascunhar_plano`
- `next_workflow_authorized`: `nenhum`
- `actions_prohibited`: `Aprovar plano, criar issues, alterar código-fonte da aplicação ou abrir PRs sem autorização formal subsequente.`
- `rejection_rule`: `O receptor recusa handoff ausente, incompatível, contraditório ou sem evidência material.`
- `logical_key`: `utility-belt/cycle-004/idear/004_interface_retro_e_telas_msdos/2c3be55`
- `check_before_mutation`: `Confirmado que o ciclo 004 era o próximo ciclo aberto e não possuía artefato de ideação prévio.`
- `reconcile_existing`: `Reconciliado artefato criado no ciclo 004 em _project/ideations/.`
- `ambiguous_state`: `Parar e solicitar intervenção humana em caso de divergência de numeração ou estado de governança.`
