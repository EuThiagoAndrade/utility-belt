# Plano de Implementação — 005: Ajuste Visual do Banner Retrô e Cinto Utilitário

> **Ciclo:** `005`
> **Status:** `Concluído`
> **Versão:** `v1`
> **Data de criação:** 2026-09-17
> **Última atualização:** 2026-09-17
> **Tipo:** `feature`
> **Prioridade:** `P1`
> **Revisão formal:** `Concluída`
> **Veredito da revisão:** `APTO PARA APROVAÇÃO`
> **Aprovação humana pós-revisão:** `Aprovada em 2026-09-17`

## Objetivo

Refinar a identidade visual de abertura do Utility Belt em `src/utility_belt/ui/screen.py` eliminando o desenho ASCII lateral do canivete e a tipografia distorcida, substituindo-os por um cinto utilitário estilizado e tipografia de grande porte com preenchimento sólido em blocos (`█`), tudo perfeitamente centralizado na moldura retrô MS-DOS e com o novo subtítulo de produto: *"Sistema de ferramentas para simplificar sua vida"*.

## Contexto e baseline

O Ciclo 004 introduziu a base retrô e o banner híbrido inicial. No entanto, o desenho lateral do canivete e a grafia anterior do título apresentaram deficiências de legibilidade e acabamento estético.
A cor ciano (`\033[1;36m`) das bordas `╔═══╗`, o subtítulo de versão `v0.1.0 • O Canivete Suíço de Terminal` e a largura máxima de 76 colunas já estabelecidos devem ser rigorosamente preservados.

## Escopo

### Dentro do escopo

- Exclusão do desenho ASCII do canivete (`knife_lines`) e do divisor vertical do banner.
- Implementação do cinto utilitário ASCII `|==[■]==[■]==[■]==[████]==[■]==[■]==[■]==|` centralizado no topo da moldura.
- Implementação da tipografia "UTILITY-BELT" em blocos maciços de 5 linhas (`█`), centralizada e com ortografia 100% correta.
- Preservação da moldura de linhas duplas `╔═══╗` com a cor ciano original.
- Atualização do subtítulo institucional para: *"Sistema de ferramentas para simplificar sua vida"*, mantendo a linha *"v0.1.0 • O Canivete Suíço de Terminal"*.
- Atualização da suíte de testes em `tests/test_screen.py`.
- Garantia de passagem em todos os gates de governança, pytest e ruff.

### Fora do escopo

- Qualquer modificação nos menus interativos (`menu.py`, `docker_menu.py`, `restic_menu.py`).
- Alterações em cabeçalhos de tela dedicada (`render_header`) ou banner compacto.
- Alterações em comandos CLI diretos (`belt run`, `belt list`, etc.).
- Modificações em outros componentes do catálogo ou adaptadores.

## Decisões e autoridades

- **Autoridade de comportamento:** `.agent/ai_behavior.md`.
- **Autoridade de ciclo:** `_project/README.md` e `_project/cycles.md`.
- **Diretiva do usuário (2026-09-17):** Escolha do Estilo A (5 linhas em blocos sólidos `█`), preservação da cor ciano original da moldura `═══`, centralização completa e pré-autorização concedida para o ciclo completo.

## Estratégia de testes

- Testes unitários com `pytest` / `uv run pytest` cobrindo `tests/test_screen.py`.
- Validação das strings de saída capturadas (`capsys`), garantindo a presença do cinto `[████]`, do novo subtítulo e a ausência do canivete antigo.
- Execução de `uv run ruff check` para garantia de conformidade de código.
- Execução de `python scripts/validate_governance.py` para garantia de integridade documental.

## Itens de implementação

### Item 1 — Atualização do Banner em screen.py e suíte de testes

**Contexto:**
Substituir o banner anterior pelo layout centralizado contendo o cinto utilitário, título em blocos sólidos e novo subtítulo.

**Ação técnica:**
1. Em `src/utility_belt/ui/screen.py`, refatorar `render_banner()` para:
   - Calcular padding centralizado para cada linha dentro da largura interna de 74 colunas (`box_w = 76`).
   - Renderizar o cinto utilitário `|==[■]==[■]==[■]==[████]==[■]==[■]==[■]==|` com destaque no fecho e elos.
   - Renderizar as 5 linhas de "UTILITY-BELT" em blocos maciços `█` com estilo alaranjado/âmbar retrô.
   - Renderizar as duas linhas de subtítulo centralizadas (versão e objetivo do produto).
   - Manter a moldura externa em Ciano (`CYAN`).
2. Em `tests/test_screen.py`, atualizar `test_render_banner_standard` para checar os novos padrões visuais.

