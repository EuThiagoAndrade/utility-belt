# Plano de Implementação — Compatibilidade e Padronização Visual de Menus

> **Ciclo:** `010`
> **Status:** `Concluído`
> **Versão:** `v2`
> **Data de criação:** 2026-10-20
> **Última atualização:** 2026-10-20
> **Tipo:** `fix`
> **Prioridade:** `P1`
> **Revisão formal:** `Concluída`
> **Veredito da revisão:** `APTO COM RESSALVAS`
> **Aprovação humana pós-revisão:** `Aprovada em 2026-10-20`

## Objetivo

Corrigir a incompatibilidade de parâmetros entre `menu_options()` e `questionary.checkbox` que causa falha em tempo de execução (`PromptSession.__init__() got an unexpected keyword argument 'use_shortcuts'`) durante fluxos interativos de seleção múltipla (`Git-Tidy` e `Janitor`), além de padronizar a identidade visual de todos os submenus do Utility Belt inserindo a linha divisória (`menu_separator()`) antes da opção `[0]` em Markdown e Desenvolvimento.

## Contexto e baseline

- Baseline: commit `99e7e37` na branch `main`.
- Ideação: `_project/ideations/010_correcoes_e_padronizacao_menus.md`.
- No ciclo `007` (commit `c002c85`), `menu_options()` foi introduzido em `src/utility_belt/ui/screen.py` definindo `use_shortcuts: False` para desativar mapeamentos de teclado indesejados em menus de escolha única (`questionary.select`).
- No ciclo `009` (commit `f7d5e11`), novos fluxos interativos de desenvolvimento (`dev_menu.py`) passaram a utilizar `prompt(questionary.checkbox, ..., **menu_options())`.
- O componente `questionary.checkbox` não aceita o parâmetro `use_shortcuts`, repassando-o via `**kwargs` para `PromptSession` do `prompt_toolkit`, gerando exceção `TypeError`. O problema permanecia dormente em ambientes limpos devido a cláusulas de guarda quando não havia branches ou caches a remover, e a suíte não o detectou porque substitui os prompts por mocks.
- Com `questionary 2.1.1`, `questionary.select` declara `use_shortcuts: bool = False`; portanto, remover a chave de `menu_options()` preserva o comportamento atual dos menus `select` (evidência registrada na revisão `v1`).
- Adicionalmente, identificou-se inconsistência visual na apresentação dos submenus: enquanto o Menu Principal, Sistema, Restic, Docker e as telas de onboarding (`guard.py`) inserem uma linha divisória horizontal (`menu_separator()`) antes da opção `[0]`, os submenus de Markdown (`markdown_menu.py`) e Desenvolvimento (`dev_menu.py`) exibem o item `[0]` colado diretamente às opções numéricas anteriores.

## Escopo

### Dentro do escopo

1. **Saneamento das opções de menu (`src/utility_belt/ui/screen.py`)**:
   - Ajustar `menu_options()` para conter exclusivamente parâmetros universais suportados por todos os prompts do Questionary (`style`, `qmark`, `pointer`, `instruction`).
   - Adicionar guarda defensiva determinística no helper central `prompt(factory, text, **kwargs)`: descartar `use_shortcuts` quando ele não for parâmetro nomeado na assinatura da fábrica.
2. **Verificação dos fluxos de checklist em Desenvolvimento (`src/utility_belt/ui/dev_menu.py`)**:
   - Sem alteração de código para as chamadas de `questionary.checkbox`: com o item 1, `run_janitor_flow`, `run_git_tidy_local_flow` e `run_git_tidy_remote_flow` deixam de receber `use_shortcuts`. `run_git_tidy_all_flow` delega aos fluxos local e remoto e fica coberto por eles.
   - A correção é comprovada pelos testes do item 4.
3. **Padronização da linha separadora (`menu_separator()`)**:
   - Inserir `menu_separator()` antes da opção `[0] Voltar ao menu principal` em `src/utility_belt/ui/markdown_menu.py`.
   - Inserir `menu_separator()` antes da opção `[0] Voltar ao menu principal` em `src/utility_belt/ui/dev_menu.py`.
4. **Testes automatizados em `tests/test_ui_experience.py`**:
   - Compatibilidade de opções: `menu_options()` sem `use_shortcuts`; `questionary.checkbox` e `questionary.select` reais instanciados e respondidos via `prompt()`.
   - Guarda defensiva: `prompt(questionary.checkbox, ..., use_shortcuts=False)` não levanta `TypeError`.
   - Fluxos `run_janitor_flow`, `run_git_tidy_local_flow` e `run_git_tidy_remote_flow` com itens elegíveis simulados, usando `questionary.checkbox` real.
   - Estrutura de separadores dos submenus alterados (Markdown e Desenvolvimento).

