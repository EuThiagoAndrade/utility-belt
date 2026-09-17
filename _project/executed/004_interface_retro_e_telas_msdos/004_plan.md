# Plano de Implementação — Interface Retrô MS-DOS e Identidade Visual

> **Ciclo:** `004`
> **Status:** `Concluído`
> **Versão:** `v1`
> **Data de criação:** 2026-09-17
> **Última atualização:** 2026-09-17
> **Tipo:** `feature`
> **Prioridade:** `P1`
> **Revisão formal:** `Concluída`
> **Veredito da revisão:** `APTO COM RESSALVAS`
> **Aprovação humana pós-revisão:** `Aprovada em 2026-09-17`

## Objetivo

Transformar a experiência visual do modo interativo (`belt menu`) do Utility Belt, substituindo a rolagem contínua linear de menus por uma navegação limpa de "telas dedicadas" inspirada em sistemas clássicos MS-DOS (com transições dinâmicas via limpeza de tela e cabeçalhos contextuais com breadcrumbs), além de introduzir uma identidade visual de abertura retrô marcante com banner híbrido combinando um canivete suíço em ASCII art e o título do projeto em tipografia de blocos isométricos 3D.

## Contexto e baseline

- **Situação atual:** O ciclo `001` estabeleceu menus interativos com `questionary` em `src/utility_belt/menu.py`, `src/utility_belt/ui/docker_menu.py` e `src/utility_belt/ui/restic_menu.py`. No entanto, cada seleção e execução de ferramenta imprime saídas nas linhas inferiores sem limpar o terminal, acumulando histórico visual vertical.
- **Identidade gráfica:** A abertura atual consiste apenas em um texto simples `UTILITY BELT - CANIVETE SUÍÇO`. Não há arte gráfica representativa nem moldura temática.
- **Ideação alinhada:** O artefato `_project/ideations/004_interface_retro_e_telas_msdos.md` consolidou a visão acordada na entrevista `/grill-me`, optando por uma abordagem leve que orquestra `typer.clear()`, molduras ASCII/UTF-8 em 80 colunas e telas dedicadas de execução sem a introdução de frameworks pesados de TUI.

## Escopo

### Dentro do escopo

1. **Módulo de tela e identidade (`src/utility_belt/ui/screen.py`):**
   - Criação de helpers para limpeza segura de tela cross-platform (`clear_screen`).
   - Renderização de banner de abertura híbrido com canivete suíço em ASCII art e título "UTILITY BELT" em blocos 3D (estilo retrô/Claude Code em tons alaranjados/âmbar), contido em moldura MS-DOS de linhas duplas (`╔═╗`) em até 78 colunas.
   - Detecção de dimensões do terminal com fallback compacto para terminais estreitos (< 80 colunas) ou não-TTY.
   - Renderização de cabeçalhos de navegação limpos com breadcrumbs (ex: `╔═ UTILITY BELT ═ DOCKER ═ EXPORTAR ═╗`).
   - Helper de execução isolada em tela dedicada (`screen_view` / `run_with_screen`): limpa a tela antes de executar uma ferramenta, imprime o cabeçalho contextual, exibe os logs e aguarda confirmação de retorno antes de limpar e redesenhar o menu anterior.
2. **Integração no Menu Principal (`src/utility_belt/menu.py`):**
   - Limpeza de tela ao renderizar o menu principal e após retorno de submenus ou ferramentas.
   - Exibição do banner híbrido no topo do menu principal.
   - Adição de atalhos numéricos híbridos nos itens de seleção (`[1]`, `[2]`, etc.) e suporte a saída rápida (`[0]`).
   - Envolvimento de `_show_diagnostics` e `_run_system_info` no padrão de tela dedicada.
3. **Integração nos Submenus (`src/utility_belt/ui/docker_menu.py` e `src/utility_belt/ui/restic_menu.py`):**
   - Adoção de limpeza de tela na entrada e retorno de cada submenu, exibindo a barra compacta de breadcrumbs no topo.
   - Envolvimento dos fluxos de exportação/importação Docker e rotinas Restic (backup, restore, wizard, check, ls) em telas dedicadas com pausa amigável antes de retornar.
   - Adição de atalhos numéricos (`[1]`, `[2]`, `[0] Voltar`).
4. **Configurabilidade e tolerância:**
   - Adição da chave `show_banner: bool` (default: `True`) na configuração persistente gerenciada por `src/utility_belt/config.py`.
   - Compatibilidade total com ambientes Windows (Windows Terminal, PowerShell, CMD) e Linux.
5. **Testes automatizados:**
   - Testes unitários para as funções de `utility_belt.ui.screen`.
   - Testes de menus atualizados em `tests/test_interactive_menus.py` garantindo que as chamadas de tela e retornos funcionam sem quebrar o Questionary mockado.

