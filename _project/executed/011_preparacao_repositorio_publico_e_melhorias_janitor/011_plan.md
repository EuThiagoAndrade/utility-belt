# Plano de Implementação — Preparação para Repositório Público e Aperfeiçoamento do Janitor

> **Ciclo:** `011`
> **Status:** `Concluído`
> **Versão:** `v1`
> **Data de criação:** 2026-10-21
> **Última atualização:** 2026-10-21
> **Tipo:** `feature`
> **Prioridade:** `P1`
> **Revisão formal:** `Concluída`
> **Veredito da revisão:** `APTO COM RESSALVAS`
> **Aprovação humana pós-revisão:** `Aprovada em 2026-10-21`

## Objetivo

Preparar o repositório `utility-belt` para abertura pública no GitHub com conformidade jurídica e comunitária completa (arquivo `LICENSE` MIT, documentação de comunidade `CONTRIBUTING.md` e `SECURITY.md`, metadados de empacotamento no `pyproject.toml`, blindagem do `.gitignore` e atualização abrangente do `README.md` incluindo o módulo `belt dev` e correções de menus, sem badge de status do CI), além de eliminar o atrito de seleção manual no `Janitor` (`belt dev janitor`) fazendo com que todos os caches descobertos venham pré-selecionados por padrão (`checked=True`) com legendas visuais claras de navegação nos checklists interativos.

## Contexto e baseline

- **Baseline técnico:** Commit `cb13947f87495b9bf8f2ca83c44d6be2ac0a2cae` na branch `main`.
- **Ideação aprovada:** `_project/ideations/011_preparacao_repositorio_publico_e_melhorias_janitor.md` (aprovada pelo responsável em 2026-10-21).
- **Decisões humanas consolidadas:**
  - Manter o padrão universal de terminal para checklists utilizando a **Barra de Espaço (`<Espaço>`)** para alternar seleção, a tecla `a` para selecionar/deselecionar todos e `Enter` para confirmar.
  - **Restrição mandatória:** **NÃO incluir Badge de Status do CI** no README.
- **Situação observada no código e documentação:**
  1. *Ausência de Licença:* Não há arquivo `LICENSE` no repositório nem campo `license` em `pyproject.toml`.
  2. *Defasagem do README:* O `README.md` não cita o módulo `belt dev` (adicionado nos ciclos 009 e 010) e descreve o menu com apenas 4 opções em vez de 5.
  3. *Atrito no Janitor:* Em `src/utility_belt/ui/dev_menu.py:60`, a expressão `checked=not c.is_active` desmarca pastas ativas nos últimos 30 dias, forçando o usuário a marcar dezenas de itens manualmente.
  4. *Legendas visuais ausentes:* As telas de checklist não exibem para o usuário os atalhos de marcação (`Espaço`, `a`, `Enter`, `Ctrl+C`).

## Escopo

### Dentro do escopo

1. **Aperfeiçoamento do Janitor (`src/utility_belt/ui/dev_menu.py`)**:
   - Inicializar todos os diretórios de cache encontrados com `checked=True` em `run_janitor_flow()`.
   - Manter a confirmação final de segurança (`questionary.confirm`) com `default=False` antes de qualquer deleção física.
   - Padronizar as mensagens de prompt de todos os checklists do menu Desenvolvimento (`run_janitor_flow`, `run_git_tidy_local_flow`, `run_git_tidy_remote_flow`) incluindo a legenda explícita:  
     `"([Espaço] Marcar/Desmarcar · [a] Todos · [Enter] Confirmar)"`.
2. **Conformidade Jurídica e Metadados do Repositório**:
   - Criação do arquivo `LICENSE` com texto integral da licença MIT atribuída a Thiago Andrade (2026).
   - Atualização de `pyproject.toml`:
     - Declarar `license = "MIT"` (compatível com Hatchling).
     - Adicionar tabela `[project.urls]` com links para Homepage, Repository, Issues e Changelog.
     - Adicionar `classifiers` oficiais do PyPI (Ambiente de console, OS Windows/Linux, Python 3.11+, Licença OSI).
     - Adicionar lista de `keywords` para busca e indexação.
   - Atualização defensiva de `.gitignore`:
     - Adicionar padrões para arquivos de ambiente (`.env`, `.env.*`, `*.local`), logs (`*.log`), e chaves/certificados (`*.pem`, `*.key`).
