# Ideação — 010: Compatibilidade e Padronização Visual de Menus

> **Ciclo:** `010`
> **Estado:** `Ideação`
> **Criado em:** 2026-10-20
> **Última atualização:** 2026-10-20

## Problema

Foram identificados dois pontos de atenção na interface de usuário do Utility Belt:

### 1. Incompatibilidade de opções em caixas de seleção múltipla (`questionary.checkbox`)
Ao executar fluxos interativos de seleção múltipla — como o **Git-Tidy: Higienização Completa** (`run_git_tidy_all_flow`), **Git-Tidy: Branches Locais** (`run_git_tidy_local_flow`), **Git-Tidy: Branches Remotas** (`run_git_tidy_remote_flow`) ou o **Janitor** (`run_janitor_flow`) —, a aplicação aborta com o seguinte erro em tempo de execução quando há itens elegíveis para exibição:

```text
[ERRO] Não foi possível concluir a operação.
PromptSession.__init__() got an unexpected keyword argument 'use_shortcuts'
```

O erro decorre do repasse do dicionário gerado por `menu_options()` (definido em `src/utility_belt/ui/screen.py`) para `questionary.checkbox(...)`. Enquanto `questionary.select(...)` suporta e consome o argumento `use_shortcuts=False`, `questionary.checkbox(...)` não possui esse parâmetro em sua assinatura formal. Consequentemente, o argumento desconhecido cai em `**kwargs` e é repassado internamente para `prompt_toolkit.shortcuts.PromptSession`, que não o aceita e lança `TypeError`.

### 2. Inconsistência na linha divisória (separador) antes do item `[0]` nos submenus
No Utility Belt existe um padrão visual consolidado nos menus: antes da opção de retorno ou saída `[0]`, é renderizada uma linha horizontal divisória usando `menu_separator()`.
Esse padrão está presente em:
- Menu Principal (antes do `[0] Sair`);
- Submenu Sistema (antes do `[0] Voltar ao menu principal`);
- Submenu Restic (antes do `[0] Voltar ao menu principal`);
- Submenu Docker (antes do `[0] Voltar ao menu principal`).

Porém, esse padrão não se repete em:
- **Markdown** (`src/utility_belt/ui/markdown_menu.py`): o item `[0]` fica imediatamente após o item `[5]`, sem linha divisória;
- **Desenvolvimento** (`src/utility_belt/ui/dev_menu.py`): o item `[0]` fica imediatamente após o item `[4]`, sem linha divisória.

Essa discrepância quebra a uniformidade visual entre os submenus do sistema.

## Contexto e evidências

- Baseline: commit `99e7e37` na branch `main`.
- Evidência do erro de runtime: Captura de tela em Windows PowerShell executando `Desenvolvimento > Git-Tidy: Higienização Completa` com a mensagem `PromptSession.__init__() got an unexpected keyword argument 'use_shortcuts'`.
- Evidência de código para o problema de opções:
  - `src/utility_belt/ui/dev_menu.py` (linhas 70, 153 e 211): chamadas a `prompt(questionary.checkbox, ..., **menu_options())`.
  - `src/utility_belt/ui/screen.py` (linhas 111-114): `menu_options()` inclui `"use_shortcuts": False`.
- Evidência de código para a inconsistência visual do separador:
  - `src/utility_belt/menu.py`: inclui `menu_separator()` antes de `[0]` no menu raiz e no submenu Sistema.
  - `src/utility_belt/ui/restic_menu.py`: inclui `menu_separator()` antes de `[0] Voltar ao menu principal`.
  - `src/utility_belt/ui/docker_menu.py`: inclui `menu_separator()` antes de `[0] Voltar ao menu principal`.
  - `src/utility_belt/ui/markdown_menu.py`: lista de escolhas define `[0] Voltar ao menu principal` diretamente na tupla de choices sem `menu_separator()`.
  - `src/utility_belt/ui/dev_menu.py`: lista de escolhas define `[0] Voltar ao menu principal` diretamente na tupla de choices sem `menu_separator()`.

## Resultado desejado

1. **Robustez nos fluxos de checklist**: Usuários conseguem utilizar `Git-Tidy` (local, remoto e completo) e `Janitor` sem qualquer quebra por `TypeError` ao selecionar itens.
2. **Saneamento de opções de prompt**:
   - `menu_options()` deve fornecer apenas opções universais compatíveis com todos os prompts do Questionary.
   - Opções exclusivas de menus `select` (como `use_shortcuts`) não devem vazar para componentes `checkbox`.
   - O helper `prompt()` em `screen.py` deve atuar de forma defensiva para evitar repasse de argumentos incompatíveis ao `PromptSession`.
3. **Padronização visual estrita em 100% dos menus**:
   - Inserir `menu_separator()` antes da opção `[0] Voltar ao menu principal` no menu de **Markdown** (`markdown_menu.py`).
   - Inserir `menu_separator()` antes da opção `[0] Voltar ao menu principal` no menu de **Desenvolvimento** (`dev_menu.py`).
   - Todos os submenus e menus do Utility Belt passam a apresentar rigorosamente a mesma estrutura visual: opções numeradas de ferramentas, linha separadora `menu_separator()`, opção `[0]` de saída/retorno e rodapé de navegação `menu_footer()`.
4. **Cobertura de testes automatizados**:
   - Testes unitários para o comportamento seguro de `menu_options()` e `prompt()`.
   - Testes nos fluxos interativos de `dev_menu` (`git-tidy` e `janitor`) e validação da estrutura de choices de `markdown_menu` e `dev_menu`.

