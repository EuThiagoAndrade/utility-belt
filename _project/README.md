# Governança do projeto

Este diretório organiza decisões, conhecimento e ciclos do `utility-belt`. Ele governa o processo e o ciclo de vida de desenvolvimento do repositório.

## Autoridades

- comportamento e autorização: `.agent/ai_behavior.md`;
- ciclo de vida, estados e convenções: este documento;
- estado e próxima numeração: `_project/cycles.md`;
- escopo de implementação: plano aprovado;
- unidade de entrega: issue;
- registro local de execução: task persistente;
- estado global de colaboração: GitHub;
- decisões e conhecimento duradouros: `decisions/` e `knowledge/`.

## Estrutura

```text
_project/
├── README.md
├── cycles.md
├── ideations/
├── drafts/
├── executed/
├── archived/
├── decisions/
└── knowledge/
```

`archived/`, `drafts/`, `ideations/` e `knowledge/` somente precisam existir quando houver artefatos correspondentes. Diretórios vazios não são artefatos e não precisam ser versionados.

## Numeração e nomes

- Ciclos usam três dígitos: `000`, `001`, `002`.
- Ideação: `_project/ideations/NNN_assunto.md`.
- Ciclo ativo: `_project/drafts/NNN_assunto/NNN_plan.md`.
- Ciclo concluído: `_project/executed/NNN_assunto/`.
- Ciclo arquivado: `_project/archived/NNN_assunto/`.
- Task de issue: `NNN_task_issue-X.md`; múltiplas issues podem usar `NNN_task_issues-X-Y.md`.
- Task de encerramento: `NNN_task_closure.md`.
- Evidências auxiliares podem usar `NNN_research_*`, `NNN_validation_*` e `NNN_handoff*`.
- ADRs e KBs têm sequências independentes: `ADR-NNN_assunto.md` e `KB-NNN_assunto.md`; registre o ciclo de origem no próprio arquivo.

O próximo ciclo é o valor declarado em `cycles.md`; não o deduza apenas pela maior pasta existente.

## Estados válidos

### Ciclo

| Estado | Local esperado | Significado |
| :-- | :-- | :-- |
| `Ideação` | `ideations/` | Problema em exploração, sem escopo executável |
| `Planejamento` | `drafts/` | Plano em redação ou revisão |
| `Em execução` | `drafts/` | Plano aprovado sendo entregue |
| `Concluído` | `executed/` | Entrega integrada e encerramento documentado |
| `Cancelado` | sem plano ou `archived/` | Trabalho interrompido deliberadamente |
| `Substituído` | `archived/` | Plano sucedido por outro ciclo ou abordagem |

### Plano

| Estado | Significado |
| :-- | :-- |
| `Rascunho` | Primeira passagem ainda não submetida à revisão crítica formal |
| `Em Revisão` | Segunda passagem em andamento ou concluída, aguardando correções ou decisão humana pós-veredito |
| `Aprovado` | Revisão formal concluída, veredito apto e aprovação humana posterior registrados |
| `Em Execução` | Pelo menos uma entrega autorizada foi iniciada com issue válida |
| `Concluído` | Todas as entregas foram integradas e o encerramento documental foi concluído |

### Transições canônicas do plano

| Evento | Precondição | Resultado | Próximo gate |
| :-- | :-- | :-- | :-- |
| Salvar primeiro plano | Ideação existente ou autorização de planejamento | `Rascunho` | Handoff para `revisar_plano` |
| Iniciar revisão | Plano em `Rascunho` | `Em Revisão` | Relatório e veredito formal |
| Concluir revisão apta | Auditoria concluída e bloqueios resolvidos | Permanece `Em Revisão` | Aprovação humana pós-revisão |
| Aprovar plano | Veredito `APTO PARA APROVAÇÃO` ou `APTO COM RESSALVAS` e manifestação humana posterior | `Aprovado` | Publicação documental e criação de issues conforme o plano |
| Iniciar primeira entrega | Plano `Aprovado`, issue válida e autorização explícita | `Em Execução` | Entrega e checks |
| Encerrar ciclo | Entregas integradas e closure validada | `Concluído` | Movimentação para `executed/` |

Transições não listadas exigem decisão explícita e correção da governança. Em particular, aprovação do `Rascunho` significa autorização para submetê-lo à revisão; não permite a transição direta para `Aprovado`.

## Fluxo normal

1. Registrar a ideação, salvo exceção explícita de bootstrap ou solicitação direta do responsável.
2. Criar o ciclo e seu plano em `drafts/`.
3. Revisar e obter aprovação humana do plano.
4. Criar issues a partir do plano aprovado.
5. Para cada issue, abrir branch, criar task persistente, implementar, validar e abrir PR.
6. Integrar somente após os gates aplicáveis e atualizar a task com evidências reais.
7. Criar uma task de closure sem issue recursiva, consolidar rastreabilidade e mover o diretório para `executed/` em PR documental própria.
8. Marcar o plano como `Concluído` e o ciclo como `Concluído` somente quando a integração do encerramento for verificável.

## Relação entre plano, task, issue e PR

- O plano define o escopo autorizado e a decomposição.
- A issue descreve uma unidade planejada de entrega sem ampliar o plano.
- A task registra branch, execução, decisões incidentais, testes, PR, checks e integração daquela unidade.
- A PR apresenta a alteração revisável e os checks; o GitHub é a autoridade de seu estado.
- Uma issue corresponde normalmente a uma PR. Exceções devem ser justificadas no plano ou na task.
- A PR de encerramento não recebe issue própria e sua task não tenta registrar o SHA do próprio merge; esse fato permanece verificável no GitHub.

## Branches e commits

- implementação: `feature/issue-N`, `fix/issue-N` ou `chore/issue-N`;
- ciclo documental: `chore/cycle-NNN-ideation`, `chore/cycle-NNN-plan` ou `chore/cycle-NNN-closure`;
- `codex/` ou outro prefixo de harness pode anteceder o nome sem substituir o tipo semântico;
- commits de issue: `feat(issue-N):`, `fix(issue-N):`, `chore(issue-N):`;
- documentação de ciclo pode usar `docs(cycle-NNN):` ou `chore(cycle-NNN):`.

## Gates mínimos

O Utility Belt utiliza Python 3.11+, `uv` como gerenciador de ambiente e dependências, `pytest` para testes e `ruff` para linting e formatação.

```sh
uv run python scripts/validate_governance.py
uv run ruff check
uv run pytest
git diff --check
git status --short
```

Antes de publicar uma entrega, execute os gates e confirme que o staging contém somente o escopo autorizado. Registre resultados reais na task. Checks críticos devem passar antes do merge. Falhas semânticas que a automação não cobre exigem revisão manual.

## Handoffs e efeitos

Workflows com mutação usam o contrato canônico de handoff em `.agent/ai_behavior.md` e devem declarar classe de efeito, identidade estável, precondições, autoridade, evidência, aceite, regra de recusa e resultado de reconciliação. Workflows somente leitura usam saída reduzida e confirmam explicitamente ausência de mutação.

Uma recomendação de próximo workflow não é autorização. O receptor deve recusar handoff ausente, incompatível, contraditório ou sem evidência material; execução parcial, conflito ou concorrência exigem intervenção humana antes de nova mutação.