**Critérios de aceite:**
- [ ] O banner exibe o cinto utilitário `|==[■]==[■]==[■]==[████]==[■]==[■]==[■]==|` centralizado.
- [ ] O título "UTILITY-BELT" é legível em blocos de 5 linhas e grafado corretamente.
- [ ] O subtítulo contém exatamente *"Sistema de ferramentas para simplificar sua vida"*.
- [ ] A moldura mantém a cor ciano original e não excede a largura padrão.
- [ ] `uv run pytest` e `uv run ruff check` passam sem erros.

## Arquivos afetados

- `src/utility_belt/ui/screen.py`
- `tests/test_screen.py`

## Decomposição em issues e PRs

- **Issue 1:** [#13](https://github.com/EuThiagoAndrade/utility-belt/issues/13) — `feat(cycle-005): ajustar banner ascii retro com cinto utilitario e tipografia solida`
- **PR 1:** [#14](https://github.com/EuThiagoAndrade/utility-belt/pull/14) — Pull Request correspondente contendo a implementação e testes.

## Dependências e blockers

- Nenhuma dependência externa nova.
- Nenhum blocker ativo.

## Riscos, suposições e rollback

- **Risco:** Largura de linha exceder terminais estreitos.
  - *Mitigação:* A largura do bloco é de 63 colunas, cabendo confortavelmente nas 74 colunas internas da moldura de 76 colunas. Terminais menores que 78 colunas continuam caindo no modo compacto existente.
- **Rollback:** Reversão do commit na branch da issue.

## Sequência recomendada

1. Criar branch `feature/issue-<N>`.
2. Criar task `005_task_issue-<N>.md`.
3. Aplicar alterações cirúrgicas em `screen.py` e `test_screen.py`.
4. Executar gates locais (`validate_governance`, `pytest`, `ruff`, `diff`).
5. Realizar commit semântico e push.
6. Abrir Pull Request vinculando a issue.

## Referências

- `_project/ideations/005_ajuste_visual_banner_retro.md`
- `.agent/ai_behavior.md`
- `_project/decisions/ADR-002_arquitetura_cli_distribuivel.md`

## Rastreabilidade

| Campo | Valor |
| :-- | :-- |
| [#13](https://github.com/EuThiagoAndrade/utility-belt/issues/13) |
| [#14](https://github.com/EuThiagoAndrade/utility-belt/pull/14) |
| Branch(es) | `feature/issue-13` |
| `handoff_schema_version` | `1` |
| `handoff_id` | `utility-belt+005+rascunhar_plano+banner_retro+093da76` |
| Destino após conclusão | `_project/executed/005_ajuste_visual_banner_retro/005_plan.md` |

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: `utility-belt+005+rascunhar_plano+banner_retro+093da76`
- `identity_source`: `utility-belt+005+rascunhar_plano+banner_retro+093da76`
- `effect_class`: `local_mutation`
- `state_before`: `Ideação 005 aprovada pelo usuário com premissas do Estilo A.`
- `state_after`: `Plano aprovado e pronto para criação de issue e execução.`
- `next_transition`: `criar_issue -> implementar_issue`
- `preconditions`: `Plano com veredito apto e aprovação humana registrada.`
- `authority`: `Pré-autorização humana explícita concedida em 2026-09-17.`
- `evidence`: `_project/drafts/005_ajuste_visual_banner_retro/005_plan.md`
- `acceptance`: `Plano completo, critérios delimitados e sem alterações fora do escopo.`
- `blockers`: `nenhum`
- `result`: `executed`
- `next_workflow_recommended`: `implementar_issue`
- `next_workflow_authorized`: `implementar_issue`
- `actions_prohibited`: `alterar componentes alheios a screen.py sem autorização`
- `rejection_rule`: `recusar handoff sem issue vinculada ou sem plano formal`
- `logical_key`: `utility-belt+005+banner_retro+093da76`
- `check_before_mutation`: `confirmar inexistência de outro plano 005 ativo`
- `reconcile_existing`: `reconciliar o plano 005 canônico`
- `ambiguous_state`: `nenhum conflito detectado`

## Revisão crítica

- **Data:** 2026-09-17
- **Versão revisada:** `v1`
- **Veredito:** `APTO PARA APROVAÇÃO`
- **Bloqueios remanescentes:** Nenhum
- **Aprovação humana pós-revisão:** `Aprovada em 2026-09-17` (pré-autorização explícita do usuário)
- **Correções materiais:** Escopo cirúrgico delimitado exclusivamente a `screen.py` e seu teste.
- **Ressalvas:** Nenhuma

## Pós-mortem

- **Data de conclusão:** 2026-09-17
- **Desvios:** Nenhum. Escopo implementado cirurgicamente conforme planejado.
- **Lições comprovadas:** A tipografia preenchida em blocos maciços (█) em 5 linhas combinada com a centralização perfeita do cinto utilitário e subtítulos elimina ambiguidades de caracteres (como 'I' e 'T') e proporciona acabamento estético superior e balanceado no terminal.\n