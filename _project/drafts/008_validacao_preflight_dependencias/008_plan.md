# Plano de Implementação — Validação prévia de dependências externas (preflight guard)

> **Ciclo:** `008`
> **Status:** `Aprovado`
> **Versão:** `v1`
> **Data de criação:** 2026-10-14
> **Última atualização:** 2026-10-14
> **Tipo:** `feature`
> **Prioridade:** `P2`
> **Revisão formal:** `Concluída`
> **Veredito da revisão:** `APTO PARA APROVAÇÃO`
> **Aprovação humana pós-revisão:** `Aprovada em 2026-10-14` — autorização explícita para o ciclo completo até a PR (merge retido para autorização humana posterior).

## Objetivo

Implementar uma camada de validação prévia (preflight guard) para dependências externas (Restic e Docker) no Utility Belt. Ao selecionar uma ferramenta cujo executável não esteja presente no sistema, o sistema intercepta a navegação antes de abrir submenus quebrados e exibe uma tela dedicada de onboarding no padrão visual canônico (`src/utility_belt/ui/screen.py`), oferecendo instruções de instalação no terminal (contextualizadas por SO), opção de abrir a página oficial de download no navegador e retorno seguro ao menu principal. Adicionalmente, enriquecer o diagnóstico do `doctor` com comandos e links para dependências ausentes.

## Contexto e baseline

- Baseline: commit `cf44c9076875b51e2806b4a6236d3fa8e969e5a9` na branch `main`.
- Ideação: `_project/ideations/008_validacao_preflight_dependencias.md`.
- No estado atual, `menu.py` invoca diretamente `show_restic_menu()` e `show_docker_menu()` sem verificar se `restic` ou `docker` estão no `PATH`.
- Falhas só acontecem em tempo de execução (`subprocess.run`), disparando `FileNotFoundError` com mensagens de erro técnicas que não instruem o usuário sobre onde e como obter o software.
- `src/utility_belt/doctor.py` já contém funções de checagem (`check_restic`, `check_docker`, `check_executable`), que serão aproveitadas e ampliadas com metadados de instalação (comandos e URLs).
- `src/utility_belt/ui/screen.py` estabelece o padrão visual da interface retrô MS-DOS / terminal.

## Escopo

### Dentro do escopo

1. **Módulo de guarda / onboarding (`ui/guard.py`)**:
   - Criação de componente visual reutilizável baseado estritamente em `screen.py` (`render_header`, `message`, `prompt`, `menu_options`, `menu_separator`, `menu_footer`).
   - Apresentação da tela de requisito ausente com título de breadcrumb, aviso contextual e menu questionary contendo:
     - `[1] Ver instruções de instalação no terminal`
     - `[2] Abrir página de download no navegador`
     - `[0] Voltar ao menu principal`
   - Exibição de comandos de instalação específicos por sistema operacional:
     - **Windows**: `winget install restic.restic` / `scoop install restic`, e para Docker o link do Docker Desktop / `winget install Docker.DockerDesktop`.
     - **Linux**: `sudo apt install restic` / `sudo dnf install restic`, e para Docker links e comandos oficiais de instalação.
   - Abertura de link via `webbrowser.open()`, garantindo que a URL seja sempre impressa em texto para terminais onde a abertura gráfica não ocorra ou falhe.
2. **Integração no Menu Principal (`menu.py`)**:
   - Interceptação antes de chamar `show_restic_menu()` ou `show_docker_menu()`.
   - Se o executável estiver ausente, direciona para o onboarding/guard.
   - Para Docker, se o executável existir mas o daemon estiver inativo/parado, exibir aviso orientando a inicialização do daemon/Docker Desktop antes de continuar.
3. **Enriquecimento do `doctor` (`doctor.py` e `cli.py`)**:
   - Incluir nos dicionários de dependências de `check_restic` e `check_docker` campos `install_guide` e `download_url`.
   - Na exibição em terminal do comando `belt doctor` e na tela `Sistema > Verificar ambiente`, exibir orientações de instalação quando a dependência estiver ausente (`[FALTA]`).
4. **Testes automatizados**:
   - Testes unitários para o módulo guard (simulando SO Windows e Linux, ausência e presença de executáveis).
   - Testes de integração para a navegação do menu principal com dependências mockadas.
   - Testes para o enriquecimento do diagnóstico do `doctor`.

### Fora do escopo

- Instalação automática em segundo plano com privilégios de administrador (`sudo` ou UAC).
- Download direto e execução de instaladores de terceiros.
- Modificações no motor Markdown (MarkItDown), que já possui governança e ambiente isolado próprios via ciclo 006.
- Adição de novos adaptadores ou comandos CLI destrutivos.
- Alteração permanente nas políticas de governança do repositório.

## Decisões e autoridades