### Fora do escopo

- Reescrever a lógica interna de comandos do Docker, Restic ou ferramentas do catálogo.
- Alterar a saída de comandos diretos da CLI quando executados fora do menu interativo (ex: `belt doctor`, `belt catalog list`, `belt tool run`).
- Migrar para bibliotecas externas pesadas de TUI (como Textual, Blessed ou Curses).
- Implementação de mouse ou janelas flutuantes com sobreposição gráfica.

## Decisões e autoridades

- **ADR-001 (Governança Agnóstica):** Estrutura e ciclo de vida seguem as autoridades canônicas em `.agent/` e `_project/`.
- **ADR-002 (Arquitetura CLI Distribuível):** Typer permanece o entrypoint principal da CLI, com questionary provendo a interação em TTY.
- **Decisão de Design Ciclo 004 (Alinhamento /grill-me):** Solução baseada em `typer.clear()` e módulo desacoplado de telas (`ui/screen.py`), descartando frameworks de TUI pesados para manter a simplicidade arquitetural ("Simplicidade Primeiro").

## Estratégia de testes

1. **Testes unitários de tela (`tests/test_screen.py`):**
   - Testar `clear_screen` verificando chamadas a `typer.clear`.
   - Testar renderização do banner com largura controlada (<= 78 caracteres por linha) e presença dos elementos visuais.
   - Testar fallback do banner para larguras reduzidas de terminal (< 80 colunas).
   - Testar renderização de cabeçalhos com diferentes níveis de breadcrumbs.
   - Testar helper de tela dedicada (`screen_view`), garantindo que a ação é executada, a pausa é solicitada e o retorno limpa a tela.
2. **Testes de integração de menus (`tests/test_interactive_menus.py`):**
   - Validar que o menu principal e os submenus exibem as novas opções com atalhos numéricos.
   - Mockar `questionary.select` e `screen_view` para garantir que o fluxo de navegação para frente e para trás (`Voltar` / `Sair`) preserva as transições esperadas.
3. **Validação de Governança e Qualidade:**
   - `python scripts/validate_governance.py` (auditoria documental).
   - `ruff check` (linting de código e imports).
   - `pytest` (execução completa de toda a suíte de testes com 100% de aprovação).

## Itens de implementação

### Item 1 — Módulo de Telas, Banner Híbrido e Suporte a Configuração

**Contexto:**
Necessidade de uma base reutilizável para gerenciar limpeza de terminal, arte gráfica retrô e molduras padronizadas para todos os menus.

**Ação técnica:**
- Criar `src/utility_belt/ui/screen.py` contendo:
  - `clear_screen()` com chamada delegada a `typer.clear()`.
  - `render_banner(compact: bool = False) -> None`: arte ASCII de canivete suíço à esquerda + título "UTILITY BELT" em blocos 3D estilizados à direita, cercados por moldura MS-DOS de linhas duplas em tons quentes (laranja/âmbar) e realces ciano.
  - `render_header(breadcrumbs: list[str]) -> None`: barra compacta de cabeçalho formatada em moldura retrô.
  - `run_dedicated_screen(title: str, func, *args, **kwargs)`: padrão de execução em tela dedicada com cabeçalho e confirmação de retorno.
- Atualizar `src/utility_belt/config.py` com o campo `show_banner` (default: `True`) e validação de carregamento.
- Criar suíte de testes unitários em `tests/test_screen.py`.

**Critérios de aceite:**
- [x] `clear_screen` executa a limpeza sem lançar exceções mesmo em ambientes não-TTY.
- [x] O banner híbrido possui largura máxima de 78 colunas e não ultrapassa os limites do terminal.
- [x] Terminais com largura inferior a 80 colunas recebem cabeçalho compacto sem distorção gráfica.
- [x] A configuração `show_banner: false` suprime a arte ASCII e renderiza cabeçalho simplificado.
- [x] Testes unitários cobrindo o módulo `ui/screen.py` implementados e passando.

### Item 2 — Refatoração e Padronização do Menu Principal e Submenus

**Contexto:**
Eliminar a rolagem contínua nos menus e submenus, adotando o módulo de telas e navegação enriquecida com atalhos.

**Ação técnica:**
- Atualizar `src/utility_belt/menu.py`:
  - Limpar a tela no início de cada iteração de `show_menu()`.
  - Exibir o banner de abertura no topo do menu principal.
  - Formatar escolhas do Questionary com atalhos numéricos (`[1] Restic`, `[2] Docker`, `[3] Doctor`, `[4] Informações do Sistema`, `[0] Sair`).
  - Executar diagnósticos e `system.info` via tela dedicada com espera de tecla e retorno limpo.
