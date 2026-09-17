# Plano de Implementação — Interface Retrô MS-DOS e Identidade Visual

> **Ciclo:** `004`
> **Status:** `Rascunho`
> **Versão:** `v1`
> **Data de criação:** 2026-09-17
> **Última atualização:** 2026-09-17
> **Tipo:** `feature`
> **Prioridade:** `P1`
> **Revisão formal:** `Pendente`
> **Veredito da revisão:** `Pendente`
> **Aprovação humana pós-revisão:** `Pendente`

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
- [ ] `clear_screen` executa a limpeza sem lançar exceções mesmo em ambientes não-TTY.
- [ ] O banner híbrido possui largura máxima de 78 colunas e não ultrapassa os limites do terminal.
- [ ] Terminais com largura inferior a 80 colunas recebem cabeçalho compacto sem distorção gráfica.
- [ ] A configuração `show_banner: false` suprime a arte ASCII e renderiza cabeçalho simplificado.
- [ ] Testes unitários cobrindo o módulo `ui/screen.py` implementados e passando.

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
- [ ] Navegar no menu principal limpa a tela a cada transição sem empilhamento de menus anteriores.
- [ ] Entrar e sair dos submenus do Docker e Restic limpa a tela mantendo cabeçalho contextual visível.
- [ ] Execução de rotinas do Docker, Restic e Doctor exibe cabeçalho dedicado e solicita confirmação antes de voltar ao menu.
- [ ] Atalhos numéricos e navegação por setas funcionam harmoniosamente em todos os menus.
- [ ] Todos os testes em `tests/test_interactive_menus.py` passam com sucesso.

## Arquivos afetados

- `src/utility_belt/ui/screen.py` (novo): Módulo centralizado de telas, banner híbrido, molduras e cabeçalhos.
- `src/utility_belt/config.py`: Suporte à chave de configuração `show_banner`.
- `src/utility_belt/menu.py`: Adoção do módulo de telas, banner de abertura e atalhos numéricos.
- `src/utility_belt/ui/docker_menu.py`: Adoção de cabeçalhos compactos, tela dedicada e atalhos.
- `src/utility_belt/ui/restic_menu.py`: Adoção de cabeçalhos compactos, tela dedicada e atalhos.
- `tests/test_screen.py` (novo): Testes unitários para o módulo de telas e banner.
- `tests/test_interactive_menus.py`: Atualização dos testes de menus interativos.
- `_project/cycles.md`: Atualização do estado do ciclo 004 para `Planejamento`.

## Decomposição em issues e PRs

1. **Issue 1 — Fundação Visual e Módulo de Telas Retrô:**
   - Escopo: Implementação de `src/utility_belt/ui/screen.py`, banner híbrido retrô com canivete ASCII e tipografia 3D, cabeçalhos com breadcrumbs, helper de tela dedicada, configuração `show_banner` e testes em `tests/test_screen.py`.
   - Branch: `feature/issue-X` (a ser numerada na criação da issue).
   - PR: 1 PR focada na infraestrutura de telas e testes unitários.
2. **Issue 2 — Adoção de Telas Dedicadas nos Menus Interativos:**
   - Escopo: Integração do módulo de telas no menu principal (`menu.py`), submenus (`docker_menu.py`, `restic_menu.py`), atalhos numéricos, telas de execução de ações e atualização de `tests/test_interactive_menus.py`.
   - Branch: `feature/issue-Y` (a ser numerada na criação da issue).
   - PR: 1 PR focada na experiência do usuário e validação dos fluxos de menu.

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
| Issue(s) | — |
| PR(s) | — |
| Branch(es) | `chore/cycle-004-plan` |
| `handoff_schema_version` | `1` |
| `handoff_id` | `utility-belt/cycle-004/rascunhar_plano/004_plan/b51503a` |
| Destino após conclusão | `_project/executed/004_interface_retro_e_telas_msdos/004_plan.md` |

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: `utility-belt/cycle-004/rascunhar_plano/004_plan/b51503a`
- `identity_source`: `utility-belt + cycle-004 + rascunhar_plano + 004_plan + b51503a`
- `effect_class`: `local_mutation`
- `state_before`: `Ideação 004 registrada; plano inexistente.`
- `state_after`: `Plano rastreável em estado Rascunho instanciando integralmente o template canônico em _project/drafts/004_interface_retro_e_telas_msdos/004_plan.md.`
- `next_transition`: `rascunho -> revisão formal (via revisar_plano)`
- `preconditions`: `Ciclo 004 identificado, objetivo delimitado e autoridade para rascunhar concedida pelo usuário.`
- `authority`: `Solicitação explícita do usuário para rascunhar o plano.`
- `evidence`: `_project/drafts/004_interface_retro_e_telas_msdos/004_plan.md e branch chore/cycle-004-plan.`
- `acceptance`: `Plano completo em estado Rascunho, decomposição em 2 issues, gates de qualidade e não-objetivos explícitos.`
- `blockers`: `nenhum`
- `result`: `executed`
- `next_workflow_recommended`: `revisar_plano`
- `next_workflow_authorized`: `nenhum`
- `actions_prohibited`: `Escrever Aprovado, criar issues, implementar código-fonte ou abrir PRs de implementação sem revisão e aprovação humana subsequente.`
- `rejection_rule`: `O receptor recusa handoff ausente, incompatível, sem revisão formal ou com status promovido indevidamente.`
- `logical_key`: `utility-belt/cycle-004/rascunhar_plano/004_plan/b51503a`
- `check_before_mutation`: `Confirmado que não existia plano prévio para o ciclo 004.`
- `reconcile_existing`: `Criado novo plano canônico na pasta drafts conforme a governança.`
- `ambiguous_state`: `Parar em caso de conflito de status, ciclo ou divergência de revisão.`

## Revisão crítica

- **Data:** —
- **Versão revisada:** —
- **Veredito:** `Pendente`
- **Bloqueios remanescentes:** —
- **Aprovação humana pós-revisão:** `Pendente`
- **Correções materiais:** —
- **Ressalvas:** —

## Pós-mortem

- **Data de conclusão:** —
- **Desvios:** —
- **Lições comprovadas:** —