### Fora do escopo

- Alterações na lógica de negócios do `git_tidy.py` (detecção de branches, execução de comandos Git).
- Alterações na lógica de descoberta e deleção de caches do `janitor.py`.
- Modificações no motor Markdown ou em dependências do `pyproject.toml`.
- Reestruturação de banners ou alteração da paleta de cores.
- Helper especializado para `questionary.select` (`select_options()` ou equivalente): o padrão `use_shortcuts=False` do Questionary já atende os menus atuais e não há consumidor concreto.
- Testes de separador para Menu Principal, Sistema, Restic, Docker e `guard.py`, que já seguem o padrão e não são alterados por este ciclo.
- `docker_menu.py:53`, que usa `questionary.checkbox` sem `menu_options()` e não é afetado pelo defeito.

## Decisões e autoridades

- **Decisão visual**: Padronizar todos os submenus para conter linha separadora (`menu_separator()`) antes da opção `[0]`, conforme solicitação e escolha do responsável em 2026-10-20.
- **Decisão arquitetural de opções**: Abordagem combinada, escolhida pelo responsável — sanear `menu_options()` na raiz compartilhada e adicionar guarda defensiva em `prompt()`.
- **Regra da guarda (v2)**: em `prompt()`, se `use_shortcuts` estiver em `kwargs` e não constar em `inspect.signature(factory).parameters`, removê-lo antes de chamar `factory`. Se a assinatura não puder ser obtida (`TypeError`/`ValueError`), os `kwargs` seguem inalterados. Nenhuma outra chave é filtrada, preservando argumentos legítimos repassados por `**kwargs` (como `input` e `output` do `prompt_toolkit`).
- **Correção pós-revisão `v1`**: `select_options()` foi retirado do escopo pela regra "Simplicidade primeiro" de `.agent/ai_behavior.md`.
- **Autoridades**: `.agent/ai_behavior.md`, `_project/README.md`, `_project/cycles.md`.

## Estratégia de testes

Todos os testes novos ficam em `tests/test_ui_experience.py`, que já reúne os contratos de navegação e apresentação dos menus. Os testes de compatibilidade não podem substituir `questionary.checkbox` por mock: usam o prompt real com `prompt_toolkit.input.create_pipe_input()` e `prompt_toolkit.output.DummyOutput()`, abordagem verificada neste ambiente durante a revisão `v1`.

- **Opções e guarda (`screen.py`)**:
  - `"use_shortcuts" not in menu_options()`.
  - `screen.prompt(questionary.checkbox, "msg", choices=["a", "b"], input=..., output=DummyOutput(), **menu_options())` com entrada `" \r"` retorna `["a"]` sem `TypeError`.
  - `screen.prompt(questionary.checkbox, ..., use_shortcuts=False, input=..., output=...)` retorna sem `TypeError` (guarda).
  - `screen.prompt(questionary.select, "msg", choices=["a", "b"], input=..., output=..., **menu_options())` com entrada `"\r"` retorna `"a"` (menus `select` preservados).
- **Fluxos do `dev_menu`** (fábrica `questionary.checkbox` real com entrada por pipe; operações de Git e disco simuladas):
  - `run_git_tidy_local_flow` com branch elegível simulada e `delete_local_branches` simulado: o checklist é respondido e a branch selecionada chega à remoção simulada.
  - `run_git_tidy_remote_flow` com branch remota elegível simulada e `delete_remote_branches` simulado: mesmo critério.
  - `run_janitor_flow` com cache elegível simulado e `delete_cache` simulado: mesmo critério.
- **Separadores**:
  - Capturar as `choices` passadas a `questionary.select` em `show_markdown_menu()` e `show_dev_menu()` e verificar que o elemento imediatamente anterior ao `Choice` de valor `exit` é uma instância de `questionary.Separator`.
- **Gates mínimos** (`_project/README.md`), executados antes da publicação e registrados na task:

  ```sh
  uv run python scripts/validate_governance.py
  uv run ruff check
  uv run pytest
  git diff --check
  git status --short
  ```

## Itens de implementação

### Item 1 — Saneamento de `menu_options()` e guarda defensiva em `prompt()`

**Contexto:**
`menu_options()` injeta `"use_shortcuts": False`. O `questionary.checkbox` não tem esse parâmetro e o repassa via `**kwargs` para `PromptSession`, gerando `TypeError`. Em `questionary.select`, o valor padrão já é `False`.

