---
description: "Listar issues relevantes do GitHub em modo somente leitura, sem criar, editar ou fechar itens."
---

# Workflow: Listar issues

## Entradas

- Repositório remoto identificado.
- Filtros de ciclo, label, estado, issue ou chave lógica, quando fornecidos.
- Organização e estados locais definidos em `_project/README.md` e `_project/cycles.md`.

## Barreira

- Consultar apenas o estado remoto; não criar, editar, fechar, comentar ou rotular issues.
- Ler `_project/README.md` e `_project/cycles.md`; ausência ou conflito entre estado local e remoto deve ser relatado, não resolvido por inferência.
- Registrar paginação, filtros e revisão temporal da consulta para que a saída seja auditável.

## Execução

1. Ler `_project/README.md` e `_project/cycles.md` para interpretar relações e estados locais válidos.
2. Consultar as issues aplicando os filtros explicitamente declarados.
3. Deduplicar por número/URL e preservar o estado retornado pelo GitHub.
4. Relacionar issues a ciclo, plano, task e PR apenas quando houver evidência local ou remota verificável.
5. Indicar lacunas sem inferir autorização ou conclusão.

## Saída estruturada reduzida

- `Contexto`: repositório, filtros e escopo da consulta.
- `context`: repositório, filtros e escopo da consulta.
- `Achados`: issues, estados, labels, links e relações verificáveis.
- `findings`: issues, estados, labels, links e relações verificáveis.
- `Bloqueios`: acesso, paginação, inconsistências ou dados ausentes.
- `blockers`: acesso, paginação, inconsistências ou dados ausentes.
- `Próximo passo provável`: ação recomendada, sem autorização implícita.
- `next_step_likely`: ação recomendada, sem autorização implícita.
- `Mutação`: `nenhuma`.
- `mutation`: `none`.

## Regras de handoff

- O resultado é somente leitura e não autoriza criação ou alteração de issue.
- Se encaminhado, o receptor deve recusar saída sem filtros, evidência remota ou indicação de lacunas.
