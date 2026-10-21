# Ideação — 011: Preparação para Repositório Público e Aperfeiçoamento do Janitor

> **Ciclo:** `011`
> **Estado:** `Ideação`
> **Criado em:** 2026-10-21
> **Última atualização:** 2026-10-21

## Problema

Com o amadurecimento das funcionalidades centrais do Utility Belt (Restic, Docker, Markdown, diagnósticos de ambiente e ferramentas de desenvolvimento com Janitor e Git-Tidy), o repositório atingiu estabilidade técnica para ser disponibilizado publicamente no GitHub. 

Contudo, foram identificadas duas frentes de lacunas antes dessa abertura:

### 1. Conformidade jurídica, documental e comunitária para repositório público
- **Ausência de Licença:** Não há arquivo `LICENSE` na raiz do repositório, e o `pyproject.toml` não declara o campo `license`. No regime padrão de direitos autorais do GitHub, um repositório público sem licença adota *All Rights Reserved*, impedindo que a comunidade utilize, instale, bifurque ou contribua legalmente.
- **Divergências no README:** O `README.md` encontra-se defasado em relação à versão real do produto:
  - Não menciona o módulo `belt dev` (ferramentas `janitor` e `git-tidy` introduzidas nos ciclos 009 e 010);
  - Descreve no menu interativo principal apenas 4 opções (*Restic, Docker, Markdown e Sistema*), omitindo a opção `[4] Desenvolvimento`;
  - A seção de licença cita genericamente *"sob licença aberta. Consulte o repositório..."* sem base fática;
  - Ausência de metadados e badges úteis de versão e compatibilidade Python (com exclusão expressa de badge de CI solicitada pelo responsável).
- **Metadados em `pyproject.toml` e `.gitignore`:**
  - `pyproject.toml` não possui `[project.urls]` (links para repositório, issues, changelog), `classifiers` e `keywords`;
  - O `.gitignore` não protege contra arquivos `.env`, `.env.*`, arquivos de log (`*.log`) ou certificados/chaves privadas, apresentando risco potencial em colaborações futuras.
- **Arquivos comunitários ausentes:** Inexistência de `CONTRIBUTING.md` (essencial devido à alta sofisticação da governança canônica e dos testes obrigatórios) e `SECURITY.md` (diretrizes de reporte responsável de vulnerabilidades).

### 2. Atrito de seleção em massa no Janitor e ausência de instruções visuais em checklists
- **Seleção manual exaustiva no Janitor:** Ao executar `belt dev janitor` ou navegar pelo menu interativo (`Desenvolvimento > Faxineiro de caches`), as opções de diretórios de cache descobertos vinham desmarcadas por padrão caso tivessem atividade nos últimos 30 dias (`checked = not c.is_active`). Em árvores de projetos com centenas ou milhares de pastas efêmeras acumuladas, a necessidade de marcar item por item torna a limpeza inviável na prática. O comportamento esperado é aproximar-se do `Git-Tidy`, onde todas as opções elegíveis já vêm marcadas por padrão (`checked=True`).
- **Instruções visuais omitidas:** Como a função `menu_options()` suprime a instrução nativa do Questionary (`"instruction": " "`), o usuário não recebe uma indicação visual padronizada e explícita sobre como operar caixas de seleção múltipla (`checkbox`).

## Contexto e evidências

- **Baseline técnico:** Revisão `cb13947f87495b9bf8f2ca83c44d6be2ac0a2cae` na branch `main`.
- **Decisão humana explícita (2026-10-21):**
  - Manter o padrão universal de terminal para seleção com a **Barra de Espaço** (`<Espaço>`), aproveitando o suporte nativo do Questionary para `a` (alternar/marcar todos) e `Enter` (confirmar);
  - **Restrição mandatória:** **NÃO incluir Badge de Status do CI** no README.
