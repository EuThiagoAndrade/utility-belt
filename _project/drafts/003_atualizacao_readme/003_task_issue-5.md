# Task — Issue #5: Atualizar README.md com comandos reais, modo interativo, configuração e governança

> **Ciclo:** `003`
> **Estado:** `Em andamento`
> **Tipo:** `chore`
> **Issue:** `#5`
> **Plano:** `_project/drafts/003_atualizacao_readme/003_plan.md`
> **Branch:** `chore/issue-5`
> **Worktree:** `C:\Programas\utility-belt`
> **PR:** —
> **Integração:** `Pendente`
> **Início:** 2026-09-16
> **Última atualização:** 2026-09-16
> **handoff_schema_version:** `1`
> **handoff_id:** utility-belt+003+implementar_issue+issue-5+4850576

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
- [ ] Criar commit intencional com prefixo `chore(issue-5):`.
- [ ] Publicar a branch `chore/issue-5` e abrir Pull Request para a Issue #5.

## Evidências

| Gate | Resultado |
| :-- | :-- |
| Testes | 52/52 aprovados (`pytest` 100%) |
| Validação | `validate_governance.py` (25 verificações OK, 0 falhas) |
| Estilo/Lint | `ruff check` (100% limpo) |
| `git diff --check` | Limpo (sem problemas de formatação ou whitespace) |
| Checks remotos | Pendente de publicação da PR |

## Decisões incidentais e desvios

- Nenhuma decisão incidental ou desvio identificado.

## Resultado

### Handoff de execução

- `handoff_schema_version`: `1`
- `handoff_id`: `utility-belt+003+implementar_issue+issue-5+4850576`
- `identity_source`: `utility-belt + 003 + implementar_issue + issue-5 + 4850576`
- `effect_class`: `local_mutation`
- `state_before`: `README.md desatualizado; issue #5 aberta no GitHub; branch chore/issue-5 criada.`
- `state_after`: `Task persistente criada; implementação em andamento.`
- `next_transition`: `implementação e testes -> publicação de PR`
- `preconditions`: `Issue #5 aberta e autorizada pelo responsável.`
- `authority`: `Autorização explícita do responsável em 2026-09-16.`
- `evidence`: `_project/drafts/003_atualizacao_readme/003_task_issue-5.md`
- `acceptance`: `Task persistente em conformidade com .agent/templates/task.md.`
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