## Hipóteses

- A unificação do padrão visual com `menu_separator()` antes do item `[0]` em `markdown_menu.py` e `dev_menu.py` é uma alteração simples e cirúrgica, reutilizando o componente canônico já testado nos demais submenus.
- A remoção de `use_shortcuts` de `menu_options()` e a criação de tratamento defensivo em `prompt()` corrige os fluxos de `checkbox` sem degradar os menus `select`.
- Ambos os itens tratam de polimento e robustez da camada de apresentação/menus (`utility_belt.ui`), fazendo sentido comporem o mesmo ciclo (ciclo `010`).

## Alternativas

### Para a compatibilidade de opções (`checkbox`):
1. **Alternativa 1 — Opções universais em `menu_options()` e especialização para `select`**:
   `menu_options()` mantém apenas opções universais (`style`, `qmark`, `pointer`, `instruction`). Caso `use_shortcuts` seja necessário em `select`, ele é aplicado especificamente.
2. **Alternativa 2 — Abordagem Combinada (Recomendada)**:
   Higienizar `menu_options()` para conter apenas parâmetros seguros e, complementarmente, aplicar filtragem defensiva em `prompt(factory, ...)` para descartar chaves incompatíveis caso surjam no futuro.

### Para a padronização dos separadores:
1. **Alternativa A — Padronizar com linha separadora antes do `[0]` em todos os menus (Escolhida)**:
   Adicionar `menu_separator()` antes do `[0]` em `markdown_menu.py` e `dev_menu.py`, alinhando-os ao Menu Principal, Restic, Docker e Sistema.
2. **Alternativa B — Remover a linha separadora de todos os menus**:
   Rejeitada, pois a separação visual do botão de retorno/saída foi avaliada como superior para usabilidade e legibilidade no terminal.

## Riscos e restrições

- **Navegação do Questionary**: `questionary.Separator` não é selecionável e é ignorado pela navegação com as setas (o cursor salta o separador), portanto não altera a ordem lógica dos valores de retorno (`choice`).
- **Testes existentes de menus**: Devemos garantir que testes que inspecionam o número de escolhas ou renderização (`tests/test_interactive_menus.py`) sejam atualizados ou continuem passando normalmente.
- **Não regressão visual**: As cores e estilos do `menu_style()` e das molduras devem permanecer inalterados.

## Perguntas em aberto

- Nenhuma pendência crítica: a inclusão do separador antes do `[0]` segue o padrão de código já adotado em `src/utility_belt/ui/docker_menu.py` e `src/utility_belt/ui/restic_menu.py`.

## Fora do escopo

- Alterações na lógica de negócios do `git_tidy` ou do `janitor`.
- Alterações nos comandos de linha de comando não interativos (`belt dev ...`, `belt md ...`).
- Criação de novos submenus ou novas ferramentas.

## Critérios para iniciar o planejamento

- Alinhamento e aprovação do escopo composto (correção do checkbox + inclusão do separador em Markdown e Desenvolvimento) pelo solicitante.
- Atualização e consolidação do registro do ciclo `010` em `_project/cycles.md`.
- Autorização humana para avançar para o workflow de rascunho de plano (`rascunhar_plano.md`).

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+010+idear+correcoes-e-padronizacao-menus+99e7e37`
- `identity_source`: `EuThiagoAndrade/utility-belt + 010 + idear + correcoes-e-padronizacao-menus + 99e7e37`
- `effect_class`: `local_mutation`
- `state_before`: erro em runtime `use_shortcuts` em `checkbox` do `dev_menu` e inconsistência visual sem linha separadora antes do `[0]` nos submenus de Markdown e Desenvolvimento.
- `state_after`: ideação do ciclo 010 expandida e documentada cobrindo a correção técnica de opções do `checkbox` e a padronização visual com `menu_separator()` em Markdown e Desenvolvimento.
- `next_transition`: `ideia -> rascunho de plano` (workflow `.agent/workflows/rascunhar_plano.md`), sujeito à autorização humana.
- `preconditions`: dois itens mapeados e alinhados com o usuário.
- `authority`: usuário, feedback em 2026-10-20.
- `evidence`: `_project/ideations/010_correcoes_e_padronizacao_menus.md`, `src/utility_belt/ui/dev_menu.py`, `src/utility_belt/ui/markdown_menu.py`, `src/utility_belt/ui/screen.py`.
- `acceptance`: ambos os problemas delimitados com contexto, alternativas e critérios de planejamento.
- `blockers`: nenhum para a fase de ideação.
- `result`: `executed`
- `next_workflow_recommended`: `rascunhar_plano`
- `next_workflow_authorized`: nenhum (aguardando autorização humana).
- `actions_prohibited`: implementar código de produção, criar issues ou abrir PRs antes do plano ser rascunhado, formalmente revisado e aprovado.
- `rejection_rule`: o receptor recusa handoff sem autoridade ou evidência material verificável.
- `logical_key`: `EuThiagoAndrade/utility-belt+010+idear+correcoes-e-padronizacao-menus+99e7e37`
- `check_before_mutation`: ciclo 010 reservado em `_project/cycles.md` como `Ideação`.
- `reconcile_existing`: atualizar o artefato caso novos refinamentos sejam pedidos antes do planejamento.
- `ambiguous_state`: interromper a mutação e solicitar alinhamento caso haja conflito de diretrizes.