**Ação técnica:**
- Em `src/utility_belt/ui/screen.py`:
  - Remover `"use_shortcuts": False` do retorno de `menu_options()`, mantendo apenas `"qmark": ""`, `"pointer": ">"`, `"style": menu_style()` e `"instruction": " "`.
  - Em `prompt(factory, text, **kwargs)`, aplicar a regra da guarda definida em "Decisões e autoridades" antes de invocar `factory(text, **kwargs)`.

**Critérios de aceite:**
- [ ] `menu_options()` não contém a chave `use_shortcuts`.
- [ ] `prompt(questionary.checkbox, ...)` com `**menu_options()` é respondido via entrada por pipe sem `TypeError`.
- [ ] `prompt(questionary.checkbox, ..., use_shortcuts=False)` é respondido sem `TypeError`.
- [ ] `prompt(questionary.select, ..., **menu_options())` continua respondendo com o valor selecionado.

### Item 2 — Padronização visual com `menu_separator()` antes do item `[0]` em Markdown e Desenvolvimento

**Contexto:**
Os submenus Markdown e Desenvolvimento não inserem `menu_separator()` antes da escolha `[0] Voltar ao menu principal`, divergindo do padrão de Restic, Docker, Sistema, Menu Principal e `guard.py`.

**Ação técnica:**
- Em `src/utility_belt/ui/markdown_menu.py`:
  - Importar `menu_separator` de `utility_belt.ui.screen`.
  - Reorganizar a lista `choices` em `show_markdown_menu()` para incluir `menu_separator()` antes de `questionary.Choice("[0] Voltar ao menu principal", "exit")`.
- Em `src/utility_belt/ui/dev_menu.py`:
  - Importar `menu_separator` de `utility_belt.ui.screen`.
  - Reorganizar a lista `choices` em `show_dev_menu()` para incluir `menu_separator()` antes de `questionary.Choice("[0] Voltar ao menu principal", "exit")`.

**Critérios de aceite:**
- [ ] Em `show_markdown_menu()`, o elemento anterior ao `Choice` `exit` é um `questionary.Separator`.
- [ ] Em `show_dev_menu()`, o elemento anterior ao `Choice` `exit` é um `questionary.Separator`.
- [ ] Os valores selecionáveis e a ordem das opções dos dois submenus permanecem inalterados.

### Item 3 — Testes automatizados e proteção contra regressão

**Contexto:**
A suíte atual não exercitava o checklist real com itens elegíveis, porque os prompts são substituídos por mocks, nem verificava o separador nos submenus Markdown e Desenvolvimento.

**Ação técnica:**
- Adicionar em `tests/test_ui_experience.py` os casos descritos na "Estratégia de testes": opções e guarda, os três fluxos de checklist do `dev_menu` com `questionary.checkbox` real e os separadores de Markdown e Desenvolvimento.

**Critérios de aceite:**
- [ ] Os testes de compatibilidade falham na baseline `99e7e37` (com `TypeError`) e passam após o Item 1.
- [ ] Os testes de separador falham na baseline e passam após o Item 2.
- [ ] Todos os gates mínimos de `_project/README.md` passam.

## Arquivos afetados

- `src/utility_belt/ui/screen.py` (saneamento de `menu_options()` e guarda em `prompt()`)
- `src/utility_belt/ui/dev_menu.py` (inclusão de `menu_separator()` antes de `[0]`)
- `src/utility_belt/ui/markdown_menu.py` (inclusão de `menu_separator()` antes de `[0]`)
- `tests/test_ui_experience.py` (testes de compatibilidade de opções, fluxos de checklist e separadores)

## Decomposição em issues e PRs

Por se tratar de correções pontuais, complementares e restritas à camada de interface e menus (`ui/`), o escopo será entregue em uma única issue e um único PR revisável:

- **Issue a criar via `.agent/workflows/criar_issues.md`** — título previsto: `fix: compatibilidade de opcoes em checkbox e padronizacao visual de menus`.
  - Escopo: Itens 1, 2 e 3.
  - Número: atribuído pelo GitHub na criação (referido aqui como `N`) e registrado em "Rastreabilidade"; o plano não antecipa o número.
  - Branch: `fix/issue-N`, conforme `_project/README.md`.
  - Commits: `fix(issue-N): ...`.
  - PR: única, vinculada à issue `N`.

## Dependências e blockers

- Nenhuma dependência externa nova.
- Sem blockers técnicos identificados.

## Riscos, suposições e rollback

