# Ideação — 009: Ferramentas Dev: Janitor e Git-Tidy

> **Ciclo:** `009`
> **Estado:** `Ideação`
> **Criado em:** 2026-10-17
> **Última atualização:** 2026-10-17

## Problema

Desenvolvedores e mantenedores de software enfrentam recorrentemente duas fontes silenciosas de atrito operacional e degradação de ambiente local:

1. **Acúmulo descontrolado de caches e dependências de build:**
   Em ambientes com múltiplos projetos (Node.js, Python, Rust, Java/Gradle, .NET), diretórios efêmeros (`node_modules`, `.venv`, `target`, `.pytest_cache`, `.next`, `__pycache__`) acumulam dezenas ou centenas de gigabytes no disco. Ferramentas convencionais de análise de disco do sistema operacional (como WinDirStat, TreeSize ou o Windows Explorer) são agnósticas a desenvolvimento: demoram muitos minutos para ler centenas de milhares de pequenos arquivos de texto, não distinguem projetos ativos de projetos inativos há meses e frequentemente falham no Windows ao tentar apagar diretórios profundos devido a limites de caminho (`MAX_PATH`) ou travas de arquivo.

2. **Cemitério de branches locais e remotas:**
   Com a prática de branches curtas para cada feature ou correção, branches mescladas no GitHub/GitLab (especialmente via *Squash and Merge* ou *Rebase and Merge*) permanecem órfãs no repositório local. O comando clássico `git branch --merged` falha em fluxos modernos de squash (pois os hashes locais divergem do commit gerado na `main`), forçando limpezas manuais trabalhosas. Paralelamente, nos servidores remotos (`origin`), branches de PRs concluídas ou abandonadas acumulam-se quando o autor não ativa a exclusão automática pós-merge. O desenvolvedor hesita em limpar por receio de apagar trabalho não publicado ou afetar branches canônicas.

## Contexto e evidências

- Baseline técnico: commit `16226574f7d432b49dfd1f14890ef9bb9dc8fdfa` na branch `main`.
- Arquitetura do Utility Belt:
  - Framework CLI baseado em `typer` (`src/utility_belt/cli.py`) com catálogo modular e classificação de risco (`read`, `write`, `destructive`).
  - Interface de Terminal (TUI) canônica estilo MS-DOS (`src/utility_belt/ui/screen.py`) com Questionary para navegação guiada por setas/atalhos numéricos, mensagens com estilo padronizado e paleta consistente.
  - Subsistema de diagnóstico e saúde do ambiente (`src/utility_belt/doctor.py`) capaz de validar a disponibilidade de binários externos (como `git`).
  - Suporte multiplataforma (Windows e Linux) respeitando caminhos e convenções de cada sistema operacional.
- Alinhamento com o responsável em 2026-10-17:
  - O responsável solicitou expressamente a criação das ferramentas de desenvolvimento:
    - `belt dev janitor` — Faxineiro de Caches e Dependências.
    - `belt dev git-tidy` — Higienizador Inteligente de Repositórios com capacidade de exclusão de branches tanto **locais** quanto **remotas** (com confirmação segura e estrita proteção de integridade).
  - Determinação de foco cirúrgico na implementação solicitada, preservando a governança, arquitetura e identidade visual do Utility Belt.

## Resultado desejado

1. **Módulo de Ferramentas de Desenvolvimento (`belt dev`):**
   - Criação do grupo de comandos `belt dev` na CLI e correspondente submenu na TUI MS-DOS.

2. **`belt dev janitor` (Limpeza de Caches de Projetos):**
   - **Varredura rápida (*Pruning Traversal*):** Busca recursiva a partir de um diretório alvo que identifica pastas de dependências e builds descartáveis conhecidas (`node_modules`, `target`, `.venv`, `.pytest_cache`, `__pycache__`, `.next`, `.turbo`, `.gradle`, `bin/`, `obj/`, etc.) e calcula seu tamanho sem descer desnecessariamente na árvore interna de cada artefato.
   - **Heurística de atividade e proteção:** Identificação da última modificação ou commit recente para classificar projetos ativos (protegidos por padrão) versus projetos inativos (candidatos à limpeza).
   - **Interface TUI interativa:** Exibição clara em tela MS-DOS com checkboxes interativos (Questionary), indicando caminho, tamanho e tempo de inatividade, com totalizador dinâmico de espaço a ser recuperado.
   - **Execução segura:** Suporte a `--dry-run`, suporte a long paths no Windows e nunca remoção de arquivos-fonte ou de configuração (`package.json`, `pyproject.toml`, `.git`, etc.).

3. **`belt dev git-tidy` (Higienização de Branches Locais e Remotas):**
   - **Sincronização prévia:** Execução de `git fetch --prune` para reconciliação com o remoto.
   - **Classificação inteligente de branches locais:**
     - Branches mergeadas diretamente;
     - Branches com remoto já removido (`[gone]`) decorrentes de *Squash & Merge*;
     - Branches com trabalho exclusivo/pendente (em destaque de advertência, desmarcadas por padrão).
   - **Higienização de branches remotas (`--remote` ou seleção na TUI):**
     - Identificação de branches em `origin` cujas PRs já foram incorporadas ou fechadas.
     - Classificação de risco `destructive` exigindo confirmação explícita antes de `git push origin --delete`.
   - **Travas estritas de proteção:** Proteção absoluta contra remoção de `HEAD` atual e de branches canônicas (`main`, `master`, `dev`, `develop`, `staging`, `production`, `release/*`).
   - **Interface TUI e CLI:** Navegação visual na tela MS-DOS e flags para uso scriptável (`--dry-run`, `--remote`, `--all`).