- Atualizar `src/utility_belt/ui/docker_menu.py`:
  - Limpar tela e exibir cabeçalho com breadcrumbs `[ UTILITY BELT > DOCKER ]`.
  - Adicionar atalhos numéricos nas opções do menu Docker.
  - Envolver `export_images` e `import_images` no fluxo de tela dedicada.
- Atualizar `src/utility_belt/ui/restic_menu.py`:
  - Limpar tela e exibir cabeçalho com breadcrumbs `[ UTILITY BELT > RESTIC ]`.
  - Padronizar opções com atalhos numéricos e envolver rotinas (wizard, backup, restore, check, ls, config) em tela dedicada.
- Atualizar `tests/test_interactive_menus.py` para refletir os novos textos de opções e chamadas de tela.

**Critérios de aceite:**
- [x] Navegar no menu principal limpa a tela a cada transição sem empilhamento de menus anteriores.
- [x] Entrar e sair dos submenus do Docker e Restic limpa a tela mantendo cabeçalho contextual visível.
- [x] Execução de rotinas do Docker, Restic e Doctor exibe cabeçalho dedicado e solicita confirmação antes de voltar ao menu.
- [x] Atalhos numéricos e navegação por setas funcionam harmoniosamente em todos os menus.
- [x] Todos os testes em `tests/test_interactive_menus.py` passam com sucesso.

## Arquivos afetados

- `src/utility_belt/ui/screen.py` (novo): Módulo centralizado de telas, banner híbrido, molduras e cabeçalhos.
- `src/utility_belt/config.py`: Suporte à chave de configuração `show_banner`.
- `src/utility_belt/menu.py`: Adoção do módulo de telas, banner de abertura e atalhos numéricos.
- `src/utility_belt/ui/docker_menu.py`: Adoção de cabeçalhos compactos, tela dedicada e atalhos.
- `src/utility_belt/ui/restic_menu.py`: Adoção de cabeçalhos compactos, tela dedicada e atalhos.
- `tests/test_screen.py` (novo): Testes unitários para o módulo de telas e banner.
- `tests/test_interactive_menus.py`: Atualização dos testes de menus interativos.
- `_project/cycles.md`: Atualização do estado do ciclo 004 para `Concluído`.

## Decomposição em issues e PRs