- **Risco**: Menus do tipo `select` mudarem de comportamento ao perder `use_shortcuts=False` explícito.
  - **Mitigação**: `questionary 2.1.1` já usa `use_shortcuts=False` por padrão em `select`; um teste com `questionary.select` real e `**menu_options()` confirma a resposta selecionada.
- **Risco**: A guarda de `prompt()` descartar argumentos legítimos.
  - **Mitigação**: a regra atua somente sobre `use_shortcuts` e só quando a fábrica não o declara; demais chaves seguem inalteradas.
- **Risco**: Asserções de testes existentes que contem o tamanho fixo da lista de `choices` falharem devido à inclusão do `menu_separator()`.
  - **Mitigação**: na revisão `v1`, nenhuma asserção de contagem fixa foi encontrada (`tests/test_ui_experience.py` já filtra `questionary.Separator`); se surgir, atualizar a asserção para desconsiderar separadores.
- **Suposição**: a versão de `questionary` fixada no ambiente (`2.1.1`) é a usada pelos gates; uma atualização de dependência está fora do escopo.
- **Rollback**: Caso haja comportamento anômalo, reversão simples do commit via Git na branch da issue.

## Sequência recomendada

1. Submeter este plano (`v2`) a nova rodada de revisão formal via `.agent/workflows/revisar_plano.md`.
2. Apresentar relatório de revisão e obter aprovação humana formal pós-revisão.
3. Criar a issue via `.agent/workflows/criar_issues.md` e registrar seu número em "Rastreabilidade".
4. Implementar via `.agent/workflows/implementar_issue.md` na branch `fix/issue-N`, com task persistente `010_task_issue-N.md`.
5. Executar os gates mínimos e registrar os resultados na task.
6. Abrir PR, obter autorização de merge e integrar na `main`.
7. Concluir ciclo 010 via PR documental de encerramento (`chore/cycle-010-closure`).

## Referências

- Ideação: `_project/ideations/010_correcoes_e_padronizacao_menus.md`
- Ciclo de governança: `_project/cycles.md`
- Convenções de branch, commit e gates: `_project/README.md`
- Implementação de referência de menus: `src/utility_belt/ui/docker_menu.py`, `src/utility_belt/ui/restic_menu.py`

## Rastreabilidade