## Hipóteses

- O uso das bibliotecas padrão do Python (`pathlib`, `os.scandir`, `shutil`, `subprocess`) é suficiente para implementar ambas as ferramentas com alta performance e sem introduzir dependências externas desnecessárias no `pyproject.toml`.
- O aproveitamento do componente visual `screen.py` assegura continuidade estética e ergonomia idêntica aos submenus já consolidados (Docker, Restic, Markdown).
- O diagnóstico do `git` via `doctor.py` garante que comandos do `git-tidy` falhem preventivamente com mensagem amigável caso o ambiente não possua Git instalado ou não esteja dentro de um repositório válido.

## Alternativas

1. **Separar `janitor` e `git-tidy` em ciclos diferentes:** Rejeitada nesta ideação porque ambas compõem de forma sinérgica o novo pilar de utilitários de desenvolvimento (`belt dev`), podendo ser decompostas em issues específicas durante o planejamento.
2. **Implementar apenas limpeza local no `git-tidy`:** Rejeitada, pois o responsável solicitou expressamente a higienização remota segura, que resolve uma dor crítica de acúmulo de branches órfãs em repositórios remotos.
3. **Depender de bibliotecas pesadas de terceiros (como `GitPython`):** Rejeitada para evitar overhead de dependências; chamadas limpas ao binário do `git` via `subprocess` com tratamento de exceções garantem simplicidade e alinhamento com a arquitetura do projeto.

## Riscos e restrições

- **Exclusão inadvertida de dados (Operação Destrutiva):**
  - O `janitor` deve possuir uma lista restritiva (*allowlist*) de nomes de pastas de cache/build elegíveis para deleção. Pastas desconhecidas ou raízes de projetos jamais serão tocadas.
  - Suporte a `--dry-run` obrigatório em ambos os comandos.
- **Risco de remoção de branch remota em uso por outros colaboradores:**
  - O `git-tidy` deve proibir terminantemente a deleção de branches protegidas.
  - Na exclusão remota, a TUI deve exigir confirmação reforçada e exibir a lista exata de nomes que serão apagados no `origin`.
- **Limites de caminhos longos no Windows (`MAX_PATH`):**
  - No Windows, diretórios como `node_modules` profundamente aninhados podem exceder 260 caracteres. A exclusão deve utilizar prefixos estendidos `\\?\` ou funções seguras do Python 3.11+.
- **Fidelidade à identidade visual:**
  - Manter rigorosamente a tipografia, cores e molduras padronizadas em `src/utility_belt/ui/screen.py`.

## Perguntas em aberto

- No `janitor`, se o usuário não informar um caminho via CLI, a ferramenta deve assumir o diretório atual (`.`) ou abrir um prompt interativo sugerindo diretórios comuns de projetos?
- No `git-tidy`, para detecção precisa de PRs com *Squash & Merge*, caso o GitHub CLI (`gh`) esteja autenticado no sistema, devemos utilizá-lo como enriquecimento opcional de telemetria?

## Fora do escopo

- Limpeza de arquivos de sistema operacional fora de repositórios/diretórios de código (como cache de Windows Update ou arquivos temporários do SO).
- Operações de histórico do Git além da exclusão de branches (como rebase interativo, reset destrutivo de commits ou limpeza de reflog).
- Criação de novos projetos ou templates (scaffolding).

## Critérios para iniciar o planejamento

- Validação formal desta ideação pelo responsável.
- Confirmação da taxonomia de subcomandos (`belt dev janitor`, `belt dev git-tidy`).
- Alinhamento sobre a separação de issues (ex.: Issue 1 para Janitor, Issue 2 para Git-Tidy).

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+009+idear+ferramentas-dev-janitor-git-tidy+1622657`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`
- `effect_class`: `local_mutation`
- `state_before`: ausência de utilitários dedicados de desenvolvimento no Utility Belt; acúmulo manual de caches pesados e branches órfãs locais e remotas.
- `state_after`: ideação do ciclo 009 registrada detalhando o problema, arquitetura de `belt dev janitor` e `belt dev git-tidy`, requisitos de segurança e riscos.
- `next_transition`: `ideia -> rascunho de plano`, condicionada à aprovação humana.
- `preconditions`: contexto do repositório compreendido, baseline de testes verde e demanda explícita do responsável.
- `authority`: responsável, alinhamento registrado em 2026-10-17.
- `evidence`: `_project/ideations/009_ferramentas_dev_janitor_git_tidy.md`, `src/utility_belt/cli.py`, `src/utility_belt/ui/screen.py`, `src/utility_belt/doctor.py`.
- `acceptance`: separação rigorosa de fatos, hipóteses, alternativas, riscos de exclusão destrutiva e travas de proteção descritas conforme o template canônico.
- `blockers`: nenhum para a fase de ideação.
- `result`: `executed`
- `next_workflow_recommended`: `rascunhar_plano`
- `next_workflow_authorized`: nenhum (aguardando aprovação humana desta ideação).
- `actions_prohibited`: implementar código de produção, criar issues, aprovar plano sem revisão formal ou abrir PR sem autorização explícita.
- `rejection_rule`: o receptor recusa handoff ausente, incompatível, sem evidência ou sem autoridade explícita.
- `logical_key`: `EuThiagoAndrade/utility-belt+009+idear+ferramentas-dev-janitor-git-tidy+1622657`
- `check_before_mutation`: ciclo 009 vago em `_project/cycles.md`, sem artefatos conflitantes.
- `reconcile_existing`: atualizar este artefato caso haja novos refinamentos sem duplicar o número do ciclo.
- `ambiguous_state`: interromper a mutação e solicitar intervenção humana caso haja divergência.
