# Task — Issue #23: Interface CLI, mensagens e versão automática

> **Ciclo:** `007`
> **Estado:** `Em andamento`
> **Tipo:** `feature`
> **Issue:** [#23](https://github.com/EuThiagoAndrade/utility-belt/issues/23)
> **Plano:** `_project/drafts/007_interface_cli_e_versionamento/007_plan.md`
> **Branch:** `feature/issue-23`
> **Worktree:** `C:/Programas/utility-belt`
> **PR:** Pendente
> **Integração:** `Pendente`
> **Início:** 2026-10-13
> **Última atualização:** 2026-10-13
> **handoff_schema_version:** `1`
> **handoff_id:** EuThiagoAndrade/utility-belt+007+implementar_issue+issue-23+e9f375f

## Objetivo

Entregar os três itens do plano em uma PR para avaliação humana, sem merge.

## Escopo autorizado

Conjunto completo confirmado pelo responsável; workflow autoaprovado até a PR, exceção ao gate pós-revisão registrada no plano. Revisão APTO COM RESSALVAS. Preservar comportamentos funcionais, consentimentos e CLI direta.

## Execução

- [x] Ideação, rascunho, revisão formal e registro da exceção humana em etapas separadas.
- [x] Issue criada e consultada; branch canônica nova em baseline igual a origin/main.
- [x] Interface, Sistema e mensagens.
- [x] Fonte única, script de release e CI.
- [x] Testes, smoke visual e build instalado.
- [ ] Revisão de diff, staging seletivo e PR.

## Evidências

| Gate | Resultado |
| :-- | :-- |
| Testes | Suíte completa: 204 passed, 36 skipped; 36 smokes reais opt-in não executados sem BELT_MARKDOWN_TEST_DATA. Após ajuste de diagnóstico/retry: 60 testes relevantes passaram. |
| Validação | 33 OK, 1 aviso explicado por reserva ativa 007, 0 falhas; ruff passou; actionlint 1.7.12 passou nos dois workflows. |
| `git diff --check` | Limpo antes do staging; conferir novamente após stage |
| Checks remotos | Pendente |

## Decisões incidentais e desvios

Ambiente .venv preexistente apontava para intérprete ausente e uv recebeu acesso negado ao tentar reconciliá-lo. Checks usam UV_PROJECT_ENVIRONMENT=.venv-cycle007 e ferramentas pytest/ruff por uv --with; sem instalação global. Não contornar proteção remota; consulta de proteção da main retornou API 403 por plano GitHub. Próximo ciclo 008 já reservado.

## Resultado

Implementação e validação locais concluídas; PR em preparação. Integração e execução remota de release pendentes.

### Validação visual e de distribuição

- `uv run --group dev --with pyte --with pillow python tests/ui_smoke.py --output _project/drafts/007_interface_cli_e_versionamento/007_validation_menu.png`: passou. Questionary real em terminal VT simulado 96x36, setas até Markdown, Sistema -> Sobre -> confirmação -> voltar -> sair. Preview PNG inspecionado; transcript em `007_validation_menu.txt`. Não é captura de um aplicativo nativo.
- `uv build`: sdist e wheel 0.1.0 construídos; versão 0.2.0 será calculada somente após merge da feature.
- Wheel instalada em `.venv-cycle007-wheel`; Python `-I` e belt executados fora do checkout no diretório de visualizações do Codex. Metadata, __version__ e --version concordam em 0.1.0; módulo efetivamente carregado de site-packages. `belt markdown --help` passou.
- Script de release testado em repositórios temporários: feat/fix/breaking, docs/chore, baseline, fonte/tag divergentes, checkout sujo, preservação de changelog e recuperação de release sem incrementar novamente.
- Revisão final corrigiu retry do workflow: snapshot de main atual -> CI Windows/Linux nessa mesma revisão -> release nessa mesma revisão; evita usar SHA antigo de evento ao repetir publicação parcial. Push atômico sem force rejeita avanço concorrente da main.
- Cache local antigo recebeu acesso negado; suíte usa `-p no:cacheprovider` e RUFF_CACHE_DIR no ambiente isolado. CI mantém comandos normais em runners novos.

### Handoff de execução

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+007+implementar_issue+issue-23+e9f375f`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`
- `effect_class`: `local_mutation`
- `state_before`: plano apto/autorizado por exceção humana; issue 23 aberta; base e Git verificados.
- `state_after`: branch feature/issue-23 e task persistente; implementação em andamento.
- `next_transition`: implementar -> validar -> PR.
- `preconditions`: escopo/issue correspondentes; gates e staging seletivo antes de publicação.
- `authority`: responsável, autorização explícita de workflow completo até a PR em 2026-10-13.
- `evidence`: issue remota, plano/revisão, baseline e comandos de Git.
- `acceptance`: três itens atendidos e evidências reais registradas.
- `blockers`: nenhum para implementar; merge sem autorização própria.
- `result`: `executed`
- `next_workflow_recommended`: revisão da PR ao terminar.
- `next_workflow_authorized`: implementação e publicação da PR, sem merge.
- `actions_prohibited`: merge, ampliação de escopo e release remoto nesta sessão.
- `rejection_rule`: recusar identidade, estado ou evidência insuficiente.
- `logical_key`: `EuThiagoAndrade/utility-belt+007+implementar_issue+issue-23+e9f375f`
- `check_before_mutation`: nenhuma issue/branch/PR equivalente antes da criação; issue 23 agora canônica.
- `reconcile_existing`: retomar branch/task/issue canônicas, sem duplicata.
- `ambiguous_state`: parar diante de conflito material.