| Campo | Valor |
| :-- | :-- |
| Issue(s) | [#33](https://github.com/EuThiagoAndrade/utility-belt/issues/33) |
| PR(s) | Documental: [#32](https://github.com/EuThiagoAndrade/utility-belt/pull/32), Entrega: [#34](https://github.com/EuThiagoAndrade/utility-belt/pull/34) |
| Branch(es) | `fix/issue-33` |
| `handoff_schema_version` | `1` |
| `handoff_id` | `EuThiagoAndrade/utility-belt+010+rascunhar_plano+correcoes-e-padronizacao-menus+99e7e37/v2` |
| Destino após conclusão | `_project/executed/010_correcoes_e_padronizacao_menus/010_plan.md` |

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+010+rascunhar_plano+correcoes-e-padronizacao-menus+99e7e37/v2`
- `identity_source`: `EuThiagoAndrade/utility-belt + 010 + rascunhar_plano + correcoes-e-padronizacao-menus + 99e7e37/v2`
- `effect_class`: `local_mutation`
- `state_before`: plano `v1` em `Em Revisão` com parecer `REQUER NOVA RODADA` (bloqueadores B1–B3, ressalvas R1–R5).
- `state_after`: plano `v2` em `Em Revisão`, com B1–B3 corrigidos, R1–R5 tratados, revisão formal da `v2` e aprovação humana `Pendente`; parecer da `v1` preservado.
- `next_transition`: `correção v2 -> nova rodada de revisão formal` (workflow `.agent/workflows/revisar_plano.md`).
- `preconditions`: plano `v2` completo segundo o template; nova rodada de revisão explicitamente autorizada.
- `authority`: usuário, autorização em 2026-10-20 ("Autorizado corrigir o plano 010 (v2) resolvendo B1–B3 e tratando R1–R5, para nova rodada de revisar_plano").
- `evidence`: `_project/drafts/010_correcoes_e_padronizacao_menus/010_plan.md` (`v2`), parecer `v1` na seção "Revisão crítica".
- `acceptance`: B1–B3 corrigidos, R1–R5 tratados, status sem promoção indevida, sem autorização tácita de implementação.
- `blockers`: nenhum para a nova rodada de revisão.
- `result`: `executed`
- `next_workflow_recommended`: `revisar_plano`
- `next_workflow_authorized`: nenhum (a nova rodada de revisão aguarda solicitação explícita).
- `actions_prohibited`: marcar status como `Aprovado`, criar issues, implementar código de produção ou abrir PRs.
- `rejection_rule`: o receptor recusa handoff com status promovido indevidamente, sem plano `v2` completo ou que trate a correção como aprovação.
- `logical_key`: `EuThiagoAndrade/utility-belt+010+rascunhar_plano+correcoes-e-padronizacao-menus+99e7e37/v2`
- `check_before_mutation`: verificar que existe um único plano canônico do ciclo 010 e que a `v1` possui parecer registrado.
- `reconcile_existing`: atualizar o plano existente sem duplicá-lo, preservando o parecer da `v1`.
- `ambiguous_state`: parar e solicitar decisão caso haja conflito de identidade ou de revisão.

## Revisão crítica

- **Data:** 2026-10-20
- **Versão revisada:** `v2` (baseline `99e7e37`); revisão anterior: `v1` em 2026-10-20.
- **Veredito:** `APTO COM RESSALVAS` (`v2`); `v1`: `REQUER NOVA RODADA`.
- **Bloqueios remanescentes:** nenhum.
- **Aprovação humana pós-revisão:** `Aprovada em 2026-10-20`
- **Correções materiais:** `v2` em 2026-10-20 — ver "Correções aplicadas na v2".
- **Ressalvas:** RV2-1 e RV2-2 (abaixo), a observar na implementação sem nova rodada de planejamento.

### Aprovação humana pós-revisão

- **Data:** 2026-10-20, posterior ao parecer `APTO COM RESSALVAS` da `v2`.
- **Autoridade:** responsável humano do repositório, em chat: "Aprovo o plano 010 v2 com as ressalvas RV2-1 e RV2-2. Registre a aprovação e o status Aprovado."
- **Versão aprovada:** `v2` (baseline `99e7e37`), incluindo as ressalvas RV2-1 e RV2-2 como condições obrigatórias da implementação.
- **Transição:** `Em Revisão` → `Aprovado`.
- **Não autorizado por esta aprovação:** publicação documental do plano, criação de issue, implementação, PR ou integração; cada etapa exige autorização própria.
- **Próximo gate:** publicação documental do plano (`chore/cycle-010-plan`) e `.agent/workflows/criar_issues.md`, mediante autorização explícita.

### Parecer v2 (2026-10-20)

#### Evidências

- Plano `v2` lido por inteiro; todas as seções e campos do template `.agent/templates/plano_implementacao.md` presentes; status `Em Revisão`, sem promoção indevida.
- `git rev-parse HEAD` = `99e7e37`; baseline inalterada desde a `v1`.
- Correções B1–B3 e R1–R5 conferidas item a item contra a tabela "Correções aplicadas na v2"; não restam referências ativas a `#31`, `31-fix-...` ou `select_options()` fora do histórico e do não-escopo.
- Viabilidade do teste de fluxo comprovada com script descartável: `run_git_tidy_local_flow` com `git_tidy` simulado, sob `prompt_toolkit.application.create_app_session(input=create_pipe_input(), output=DummyOutput())` e entrada `"\r"` + `"y"`, levanta o `TypeError` de `use_shortcuts` na baseline e, com `menu_options()` saneado, conclui chamando `delete_local_branches(['feat/x'])`. Checklist e confirmação reais respondidos no mesmo pipe.
- Gates na baseline: `uv run ruff check` → `All checks passed!`; `uv run pytest -q` → `241 passed, 36 skipped`; `uv run python scripts/validate_governance.py` → `39 OK`; `git diff --check` limpo.

#### Bloqueadores

- Nenhum.

#### Ressalvas

- **RV2-1 — Mecanismo de injeção nos fluxos não especificado.** Os fluxos do `dev_menu` chamam `prompt()` sem `input`/`output`, e a estratégia não diz como o pipe chega ao checklist real. Usar `create_app_session(input=..., output=DummyOutput())`, mecanismo verificado acima. Evitar envolver `questionary.checkbox` em uma função com assinatura própria: a guarda de `prompt()` descartaria `use_shortcuts` e o teste deixaria de exercitar o saneamento de `menu_options()` nos fluxos.
- **RV2-2 — Critério "falham na baseline" amplo demais.** O teste de `questionary.select` com `**menu_options()` é de não regressão e passa na baseline por construção (verificado na `v1`). O critério do Item 3 vale para os testes de `menu_options()`, da guarda, dos fluxos de checklist e dos separadores, não para o teste de `select`.

#### Itens atendidos

- B1: número de issue não antecipado; registro após `criar_issues`.
- B2: branch `fix/issue-N`, commits `fix(issue-N):` e closure `chore/cycle-010-closure` conforme `_project/README.md`.
- B3: os cinco gates mínimos de `_project/README.md` constam da estratégia e dos critérios.
- R1: `select_options()` fora do escopo, com justificativa e mitigação coerentes com o padrão do Questionary.
- R2: regra da guarda única, determinística e restrita a `use_shortcuts`, com tratamento de assinatura indisponível.
- R3: testes com prompts reais e critério de falha na baseline.
- R4: arquivo único `tests/test_ui_experience.py`; separadores testados apenas nos submenus alterados, demais em não-escopo explícito.
- R5: item 2 do escopo tratado como verificação, incluindo `run_git_tidy_all_flow`.
- Objetivo, não-escopo, sequência, dependências, riscos e rollback coerentes entre si e com `.agent/ai_behavior.md`, `_project/README.md` e `_project/cycles.md`.

#### Handoff da revisão v2

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+010+revisar_plano+correcoes-e-padronizacao-menus+99e7e37/v2`
- `identity_source`: `EuThiagoAndrade/utility-belt + 010 + revisar_plano + correcoes-e-padronizacao-menus + 99e7e37/v2`
- `effect_class`: `local_mutation`
- `state_before`: plano `v2` em `Em Revisão`, revisão formal da `v2` `Pendente`, aprovação humana `Pendente`.
- `state_after`: plano `v2` em `Em Revisão`, parecer `APTO COM RESSALVAS` registrado, aprovação humana `Pendente`.
- `next_transition`: `parecer -> aprovação humana`.
- `preconditions`: manifestação humana explícita, posterior a este parecer, aprovando o plano `v2` com as ressalvas RV2-1 e RV2-2.
- `authority`: responsável humano do repositório.
- `evidence`: registro da aprovação no cabeçalho e nesta seção (`Aprovada em AAAA-MM-DD`), com status `Aprovado`.
- `acceptance`: aprovação explícita e posterior ao parecer; aptidão não equivale a aprovação.
- `blockers`: nenhum técnico; aprovação humana pendente.
- `result`: `executed`
- `next_workflow_recommended`: registro da aprovação, publicação documental do plano (`chore/cycle-010-plan`) e `criar_issues`, nessa ordem e conforme gates próprios.
- `next_workflow_authorized`: nenhum.
- `actions_prohibited`: marcar `Aprovado` sem manifestação humana posterior, criar issue, implementar, publicar PR ou integrar.
- `rejection_rule`: o receptor recusa handoff que trate `APTO COM RESSALVAS` como aprovação ou omita as ressalvas.
- `logical_key`: `EuThiagoAndrade/utility-belt+010+revisar_plano+correcoes-e-padronizacao-menus+99e7e37/v2`
- `check_before_mutation`: não havia parecer para a `v2`; o parecer da `v1` permanece preservado.
- `reconcile_existing`: reexecução sobre a `v2` atualiza este parecer sem duplicá-lo.
- `ambiguous_state`: parar se o plano mudar após este parecer ou houver decisões conflitantes.

### Correções aplicadas na v2

| Achado `v1` | Tratamento na `v2` |
| :-- | :-- |
| B1 — número de issue `#31` ocupado | Número não antecipado; issue "a criar via `criar_issues`", referida como `N` e registrada em "Rastreabilidade" após a criação. |
| B2 — branch fora da convenção | Branch `fix/issue-N` e commits `fix(issue-N):`, conforme `_project/README.md`; closure em `chore/cycle-010-closure`. |
| B3 — gates mínimos incompletos | Os cinco gates mínimos de `_project/README.md`, via `uv run`, constam da estratégia de testes e dos critérios do Item 3. |
| R1 — `select_options()` especulativo | Retirado do escopo e listado em "Fora do escopo"; mitigação do risco de `select` reescrita com base no padrão `use_shortcuts=False`. |
| R2 — guarda ambígua | Regra única e determinística em "Decisões e autoridades": remove somente `use_shortcuts` quando a fábrica não o declara; assinatura indisponível mantém `kwargs`. |
| R3 — testes mascarando o defeito | Testes com `questionary.checkbox`/`select` reais via `create_pipe_input()` + `DummyOutput()`; critério de falhar na baseline e passar após a correção. |
| R4 — escopo de testes inconsistente | Arquivo único `tests/test_ui_experience.py`; testes de separador restritos a Markdown e Desenvolvimento, demais menus em "Fora do escopo". |
| R5 — item 2 sem alteração de código | Item 2 do escopo reescrito como verificação, incluindo a delegação de `run_git_tidy_all_flow`. |

### Parecer v1 (2026-10-20) — preservado

- **Versão revisada:** `v1` (baseline `99e7e37`)
- **Veredito:** `REQUER NOVA RODADA`
- **Bloqueios:** B1, B2 e B3 (abaixo).
- **Ressalvas:** R1 a R5 (abaixo).

### Evidências da revisão

- Template `.agent/templates/plano_implementacao.md` lido; todas as seções e campos de cabeçalho estão presentes.
- `git rev-parse HEAD` = `99e7e37`, confirmando a baseline declarada.
- Defeito reproduzido com `questionary 2.1.1`: `questionary.checkbox(..., **menu_options())` com `create_pipe_input()` e `DummyOutput()` levanta `TypeError: PromptSession.__init__() got an unexpected keyword argument 'use_shortcuts'`; sem a chave, o prompt é instanciado sem erro.
- `inspect.signature`: `questionary.select` declara `use_shortcuts: bool = False`; `questionary.checkbox` não declara o parâmetro e aceita `**kwargs`.
- Separadores conferidos: `menu.py` (principal e Sistema), `restic_menu.py`, `docker_menu.py` e `guard.py` usam `menu_separator()` antes de `[0]`; `markdown_menu.py` e `dev_menu.py` não.
- Testes existentes: `tests/test_ui_experience.py` já filtra `questionary.Separator` ao comparar valores; `tests/test_markdown_cli.py` substitui `questionary.select` por mock. Nenhuma asserção de contagem fixa de `choices` foi encontrada.
- GitHub: o número `#31` pertence à PR `chore(cycle-009)` integrada em `99e7e37` (`gh pr list --state all`).

### Bloqueadores

- **B1 — Número de issue inválido.** O plano prevê "Issue #31" em Decomposição, Sequência e Rastreabilidade, mas `#31` já é a PR de encerramento do ciclo `009`; issues e PRs compartilham numeração no GitHub. O plano não deve antecipar número: registrar "issue a criar via `criar_issues`" e preencher o número real após a criação.
- **B2 — Branch fora da convenção.** `31-fix-compatibilidade-e-padronizacao-menus` contraria `_project/README.md` (`fix/issue-N`) e a regra de `.agent/ai_behavior.md` de consumir a nomenclatura da autoridade. Usar `fix/issue-N`, com commits `fix(issue-N):`.
- **B3 — Gates mínimos incompletos.** A estratégia de testes e os critérios citam apenas `pytest tests/` e `ruff check .`; faltam `uv run python scripts/validate_governance.py`, `git diff --check` e `git status --short`, e os comandos devem rodar via `uv run`, conforme "Gates mínimos" de `_project/README.md`.

### Ressalvas

- **R1 — `select_options()` é especulativo.** `questionary.select` já usa `use_shortcuts=False` por padrão e nenhum chamador está previsto para o novo helper; remover `use_shortcuts` de `menu_options()` é neutro para os menus `select`. Pela regra "Simplicidade primeiro", retirar `select_options()` do escopo (ou justificar um consumidor concreto) e ajustar a mitigação do primeiro risco, que depende dessa premissa.
- **R2 — Regra da guarda em `prompt()` ambígua.** "se `factory` for `questionary.checkbox` (ou se ... a assinatura não o declare)" admite duas implementações distintas. Fixar uma regra determinística e restrita, por exemplo: descartar `use_shortcuts` quando ele não for parâmetro nomeado na assinatura da fábrica. Filtrar todas as chaves não declaradas eliminaria argumentos legítimos repassados via `**kwargs` (como `input`/`output` do `prompt_toolkit`).
- **R3 — Testes não podem mascarar o defeito.** O bug escapou porque os testes substituem os prompts por mocks. Os testes de compatibilidade devem instanciar o `questionary.checkbox` real (ex.: `create_pipe_input()` + `DummyOutput()`, comprovadamente funcional neste ambiente) ou verificar que os `kwargs` entregues à fábrica não contêm `use_shortcuts`. O critério "Menus `select` continuam navegáveis" deve ter verificação automatizada equivalente.
- **R4 — Escopo de testes inconsistente.** O item 4 do escopo cobre separadores em `restic`, `docker`, `markdown`, `dev` e `sistema`; a estratégia e o Item 3 cobrem apenas Markdown e Desenvolvimento. O arquivo de teste também está indefinido (`test_interactive_menus.py` "ou" `test_screen_options.py`), enquanto Arquivos afetados lista só o primeiro. Escolher um conjunto e um arquivo.
- **R5 — Item 2 do escopo sem alteração de código.** Após o Item 1, as chamadas de `checkbox` em `dev_menu.py` não precisam mudar; explicitar que esse item é coberto por verificação (incluindo `run_git_tidy_all_flow`, que delega aos fluxos local e remoto).

### Itens atendidos

- Objetivo, causa raiz e baseline corretos e reproduzidos.
- Não-escopo coerente com a ideação (sem mudanças em `git_tidy.py`, `janitor.py`, motor Markdown, dependências ou paleta).
- Decisões do responsável (separador em todos os submenus; abordagem combinada) registradas com data.
- Riscos e rollback proporcionais; o risco de contagem fixa de `choices` não se materializa nos testes atuais.
- Ciclo, caminho do plano e estado `Planejamento` coerentes com `_project/cycles.md`.
- Observação fora do escopo, sem ação: `docker_menu.py:53` usa `questionary.checkbox` sem `menu_options()` e não é afetado pelo defeito.

### Handoff da revisão

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+010+revisar_plano+correcoes-e-padronizacao-menus+99e7e37/v1`
- `identity_source`: `EuThiagoAndrade/utility-belt + 010 + revisar_plano + correcoes-e-padronizacao-menus + 99e7e37/v1`
- `effect_class`: `local_mutation`
- `state_before`: plano `v1` em `Rascunho`, revisão formal `Pendente`, aprovação humana `Pendente`.
- `state_after`: plano `v1` em `Em Revisão`, parecer `REQUER NOVA RODADA` registrado, aprovação humana `Pendente`.
- `next_transition`: `parecer -> correção do plano (v2) -> nova rodada de revisão`.
- `preconditions`: B1, B2 e B3 corrigidos; R1 a R5 tratados ou justificados no plano.
- `authority`: responsável humano autoriza a correção do plano e a nova rodada; não há autorização de aprovação.
- `evidence`: diff do plano `v2` e novo parecer de `revisar_plano`.
- `acceptance`: plano `v2` sem bloqueios e parecer `APTO PARA APROVAÇÃO` ou `APTO COM RESSALVAS`.
- `blockers`: B1, B2, B3.
- `result`: `executed`
- `next_workflow_recommended`: correção do plano seguida de `revisar_plano`; `criar_issues` somente após parecer apto e aprovação humana.
- `next_workflow_authorized`: nenhum.
- `actions_prohibited`: marcar `Aprovado`, criar issue, implementar, publicar PR documental ou integrar.
- `rejection_rule`: o receptor recusa handoff que trate este parecer como aptidão ou aprovação.
- `logical_key`: `EuThiagoAndrade/utility-belt+010+revisar_plano+correcoes-e-padronizacao-menus+99e7e37/v1`
- `check_before_mutation`: não havia parecer anterior para a versão `v1`.
- `reconcile_existing`: reexecução sobre `v1` atualiza este parecer sem duplicá-lo; versão `v2` recebe parecer próprio, preservando este.
- `ambiguous_state`: parar se o plano mudar durante a revisão ou houver decisões conflitantes.

## Pós-mortem

- **Data de conclusão:** 2026-10-20
- **Desvios:** Nenhum desvio técnico em relação ao plano aprovado (v2). A simplificação formalizada na revisão eliminou código especulativo desnecessário e manteve a implementação cirúrgica.
- **Lições comprovadas:** Parâmetros repassados genericamente via `**kwargs` para bibliotecas com múltiplas fábricas (como `questionary.select` e `questionary.checkbox`) devem ser compatibilizados ou filtrados contra a assinatura da fábrica executada para evitar vazamento de argumentos inválidos para classes internas do `prompt_toolkit`.

## Integração e encerramento

Responsável autorizou: "Sim autorizado o merge da PR 34", em 2026-10-20, após apresentação da PR #34 validada com 100% de aprovação nos gates locais e remotos. PR #34 integrada em `e943a47`; issue #33 fechada formalmente. Release automático [39514115629](https://github.com/EuThiagoAndrade/utility-belt/actions/runs/39514115629) passou em Windows/Ubuntu e publicou [v0.4.1](https://github.com/EuThiagoAndrade/utility-belt/releases/tag/v0.4.1), commit bot `9e1e558`. Encerramento documental em branch própria `chore/cycle-010-closure` conforme `_project/README.md`, sem issue recursiva. Estado Concluído nesta branch é proposta; efeito canônico somente após integração verificável da PR de closure. Handoff operacional do encerramento em `010_task_closure.md`.
