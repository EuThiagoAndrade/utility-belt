# Task — Issue #46: orientar erros e desbloqueio assistido no Restic

> **Ciclo:** `013`
> **Estado:** `Em andamento`
> **Tipo:** `feature`
> **Issue:** `#46`
> **Plano:** `_project/drafts/013_tratamento_erros_restic/013_plan.md`
> **Branch:** `feature/issue-46`
> **Worktree:** `c:\Programas\utility-belt`
> **PR:** —
> **Integração:** `Pendente`
> **Início:** 2026-11-03
> **Última atualização:** 2026-11-03
> **handoff_schema_version:** `1`
> **handoff_id:** `EuThiagoAndrade/utility-belt+013+implementar_issue+issue-46+c5a679a3e6a2/v1-in-progress`

## Objetivo

Explicar erros e resultados incompletos do Restic em linguagem acionável, preservar o diagnóstico e código de saída originais, e oferecer `unlock` assistido quando houver falha de lock, sem iniciar recuperação ou repetição de operação sem decisão explícita do usuário.

## Escopo autorizado

1. **Item 1 — Diagnóstico acionável e preservação dos resultados**: Helper específico (`src/utility_belt/restic_diagnostics.py`) integrado ao `ResticController` e a `ui/restic_menu.py`. Preservação da saída bruta e dos códigos de saída originais (inclusive código 3 existente). No CLI, orientação suplementar ao final em `stderr` sem prompt interativo; no menu, orientação contextual. Na restauração com erro, informar falha, exibir detalhe e caminho reportado pelo Restic, orientar conferência do destino e nunca rotular como restauração completa.
2. **Item 2 — Subcomando unlock e recuperação assistida**: Expor `belt restic unlock` no motor (`tools/restic_backup/main.py`), no adaptador CLI (`adapters/restic.py`) e no menu (`ui/restic_menu.py`) com `--repo` e `--profile`. No menu, oferecer a ação explícita `Desbloquear locks obsoletos` sob confirmação. Em caso de código 11, apresentar opções `Aguardar e tentar novamente` (com `--retry-lock 1m` por decisão única do usuário), `Executar unlock` (com confirmação e sem `--remove-all`) e `Voltar`. Preservar o retorno da operação original sem repetição automática após desbloqueio.
3. **Item 3 — Documentação e cobertura do fluxo**: Atualizar o `README.md` (seção Restic) documentando `unlock` e a interpretação de restauração parcial/incompleta. Implementar testes cobrindo o helper, adaptador, menu interativo e códigos de erro/retorno.
4. **Ressalvas vinculantes incorporadas (R1–R3)**:
   - **R1**: Isolamento de testes com mock de `run_tool` em `test_belt_restic_with_subcommand_does_not_open_menu` (e Docker) para não acessar o repositório/configuração real do host ou bloquear em `getpass.getpass()`; suportar `--non-interactive` em `unlock` e recusar `getpass` quando `stdin` não for TTY.
   - **R2**: Streaming de `stdout`/progresso em tempo real (sem buffer) com captura apenas de `stderr`, reemitindo `stderr` integralmente antes do resumo suplementar; invocar `verify_repo_id()` com `--no-lock` (`restic cat config --no-lock`) para não bloquear em lock existente.
   - **R3**: Semântica estrita de retorno em `ui/restic_menu.py`: `do_restore()` só pode informar sucesso ou oferecer abrir pasta quando `result.returncode == 0`; operações com código diferente de zero são sempre tratadas como não concluídas.

## Execução