- **Autoridades**: `.agent/ai_behavior.md`, `_project/README.md`, `_project/cycles.md`.
- **Fidelidade visual canônica**: Estrita observância de `src/utility_belt/ui/screen.py`. Nenhuma moldura ASCII arbitrária; uso de `render_header`, `message("AVISO", ...)`, `questionary.select` com `menu_style()`.
- **Instrução humana explícita (2026-10-14)**: "Pode fazer o ciclo completo até o PR. Contudo me peça para autorizar o merge. Ok."
  Essa instrução autoriza o ciclo completo (rascunho, revisão, issue, branch, implementação, gates, PR), estabelecendo parada obrigatória antes da integração (merge).
- **Tratamento de Docker Daemon**: Se `docker` existir no `PATH` mas o daemon estiver desligado, o guard exibirá aviso orientando o início do daemon/Docker Desktop, com opção de tentar novamente ou voltar ao menu.
- **Respeito a ambientes headless**: Se o terminal não for interativo (`not sys.stdin.isatty()`), o guard não trava em prompts interativos de browser e emite mensagens claras de diagnóstico.

## Estratégia de testes

- Gates mínimos:
  - `python scripts/validate_governance.py`
  - `uv run ruff check` / `python -m ruff check`
  - `uv run pytest` / `python -m pytest`
  - `git diff --check`
- Testes automatizados em `tests/test_guard.py`:
  - Verificar renderização e escolhas do guard com executáveis presentes vs ausentes.
  - Verificar tratamento de plataforma (Windows vs Linux).
  - Verificar tratamento de `webbrowser.open` com fallback textual da URL.
  - Verificar integração com `menu.py` garantindo que o guard é acionado quando Restic ou Docker faltam.
- Testes atualizados em `tests/test_doctor.py` e `tests/test_interactive_menus.py`.

## Itens de implementação

### Item 1 — Módulo de Preflight Guard e Onboarding (`ui/guard.py`)

**Contexto:**
Necessidade de uma interface consistente para interceptar ferramentas que exigem executáveis externos ausentes.

**Ação técnica:**
Criar `src/utility_belt/ui/guard.py` com funções:
- `ensure_dependency(dep_name: str, check_fn: Callable) -> bool`
- `show_dependency_onboarding(dep_name: str, details: dict) -> None`
- Metadados de instalação para Restic e Docker com comandos e URLs para Windows e Linux.
- Ações interativas: ver comandos no terminal, abrir link no navegador e voltar.

**Critérios de aceite:**
- [ ] Retorna `True` imediatamente se a dependência estiver presente e saudável.
- [ ] Renderiza tela dedicada usando `render_header(["UTILITY BELT", tool_name, "REQUISITO AUSENTE"])` e `message("AVISO", ...)`.
- [ ] Opção 1 exibe comandos do SO sem sair da tela e aguarda confirmação antes de voltar.
- [ ] Opção 2 invoca `webbrowser.open` e imprime a URL na tela para terminais headless/sem GUI.
- [ ] Opção 0 retorna `False` e volta ao menu principal.

### Item 2 — Integração nos Menus Interativos (`menu.py`, `ui/restic_menu.py`, `ui/docker_menu.py`)

**Contexto:**
Conectar o guard ao menu principal e submenus para que o usuário seja alertado antes da execução de operações quebradas.

**Ação técnica:**
- Modificar `show_menu()` em `src/utility_belt/menu.py` para chamar o guard antes de despachar para `show_restic_menu()` e `show_docker_menu()`.
- Tratar estado específico do Docker (binário presente, mas daemon inativo).

**Critérios de aceite:**
- [ ] `escolha == "restic"` executa o guard de restic antes de abrir `show_restic_menu()`.
- [ ] `escolha == "docker"` executa o guard de docker antes de abrir `show_docker_menu()`.
- [ ] Docker com daemon inativo apresenta aviso específico e orienta iniciar o Docker Desktop.

### Item 3 — Enriquecimento do Diagnóstico (`doctor.py` e `cli.py`)

**Contexto:**
Comando `belt doctor` e tela `Sistema > Verificar ambiente` mostram apenas `[FALTA]`, sem informar comandos de instalação.

**Ação técnica:**
- Atualizar `check_restic()` e `check_docker()` em `doctor.py` para retornar dicionário com orientações de instalação (`install_guide` e `download_url`).
- Atualizar exibição em `cli.py` (`doctor()`) e `menu.py` (`_show_diagnostics()`) para exibir dicas úteis para dependências faltantes.

**Critérios de aceite:**
- [ ] `belt doctor` e `_show_diagnostics()` exibem comandos sugeridos para dependências ausentes.
- [ ] Saída `--json` do doctor preserva compatibilidade retroativa e inclui campos adicionais informativos.

### Item 4 — Cobertura de Testes Automatizados

**Contexto:**
Garantir que a nova camada de guard funcione em múltiplos ambientes sem regressões.

**Ação técnica:**
- Criar `tests/test_guard.py` com mocks para `shutil.which`, `subprocess.run` e `questionary.select`.
- Atualizar testes existentes de menus e doctor para cobrir o fluxo de preflight.

**Critérios de aceite:**
- [ ] 100% dos testes passam no `pytest`.
- [ ] Sem violações no `ruff check`.
- [ ] Sem regressões na governança (`validate_governance.py`).

## Arquivos afetados

