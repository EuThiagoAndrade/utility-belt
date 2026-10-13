# Task — Issue #23: Interface CLI, mensagens e versão automática

> **Ciclo:** `007`
> **Estado:** `Aguardando revisão`
> **Tipo:** `feature`
> **Issue:** [#23](https://github.com/EuThiagoAndrade/utility-belt/issues/23)
> **Plano:** `_project/drafts/007_interface_cli_e_versionamento/007_plan.md`
> **Branch:** `feature/issue-23`
> **Worktree:** `C:/Programas/utility-belt`
> **PR:** [#24](https://github.com/EuThiagoAndrade/utility-belt/pull/24)
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
- [x] Revisão de diff, staging seletivo e PR #24 publicada sem merge.

## Evidências

| Gate | Resultado |
| :-- | :-- |
| Testes | Suíte completa final: 205 passed, 36 skipped; 36 smokes reais opt-in não executados sem BELT_MARKDOWN_TEST_DATA. Testes Restic isolados: 7 passaram. |
| Validação | 33 OK, 1 aviso explicado por reserva ativa 007, 0 falhas; ruff passou; actionlint 1.7.12 passou nos dois workflows. |
| `git diff --check` | Limpo no working tree e no staging seletivo |
| Checks remotos | [CI 38420681131](https://github.com/EuThiagoAndrade/utility-belt/actions/runs/38420681131) passou em Windows e Linux na revisão b2994ccb0e191ed8e0be71bc9c873af15f30ec07. Registro seguinte altera somente esta evidência documental; GitHub permanece autoridade dos checks da ponta atual. |

## Decisões incidentais e desvios

Ambiente .venv preexistente apontava para intérprete ausente e uv recebeu acesso negado ao tentar reconciliá-lo. Checks usam UV_PROJECT_ENVIRONMENT=.venv-cycle007 e ferramentas pytest/ruff por uv --with; sem instalação global. Não contornar proteção remota; consulta de proteção da main retornou API 403 por plano GitHub. Próximo ciclo 008 já reservado.

## Resultado

Implementação e validação locais concluídas; PR #24 publicada. Commit de implementação `c002c85b43df9db6cb91a4afd2f817a59a51228c`. Integração e execução remota de release pendentes; ciclo permanece Em execução.

### Validação visual e de distribuição

- `uv run --group dev --with pyte --with pillow python tests/ui_smoke.py --output _project/drafts/007_interface_cli_e_versionamento/007_validation_menu.png`: passou. Questionary real em terminal VT simulado 96x36, setas até Markdown, Sistema -> Sobre -> confirmação -> voltar -> sair. Preview PNG inspecionado; transcript em `007_validation_menu.txt`. Não é captura de um aplicativo nativo.
- `uv build`: sdist e wheel 0.1.0 construídos; versão 0.2.0 será calculada somente após merge da feature.
- Wheel instalada em `.venv-cycle007-wheel`; Python `-I` e belt executados fora do checkout no diretório de visualizações do Codex. Metadata, __version__ e --version concordam em 0.1.0; módulo efetivamente carregado de site-packages. `belt markdown --help` passou.
- Script de release testado em repositórios temporários: feat/fix/breaking, docs/chore, baseline, fonte/tag divergentes, checkout sujo, preservação de changelog e recuperação de release sem incrementar novamente.
- Revisão final corrigiu retry do workflow: snapshot de main atual -> CI Windows/Linux nessa mesma revisão -> release nessa mesma revisão; evita usar SHA antigo de evento ao repetir publicação parcial. Push atômico sem force rejeita avanço concorrente da main.
- Cache local antigo recebeu acesso negado; suíte usa `-p no:cacheprovider` e RUFF_CACHE_DIR no ambiente isolado. CI mantém comandos normais em runners novos.
- Primeira execução remota 38419751590 falhou em três testes Restic existentes: dependiam implicitamente de restic no PATH mesmo simulando subprocessos. Fixture de teste passou a simular também a presença do executável, com caso explícito para ausência; nenhuma alteração no comportamento Restic de produção. Correção necessária para o CI limpo previsto no plano.
- Primeiro ajuste do harness não alcançava a CLI em processo filho; teste de ausência sinalizou isso. Correção final executa a ferramenta no processo do teste, preservando a passagem dos argumentos da CLI e tornando efetivos os mocks de senha/executável/subprocesso. Nova suíte completa passou com 205 testes; a revisão corrente da PR é a autoridade dos checks remotos finais.

### Handoff de execução

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+007+implementar_issue+issue-23+e9f375f`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`
- `effect_class`: `remote_mutation`
- `state_before`: plano apto/autorizado por exceção humana; issue 23 aberta; base e Git verificados.
- `state_after`: branch feature/issue-23 publicada, escopo implementado e validado, PR #24 aberta sem merge.
- `next_transition`: PR -> revisão/checks -> decisão humana sobre integração.
- `preconditions`: checks críticos aprovados e OK humano explícito antes do merge.
- `authority`: responsável, autorização explícita de workflow completo até a PR em 2026-10-13.
- `evidence`: issue #23, PR #24, plano/revisão, handoffs, commit c002c85, gates e preview acima.
- `acceptance`: três itens atendidos e evidências reais registradas.
- `blockers`: aprovação/merge humanos pendentes; CI da implementação aprovado em Windows/Linux, sem bloqueio local. Conferir checks da ponta atual no GitHub antes de integrar.
- `result`: `executed`
- `next_workflow_recommended`: revisão da PR ao terminar.
- `next_workflow_authorized`: avaliação da PR; merge não autorizado.
- `actions_prohibited`: merge, ampliação de escopo e release remoto nesta sessão.
- `rejection_rule`: recusar identidade, estado ou evidência insuficiente.
- `logical_key`: `EuThiagoAndrade/utility-belt+007+implementar_issue+issue-23+e9f375f`
- `check_before_mutation`: nenhuma issue/branch/PR equivalente antes da criação; issue 23 agora canônica.
- `reconcile_existing`: retomar branch/task/issue canônicas, sem duplicata.
- `ambiguous_state`: parar diante de conflito material.
