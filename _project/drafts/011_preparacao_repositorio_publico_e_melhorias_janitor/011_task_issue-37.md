# Task — Issue #37: chore: preparar repositorio publico com licenca, metadados, comunidade e readme (ciclo 011)

> **Ciclo:** `011`
> **Estado:** `Em andamento`
> **Tipo:** `chore`
> **Issue:** `#37`
> **Plano:** `_project/drafts/011_preparacao_repositorio_publico_e_melhorias_janitor/011_plan.md`
> **Branch:** `chore/issue-37`
> **Worktree:** `C:\Programas\utility-belt`
> **PR:** —
> **Integração:** `Pendente`
> **Início:** 2026-10-21
> **Última atualização:** 2026-10-21
> **handoff_schema_version:** `1`
> **handoff_id:** `EuThiagoAndrade/utility-belt+011+implementar_issue+chore-issue-37+daec63c`

## Objetivo

Preparar o repositório `utility-belt` para abertura pública no GitHub com conformidade jurídica completa (licença MIT), documentação de comunidade (`CONTRIBUTING.md` e `SECURITY.md`), metadados enriquecidos no `pyproject.toml` (incluindo `"/LICENSE"` no sdist por R3), blindagem do `.gitignore` contra credenciais e logs, e atualização integral do `README.md` documentando o módulo `belt dev` e seus comandos com rigor (Ressalva R4), respeitando o veto irrestrito a badges de CI.

## Escopo autorizado

1. **Item 2 do Plano — Licença, Metadados e `.gitignore`**:
   - Criação de `LICENSE` MIT atribuída a Thiago Andrade (2026).
   - Atualização de `pyproject.toml`:
     - `license = "MIT"`
     - Tabela `[project.urls]` (`Homepage`, `Repository`, `Issues`, `Changelog`).
     - Lista de `classifiers` oficiais do PyPI.
     - Lista de `keywords` para indexação.
     - Inclusão de `"/LICENSE"` na lista `include` de `[tool.hatch.build.targets.sdist]` (Ressalva R3).
   - Atualização do `.gitignore`: inclusão de `.env*`, `*.local`, `*.log`, `*.pem`, `*.key`.
2. **Item 3 do Plano — Documentação Comunitária**:
   - Criação de `CONTRIBUTING.md`: setup local com `uv sync`, suíte de testes e gates, convenção de commits e branches.
   - Criação de `SECURITY.md`: reporte responsável de vulnerabilidades via GitHub Private Vulnerability Reporting.
3. **Item 4 do Plano — Atualização Abrangente do `README.md`**:
   - Badges no topo: versão (`v0.5.0`), Python (`3.11+`), licença (`MIT`) — **VETO EXPLÍCITO À BADGE DE STATUS DO CI**.
   - Seção *Recursos Principais*: inclusão do módulo Ferramentas de Desenvolvimento (`belt dev`).
   - Seção *Experiência Interativa (TUI)*: correção das opções do menu principal (`[4] Desenvolvimento`, `[5] Sistema`) e inclusão de atalhos (`belt dev menu`, `belt dev`).
   - Seção *Referência da CLI*: subseção completa `### Ferramentas de Desenvolvimento (belt dev)` documentando `janitor`, `git-tidy`, `menu`, flags (`--dry-run`, `--days/-d`, `--yes/-y`, `--remote`, `--all`), códigos de retorno (`0`, `1`, `2`) e catálogo (Ressalva R4).
   - Seção *Licença*: apontamento formal para o arquivo `LICENSE` MIT.
4. **Gates Mínimos e Validação**:
   - `uv run python scripts/validate_governance.py`
   - `uv run ruff check`
   - `uv run pytest`
   - `git diff --check`
   - `git status --short`
   - `uv build` e `uv lock`

## Execução

- [x] Item 1: Criar arquivo `LICENSE` MIT.
- [x] Item 2: Atualizar `pyproject.toml` com licença, URLs, classifiers, keywords e `"/LICENSE"` no sdist.
- [x] Item 3: Atualizar `.gitignore` defensivo contra segredos e logs.
- [x] Item 4: Criar `CONTRIBUTING.md` e `SECURITY.md`.
- [x] Item 5: Atualizar `README.md` de forma abrangente sem badge de CI.
- [x] Item 6: Executar todos os 5 gates locais mínimos e validações de build.
- [ ] Item 7: Fazer commit semântico `chore(issue-37): preparar repositorio publico com licenca, metadados, comunidade e readme` via staging seletivo.
- [ ] Item 8: Publicar branch `chore/issue-37` e abrir PR vinculada à issue #37.

## Evidências

| Gate | Resultado |
| :-- | :-- |
| `uv run python scripts/validate_governance.py` | 41 OK \| 0 Avisos \| 0 Falhas |
| `uv run ruff check` | All checks passed! |
| `uv run pytest` | 253 passed, 36 skipped, 1 warning in 51.21s |
| `git diff --check` | Limpo |
| `git status --short` | Staging seletivo isolado |
| `uv build` | Sucesso (utility_belt-0.5.0 tar.gz e whl) |
| `uv lock` | Resolvido (26 packages in 1ms) |
| Checks remotos | Pendente (após PR) |

## Decisões incidentais e desvios

- Ressalva R1: Tipo semântico `chore`, branch `chore/issue-37` e commit `chore(issue-37): ...`.
- Ressalva R2: Integrada após a Issue 1 e release v0.5.0, refletindo a versão vigente `v0.5.0` nas badges sem defasagem.
- Ressalva R3: `"/LICENSE"` incluído no alvo `sdist` de `pyproject.toml`.
- Ressalva R4: Todas as opções reais expostas por `src/utility_belt/adapters/dev.py` documentadas detalhadamente.
- Ressalva R5: Execução completa dos 5 gates mínimos registrada com evidências materiais.

## Resultado

### Handoff de execução

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+011+implementar_issue+chore-issue-37+daec63c`
- `identity_source`: `EuThiagoAndrade/utility-belt + 011 + implementar_issue + chore-issue-37 + daec63c`
- `effect_class`: `local_mutation -> remote_mutation`
- `state_before`: issue #37 aberta, repositório sem LICENSE, pyproject.toml sem URLs/classifiers/keywords, README defasado sem belt dev.
- `state_after`: implementação em andamento.
- `next_transition`: `implementação -> validação de gates -> publicação de PR`.
- `preconditions`: issue #37 aberta, autorização concedida em 2026-10-21.
- `authority`: responsável humano do repositório.
- `evidence`: `_project/drafts/011_preparacao_repositorio_publico_e_melhorias_janitor/011_task_issue-37.md`.
- `acceptance`: conformidade de comunidade, metadados e documentação sem badge de CI.
- `blockers`: nenhum.
- `result`: `not_executed`
- `next_workflow_recommended`: abrir PR após validação dos gates locais.
- `next_workflow_authorized`: implementação e abertura de PR autorizadas; merge pendente.
- `actions_prohibited`: fazer merge sem aprovação humana.
- `rejection_rule`: recusar handoff com gates incompletos ou badge de CI incluída.
- `logical_key`: `EuThiagoAndrade/utility-belt+011+implementar_issue+chore-issue-37+daec63c`
- `check_before_mutation`: verificar branch limpa e issue #37 aberta.
- `reconcile_existing`: atualizar esta task a cada avanço real.
- `ambiguous_state`: parar se houver divergência documental.
