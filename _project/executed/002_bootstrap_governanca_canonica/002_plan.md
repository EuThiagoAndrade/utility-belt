# Plano de Implementação — Bootstrap da Governança Canônica

> **Ciclo:** `002`
> **Status:** `Concluído`
> **Versão:** `v1`
> **Data de criação:** 2026-09-13
> **Última atualização:** 2026-09-13
> **Tipo:** `chore`
> **Prioridade:** `P1`
> **Revisão formal:** `Concluída`
> **Veredito da revisão:** `APTO PARA APROVAÇÃO`
> **Aprovação humana pós-revisão:** `Aprovada em 2026-09-13`

## Objetivo

Implantar o modelo de governança canônica agnóstica no repositório `utility-belt`, adaptando a estrutura das pastas `_project` e `.agent`, expurgando arquivos alheios do projeto anterior, formalizando os ciclos históricos 000 e 001 e integrando validação e gates nativos em Python (`uv`, `pytest`, `ruff`).

## Contexto e baseline

As pastas `_project` e `.agent` foram importadas de outro projeto (`euthiagoandrade-api`), contendo histórico de ciclos, ADRs de API editorial e validações baseadas em Node.js. Era necessário adaptar o contexto para o canivete suíço `utility-belt`, remover artefatos estranhos e criar automações em Python.

## Escopo

### Dentro do escopo
- Remoção completa de `_project/ideations/`, ciclos executados do outro projeto (`000` a `012`), ADRs de persistência/API e artigos de conhecimento.
- Formalização dos ciclos concluídos do Utility Belt em `_project/executed/` (Ciclo 000: Fundação CLI e Ciclo 001: Menus Interativos).
- Atualização das autoridades canônicas: `_project/README.md`, `_project/cycles.md` e `.agent/ai_behavior.md`.
- Registro de decisões arquiteturais: `ADR-001` (Governança agnóstica com adapters) e `ADR-002` (Arquitetura CLI distribuível).
- Atualização de `.agent/lessons_learned.md` com lições técnicas do Utility Belt.
- Criação dos adapters de descoberta na raiz: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`.
- Criação dos templates de issues e PR em `.github/`.
- Desenvolvimento do validador de governança em Python puro (`scripts/validate_governance.py`) e seu teste associado (`tests/test_governance.py`).

### Fora do escopo
- Alterações funcionais na CLI do Utility Belt.

## Decisões e autoridades
- **ADR-001:** Governança agnóstica com adapters de descoberta.
- **Entrevista /grill-me:** Decisões validadas com o usuário Thiago Andrade em 2026-09-13.

## Estratégia de testes
- `uv run python scripts/validate_governance.py` (24 verificações de integridade).
- `uv run ruff check` (estilo e formatação).
- `uv run pytest` (52 testes unitários passando).
- `git diff --check`.

## Rastreabilidade

| Campo | Valor |
| :-- | :-- |
| Handoff Schema Version | `1` |
| Local do plano | `_project/executed/002_bootstrap_governanca_canonica/002_plan.md` |

## Revisão crítica

- **Data:** 2026-09-13
- **Veredito:** `APTO PARA APROVAÇÃO`
- **Aprovação humana pós-revisão:** Aprovada em 2026-09-13
