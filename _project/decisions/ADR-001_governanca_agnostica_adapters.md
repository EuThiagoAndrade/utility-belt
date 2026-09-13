---
title: "Governança agnóstica com adapters de descoberta"
tags:
  - governança
  - agentes
  - arquitetura
author: "Thiago Andrade"
module: "Governança"
last_updated: "2026-09-13"
origin_cycle: "000"
---

# ADR-001: Governança agnóstica com adapters de descoberta

## Status

Aceito

## Contexto

O `utility-belt` precisa operar com diferentes ferramentas e assistentes agênticos (Claude Code, Antigravity/Gemini CLI, Codex/OpenAI, etc.) sem transferir suas autoridades para a estrutura proprietária de um único fornecedor. Duplicar políticas em cada entrypoint criaria fontes concorrentes de verdade; ignorar a descoberta nativa de cada assistente tornaria o bootstrap imprevisível.

## Decisão

Manter `.agent/` e `_project/` como o núcleo canônico independente de ferramenta. `AGENTS.md`, `CLAUDE.md` e `GEMINI.md` na raiz do projeto são adapters mínimos: apontam para `.agent/ai_behavior.md`, mas não definem políticas substantivas próprias.

| Harness / Assistente | Adapter local |
| :-- | :-- |
| Codex / OpenAI | `AGENTS.md` com instrução explícita para leitura de `.agent/ai_behavior.md` |
| Claude Code | `CLAUDE.md` com import `@./.agent/ai_behavior.md` |
| Gemini CLI / Antigravity | `GEMINI.md` com import `@./.agent/ai_behavior.md` |

A matriz de autoridade reside em `.agent/ai_behavior.md`. Workflows, templates, skills, validadores e automações consomem essa autoridade; nenhum adapter cria política concorrente. O ferramental de validação documental é implementado em Python nativo (`scripts/validate_governance.py`), alinhado à stack do projeto.

## Consequências

### Positivas
- Núcleo portável e uma única fonte substantiva de autoridade por responsabilidade.
- Adapters mínimos, substituíveis e sem duplicação de regras.
- Operação transparente com múltiplos assistentes de IA no mesmo repositório.

### Trade-offs
- Cada assistente com convenção própria de descoberta requer um adapter na raiz.
- Atualizações de sintaxe dos assistentes exigem revisão periódica dos adapters.

## Alternativas consideradas
- Eleger o padrão proprietário de um assistente como autoridade global.
- Duplicar as regras em todos os arquivos de contexto de agentes.
- Não manter arquivos de governança, confiando apenas no prompt do usuário.
