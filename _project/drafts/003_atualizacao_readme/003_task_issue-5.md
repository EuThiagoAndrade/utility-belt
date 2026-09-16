# Task — Issue #5: Atualizar README.md com comandos reais, modo interativo, configuração e governança

> **Ciclo:** `003`
> **Estado:** `PR Aberta`
> **Tipo:** `chore`
> **Issue:** `#5`
> **Plano:** `_project/drafts/003_atualizacao_readme/003_plan.md`
> **Branch:** `chore/issue-5`
> **Worktree:** `C:\Programas\utility-belt`
> **PR:** [#6](https://github.com/EuThiagoAndrade/utility-belt/pull/6)
> **Integração:** `Pendente`
> **Início:** 2026-09-16
> **Última atualização:** 2026-09-16
> **handoff_schema_version:** `1`
> **handoff_id:** utility-belt+003+implementar_issue+issue-5+b7f1547

## Objetivo

Reestruturar e enriquecer o `README.md` da raiz do repositório para refletir as reais capacidades da CLI do Utility Belt (`belt`), incorporando os avanços entregues nos Ciclos 000, 001 e 002.

## Escopo autorizado

- Reestruturar o `README.md` com:
  1. Apresentação do produto, arquitetura de catálogo declarativo (`tool.toml`) e classificação de risco (`read`, `write`, `destructive`).
  2. Experiência guiada TUI via `questionary` como comportamento padrão de `belt` em terminais interativos (TTY).
  3. Referência completa dos subcomandos e flags de Docker (`export`, `import`, `menu`) e Restic (`backup`, `restore`, `check`, `snapshots`, `init`, `migrate-config`, `menu`).
  4. Documentação de `belt show-completion` com shells suportados (`powershell`, `bash`, `zsh`, `fish`).
  5. Guia de persistência e perfis em `config.toml` (`platformdirs` / `tomli-w`).
  6. Guia para desenvolvedores cobrindo ambiente virtual (`uv`), testes (`pytest`), linters (`ruff`), script de governança (`scripts/validate_governance.py`) e autoridade canônica em `_project/README.md`.
  7. Menção explícita de que Docker e Restic são dependências externas no sistema operacional host.

## Execução

- [x] Instanciar a task persistente em `_project/drafts/003_atualizacao_readme/003_task_issue-5.md`.
- [x] Atualizar o `README.md` com a nova estrutura completa e precisa.
- [x] Executar os gates locais: `python scripts/validate_governance.py`, `pytest`, `ruff check`, `git diff --check`.
- [x] Criar commit intencional com prefixo `chore(issue-5):` (`b7f1547`).
- [x] Publicar a branch `chore/issue-5` e abrir Pull Request para a Issue #5 ([PR #6](https://github.com/EuThiagoAndrade/utility-belt/pull/6)).

## Evidências

| Gate | Resultado |
| :-- | :-- |
| Testes | 52/52 aprovados (`pytest` 100%) |
| Validação | `validate_governance.py` (25 verificações OK, 0 falhas) |
| Estilo/Lint | `ruff check` (100% limpo) |
| `git diff --check` | Limpo (sem problemas de formatação ou whitespace) |
| Checks remotos | Sem checks de CI configurados no repositório |

## Decisões incidentais e desvios

- Nenhuma decisão incidental ou desvio identificado.

## Resultado

### Handoff de execução

- `handoff_schema_version`: `1`
- `handoff_id`: `utility-belt+003+implementar_issue+issue-5+b7f1547`
- `identity_source`: `utility-belt + 003 + implementar_issue + issue-5 + b7f1547`
- `effect_class`: `local_mutation -> remote_mutation`
- `state_before`: `README.md desatualizado; issue #5 aberta no GitHub; branch chore/issue-5 criada.`
- `state_after`: `README.md atualizado; gates validados; commit b7f1547 publicado; PR #6 aberta e aguardando revisão.`
- `next_transition`: `PR -> revisão humana -> merge/integração autorizada`
- `preconditions`: `PR #6 aberta no GitHub, vinculada à Issue #5 e com gates 100% satisfeitos.`
- `authority`: `Autorização explícita do responsável em 2026-09-16 para implementar a issue #5.`
- `evidence`: `https://github.com/EuThiagoAndrade/utility-belt/pull/6`
- `acceptance`: `README.md cobre todos os critérios de aceite da issue #5; gates locais executados com 100% de aprovação.`
- `blockers`: `nenhum`
- `result`: `executed`
- `next_workflow_recommended`: `concluir implementação e abrir PR`
- `next_workflow_authorized`: `implementação da issue #5 autorizada`
- `actions_prohibited`: `fazer merge automático sem revisão humana da PR.`
- `rejection_rule`: `recusar handoff se gates falharem ou se houver alteração fora de escopo.`
- `logical_key`: `utility-belt+003+implementar_issue+issue-5+4850576`
- `check_before_mutation`: `verificado que a branch chore/issue-5 está ativa.`
- `reconcile_existing`: `iniciada a task persistente.`
- `ambiguous_state`: `interromper se houver conflito de branch ou issue.`
