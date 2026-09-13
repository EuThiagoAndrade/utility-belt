## Rastreabilidade

- **Ciclo:** `NNN`
- **Plano:** `_project/drafts/NNN_assunto/NNN_plan.md` ou `_project/executed/...`
- **Issue vinculada:** Fixes #N / Closes #N
- **Task persistente:** `NNN_task_issue-N.md`

## Resumo das alterações

<!-- Descreva de forma concisa as modificações introduzidas por esta PR -->

## Checklist de Gates

- [ ] `uv run python scripts/validate_governance.py` passou sem erros
- [ ] `uv run ruff check` passou sem avisos/erros
- [ ] `uv run pytest` executou com 100% de sucesso
- [ ] `git diff --check` limpo
- [ ] Staging seletivo contendo estritamente o escopo autorizado

## Handoff

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+NNN+workflow+logical_target+source_revision`
- `result`: `executed`
- `next_transition`: Revisão e integração autorizada