3. **Padrões da Comunidade GitHub**:
   - Criação de `CONTRIBUTING.md`:
     - Guia de setup com `uv sync`.
     - Instruções dos comandos de teste e qualidade (`pytest`, `ruff check`, `validate_governance.py`).
     - Explicação da convenção de branches e commits do projeto (`feat(issue-N): ...`).
   - Criação de `SECURITY.md`:
     - Procedimentos para reporte confidencial de vulnerabilidades utilizando o recurso nativo de *Private Vulnerability Reporting* do GitHub, preservando a segurança dos usuários.
4. **Atualização Completa do `README.md`**:
   - Adicionar badges de versão (`v0.4.1`), versão mínima do Python (`3.11+`) e licença (`MIT`) no topo — **sem a badge de status do CI**.
   - Atualizar a seção *Recursos Principais* incluindo o módulo **Ferramentas de Desenvolvimento (`belt dev`)**.
   - Atualizar a seção *Experiência Interativa (TUI)* corrigindo o menu principal (opções `[4] Desenvolvimento` e `[5] Sistema`) e incluindo `belt dev menu`.
   - Adicionar subseção completa na *Referência da CLI* documentando `belt dev janitor` e `belt dev git-tidy` com exemplos práticos, parâmetros (`--dry-run`, caminhos personalizados) e códigos de retorno.
   - Atualizar a seção *Licença* apontando formalmente para o arquivo `LICENSE` MIT.
5. **Testes Automatizados e Auditoria de Governança**:
   - Testes unitários para validar a pré-seleção (`checked=True`) no Janitor mesmo com caches recentes.
   - Testes garantindo que as mensagens de prompt em `dev_menu.py` possuem as legendas padronizadas.
   - Execução com 100% de sucesso da suíte de testes (`pytest`), linting (`ruff`), validação canônica (`validate_governance.py`) e integridade git (`git diff --check`).

### Fora do escopo

- Badge de status do CI no README (vetada explicitamente pelo responsável).
- Publicação do pacote no índice público PyPI (distribuição via Git e `uv tool` mantida).
- Alteração na lógica de busca e poda de diretórios do `janitor.py` (a poda e cálculo continuam íntegros).
- Alteração na lógica de identificação de branches mergeadas do `git_tidy.py`.
- Remapeamento interno de eventos do teclado para que a tecla `Tab` funcione como seleção.

## Decisões e autoridades

- **Decisão de Usabilidade do Janitor:** Pré-selecionar 100% dos caches descobertos (`checked=True`), alinhando o comportamento ao Git-Tidy e diminuindo o atrito em repositórios com muitos caches efêmeros.
- **Decisão de Navegação e Teclado:** Utilizar a Barra de Espaço (`<Espaço>`) como padrão universal de terminal, apoiando-se nos atalhos nativos do Questionary (`a` para todos, `Enter` para confirmar) e exibindo a instrução de forma evidente em tela.
- **Decisão de Licenciamento:** Adoção da licença permissiva MIT, padrão na indústria e totalmente compatível com as dependências do Utility Belt.
- **Autoridades:** `.agent/ai_behavior.md`, `_project/README.md`, `_project/cycles.md`, e aprovação humana registrada em 2026-10-21.

## Estratégia de testes

1. **Testes de UI / Interatividade (`tests/test_ui_experience.py` e/ou `tests/test_dev_cli.py`)**:
   - Simular varredura do Janitor com instâncias de `DiscoveredCache` ativas (`is_active=True`) e inativas (`is_active=False`).
   - Inspecionar a lista de `choices` gerada para `questionary.checkbox` e validar que todas possuem `checked=True`.
   - Verificar que os textos de mensagem dos prompts de checklist contêm a legenda `[Espaço] Marcar/Desmarcar`.
2. **Auditoria de Governança (`scripts/validate_governance.py`)**:
   - Garantir que a suíte de validação reconhece a nova estrutura documental e passa sem nenhum aviso ou falha.
3. **Gates Mínimos Obrigatórios**:
   ```bash
   uv run python scripts/validate_governance.py
   uv run ruff check
   uv run pytest
   git diff --check
   ```

