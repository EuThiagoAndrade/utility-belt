# Task — Issue #29: feat: adicionar ferramentas dev janitor e git-tidy (ciclo 009)

> **Ciclo:** `009`
> **Estado:** `Em andamento`
> **Tipo:** `feature`
> **Issue:** `#29`
> **Plano:** `_project/drafts/009_ferramentas_dev_janitor_git_tidy/009_plan.md`
> **Branch:** `feature/issue-29`
> **Worktree:** `c:\Programas\utility-belt`
> **PR:** [#30](https://github.com/EuThiagoAndrade/utility-belt/pull/30)
> **Integração:** `Pendente`
> **Início:** 2026-10-17
> **Última atualização:** 2026-10-17
> **handoff_schema_version:** `1`
> **handoff_id:** `EuThiagoAndrade/utility-belt+009+implementar_issue+issue-29+e68aa39`

## Objetivo

Implementar o módulo `belt dev` reunindo:
1. `janitor`: limpeza seletiva e rápida de caches/dependências (`node_modules`, `target`, `.venv`, `.pytest_cache`, etc.) com heurística de atividade e `--dry-run`.
2. `git-tidy`: higienização de branches locais e remotas com suporte a *Squash & Merge* órfãos, proteção de branches canônicas/HEAD e suporte a `--dry-run`.
3. Menu TUI MS-DOS `src/utility_belt/ui/dev_menu.py`, integração ao menu principal, catálogo declarativo e diagnóstico `doctor.py`.

## Escopo autorizado

- `src/utility_belt/dev/__init__.py`
- `src/utility_belt/dev/janitor.py`
- `src/utility_belt/dev/git_tidy.py`
- `src/utility_belt/ui/dev_menu.py`
- `src/utility_belt/cli.py`
- `src/utility_belt/ui/menu.py`
- `src/utility_belt/catalog.py`
- `src/utility_belt/doctor.py`
- Testes automatizados correspondentes

## Execução

- [x] Implementar `src/utility_belt/dev/janitor.py` (scan com poda de busca, cálculo de tamanho, filtro de modificação recente e remoção segura).
- [x] Implementar `src/utility_belt/dev/git_tidy.py` (inspeção local/remota, proteção inviolável de branches canônicas, detecção de gone/squash e exclusão segura).
- [x] Implementar `src/utility_belt/ui/dev_menu.py` com telas MS-DOS padronizadas usando `screen.py`.
- [x] Integrar comandos no `src/utility_belt/cli.py`, submenu em `src/utility_belt/ui/menu.py`, ferramentas em `src/utility_belt/catalog.py` e diagnóstico em `src/utility_belt/doctor.py`.
- [x] Criar testes unitários e de integração (`test_dev_janitor.py`, `test_dev_git_tidy.py`, `test_dev_cli.py`, `test_interactive_menus.py`).
- [x] Executar gates locais: `scripts/validate_governance.py`, `ruff check`, `pytest`, `git diff --check`.
- [x] Publicar branch `feature/issue-29` e abrir PR vinculada à Issue #29 ([PR #30](https://github.com/EuThiagoAndrade/utility-belt/pull/30)).

## Evidências

| Gate | Resultado |
| :-- | :-- |
| Testes (`pytest`) | 241 passaram, 36 ignorados, 0 falhas (46.81s) |
| Validação de governança | 37 OK \| 0 Avisos \| 0 Falhas (`validate_governance.py`) |
| Lint / Formatação (`ruff`) | Aprovado (0 erros) |
| `git diff --check` | Aprovado (0 erros) |
| Checks remotos de CI | Aguardando publicação da PR |

## Decisões incidentais e desvios

- Nenhuma dependência externa adicionada no `pyproject.toml`; utilização exclusiva de módulos padrão do Python e binários do sistema (`git`).
- Na deleção de arquivos no Windows pelo `janitor`, implementar tratamento de atributos somente-leitura com `os.chmod` no callback `on_exc`/`onerror` do `shutil.rmtree`.
- Na deleção remota do `git-tidy`, classificar como `destructive` com confirmação explícita no terminal e suporte a `--dry-run`.

## Resultado

### Handoff de execução

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+009+implementar_issue+issue-29+e68aa39`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`
- `effect_class`: `local_mutation -> remote_mutation`
- `state_before`: issue #29 aberta e autorizada; branch feature/issue-29 criada.
- `state_after`: implementação em andamento.
- `next_transition`: `implementação -> validação dos gates -> abertura de PR`.
- `preconditions`: plano aprovado, issue #29 existente, branch correspondente e task inicializada.
- `authority`: autorização explícita do responsável em 2026-10-17.
- `evidence`: `_project/drafts/009_ferramentas_dev_janitor_git_tidy/009_task_issue-29.md`.
- `acceptance`: critérios de aceite da issue #29 atendidos e gates validados.
- `blockers`: nenhum.
- `result`: `executed`
- `next_workflow_recommended`: `abertura_pr`
- `next_workflow_authorized`: implementação e abertura de PR (merge bloqueado até autorização posterior).
- `actions_prohibited`: merge automático da PR.
- `rejection_rule`: o receptor recusa handoff ausente, incompatível ou sem rastreabilidade.
- `logical_key`: `EuThiagoAndrade/utility-belt+009+implementar_issue+issue-29+e68aa39`
- `check_before_mutation`: verificar integridade de feature/issue-29 e task.
- `reconcile_existing`: atualizar esta task persistente durante a implementação.
- `ambiguous_state`: parar antes de mutações caso haja inconsistência de branch ou issue.
