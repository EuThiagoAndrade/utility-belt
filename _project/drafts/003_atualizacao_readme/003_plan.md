# Plano de Implementação — Atualização do README com a CLI Real

> **Ciclo:** `003`
> **Status:** `Aprovado`
> **Versão:** `v1`
> **Data de criação:** 2026-09-16
> **Última atualização:** 2026-09-16
> **Tipo:** `chore`
> **Prioridade:** `P2`
> **Revisão formal:** `Concluída`
> **Veredito da revisão:** `APTO PARA APROVAÇÃO`
> **Aprovação humana pós-revisão:** `Aprovada em 2026-09-16`

## Objetivo

Atualizar o `README.md` principal do repositório para refletir com exatidão as capacidades, arquitetura, comandos e modos de operação reais da CLI do Utility Belt (`belt`), incorporando os avanços entregues nos Ciclos `000` (Fundação CLI), `001` (Menus Interativos com Questionary) e `002` (Governança Canônica).

## Contexto e baseline

O `README.md` atual possui apenas 38 linhas e foi concebido no início do ciclo `000` como um documento preliminar mínimo. Desde então, o projeto evoluiu significativamente:
- **Ciclo 001:** Implementou a experiência interativa TUI completa via `questionary`, tornando o menu guiado o comportamento padrão ao executar `belt`, `belt docker` ou `belt restic` sem argumentos em terminal interativo (TTY).
- **Ciclo 002:** Estabeleceu o modelo de governança canônica agnóstica (`_project/`, `.agent/`), validações de integridade em Python (`scripts/validate_governance.py`), convenções de ciclo de vida e gates de qualidade (`pytest`, `ruff`).
- **Comandos existentes na CLI:** A CLI real conta com múltiplos comandos e opções essenciais que não constam no README atual, incluindo comandos de snapshots, inicialização e migração de configuração no Restic, opções de visualização (`--json`, `--all`), diagnóstico avançado (`belt doctor [alvo]`) e instruções de autocompletar para shells (`belt show-completion`).

O `README.md` atual omite essas capacidades, transmitindo uma visão defasada e incompleta do produto.

## Escopo

### Dentro do escopo

- Reestruturar o `README.md` da raiz com as seguintes seções bem delimitadas:
  1. **Apresentação e Proposta de Valor:** Explicar o que é o Utility Belt, suporte multiplataforma (Windows e Linux) e o conceito de catálogo declarativo baseado em manifestos (`tool.toml`) com metadados de risco (`read`, `write`, `destructive`).
  2. **Instalação e Atualização:** Manter instruções claras de instalação isolada e upgrade via `uv tool`.
  3. **Experiência Interativa (TUI):** Destacar a navegação guiada interativa via `questionary` como comportamento padrão de `belt` em terminais TTY.
  4. **Referência da CLI (Modo Direto / Scriptable):**
     - Comandos fundamentais: `belt`, `belt --help`, `belt --version` / `-v`, `belt list [--all] [--json]`, `belt doctor [alvo] [--json]`, `belt menu`, `belt show-completion [shell]`, `belt run <tool_id> [--non-interactive]`.
     - Subcomandos Docker: `belt docker export`, `belt docker import`, `belt docker menu` e flags (`--dry-run`, `--run`, `--all`, `-i`, `-o`).
     - Subcomandos Restic: `belt restic backup`, `belt restic restore`, `belt restic check`, `belt restic snapshots`, `belt restic init`, `belt restic migrate-config`, `belt restic menu` e flags (`--profile`, `--dry-run`, `--non-interactive`).
  5. **Configuração e Perfis:** Explicar a persistência atômica via `platformdirs` / `tomli-w` (`config.toml`) e suporte a múltiplos perfis no Restic.
  6. **Desenvolvimento, Testes e Governança:** Instruções para desenvolvedores rodarem localmente (`uv sync`), executarem os testes (`pytest`), linters (`ruff`) e a validação de governança (`scripts/validate_governance.py`), com link explícito para `_project/README.md`.

### Fora do escopo