## Itens de implementação

### Item 1 — Aperfeiçoamento do Janitor e Legendas de Checklists em `dev_menu.py`

**Contexto:**
Atualmente os caches ativos nos últimos 30 dias vêm desmarcados por padrão, obrigando o usuário a marcar dezenas de itens manualmente. Além disso, as telas de checklist não exibem instruções visuais claras de operação.

**Ação técnica:**
- Em `src/utility_belt/ui/dev_menu.py`:
  - No fluxo `run_janitor_flow()`, alterar a construção de `choices` para que `checked=True` seja atribuído a todos os itens:
    ```python
    choices = [
        questionary.Choice(
            f"{c.target_name} ({c.formatted_size}) — {c.formatted_time_ago}\n    {c.path}",
            value=c,
            checked=True,
        )
        for c in caches
    ]
    ```
  - Atualizar os textos de prompt de `run_janitor_flow`, `run_git_tidy_local_flow` e `run_git_tidy_remote_flow` incluindo a legenda visual explícita:
    - `"Selecione as pastas para exclusão ([Espaço] Marcar/Desmarcar · [a] Todos · [Enter] Confirmar):"`
    - `"Selecione as branches locais para remoção ([Espaço] Marcar/Desmarcar · [a] Todos · [Enter] Confirmar):"`
    - `"Selecione as branches remotas a excluir no origin ([Espaço] Marcar/Desmarcar · [a] Todos · [Enter] Confirmar):"`
- Em `tests/test_ui_experience.py`:
  - Adicionar testes verificando que todos os caches gerados possuem `checked=True` e que a mensagem do prompt contém a legenda.

**Critérios de aceite:**
- [ ] O Janitor exibe todas as opções descobertas pré-selecionadas por padrão.
- [ ] O prompt do Janitor e do Git-Tidy contém a legenda visual padronizada.
- [ ] A confirmação final (`questionary.confirm`) com `default=False` permanece protegendo a exclusão.
- [ ] Testes automatizados cobrem a pré-seleção e a mensagem do prompt.

---

### Item 2 — Conformidade de Repositório Público: Licença, Metadados e `.gitignore`

**Contexto:**
A ausência de `LICENSE` bloqueia o uso comunitário legítimo, o `pyproject.toml` carece de metadados essenciais e o `.gitignore` necessita de blindagem contra credenciais ou logs acidentais.

**Ação técnica:**
- Criar `LICENSE` na raiz com o texto completo da licença MIT para Thiago Andrade (2026).
- Atualizar `pyproject.toml`:
  - Adicionar `license = "MIT"`.
  - Adicionar `[project.urls]` com `Homepage`, `Repository`, `Issues` e `Changelog`.
  - Adicionar `classifiers` e `keywords`.
- Atualizar `.gitignore`:
  - Adicionar regras para `.env*`, `*.local`, `*.log`, `*.pem`, `*.key`.

**Critérios de aceite:**
- [ ] Arquivo `LICENSE` MIT presente na raiz do repositório.
- [ ] `pyproject.toml` declara `license`, `urls`, `classifiers` e `keywords` válidos para o `hatchling`.
- [ ] `uv build` e `uv lock` executam sem erros com os novos metadados.
- [ ] `.gitignore` contém proteções contra variáveis de ambiente e arquivos sensíveis.

---

### Item 3 — Documentação Comunitária (`CONTRIBUTING.md` e `SECURITY.md`)

**Contexto:**
Colaboradores externos e pesquisadores de segurança precisam de diretrizes claras sobre como submeter melhorias e reportar vulnerabilidades.

**Ação técnica:**
- Criar `CONTRIBUTING.md`:
  - Descrever o fluxo de trabalho local com `uv sync`.
  - Relacionar os comandos de teste (`pytest`, `ruff`, `validate_governance.py`).
  - Instruir sobre a convenção de commits convencionais e abertura de issues/PRs.
- Criar `SECURITY.md`:
  - Estabelecer a política de divulgação responsável via GitHub Private Vulnerability Reporting ou canal confidencial.

**Critérios de aceite:**
- [ ] `CONTRIBUTING.md` fornece instruções claras e reprodutíveis para desenvolvedores.
- [ ] `SECURITY.md` define claramente o fluxo seguro de reporte.
- [ ] Links entre arquivos preservados e consistentes com o repositório.