- [x] Criar helper `src/utility_belt/restic_diagnostics.py` com análise de código de saída (11, restore error com path, code 3, desconhecidos) e formatação de diagnóstico.
- [x] Atualizar `src/utility_belt/tools/restic_backup/main.py` com comando `unlock`, streaming de stdout e captura de stderr em tempo real (R2), `--no-lock` em `verify_repo_id()` (R2) e verificação não-interativa / TTY em `get_password()` (R1).
- [x] Atualizar `src/utility_belt/adapters/restic.py` com subcomando `unlock` aceitando `--repo`, `--profile` e repassando argumentos.
- [x] Atualizar `src/utility_belt/ui/restic_menu.py` com opção `Desbloquear locks obsoletos`, tratamento de código 11 com opções contextuais (aguardar com `--retry-lock 1m`, unlock com confirmação, voltar), sem repetição automática e com validação estrita em `do_restore()` (R3).
- [x] Atualizar `README.md` documentando `belt restic unlock` e orientações de restauração e locks.
- [x] Isolar testes em `tests/test_interactive_menus.py` com mock de `run_tool` (R1).
- [x] Criar testes unitários para o helper em `tests/test_restic_diagnostics.py`.
- [x] Atualizar `tests/test_restic_adapter.py` cobrindo o novo subcomando `unlock`.
- [x] Criar testes do menu em `tests/test_restic_menu.py` cobrindo unlock, código 11, retry-lock e restore incompleto.
- [x] Executar e registrar os 5 gates locais: `validate_governance.py`, `ruff check`, `pytest`, `git diff --check`, `git status --short`.
- [ ] Publicar branch `feature/issue-46` e abrir PR vinculada à Issue #46.

## Evidências

| Gate | Resultado |
| :-- | :-- |
| Testes (`pytest`) | 275 passed, 36 skipped em 53.43s (100% sucesso) |
| Validação de governança (`validate_governance.py`) | 46 verificações (45 OK, 1 Aviso esperado de ciclo, 0 Falhas) |
| Linter (`ruff check`) | All checks passed! (0 avisos/erros) |
| `git diff --check` | 100% limpo |
| Checks remotos | Pendente de abertura da PR |

## Decisões incidentais e desvios

- No extrator de caminhos de restauração em `restic_diagnostics.py`, ajustado o parser para respeitar letras de unidade do Windows (ex.: `C:\...`), buscando o delimitador `:` subsequente ao prefixo de disco.
- Em `main.py` e `restic_menu.py`, adicionada guarda de tipo `isinstance(res.stderr, str)` antes de invocar `sys.stderr.write()`, blindando a execução contra objetos mock nos testes.

## Resultado

### Handoff de execução

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+013+implementar_issue+issue-46+c5a679a3e6a2/v1-in-progress`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision` = `EuThiagoAndrade/utility-belt + 013 + implementar_issue + issue-46 + c5a679a3e6a2068fc28b3bb63fd2794d6c671cdf/v1-in-progress`
- `effect_class`: `local_mutation`
- `state_before`: issue #46 criada, branch `feature/issue-46` criada, plano v1 `Em Execução`, implementação iniciada.
- `state_after`: implementação em andamento.
- `next_transition`: `implementação -> validação dos gates -> abertura de PR`.
- `preconditions`: implementação dos itens 1, 2 e 3 e validação dos gates locais.
- `authority`: responsável humano (autorização para implementação da Issue #46 em 2026-11-03).
- `evidence`: esta task, arquivos modificados e testes criados.
- `acceptance`: todos os critérios de aceite da Issue #46 e do plano atendidos.
- `blockers`: nenhum bloqueador técnico.
- `result`: `in_progress`
- `next_workflow_recommended`: conclusão da implementação e publicação de PR.
- `next_workflow_authorized`: apenas implementação e abertura de PR (sem merge automático).
- `actions_prohibited`: merge automático da PR ou ampliação de escopo para ferramentas fora do Restic.
- `rejection_rule`: o receptor recusa handoff ausente, incompatível, contraditório ou sem evidência material.
- `logical_key`: `EuThiagoAndrade/utility-belt+013+implementar_issue+issue-46+c5a679a3e6a2`
- `check_before_mutation`: verificar branch, issue e plano antes de alterações.
- `reconcile_existing`: task mantida em `_project/drafts/013_tratamento_erros_restic/013_task_issue-46.md`.
- `ambiguous_state`: parar se houver divergência entre issue, task e plano.
