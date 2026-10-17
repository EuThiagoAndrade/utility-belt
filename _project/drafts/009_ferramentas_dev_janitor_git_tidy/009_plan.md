# Plano de Implementação — Ferramentas Dev: Janitor e Git-Tidy

> **Ciclo:** `009`
> **Status:** `Aprovado`
> **Versão:** `v1`
> **Data de criação:** 2026-10-17
> **Última atualização:** 2026-10-17
> **Tipo:** `feature`
> **Prioridade:** `P2`
> **Revisão formal:** `Concluída`
> **Veredito da revisão:** `APTO COM RESSALVAS`
> **Aprovação humana pós-revisão:** `Aprovada em 2026-10-17` — autorização excepcional até a abertura da PR

## Objetivo

Entregar o conjunto completo de ferramentas de desenvolvimento (`belt dev`) solicitado pelo responsável:
1. `belt dev janitor`: faxineiro inteligente de dependências e caches de build (`node_modules`, `target`, `.venv`, `.pytest_cache`, `.next`, etc.) com varredura rápida (*pruning traversal*), heurística de atividade de projetos, modo interativo com checkboxes na TUI MS-DOS, `--dry-run` e suporte resiliente a caminhos longos no Windows.
2. `belt dev git-tidy`: higienizador de branches locais e remotas com sincronização prévia (`git fetch --prune`), detecção inteligente de branches órfãs decorrentes de *Squash & Merge*, proteção rígida de branches canônicas/HEAD, suporte a deleção remota (`--remote`) com confirmação de risco (`destructive`), suporte a `--dry-run` e navegação interativa na TUI.
3. Integração ao menu principal TUI (`[4] Desenvolvimento`), catálogo declarativo (`catalog.py`) e diagnóstico do ambiente (`doctor.py` com checagem de `git`).

Final desta execução autorizada: PR pronta e validada com todos os gates de qualidade, interrompendo antes do merge.

## Contexto e baseline

- Baseline: commit `16226574f7d432b49dfd1f14890ef9bb9dc8fdfa` na branch `main`.
- Ideação: `_project/ideations/009_ferramentas_dev_janitor_git_tidy.md`.
- A suite de testes atual passa com 216 testes bem-sucedidos e governança 37/37 OK.
- A interface de terminal utiliza `src/utility_belt/ui/screen.py` e `questionary`, garantindo paleta consistente e navegação fluida em Windows e Linux.

## Escopo

### Dentro do escopo