- `src/utility_belt/ui/guard.py` (novo)
- `src/utility_belt/menu.py`
- `src/utility_belt/doctor.py`
- `src/utility_belt/cli.py`
- `tests/test_guard.py` (novo)
- `tests/test_doctor.py`
- `_project/cycles.md`
- Artefatos documentais do ciclo 008 em `_project/drafts/008_validacao_preflight_dependencias/`.

## Decomposição em issues e PRs

- **Issue**: 1 feature issue no GitHub cobrindo a implementação da validação prévia de dependências externas (preflight guard), enriquecimento do doctor e testes.
- **PR**: 1 Pull Request correspondente com rastreabilidade completa e sem merge automático.

## Dependências e blockers

- Nenhuma dependência externa nova no `pyproject.toml` (utilização da biblioteca padrão `webbrowser` e componentes existentes `questionary` e `typer`).
- Nenhum blocker técnico identificado.

## Riscos, suposições e rollback

- **Risco de dependência de GUI**: `webbrowser.open` pode não abrir navegador em ambientes SSH/WSL sem servidor X; mitigado pela impressão obrigatória da URL em formato texto.
- **Risco de latência no menu**: A checagem de executável via `shutil.which` leva frações de milissegundo e é executada somente ao clicar no item (on-demand), não atrasando a inicialização do menu principal.
- **Rollback**: Reversão da branch/PR via Git sem efeitos colaterais em dados ou configurações do usuário.

## Sequência recomendada

1. Rascunho do plano -> Revisão formal e emissão de veredito.
2. Registro de aprovação humana com base na autorização prévia para ciclo completo até a PR.
3. Criação da issue no GitHub via MCP.
4. Criação da branch `feature/issue-N` e task persistente.
5. Implementação de código e testes.
6. Validação de gates e commit semântico.
7. Publicação da branch e abertura da PR no GitHub.
8. Parada obrigatória e solicitação de autorização humana para merge.

## Referências

- Ideação 008: `_project/ideations/008_validacao_preflight_dependencias.md`
- [Restic Installation Docs](https://restic.readthedocs.io/en/stable/020_installation.html)
- [Docker Engine / Desktop Installation Docs](https://docs.docker.com/get-docker/)
- `src/utility_belt/ui/screen.py`

## Rastreabilidade

| Campo | Valor |
| :-- | :-- |
| Issue(s) | [#26](https://github.com/EuThiagoAndrade/utility-belt/issues/26) |
| PR(s) | [PR #27](https://github.com/EuThiagoAndrade/utility-belt/pull/27) |
| Branch(es) | `feature/issue-26` |
| `handoff_schema_version` | `1` |
| `handoff_id` | `EuThiagoAndrade/utility-belt+008+rascunhar_plano+preflight-guard+cf44c90` |
| Destino após conclusão | `_project/executed/008_validacao_preflight_dependencias/008_plan.md` |

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+008+rascunhar_plano+preflight-guard+cf44c90`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`
- `effect_class`: `local_mutation`
- `state_before`: ideação concluída; ciclo 008 em planejamento sem plano rascunhado.
- `state_after`: plano rascunhado em `_project/drafts/008_validacao_preflight_dependencias/008_plan.md` em estado `Rascunho`.
- `next_transition`: `rascunho -> revisão formal` (Workflow: `revisar_plano`).
- `preconditions`: ciclo 008 identificado, template `plano_implementacao.md` instanciado integralmente.
- `authority`: autorização explícita do responsável em 2026-10-14.
- `evidence`: `_project/drafts/008_validacao_preflight_dependencias/008_plan.md`.
- `acceptance`: plano completo, gates definidos, critérios de aceite rastreáveis e não-objetivos explícitos.
- `blockers`: nenhum.
- `result`: `executed`
- `next_workflow_recommended`: `revisar_plano`
- `next_workflow_authorized`: `revisar_plano`
- `actions_prohibited`: marcar `Aprovado` sem revisão formal, criar issue ou implementar antes do parecer.
- `rejection_rule`: recusar handoff ausente, incompatível ou com status promovido indevidamente.
- `logical_key`: `EuThiagoAndrade/utility-belt+008+rascunhar_plano+preflight-guard+cf44c90`
- `check_before_mutation`: verificar se diretório e arquivo de rascunho existem.
- `reconcile_existing`: atualizar o rascunho compatível sem duplicar artefatos.
- `ambiguous_state`: parar se houver conflito de plano.

## Revisão crítica

- **Data:** 2026-10-14
- **Versão revisada:** v1
- **Veredito:** `APTO PARA APROVAÇÃO`
- **Bloqueios remanescentes:** Nenhum
- **Aprovação humana pós-revisão:** `Aprovada em 2026-10-14` — autorização humana explícita do responsável ("Pode fazer o ciclo completo até o PR. Contudo me peça para autorizar o merge. Ok.")
- **Correções materiais:** Nenhuma
- **Ressalvas:** Nenhuma. Abertura do navegador em headless sempre deve imprimir a URL no terminal para não depender de GUI.

## Pós-mortem

- **Data de conclusão:** —
- **Desvios:** —
- **Lições comprovadas:** —
