---
name: governance-check
description: "Audita estrutura, estado e rastreabilidade da governança usando as autoridades canônicas e o validador local em Python."
---

# Governance Check

Pode ser usado diretamente para uma auditoria ou chamado por outro workflow. Em ambos os modos, recebe o root auditado e o escopo da revisão; não pressupõe permissão de escrita.

1. Leia `.agent/ai_behavior.md`, `_project/README.md`, `_project/cycles.md` e o plano ativo.
2. Execute `uv run python scripts/validate_governance.py`.
3. Execute `uv run ruff check`.
4. Execute `uv run pytest`.
5. Execute `git diff --check` e revise `git status --short`.
6. Compare task, issue, PR e checks com seus estados reais.
7. Relate separadamente erros bloqueantes, avisos e julgamentos manuais; não altere arquivos durante a auditoria sem pedido explícito.

## Handoff estruturado

Retorne: root auditado, comandos executados, erros, avisos, itens manuais, estado do Git e conclusão `passou | falhou | bloqueado`.