- **Evidências de código:**
  - `src/utility_belt/ui/dev_menu.py` (linha 60): `checked=not c.is_active` desmarca caches recentes;
  - `src/utility_belt/ui/dev_menu.py` (linha 145): `checked=True` é adotado no Git-Tidy para seleção automática;
  - `src/utility_belt/cli.py` (linha 31): `app.add_typer(dev_app, name="dev")` implementado, porém ausente no README;
  - `src/utility_belt/menu.py` (linha 49): opção `[4] Desenvolvimento` presente na TUI real, divergindo do README;
  - Ausência dos arquivos `LICENSE`, `CONTRIBUTING.md` e `SECURITY.md` constatada via `git ls-files`.

## Resultado desejado

1. **Repositório Público Pronto e Protegido:**
   - Adição do arquivo `LICENSE` adotando licença de código aberto permissiva (recomendada: MIT);
   - Criação de `CONTRIBUTING.md` orientando sobre o ambiente virtual (`uv`), gates de qualidade (`pytest`, `ruff`, `validate_governance.py`) e padrão de PRs/commits;
   - Criação de `SECURITY.md` estabelecendo política de reporte confidencial;
   - Atualização do `pyproject.toml` com licença formal, `project.urls`, `classifiers` e `keywords`;
   - Blindagem do `.gitignore` com exclusão de `.env*`, `*.log`, `*.pem`, `*.key`.
2. **README.md Alinhado e Completo:**
   - Documentação completa da CLI de desenvolvimento (`belt dev janitor`, `belt dev git-tidy`) e seus parâmetros (`--dry-run`, caminhos customizados);
   - Correção da descrição do menu interativo TUI (destacando a opção 4 - Desenvolvimento);
   - Correção da seção de licença referenciando o arquivo `LICENSE`;
   - Adição de badges informativas (versão atual `v0.4.1`, Python `3.11+`, licença MIT) — **sem a badge de status do CI**.
3. **Janitor Eficiente com Pré-seleção Total:**
   - No fluxo interativo do Janitor (`run_janitor_flow`), todas as opções descobertas são inicializadas com `checked=True`;
   - O usuário pode prosseguir imediatamente com a exclusão de todos os caches pressionando `Enter` e confirmando no prompt de segurança, ou desmarcar seletivamente exceções com a Barra de Espaço;
   - Preservação da confirmação explícita (`questionary.confirm`, `default=False`) exibindo a contagem e total de bytes antes de qualquer exclusão destrutiva.
4. **Instruções Visuais Padronizadas:**
   - Inclusão de legenda clara nos prompts de seleção múltipla do módulo de desenvolvimento:  
     `"[Espaço] Marcar/Desmarcar · [a] Todos · [Enter] Confirmar · [Ctrl+C] Cancelar"`.

## Hipóteses

- A adoção da licença MIT confere segurança jurídica completa e alinha o projeto às melhores práticas de código aberto permissivo.
- A pré-seleção total (`checked=True`) no Janitor elimina o maior gargalo de usabilidade relatado em diretórios com múltiplos projetos, sem reduzir a segurança operacional, pois o gate de confirmação continua exigindo validação humana antes da remoção em disco.
- Manter a Barra de Espaço e os atalhos nativos (`a`, `i`) com legenda visual evidente é mais robusto e intuitivo do que customizar artificialmente o evento da tecla `Tab`.

## Alternativas

### Quanto ao escopo do ciclo:
1. **Abordagem Integrada (Escolhida):** Consolidar a preparação para repositório público e o aperfeiçoamento do Janitor no Ciclo `011`, permitindo que o repositório se torne público já com a experiência de desenvolvimento polida.
2. **Abordagem Dividida em Dois Ciclos:** Realizar um ciclo puramente documental para a publicação e outro funcional para o Janitor. Rejeitada para atender prontamente à expectativa do responsável de unificar as melhorias na próxima entrega.

### Quanto às badges do README:
1. **Badges Completas (com CI):** Descartada expressamente por instrução do responsável.
2. **Badges Selecionadas (sem CI, Escolhida):** Exibir apenas versão estável, versão mínima do Python e licença.

### Quanto ao atalho de seleção:
1. **Barra de Espaço Nativamente Apoiada (Escolhida):** Padrão do Questionary com legenda explícita na tela (`[Espaço] Marcar/Desmarcar · [a] Todos`).
2. **Sobrecarga da Tecla Tab:** Rejeitada para evitar conflito com convenções de acessibilidade de terminal e foco de janelas.