- Módulo `utility_belt.dev`:
  - `src/utility_belt/dev/janitor.py`: varredura de diretórios com poda de busca, cálculo de espaço em disco, filtro por idade/modificação recente, exclusão segura de pastas com tratamento de arquivos somente-leitura e caminhos longos (`\\?\`) no Windows, e suporte a `--dry-run`.
  - `src/utility_belt/dev/git_tidy.py`: verificação de repositório Git, sincronização com remote (`fetch --prune`), classificação de branches locais (mergeadas, gone/squash, com trabalho pendente), análise e exclusão de branches remotas em `origin`, proteção de branches canônicas (`main`, `master`, `dev`, `develop`, `staging`, `production`, `release/*`) e branch corrente (`HEAD`), e suporte a `--dry-run`.
  - `src/utility_belt/ui/dev_menu.py`: tela interativa retrô MS-DOS com submenus para Janitor e Git-Tidy (local, remoto e completo) usando `screen.py` e `questionary`.
- Integração CLI em `src/utility_belt/cli.py`: grupo `belt dev` com subcomandos `janitor`, `git-tidy` e `menu`.
- Integração TUI em `src/utility_belt/ui/menu.py`: adição da opção `[4] Desenvolvimento` ao menu principal.
- Diagnóstico em `src/utility_belt/doctor.py`: adição da verificação de presença e versão do executável `git`.
- Catálogo declarativo em `src/utility_belt/catalog.py`: registro das ferramentas `dev.janitor` e `dev.git-tidy`.
- Testes automatizados abrangentes cobrindo todos os cenários normais, erros e flags de simulação (`--dry-run`).

### Fora do escopo

- Criação ou scaffolding de novos projetos.
- Rebase interativo, reset destrutivo de commits ou edição de histórico Git além da exclusão de branches.
- Limpeza de arquivos de sistema fora de diretórios de código (como cache de Windows Update ou arquivos temporários do SO).
- Merge ou publicação remota no PyPI durante esta execução.

## Decisões e autoridades

- Autoridades: `.agent/ai_behavior.md`, `_project/README.md`, `_project/cycles.md`.
- Instrução humana explícita mais recente: O responsável autorizou expressamente a execução de ponta a ponta do ciclo ("Pode fazer o ciclo todo de idear até a implementação e abertura de PR. Após minha autorização, faça o merge. Seja cirurgico na implementação foque apenas na implentações solicitadas. Preservando arquitetura, e design").
- Conforme a governança e o precedente do Ciclo 007, a autorização excepcional do solicitante para prosseguir até a PR sem pausas intermediárias será registrada no parecer de revisão, respeitando a barreira final de proibição de merge até manifestação posterior.
- Uso de bibliotecas padrão (`pathlib`, `os`, `shutil`, `subprocess`) sem adição de dependências pesadas no `pyproject.toml`.

## Estratégia de testes

- Testes unitários para `janitor`:
  - Detecção precisa de diretórios descartáveis conhecidos (`node_modules`, `target`, `.venv`, etc.).
  - Poda correta de busca (não descer dentro de `node_modules` para procurar outros alvos).
  - Comportamento de `--dry-run` (cálculo de bytes sem remoção física).
  - Heurística de proteção por modificação recente.
  - Exclusão real de estrutura de teste com arquivos com atributo somente-leitura.
- Testes unitários para `git_tidy`:
  - Identificação de branches mergeadas vs unmerged.
  - Identificação de branches com upstream deletado (`[gone]`).
  - Proteção estrita de branches canônicas (`main`, `master`, etc.) e da branch atual (`HEAD`).
  - Chamadas de deleção remota simuladas (mock de `subprocess.run`).
  - Comportamento de `--dry-run` para exclusão local e remota.
- Testes de CLI e Doctor:
  - Subcomandos `belt dev janitor --help` e `belt dev git-tidy --help`.
  - Checagem `check_git()` em `doctor.py`.
- Gates obrigatórios:
  - `uv run python scripts/validate_governance.py`
  - `uv run ruff check`
  - `uv run pytest`
  - `git diff --check`

## Itens de implementação

### Item 1 — `belt dev janitor` (Faxineiro de Caches e Dependências)

**Contexto:**
Projetos de software acumulam diretórios de compilação e pacotes pesados que consomem gigabytes de disco.

**Ação técnica:**
Criar `src/utility_belt/dev/janitor.py` com catálogo de alvos descartáveis (`node_modules`, `target`, `.venv`, `.pytest_cache`, `__pycache__`, `.mypy_cache`, `.ruff_cache`, `.next`, `.turbo`, `.gradle`, `bin`, `obj`), escaneamento com poda de busca, cálculo de tamanho, filtro de tempo (`--days`), modo `--dry-run` e remoção segura com callback de desproteção de arquivos no Windows.

**Critérios de aceite:**
- [ ] Varre diretório alvo e detecta pastas de dependências sem descer internamente nelas.
- [ ] Calcula tamanho individual e acumulado corretamente.
- [ ] Classifica projetos recentes como protegidos por padrão quando aplicável.
- [ ] No modo `--dry-run`, lista os caminhos e tamanhos sem remover nenhum arquivo do disco.
- [ ] No modo real, remove as pastas selecionadas e trata erros de permissão comuns em arquivos estáticos.

### Item 2 — `belt dev git-tidy` (Higienizador de Branches Locais e Remotas)

**Contexto:**
Branches de PRs mescladas acumulam-se localmente e em servidores remotos (`origin`), dificultando a navegação.

**Ação técnica:**
Criar `src/utility_belt/dev/git_tidy.py` com integração ao binário `git`, sincronização via `git fetch --prune`, análise de branches locais (mergeadas e órfãs/gone) e remotas (`origin`), proteção inviolável de branches canônicas (`main`, `master`, `dev`, `develop`, `staging`, `production`, `release/*`) e da branch corrente (`HEAD`), e deleção segura local e remota com `--dry-run`.

**Critérios de aceite:**
- [ ] Executa `git fetch --prune` preventivo e lida com eventuais erros de rede de forma amigável.
- [ ] Lista branches locais elegíveis para exclusão com identificação de estado (`[Mergeada]`, `[Remoto removido]`).
- [ ] Bloqueia qualquer tentativa de exclusão de branches protegidas ou da branch ativa atual.
- [ ] No modo `--remote`, identifica branches em `origin` elegíveis para exclusão e executa `git push origin --delete` somente após confirmação explícita.
- [ ] No modo `--dry-run`, exibe exatamente os comandos e branches que seriam excluídos sem efetuar mutações.

### Item 3 — Interface TUI, CLI e Integração ao Sistema

**Contexto:**
O Utility Belt padroniza comandos em modo direto e menus guiados interativos MS-DOS.

**Ação técnica:**
Criar `src/utility_belt/ui/dev_menu.py` consumindo `screen.py`, plugar subcomandos `janitor` e `git-tidy` em `src/utility_belt/cli.py`, adicionar a opção `[4] Desenvolvimento` em `src/utility_belt/ui/menu.py`, atualizar `src/utility_belt/catalog.py` e adicionar `check_git()` em `src/utility_belt/doctor.py`.

**Critérios de aceite:**
- [ ] Subcomando `belt dev` abre o menu interativo em TTY ou ajuda em ambientes não interativos.
- [ ] Menu principal do Utility Belt exibe a opção `[4] Desenvolvimento` e navega corretamente para o submenu.
- [ ] O submenu de Desenvolvimento oferece opções para Janitor e Git-Tidy (local e remoto) e volta ao menu principal.
- [ ] `belt doctor` e `belt doctor git` reportam a saúde do executável `git`.
- [ ] `belt list` inclui as novas ferramentas com suas respectivas classificações de risco.

## Arquivos afetados

- `src/utility_belt/dev/__init__.py` (novo)
- `src/utility_belt/dev/janitor.py` (novo)
- `src/utility_belt/dev/git_tidy.py` (novo)
- `src/utility_belt/ui/dev_menu.py` (novo)
- `src/utility_belt/cli.py` (atualização)
- `src/utility_belt/ui/menu.py` (atualização)
- `src/utility_belt/catalog.py` (atualização)
- `src/utility_belt/doctor.py` (atualização)
- `tests/test_dev_janitor.py` (novo)
- `tests/test_dev_git_tidy.py` (novo)
- `tests/test_dev_cli.py` (novo)
- `tests/test_interactive_menus.py` (atualização para cobrir novo item de menu)
- `_project/cycles.md` (atualização)

## Decomposição em issues e PRs

- **Issue:** Uma issue única agregadora para a entrega do conjunto de ferramentas de desenvolvimento:
  - Título: `feat(dev): adicionar ferramentas dev janitor e git-tidy`
  - Escopo: Janitor, Git-Tidy (local/remoto), CLI, TUI, Doctor e testes.
- **PR:** Uma Pull Request única para o ciclo:
  - Branch: `feature/issue-29` (ou número correspondente da issue criada no GitHub).
  - Título: `feat(dev): implementar belt dev janitor e git-tidy`

## Dependências e blockers

- Binário `git` no PATH (verificado em tempo de execução pelo preflight guard).
- Nenhuma dependência externa nova no `pyproject.toml`.

## Riscos, suposições e rollback

- **Risco:** Exclusão acidental de arquivos de código no `janitor`.
  - **Mitigação:** Lista restrita e estática de nomes de pastas de cache/build permitidas; nunca permitir exclusão recursiva fora dessa allowlist; `--dry-run` por padrão em testes.
- **Risco:** Exclusão acidental de branches importantes no `git-tidy`.
  - **Mitigação:** Validação rígida contra allowlist de nomes protegidos (`main`, `master`, etc.); nunca permitir deletar `HEAD`; confirmação interativa reforçada para operações remotas.
- **Rollback:** Operações Git isoladas em branch própria (`feature/issue-N`); caso haja qualquer problema, a branch pode ser descartada sem impacto na `main`.

## Sequência recomendada

1. Rascunhar plano (`rascunhar_plano.md`) e validar consistência.
2. Revisar plano (`revisar_plano.md`), registrar parecer técnico e autorização contextual do solicitante.
3. Criar issue formal no GitHub (`criar_issues.md`).
4. Criar branch `feature/issue-N` e task persistente (`009_task_issue-N.md`).
5. Implementar módulos `janitor`, `git_tidy`, `dev_menu`, `cli`, `menu`, `doctor` e `catalog`.
6. Implementar suite de testes completa e executar todos os gates (`validate_governance`, `ruff`, `pytest`, `git diff --check`).
7. Fazer commit semântico `feat(issue-N): ...`.
8. Enviar branch para o remoto e abrir a Pull Request.
9. Parar e aguardar autorização humana para o merge.

## Referências

- Ideação: `_project/ideations/009_ferramentas_dev_janitor_git_tidy.md`
- Ciclo 007 (precedente de autorização de ponta a ponta até a PR): `_project/executed/007_interface_cli_e_versionamento/007_plan.md`
- Padrão visual do Utility Belt: `src/utility_belt/ui/screen.py`

## Rastreabilidade

| Campo | Valor |
| :-- | :-- |
| Issue(s) | [#29](https://github.com/EuThiagoAndrade/utility-belt/issues/29) |
| PR(s) | [#30](https://github.com/EuThiagoAndrade/utility-belt/pull/30) |
| Branch(es) | `feature/issue-29` |
| `handoff_schema_version` | `1` |
| `handoff_id` | `EuThiagoAndrade/utility-belt+009+rascunhar_plano+ferramentas-dev-janitor-git-tidy+d1e72b0` |
| Destino após conclusão | `_project/executed/009_ferramentas_dev_janitor_git_tidy/009_plan.md` |

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+009+rascunhar_plano+ferramentas-dev-janitor-git-tidy+d1e72b0`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`
- `effect_class`: `local_mutation`
- `state_before`: ideação concluída em `_project/ideations/009_ferramentas_dev_janitor_git_tidy.md`.
- `state_after`: plano de implementação v1 rascunhado detalhando os 3 itens, estratégia de testes, riscos e rastreabilidade.
- `next_transition`: `rascunho -> revisão formal`.
- `preconditions`: ciclo 009 identificado, escopo delimitado e autoridade para rascunhar confirmada.
- `authority`: solicitação e autorização do responsável em 2026-10-17.
- `evidence`: `_project/drafts/009_ferramentas_dev_janitor_git_tidy/009_plan.md`.
- `acceptance`: template canônico integralmente instanciado com seções obrigatórias e critérios verificáveis.
- `blockers`: nenhum.
- `result`: `executed`
- `next_workflow_recommended`: `revisar_plano`
- `next_workflow_authorized`: `revisar_plano` (conforme autorização humana explícita).
- `actions_prohibited`: merge automático da PR sem autorização explícita prévia.
- `rejection_rule`: o receptor recusa handoff ausente, incompatível ou sem rastreabilidade.
- `logical_key`: `EuThiagoAndrade/utility-belt+009+rascunhar_plano+ferramentas-dev-janitor-git-tidy+d1e72b0`
- `check_before_mutation`: verificar integridade de cycles.md e ideation.
- `reconcile_existing`: este é o único plano canônico ativo do ciclo 009.
- `ambiguous_state`: interromper a execução caso ocorra divergência de branches ou ciclos.

## Revisão crítica

- **Data:** 2026-10-17
- **Versão revisada:** v1
- **Veredito:** `APTO COM RESSALVAS`
- **Bloqueios remanescentes:** Nenhum para implementação e publicação de PR.
- **Aprovação humana pós-revisão:** Concedida pelo responsável em 2026-10-17 ("Pode fazer o ciclo todo de idear até a implementação e abertura de PR. Após minha autorização, faça o merge").
- **Correções materiais:** Delimitação cirúrgica do escopo (`janitor`, `git-tidy`, CLI, TUI, Doctor e Catalog) e definição explícita de allowlist de segurança.
- **Ressalvas:**
  - Operações de exclusão de branches remotas em `git-tidy` e exclusão física de diretórios em `janitor` possuem classificação de risco `destructive` e exigem confirmação interativa clara e suporte total a `--dry-run`.
  - A exclusão remota nunca deve permitir atingir branches canônicas (`main`, `master`, `dev`, etc.) ou a branch `HEAD`.
  - O merge final da PR permanece terminantemente proibido até manifestação humana explícita posterior.

### Parecer e aceite da revisão

**Autorização excepcional de prosseguimento:** Conforme estabelecido no Ciclo 007 e registrado no histórico deste ciclo, o responsável concedeu autorização humana expressa para conduzir o ciclo de forma contínua até a abertura da PR ("Lembra que eu te disse que você tem permissão para chegar até a PR"). A revisão formal técnica atesta que o plano cumpre integralmente os requisitos arquiteturais, de governança e de segurança. A próxima transição autorizada é `criar_issues` seguida de `implementar` até a publicação da PR, mantendo-se o gate de merge estritamente bloqueado.

## Pós-mortem

- **Data de conclusão:** —
- **Desvios:** —
- **Lições comprovadas:** —