---

### Item 4 — Atualização Abrangente do `README.md`

**Contexto:**
O `README.md` é a vitrine principal do repositório público e precisa refletir com fidelidade 100% dos comandos disponíveis e da interface gráfica.

**Ação técnica:**
- No início do `README.md`:
  - Adicionar badges de versão (`v0.4.1`), Python (`3.11+`) e licença (`MIT`) — **sem a badge de status do CI**.
- Na seção *Recursos Principais*:
  - Adicionar o bullet com as ferramentas de desenvolvimento (`belt dev`): Janitor e Git-Tidy.
- Na seção *Experiência Interativa (TUI)*:
  - Adicionar `belt dev menu` e `belt dev` na lista de atalhos diretos.
  - Atualizar o parágrafo descritivo do menu principal: explicitar as opções Restic, Docker, Markdown, Desenvolvimento e Sistema.
- Na seção *Referência da CLI*:
  - Criar subseção completa `### Ferramentas de Desenvolvimento (belt dev)` documentando:
    - `belt dev janitor [CAMINHO] [--dry-run]`
    - `belt dev git-tidy [--dry-run]`
    - Detalhes de comportamento, segurança e limpeza.
- Na seção *Licença*:
  - Indicar explicitamente a licença MIT e fornecer link para o arquivo `LICENSE`.

**Critérios de aceite:**
- [ ] O `README.md` documenta integralmente o módulo `belt dev` e suas ferramentas.
- [ ] As opções descritas da TUI correspondem rigorosamente ao menu do produto real.
- [ ] A seção de licença cita a licença MIT e referencia o arquivo `LICENSE`.
- [ ] Nenhuma badge de CI está presente no README.
- [ ] Links no README são válidos e funcionais.

---

## Arquivos afetados

| Arquivo | Natureza da alteração |
| :-- | :-- |
| `src/utility_belt/ui/dev_menu.py` | Modificação: `checked=True` no Janitor e legendas nos prompts |
| `LICENSE` | Criação: Licença MIT |
| `pyproject.toml` | Modificação: Licença, URLs, classifiers e keywords |
| `.gitignore` | Modificação: Inclusão de `.env*`, `*.log`, certs |
| `CONTRIBUTING.md` | Criação: Guia de contribuição e ambiente |
| `SECURITY.md` | Criação: Política de segurança e reporte |
| `README.md` | Modificação: Módulo `belt dev`, menus, licença e badges (sem CI) |
| `tests/test_ui_experience.py` | Modificação/Adição: Testes de pré-seleção e legendas |
| `_project/cycles.md` | Modificação: Registro de estado do ciclo 011 |

## Decomposição em issues e PRs

Para manter os princípios de rastreabilidade e simplicidade de governança, o ciclo será decomposto em duas entregas modulares e complementares:

1. **Issue 1 (`feature`) — Aperfeiçoamento do Janitor e legendas de checklist**
   - **Issue criada:** [#36](https://github.com/EuThiagoAndrade/utility-belt/issues/36)
   - **Escopo:** Item 1 e testes automatizados correspondentes.
   - **Branch sugerida:** `feature/issue-36`
   - **Commit esperado:** `feat(issue-36): pre-selecionar caches no janitor e padronizar legendas de checklist`
   - **PR 1:** Submetida em [#38](https://github.com/EuThiagoAndrade/utility-belt/pull/38) (checks verdes)

2. **Issue 2 (`chore`) — Preparação para repositório público**
   - **Issue criada:** [#37](https://github.com/EuThiagoAndrade/utility-belt/issues/37)
   - **Escopo:** Itens 2, 3 e 4 (LICENSE, pyproject.toml, .gitignore, CONTRIBUTING, SECURITY e README.md).
   - **Branch sugerida:** `chore/issue-37` (conforme Ressalva R1)
   - **Commit esperado:** `chore(issue-37): preparar repositorio publico com licenca, metadados, comunidade e readme`
   - **PR 2:** Submetida em [#39](https://github.com/EuThiagoAndrade/utility-belt/pull/39) (checks verdes)

## Dependências e blockers

- **Dependências internas:** A Issue 1 deve ser concluída antes ou em paralelo à Issue 2, pois a Issue 2 atualizará o README documentando a experiência já polida do Janitor.
- **Blockers atuais:** Nenhum. Todas as bibliotecas necessárias (`questionary`, `typer`) já estão no ambiente.

## Riscos, suposições e rollback

- **Risco:** Com todos os caches marcados por padrão, exclusões não intencionais poderiam ocorrer caso o usuário confirme inadvertidamente.
  - *Mitigação:* A confirmação final por `questionary.confirm` continua tendo valor padrão negativo (`default=False`), exigindo que o usuário digite `y` ou selecione explicitamente "Sim" após ver o total de bytes e contagem de pastas.
- **Suposição:** A Barra de Espaço funciona igualmente no Windows Terminal, PowerShell, CMD e terminais Linux (confirmado pelas especificações do Questionary e Prompt-Toolkit).
- **Rollback:** Caso alguma alteração visual não agrade, reversão atômica via `git revert` na branch da issue correspondente.

## Sequência recomendada

1. Submeter este plano para a revisão formal (`.agent/workflows/revisar_plano.md`).
2. Aguardar veredito e aprovação humana pós-revisão.
3. Criar as issues no GitHub e vincular as branches correspondentes.
4. Implementar a Issue 1 (Janitor `checked=True` + legendas + testes) e abrir PR.
5. Implementar a Issue 2 (LICENSE + pyproject.toml + .gitignore + CONTRIBUTING + SECURITY + README) e abrir PR.
6. Integrar as entregas após checks aprovados e autorização do responsável.
7. Realizar a PR de encerramento documental consolidando o ciclo em `_project/executed/011_.../`.

## Referências

- Ideação aprovada: `_project/ideations/011_preparacao_repositorio_publico_e_melhorias_janitor.md`
- Código do Janitor TUI: `src/utility_belt/ui/dev_menu.py`
- Padrão de opções de tela: `src/utility_belt/ui/screen.py`
- Validador canônico: `scripts/validate_governance.py`

## Rastreabilidade

| Campo | Valor |
| :-- | :-- |
| Issue(s) | [#36](https://github.com/EuThiagoAndrade/utility-belt/issues/36), [#37](https://github.com/EuThiagoAndrade/utility-belt/issues/37) |
| PR(s) | [#38](https://github.com/EuThiagoAndrade/utility-belt/pull/38) (Issue #36), [#39](https://github.com/EuThiagoAndrade/utility-belt/pull/39) (Issue #37) |
| Branch(es) | `feature/issue-36`, `chore/issue-37` (previstas) |
| `handoff_schema_version` | `1` |
| `handoff_id` | `EuThiagoAndrade/utility-belt+011+rascunhar_plano+preparacao-repositorio-publico-melhorias-janitor+cb13947` |
| Destino após conclusão | `_project/executed/011_preparacao_repositorio_publico_e_melhorias_janitor/011_plan.md` |

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+011+rascunhar_plano+preparacao-repositorio-publico-melhorias-janitor+cb13947`
- `identity_source`: `EuThiagoAndrade/utility-belt + 011 + rascunhar_plano + preparacao-repositorio-publico-melhorias-janitor + cb13947`
- `effect_class`: `local_mutation`
- `state_before`: Ideação do Ciclo 011 aprovada pelo responsável; plano ainda não redigido.
- `state_after`: Rascunho completo do plano de implementação redigido em conformidade com o template e pronto para auditoria formal de revisão.
- `next_transition`: `rascunho -> revisão formal`
- `preconditions`: Ideação válida, objetivo delimitado, restrições humanas contempladas e estrutura documental conforme autoridades.
- `authority`: Responsável (aprovação da ideação em 2026-10-21).
- `evidence`: `_project/drafts/011_preparacao_repositorio_publico_e_melhorias_janitor/011_plan.md`, `_project/ideations/011_preparacao_repositorio_publico_e_melhorias_janitor.md`.
- `acceptance`: Plano completo, campos do template preenchidos, não-objetivos definidos e veto de badge de CI respeitado.
- `blockers`: Nenhum.
- `result`: `executed`
- `next_workflow_recommended`: `revisar_plano` (`.agent/workflows/revisar_plano.md`)
- `next_workflow_authorized`: Nenhum (aguardando autorização humana para iniciar a revisão).
- `actions_prohibited`: Promover o plano para `Aprovado`, criar issues, implementar código ou abrir PR sem revisão formal e aprovação humana pós-veredito.
- `rejection_rule`: O receptor recusa handoff ausente, incompatível, contraditório ou com status promovido prematuramente.
- `logical_key`: `EuThiagoAndrade/utility-belt+011+rascunhar_plano+preparacao-repositorio-publico-melhorias-janitor+cb13947`
- `check_before_mutation`: Diretório `_project/drafts/011_preparacao_repositorio_publico_e_melhorias_janitor/` livre de planos anteriores conflitantes.
- `reconcile_existing`: Reutilizar este rascunho sem criar novos planos paralelos para o ciclo 011.
- `ambiguous_state`: Parar e solicitar intervenção humana caso haja conflito de revisão ou identidade.

## Revisão crítica

- **Data:** 2026-10-21
- **Versão revisada:** `v1` (baseline `cb13947`)
- **Veredito:** `APTO COM RESSALVAS`
- **Bloqueios remanescentes:** nenhum.
- **Aprovação humana pós-revisão:** `Aprovada em 2026-10-21`
- **Correções materiais:** nenhuma exigida em nova rodada de planejamento; ressalvas R1–R5 vinculantes para a criação de issues e implementação.
- **Ressalvas:** R1 a R5 (detalhadas abaixo), a observar obrigatoriamente na criação das issues e na implementação sem necessidade de nova rodada de revisão.

### Aprovação humana pós-revisão

- **Data:** 2026-10-21, posterior ao parecer `APTO COM RESSALVAS` da `v1`.
- **Autoridade:** responsável humano do repositório, em chat: `"aprovo o plano 011 (v1) com as ressalvas R1–R5"`.
- **Versão aprovada:** `v1` (baseline `cb13947`), incluindo as ressalvas R1–R5 como condições obrigatórias da criação de issues e da implementação.
- **Transição:** `Em Revisão` → `Aprovado`.
- **Não autorizado por esta aprovação:** publicação documental remota do plano, criação de issues no GitHub, implementação de código, abertura de PR ou integração; cada etapa exige autorização explícita.
- **Próximo gate:** publicação documental do plano (`chore/cycle-011-plan`) e criação das issues via `.agent/workflows/criar_issues.md`, mediante autorização explícita.

### Parecer v1 (2026-10-21)

#### Evidências verificadas

- Template `.agent/templates/plano_implementacao.md` lido e conferido: todas as seções obrigatórias, metadados de cabeçalho, tabela de rastreabilidade e contrato canônico de handoff (`handoff_schema_version: 1`) estão presentes e bem formados.
- `git rev-parse HEAD` = `cb13947f87495b9bf8f2ca83c44d6be2ac0a2cae`, confirmando o baseline declarado no plano e na ideação.
- Código-fonte real inspecionado:
  - `src/utility_belt/ui/dev_menu.py:60`: confirmado `checked=not c.is_active` no `run_janitor_flow()`, em contraste com `checked=True` nas linhas `145` e `203` do Git-Tidy.
  - `src/utility_belt/ui/dev_menu.py:68,152,210`: confirmados os três prompts de `questionary.checkbox` que receberão a legenda visual padronizada.
  - `src/utility_belt/menu.py:49`: confirmada a opção `[4] Desenvolvimento` no menu principal, ausente na descrição atual de `README.md:77`.
  - `src/utility_belt/adapters/dev.py`: confirmados os subcomandos `janitor`, `git-tidy` e `menu` e suas flags (`--dry-run`, `--days/-d`, `--yes/-y`, `--remote`, `--all`).
  - `pyproject.toml`, `.gitignore` e `README.md`: confirmadas as lacunas descritas no contexto do plano e a ausência de `LICENSE`, `CONTRIBUTING.md` e `SECURITY.md` na raiz.
- Gates verificados na baseline (`cb13947`):
  - `uv run python scripts/validate_governance.py` → `41 verificações | 41 OK | 0 Avisos | 0 Falhas`.
  - `uv run ruff check` → `All checks passed!`.
  - `uv run pytest -q` → `250 passed, 36 skipped`.

#### Bloqueadores

- Nenhum.

#### Ressalvas (vinculantes para a execução após aprovação)

- **R1 — Nomenclatura canônica de branch e commit da Issue 2 (`_project/README.md` e `.agent/ai_behavior.md`).** Na seção "Decomposição em issues e PRs", a Issue 2 sugere branch `docs/issue-Y` e commit `docs(issue-Y): ...`. Contudo, `_project/README.md` (seção "Branches e commits") estabelece que branches de issue usam exclusivamente `feature/issue-N`, `fix/issue-N` ou `chore/issue-N`, e commits de issue usam `feat(issue-N):`, `fix(issue-N):` ou `chore(issue-N):` (sendo `docs(cycle-NNN):` reservado à documentação de ciclo). Na criação e implementação da Issue 2, adotar tipo `chore`, branch `chore/issue-Y` e commit `chore(issue-Y): preparar repositorio publico com licenca, metadados, comunidade e readme`.
- **R2 — Isolamento da PR documental do ciclo (`chore/cycle-011-plan`) e ordem de integração entre Issue 1 e Issue 2.** Os artefatos de governança do ciclo (`_project/cycles.md`, `_project/ideations/011_...md` e este plano) encontram-se modificados/não rastreados na árvore local. Conforme `_project/README.md` ("Transições canônicas do plano") e `.agent/ai_behavior.md` ("Mudanças cirúrgicas"), após a aprovação humana pós-revisão, a publicação documental do ciclo deve ocorrer em branch própria (`chore/cycle-011-plan`), sem vazar no staging das branches `feature/issue-X` ou `chore/issue-Y`. Adicionalmente, como a Issue 1 (`feat(issue-X): ...`) dispara incremento automático de versão (`v0.4.1` → `v0.5.0`) via `scripts/release.py` ao ser integrada na `main`, a Issue 2 deve preferir badge dinâmica de release do GitHub (ex.: `https://img.shields.io/github/v/release/EuThiagoAndrade/utility-belt`, respeitando estritamente o veto à badge de CI) ou ser integrada após a Issue 1 refletindo a versão vigente, evitando que o `README.md` nasça com versão estática defasada.
- **R3 — Inclusão de `/LICENSE` no alvo `sdist` do `pyproject.toml`.** Em `pyproject.toml:37-43`, `[tool.hatch.build.targets.sdist]` declara uma lista explícita `include = ["/src", "/tests", "/README.md", "/pyproject.toml"]`. Ao implementar o Item 2, adicionar `"/LICENSE"` nessa lista (ou configurar `license-files = ["LICENSE"]`) para garantir que `uv build` empacote o arquivo `LICENSE` também na distribuição de código-fonte (`sdist`).
- **R4 — String canônica da legenda de checklist (Item 1) e completude das flags de `belt dev` no `README.md` (Item 4).**
  - No Item 1, o sufixo canônico a aplicar nos três prompts de `dev_menu.py` e a aferir em `tests/test_ui_experience.py` é exatamente `"([Espaço] Marcar/Desmarcar · [a] Todos · [Enter] Confirmar):"` (prevalecendo sobre a menção descritiva a `Ctrl+C` na linha 29 do contexto).
  - No Item 4, a seção `### Ferramentas de Desenvolvimento (belt dev)` do `README.md` deve documentar todas as opções reais expostas por `src/utility_belt/adapters/dev.py`: `belt dev janitor [CAMINHO] [--dry-run] [--days/-d DIAS] [--yes/-y]`, `belt dev git-tidy [--dry-run] [--remote] [--all] [--yes/-y]`, `belt dev menu`, códigos de saída (`0`, `1`, `2`), IDs de catálogo (`dev.janitor`, `dev.git-tidy`) e verificação `belt doctor git`.
- **R5 — Execução completa dos 5 gates mínimos.** Na validação de cada entrega (seção "Estratégia de testes"), executar e registrar na task os 5 comandos canônicos de `_project/README.md`, incluindo `git status --short` além de `validate_governance.py`, `ruff check`, `pytest` e `git diff --check`.

#### Itens atendidos

- Objetivo e escopo claramente delimitados e aderentes à ideação `011` aprovada pelo responsável.
- Restrições humanas mandatórias integralmente respeitadas: veto absoluto à badge de status do CI no `README.md` e manutenção da Barra de Espaço (`<Espaço>`) sem remapeamento da tecla `Tab`.
- Segurança operacional preservada no Janitor: apesar de `checked=True` em todos os itens descobertos, a confirmação destrutiva final (`questionary.confirm` com `default=False`) e a exibição do volume total e contagem de pastas permanecem intactas.
- Decomposição em duas entregas coesas (Issue 1 funcional/TUI com testes; Issue 2 documental/metadados/comunidade) facilita revisão cirúrgica e rollback independente.
- Compatibilidade verificada com `.agent/ai_behavior.md`, `_project/README.md` e `_project/cycles.md`.

#### Handoff da revisão v1

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+011+revisar_plano+preparacao-repositorio-publico-melhorias-janitor+cb13947/v1`
- `identity_source`: `EuThiagoAndrade/utility-belt + 011 + revisar_plano + preparacao-repositorio-publico-melhorias-janitor + cb13947/v1`
- `effect_class`: `local_mutation`
- `state_before`: plano `v1` em `Rascunho`, revisão formal `Pendente`, veredito `Pendente`, aprovação humana pós-revisão `Pendente`.
- `state_after`: plano `v1` em `Em Revisão`, revisão formal `Concluída`, parecer `APTO COM RESSALVAS` (R1–R5) registrado, aprovação humana pós-revisão `Pendente`.
- `next_transition`: `parecer -> aprovação humana pós-revisão`.
- `preconditions`: manifestação humana explícita, posterior a este parecer, aprovando o plano `v1` com as ressalvas R1–R5 (ou solicitando ajustes em uma `v2`).
- `authority`: responsável humano do repositório.
- `evidence`: `_project/drafts/011_preparacao_repositorio_publico_e_melhorias_janitor/011_plan.md` (seção `## Revisão crítica`), `src/utility_belt/ui/dev_menu.py`, `src/utility_belt/adapters/dev.py`, `pyproject.toml`, `README.md`, `uv run python scripts/validate_governance.py` (`41 OK`).
- `acceptance`: parecer técnico explícito, ressalvas R1–R5 classificadas e aprovação humana não inferida (`Aprovação humana pós-revisão: Pendente`).
- `blockers`: nenhum bloqueio técnico; aguarda decisão humana pós-revisão.
- `result`: `executed`
- `next_workflow_recommended`: após aprovação humana pós-revisão, registrar status `Aprovado`, publicar documentação do plano (`chore/cycle-011-plan`) e executar `criar_issues` (`.agent/workflows/criar_issues.md`).
- `next_workflow_authorized`: nenhum (aguardando manifestação humana pós-revisão).
- `actions_prohibited`: promover status para `Aprovado` sem manifestação humana posterior, criar issues, implementar código, abrir PR ou integrar.
- `rejection_rule`: o receptor recusa handoff que trate `APTO COM RESSALVAS` como aprovação humana consumada ou que ignore as ressalvas R1–R5.
- `logical_key`: `EuThiagoAndrade/utility-belt+011+revisar_plano+preparacao-repositorio-publico-melhorias-janitor+cb13947/v1`
- `check_before_mutation`: verificado que o plano `v1` encontrava-se em `Rascunho` e sem parecer anterior registrado.
- `reconcile_existing`: reexecução sobre a `v1` reconcilia este parecer sem duplicar seções.
- `ambiguous_state`: parar e solicitar intervenção humana caso o plano seja alterado fora do fluxo ou haja conflito de decisão.

## Pós-mortem

- **Data de conclusão:** 2026-10-21
- **Desvios:** Nenhum. A decomposição em duas entregas modulares (Issue #36 funcional/TUI e Issue #37 documental/metadados) garantiu a ordem de precedência ideal para que o incremento de versão (v0.5.0 disparado pela Issue #36) estivesse consolidado na release antes da publicação do README e documentação de comunidade da Issue #37.
- **Lições comprovadas:** A governança desacoplada e o pipeline automatizado de releases funcionam de forma previsível e robusta quando a separação semântica (`feat` vs `chore`) é respeitada no planejamento e na execução.