## Riscos e restrições

- **Risco de exclusão inadvertida no Janitor:** Com todos os caches marcados por padrão, um usuário distraído pode excluir uma pasta desejada. **Mitigação:** Manter a pergunta final de confirmação com valor padrão estritamente negativo (`default=False`) e exibição destacada do volume total liberado.
- **Restrição de CI no README:** É imperativo que a redação do README não introduza a badge de CI nem nos rascunhos nem no artefato final.
- **Regras de integridade de governança:** Quaisquer novos arquivos de documentação (`CONTRIBUTING.md`, `SECURITY.md`) ou alterações em templates devem passar com 100% de sucesso em `python scripts/validate_governance.py`.

## Perguntas em aberto

- O e-mail de contato do mantenedor deve ser exibido em `pyproject.toml` e `SECURITY.md` ou devemos orientar o uso exclusivo de canais do GitHub (Issues / Private Vulnerability Reporting)? (Recomendação: usar o canal nativo do GitHub para preservar privacidade).
- Confirmação formal da adoção da licença MIT.

## Fora do escopo

- Publicação do pacote no índice PyPI (a distribuição permanece baseada em Git e `uv tool install`).
- Adição de novas ferramentas ou linguagens monitoradas no Janitor além do catálogo já coberto por `DEFAULT_TARGET_DIRS`.
- Remapeamento de bindings internos do Prompt-Toolkit para a tecla Tab.

## Critérios para iniciar o planejamento

- Aprovação humana deste artefato de ideação pelo responsável.
- Confirmação da licença sugerida (MIT) e do tratamento de contato.

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+011+idear+preparacao-repositorio-publico-melhorias-janitor+cb13947`
- `identity_source`: `EuThiagoAndrade/utility-belt + 011 + idear + preparacao-repositorio-publico-melhorias-janitor + cb13947`
- `effect_class`: `local_mutation`
- `state_before`: Repositório com maturidade técnica, porém sem arquivos canônicos de publicação aberta (LICENSE, CONTRIBUTING, SECURITY), README desatualizado sem citar `belt dev`, Janitor exigindo marcação manual de caches e ausência de legendas visuais nos checklists.
- `state_after`: Ideação do Ciclo 011 registrada, detalhando o problema, contexto, decisão de manter Barra de Espaço, veto explícito à badge de CI, arquitetura do Janitor com `checked=True` e requisitos para abertura pública.
- `next_transition`: `ideia -> rascunho de plano`, condicionada à aprovação humana.
- `preconditions`: Contexto compreendido, baseline estável e diretrizes fornecidas pelo responsável.
- `authority`: Responsável (interação em 2026-10-21).
- `evidence`: `_project/ideations/011_preparacao_repositorio_publico_e_melhorias_janitor.md`, `src/utility_belt/ui/dev_menu.py`, `README.md`, `pyproject.toml`.
- `acceptance`: Fatos e hipóteses separados, alternativas ponderadas, veto de badge de CI respeitado e próximo workflow indicado conforme `.agent/templates/ideacao.md`.
- `blockers`: nenhum para a fase de ideação.
- `result`: `executed`
- `next_workflow_recommended`: `rascunhar_plano`
- `next_workflow_authorized`: nenhum (aguardando aprovação humana desta ideação).
- `actions_prohibited`: Criar plano, issues, implementar código ou publicar PRs sem autorização explícita posterior.
- `rejection_rule`: O receptor recusa handoff ausente, incompatível, contraditório ou sem autoridade explícita.
- `logical_key`: `EuThiagoAndrade/utility-belt+011+idear+preparacao-repositorio-publico-melhorias-janitor+cb13947`
- `check_before_mutation`: Ciclo 011 livre para ideação em `_project/cycles.md`.
- `reconcile_existing`: Atualizar esta ideação caso surjam novos apontamentos sem alterar o número do ciclo.
- `ambiguous_state`: Parar e solicitar intervenção humana caso haja divergência de contexto ou número de ciclo.
