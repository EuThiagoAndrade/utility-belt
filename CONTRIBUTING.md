# Guia de Contribuição — Utility Belt

Obrigado pelo interesse em contribuir com o **Utility Belt**! Este projeto segue padrões rígidos de qualidade, governança desacoplada e simplicidade técnica.

---

## Primeiros Passos e Ambiente Local

O projeto utiliza o gerenciador [`uv`](https://docs.astral.sh/uv/) para gerenciamento de dependências e ambientes virtuais isolados em Python 3.11+.

### 1. Clonar o repositório

```bash
git clone https://github.com/EuThiagoAndrade/utility-belt.git
cd utility-belt
```

### 2. Sincronizar dependências

```bash
uv sync
```

### 3. Executar a CLI em desenvolvimento

```bash
uv run belt --help
```

---

## Comandos de Qualidade e Gates Mínimos

Antes de abrir uma Pull Request ou submeter commits, todos os 5 gates locais obrigatórios devem ser executados e passar com 100% de sucesso:

```bash
# 1. Auditoria formal de governança
uv run python scripts/validate_governance.py

# 2. Linter e padronização de código
uv run ruff check

# 3. Suíte de testes unitários e de integração
uv run pytest

# 4. Checagem de quebras de linha e integridade git
git diff --check

# 5. Validação de empacotamento
uv build
```

---

## Padrão de Branches e Commits

O repositório consome a governança canônica descrita em `_project/README.md`.

### Nomenclatura de Branches

Toda branch de desenvolvimento deve estar estritamente vinculada a uma Issue do GitHub:

- `feature/issue-N`: para novas funcionalidades ou melhorias planejadas
- `fix/issue-N`: para correções de defeitos (bugfixes)
- `chore/issue-N`: para tarefas de manutenção interna, documentação de issue ou infraestrutura
- `chore/cycle-NNN-plan`: para publicação documental do plano aprovado de um ciclo
- `chore/cycle-NNN-closure`: para encerramento documental de um ciclo concluído

### Convenção de Commits

Os commits devem ser atômicos e seguir o formato convencional consumido pelo release automático:

- `feat(issue-N): <descrição>` (dispara incremento MINOR na release: `0.1.0` → `0.2.0`)
- `fix(issue-N): <descrição>` (dispara incremento PATCH na release: `0.2.0` → `0.2.1`)
- `chore(issue-N): <descrição>` (não incrementa versão)
- `docs(cycle-NNN): <descrição>` (tarefas documentais de ciclo)

---

## Fluxo de Trabalho (Issues e Pull Requests)

1. **Issues**: Toda alteração material deve ter uma Issue registrada no GitHub, criada a partir de um dos templates em `.github/ISSUE_TEMPLATE/` (`feature_request.yml`, `bug_report.yml` ou `chore.yml`).
2. **Pull Requests**:
   - Abra PRs contra a branch `main`.
   - Preencha todas as seções obrigatórias do template (`.github/PULL_REQUEST_TEMPLATE/pull_request_template.md`), incluindo rastreabilidade da issue vinculada (`Closes #N`), resumo das alterações, checklist de gates e bloco de handoff canônico.
   - Aguarde a conclusão dos checks remotos do GitHub Actions (`ubuntu-latest` e `windows-latest`).
   - Merges na branch `main` são realizados após aprovação formal do responsável.

---

## Governança do Projeto

Para entender o processo de tomadas de decisão, ciclos de vida de planejamento e políticas de automação:

- [Governança do Projeto](_project/README.md)
- [Registro Canônico de Ciclos](_project/cycles.md)
- [Diretrizes de Comportamento para Agentes](.agent/ai_behavior.md)