1. **Issue 1 — Fundação Visual e Módulo de Telas Retrô:**
   - Escopo: Implementação de `src/utility_belt/ui/screen.py`, banner híbrido retrô com canivete ASCII e tipografia 3D, cabeçalhos com breadcrumbs, helper de tela dedicada, configuração `show_banner` e testes em `tests/test_screen.py`.
   - Issue: [#8](https://github.com/EuThiagoAndrade/utility-belt/issues/8)
   - Branch: `feature/issue-8`
   - PR: [#10](https://github.com/EuThiagoAndrade/utility-belt/pull/10) (Merged `76a8367`)
2. **Issue 2 — Adoção de Telas Dedicadas nos Menus Interativos:**
   - Escopo: Integração do módulo de telas no menu principal (`menu.py`), submenus (`docker_menu.py`, `restic_menu.py`), atalhos numéricos, telas de execução de ações e atualização de `tests/test_interactive_menus.py`.
   - Issue: [#9](https://github.com/EuThiagoAndrade/utility-belt/issues/9)
   - Branch: `feature/issue-9`
   - PR: [#11](https://github.com/EuThiagoAndrade/utility-belt/pull/11) (Merged `0db69dc`)

## Dependências e blockers

- **Dependências técnicas:** Typer e Questionary já presentes nas dependências do projeto (`pyproject.toml`). Nenhuma dependência externa adicional é necessária.
- **Blockers:** Nenhum. Todas as decisões de arquitetura e design foram alinhadas na entrevista `/grill-me`.

## Riscos, suposições e rollback

- **Risco:** Quebra de renderização de caracteres UTF-8 em terminais Windows CMD legados.
  - *Mitigação:* Usar codificação UTF-8 explícita e fornecer fallback ASCII para caracteres de caixa caso necessário.
- **Risco:** Quebra de testes existentes que esperam strings exatas de prompt do Questionary.
  - *Mitigação:* Atualizar os testes com as novas strings de escolhas (contendo atalhos numéricos) garantindo validação completa.
- **Suposição:** Usuários do terminal operam com largura mínima padrão de 80 colunas; larguras menores recebem cabeçalho compacto automático.
- **Rollback:** Cada issue possui PR isolada e revisável; em caso de regressão imprevista, o commit da respectiva entrega pode ser revertido mantendo a integridade da CLI.

## Sequência recomendada

1. Submeter este plano para revisão crítica formal via `.agent/workflows/revisar_plano.md`.
2. Obter parecer e autorização humana pós-revisão.
3. Criar as issues correspondentes no GitHub.
4. Implementar a Issue 1 (Módulo de telas e banner).
5. Implementar a Issue 2 (Adoção nos menus interativos).
6. Executar validação completa de gates (`validate_governance`, `ruff`, `pytest`).
7. Concluir o ciclo com task de encerramento e PR documental.

## Referências

- Documento de ideação: [`_project/ideations/004_interface_retro_e_telas_msdos.md`](file:///c:/Programas/utility-belt/_project/ideations/004_interface_retro_e_telas_msdos.md)
- Diretrizes de governança: [`_project/README.md`](file:///c:/Programas/utility-belt/_project/README.md)
- Comportamento de agentes: [`.agent/ai_behavior.md`](file:///c:/Programas/utility-belt/.agent/ai_behavior.md)
- Registro de ciclos: [`_project/cycles.md`](file:///c:/Programas/utility-belt/_project/cycles.md)

## Rastreabilidade

| Campo | Valor |
| :-- | :-- |
| Issue(s) | [#8](https://github.com/EuThiagoAndrade/utility-belt/issues/8), [#9](https://github.com/EuThiagoAndrade/utility-belt/issues/9) |
| PR(s) | [#10](https://github.com/EuThiagoAndrade/utility-belt/pull/10) |
| Branch(es) | `feature/issue-8`, `feature/issue-9` |
| `handoff_schema_version` | `1` |
| `handoff_id` | `utility-belt/cycle-004/criar_issues/004_plan/53dd891` |
| Destino após conclusão | `_project/executed/004_interface_retro_e_telas_msdos/004_plan.md` |

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: `utility-belt/cycle-004/criar_issues/004_plan/53dd891`
- `identity_source`: `utility-belt + cycle-004 + criar_issues + 004_plan + 53dd891`
- `effect_class`: `remote_mutation`
- `state_before`: `Plano aprovado e issues remotas ainda ausentes no GitHub.`
- `state_after`: `Issues #8 e #9 criadas no GitHub e registradas no plano com rastreabilidade completa.`
- `next_transition`: `issue -> implementação autorizada`
- `preconditions`: `Plano aprovado pelo usuário, decomposição válida e acesso remoto confirmado.`
- `authority`: `Autorização explícita do usuário para criar as issues do plano.`
- `evidence`: `https://github.com/EuThiagoAndrade/utility-belt/issues/8 e https://github.com/EuThiagoAndrade/utility-belt/issues/9.`
- `acceptance`: `Issues #8 e #9 criadas com sucesso, títulos, labels e corpos estritamente rastreáveis ao plano.`
- `blockers`: `nenhum`
- `result`: `executed`
- `next_workflow_recommended`: `implementar_issue`
- `next_workflow_authorized`: `nenhum`
- `actions_prohibited`: `Implementar, alterar código, abrir PR de implementação ou integrar PR sem autorização explícita subsequente.`
- `rejection_rule`: `O receptor recusa handoff ausente, incompatível, sem aprovação, sem issue canônica ou sem evidência remota.`
- `logical_key`: `utility-belt/cycle-004/criar_issues/004_plan/53dd891`
- `check_before_mutation`: `Confirmado que não existiam issues abertas para o ciclo 004 no repositório.`
- `reconcile_existing`: `Issues criadas e vinculadas aos itens do plano.`
- `ambiguous_state`: `Parar em caso de divergência de numeração ou falha de conectividade remota.`

## Revisão crítica

- **Data:** 2026-09-17
- **Versão revisada:** v1 (commit `c554376`)
- **Veredito:** `APTO COM RESSALVAS`
- **Bloqueios remanescentes:** Nenhum
- **Aprovação humana pós-revisão:** Aprovada em 2026-09-17
- **Correções materiais:** Nenhuma correção estrutural necessária no plano; todas as seções canônicas foram atendidas com precisão.
- **Ressalvas:**
  1. No módulo `src/utility_belt/ui/screen.py`, a verificação de largura do terminal deve usar `shutil.get_terminal_size(fallback=(80, 24))` de forma estritamente defensiva, assegurando que pipes e ambientes de teste não-interativos operem sem erros.
  2. O helper de tela dedicada (`run_dedicated_screen`) deve conter parâmetro ou ponto de injeção para suprimir a pausa `press_any_key_to_continue` durante testes automatizados, evitando bloqueios na execução do pytest.

## Pós-mortem

- **Data de conclusão:** —
- **Desvios:** —
- **Lições comprovadas:** —