- Alterações de código funcional no pacote `utility_belt`.
- Adição ou remoção de comandos na CLI.
- Criação de sites externos de documentação (ex.: MkDocs) ou diretório `docs/`.
- Modificação das autoridades ou adapters de governança (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`).

## Decisões e autoridades

- **ADR-001:** Governança agnóstica com adapters de descoberta.
- **ADR-002:** Arquitetura CLI distribuível via `uv`, `typer`, `platformdirs` e `tomli-w`.
- **Solicitação direta do responsável (2026-09-16):** Autorização explícita para dispensar ideação prévia e iniciar o Ciclo 003 diretamente com o workflow `rascunhar_plano.md`.

## Estratégia de testes

- Conferência cruzada estrita entre as seções documentadas no `README.md` e as assinaturas reais da CLI em `src/utility_belt/cli.py`, `src/utility_belt/adapters/docker.py` e `src/utility_belt/adapters/restic.py`.
- Validação estática de links internos e sintaxe Markdown.
- Execução dos gates de qualidade e governança:
  - `python scripts/validate_governance.py` (25 verificações de integridade documental).
  - `python -m pytest tests/test_governance.py` (validação automatizada de governança).
  - `git diff --check` (conferência de formatação e quebras de linha).

## Itens de implementação

### Item 1 — Atualização integral do README.md com a CLI real e governança

**Contexto:**
O `README.md` existente não reflete a TUI do ciclo 001, omite subcomandos reais da CLI e não apresenta o fluxo de desenvolvimento e governança do ciclo 002.

**Ação técnica:**
Reescrever o `README.md` na raiz do repositório incorporando a experiência TUI interativa, a referência completa de comandos/flags, o modelo de configuração e perfis, e o guia de desenvolvimento local e governança canônica.

**Critérios de aceite:**
- [ ] O `README.md` evidencia que executar `belt` sem subcomandos em TTY abre o menu interativo (`questionary`).
- [ ] Todos os subcomandos e flags de Docker (`export`, `import`, `menu`) e Restic (`backup`, `restore`, `check`, `snapshots`, `init`, `migrate-config`, `menu`) estão fielmente documentados.
- [ ] As opções de `belt list` (`--all`, `--json`) e `belt doctor` (`[target]`, `--json`) constam no documento.
- [ ] O comando `belt show-completion` e seus shells suportados são explicados.
- [ ] O modelo de configuração (`config.toml` via `platformdirs`) e perfis é introduzido.
- [ ] Há uma seção para desenvolvedores com os gates `pytest`, `ruff`, `validate_governance.py` e link para `_project/README.md`.
- [ ] Nenhum comando inexistente ou assinatura divergente é incluído.

## Arquivos afetados

- `_project/cycles.md` (registro do Ciclo 003 em planejamento)
- `_project/drafts/003_atualizacao_readme/003_plan.md` (este plano de implementação)
- `README.md` (a ser modificado na entrega da issue)

## Decomposição em issues e PRs

- **Issue 1 (Chore/Docs):** [#5 — chore(cycle-003): atualizar README.md com comandos reais, modo interativo, configuracao e governanca](https://github.com/EuThiagoAndrade/utility-belt/issues/5)
- **PR 1:** Branch `chore/issue-5` implementando a revisão do `README.md`.
- **PR de Encerramento:** Branch `chore/cycle-003-closure` movendo o ciclo para `_project/executed/003_atualizacao_readme/` e consolidando a rastreabilidade.

## Dependências e blockers

- **Dependências:** Nenhuma dependência externa. Todas as funcionalidades a documentar já estão implementadas e testadas na base de código.
- **Blockers:** Nenhum.

## Riscos, suposições e rollback

- **Risco:** Documentar comandos ou parâmetros com nomenclatura divergente da CLI real do Typer.
  - *Mitigação:* Validação cruzada com `src/utility_belt/cli.py` e os módulos de adaptadores durante a redação.
- **Suposição:** O `README.md` deve atender tanto o usuário final da CLI quanto o desenvolvedor interessado na estrutura do projeto.
- **Rollback:** Reversão simples do commit via Git caso qualquer inconsistência seja identificada.

## Sequência recomendada

1. Submeter este plano `003_plan.md` ao workflow `.agent/workflows/revisar_plano.md`. (Concluído)
2. Realizar a auditoria crítica e emitir o relatório de revisão com o veredito formal. (Concluído — APTO PARA APROVAÇÃO)
3. Obter aprovação humana pós-revisão. (Concluído — Aprovado pelo responsável em 2026-09-16)
4. Criar a issue correspondente no GitHub. (Concluído — Issue #5)
5. Criar a branch de implementação da issue (`chore/issue-5`), registrar a task persistente, atualizar o `README.md`, executar os gates e abrir PR.
6. Integrar a PR de implementação e executar a PR de closure do ciclo 003.

## Referências

- `_project/README.md` (Autoridade de ciclo de vida e estrutura)
- `.agent/ai_behavior.md` (Autoridade de comportamento de agentes)
- `_project/executed/000_fundacao_cli_distribuicao/000_plan.md`
- `_project/executed/001_menus_interativos/001_plan.md`
- `_project/executed/002_bootstrap_governanca_canonica/002_plan.md`
- `src/utility_belt/cli.py`
- `src/utility_belt/adapters/docker.py`
- `src/utility_belt/adapters/restic.py`

## Rastreabilidade

| Campo | Valor |
| :-- | :-- |
| Issue(s) | [#5](https://github.com/EuThiagoAndrade/utility-belt/issues/5) |
| PR(s) | — |
| Branch(es) | `chore/cycle-003-plan`, `chore/issue-5` (prevista) |
| `handoff_schema_version` | `1` |
| `handoff_id` | `utility-belt+003+criar_issues+atualizacao_readme+4850576` |
| Destino após conclusão | `_project/executed/003_atualizacao_readme/003_plan.md` |

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: `utility-belt+003+criar_issues+atualizacao_readme+4850576`
- `identity_source`: `utility-belt + 003 + criar_issues + atualizacao_readme + 4850576`
- `effect_class`: `remote_mutation`
- `state_before`: `Plano Aprovado pelo responsável; nenhuma issue aberta no GitHub para o Ciclo 003.`
- `state_after`: `Issue #5 criada no GitHub com rastreabilidade total ao Ciclo 003 e critérios do Issue Form chore.yml.`
- `next_transition`: `issue -> implementação autorizada`
- `preconditions`: `Plano aprovado, issue criada e verificada no GitHub, branch prevista identificada.`
- `authority`: `Autorização explícita do responsável em 2026-09-16 para aprovar o plano e criar as issues.`
- `evidence`: `https://github.com/EuThiagoAndrade/utility-belt/issues/5`
- `acceptance`: `Issue #5 criada com labels ['chore'], checklist canônico e vínculo explícito ao plano aprovado.`
- `blockers`: `nenhum`
- `result`: `executed`
- `next_workflow_recommended`: `implementar_issue (.agent/workflows/implementar_issue.md)`
- `next_workflow_authorized`: `nenhum (aguarda autorização explícita para iniciar a implementação)`
- `actions_prohibited`: `implementar alterações em README.md, abrir PR ou integrar PR sem autorização prévia de execução.`
- `rejection_rule`: `o receptor recusa handoff ausente, incompatível, sem issue canônica verificável no GitHub ou sem autorização expressa.`
- `logical_key`: `utility-belt+003+criar_issues+atualizacao_readme(chore+issue-5)+4850576`
- `check_before_mutation`: `consultado repositório remoto via list_issues/gh; confirmado 0 issues prévias.`
- `reconcile_existing`: `criada issue canônica #5 e atualizada a rastreabilidade documental local.`
- `ambiguous_state`: `interromper caso houvesse duplicidade ou issue concorrente com o mesmo objetivo.`

## Revisão crítica

- **Data:** 2026-09-16
- **Versão revisada:** `v1`
- **Veredito:** `APTO PARA APROVAÇÃO`
- **Bloqueios remanescentes:** Nenhum
- **Aprovação humana pós-revisão:** Aprovada em 2026-09-16
- **Correções materiais:** Nenhuma correção estrutural exigida no plano rascunhado.
- **Ressalvas:**
  1. *Comando de autocompletar:* Garantir que a documentação de `belt show-completion` liste explicitamente os shells homologados (`powershell`, `bash`, `zsh`, `fish`).
  2. *Dependências de terceiros:* Deixar claro no README que Docker e Restic são pré-requisitos externos no sistema operacional (o `belt` atua como orquestrador e adaptador, não empacota os binários de docker/restic internamente).
  3. *Comandos de desenvolvimento:* No guia de desenvolvimento, especificar o uso do ambiente virtual gerenciado por `uv` (`uv run pytest`, `uv run ruff check`, `python scripts/validate_governance.py`).

## Pós-mortem

- **Data de conclusão:** —
- **Desvios:** —
- **Lições comprovadas:** —
