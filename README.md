# Utility Belt (`belt`)

[![Release](https://img.shields.io/github/v/release/EuThiagoAndrade/utility-belt)](https://github.com/EuThiagoAndrade/utility-belt/releases)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Canivete suíço pessoal de terminal para Windows e Linux.

O **Utility Belt** unifica ferramentas de linha de comando em um pacote Python isolado, distribuível e de fácil atualização. Ele organiza scripts e utilitários em um catálogo declarativo baseado em manifestos (`tool.toml`), oferecendo tanto execução direta e scriptável via CLI quanto uma interface interativa de terminal (TUI) rica com navegação guiada.

---

## Recursos Principais

- **Interface Dupla:** Uso via linha de comando direta (scriptável em CI/automações) ou via menus interativos no terminal (TUI orientada a prompts com `questionary`).
- **Catálogo Modular:** Ferramentas registradas de forma declarativa com metadados de plataforma, tempo de execução e classificação de risco (`read`, `write`, `destructive`).
- **Adaptadores de Ferramentas:**
  - **Docker:** Exportação e importação segura de imagens com manifestos e simulação (`--dry-run`).
  - **Restic:** Gerenciamento de repositórios, backups incrementais, restauração de snapshots e conferência de integridade.
  - **Markdown:** Arquivo/URL, lote recursivo, monitor de novos arquivos, clipboard e pasta central configurável.
  - **Desenvolvimento (`belt dev`):** Faxineiro de caches e dependências de compilação (`janitor`) com pré-seleção universal e modo simulação, e higienizador seguro de branches locais e remotas órfãs ou mescladas (`git-tidy`).
  - **System Info:** Coleta rápida de diagnósticos do ambiente de execução.
- **Configuração Atômica e Perfis:** Persistência segura em TOML (`tomli-w`) no diretório padrão do usuário (`platformdirs`), com suporte a múltiplos perfis de backup.
- **Diagnóstico do Ambiente (`doctor`):** Verificação imediata da integridade de binários e dependências externas instaladas no sistema operacional.

---

## Pré-requisitos

- Python 3.11 ou superior
- Gerenciador [`uv`](https://docs.astral.sh/uv/) (recomendado para instalação e desenvolvimento)
- **Dependências externas do sistema (conforme o uso):**
  - [Docker Engine / Docker Desktop](https://www.docker.com/) (necessário para subcomandos `belt docker`)
  - [Restic](https://restic.net/) instalado e acessível no `PATH` (necessário para subcomandos `belt restic`)

---

## Instalação e Atualização

Instalação isolada recomendada como ferramenta global via `uv`:

```bash
uv tool install "git+https://github.com/EuThiagoAndrade/utility-belt.git@main"
uv tool update-shell
```

Para atualizar para a versão mais recente em qualquer máquina:

```bash
uv tool upgrade utility-belt
```

Para verificar a versão instalada:

```bash
belt --version
```

*(O comando alternativo `utility-belt` também é disponibilizado como alias).*

---

## Experiência Interativa (TUI)

Em qualquer terminal interativo (TTY), **basta digitar `belt` sem parâmetros** para abrir o menu guiado geral:

```bash
belt
```

Você também pode navegar diretamente para menus dedicados de cada módulo:

```bash
belt menu             # Menu interativo principal
belt docker menu      # Menu interativo de operações com Docker (ou apenas 'belt docker')
belt restic menu      # Menu interativo de operações com Restic (ou apenas 'belt restic')
belt markdown menu    # Menu das cinco ações Markdown (ou apenas 'belt markdown')
belt dev menu         # Menu interativo de ferramentas de desenvolvimento (ou apenas 'belt dev')
```

> **Nota:** Em ambientes não interativos (como rotinas de CI ou cron jobs), chamar `belt` sem argumentos exibe a ajuda padrão em vez de aguardar entrada do usuário.

O menu principal apresenta **Restic**, **Docker**, **Markdown**, **Desenvolvimento** e **Sistema**, com
descrições curtas e seleção destacada. **Desenvolvimento** reúne o Faxineiro de Caches (Janitor)
e o Higienizador Git-Tidy (local e remoto). **Sistema** reúne Verificar ambiente,
Informações do computador e Sobre o Utility Belt. Navegue com ↑↓ e Enter;
em telas de seleção múltipla (checklists), a Barra de Espaço marca/desmarca, a tecla 'a' seleciona
todos e Enter confirma; Ctrl+C volta do submenu ou encerra o menu principal. Os números identificam as
opções; a seleção é por setas e Enter.

As operações mostram informação, sucesso, aviso, erro ou cancelamento em blocos
separados. Resultados permanecem visíveis até a confirmação de retorno. A
conversão Markdown informa as etapas e a localização do arquivo gerado, com um
resumo ao terminar um lote. `NO_COLOR=1` desativa as cores; saídas redirecionadas
não recebem cores ou limpeza de tela. O cabeçalho se adapta à largura disponível.

---

## Referência da CLI (Modo Direto)

### Versões e releases automáticos

A fonte única de versão é `src/utility_belt/__init__.py`. Os metadados do pacote,
o cabeçalho, Sobre e `belt --version` usam essa mesma versão.

Após integrar mudanças na `main`, o workflow Release valida a revisão em
Windows e Linux, calcula o incremento pelos commits convencionais e verifica o
build. Ele publica um commit mecânico com versão, `uv.lock` e `CHANGELOG.md`, uma
tag `vX.Y.Z` e uma GitHub Release. Os commits seguem a convenção do projeto:

- `feat(issue-N): ...`: incrementa MINOR (`0.1.0` → `0.2.0`).
- `fix(issue-N): ...`: incrementa PATCH (`0.2.0` → `0.2.1`).
- `!` no cabeçalho ou `BREAKING CHANGE:` no corpo: MINOR em `0.x`; MAJOR a partir de `1.x`.
- `docs`/`chore` isolados: não incrementam a versão.

Vários commits pendentes usam o maior incremento uma vez. Se fizer squash,
preserve a convenção no título/corpo do commit resultante. O primeiro release
considera apenas mudanças posteriores ao baseline `e9f375f`; os seguintes usam
a tag da versão atual. Não há renumeração retroativa dos ciclos anteriores.

A automação utiliza `GITHUB_TOKEN` com `contents: write`, sem segredo adicional.
Commit e tag são enviados atomicamente, sem force; concorrência ou proteção da
branch podem impedir a publicação, e o workflow falha sem contornar regras. Uma
reexecução reconcilia a release da tag existente sem duplicar versão. Commits do
bot não disparam novamente o workflow de push. Não há publicação automática no
PyPI nem instalação automática em computadores de usuários; atualize com
`uv tool upgrade utility-belt`. A automação só começa após o merge da PR que a
introduz; nenhuma release é criada ao abrir essa PR.

Para conferir o cálculo localmente, sem alterar arquivos ou publicar:

```bash
uv run python scripts/release.py
```

### Diagnóstico e Saúde do Ambiente (`belt doctor`)

O `doctor` avalia a plataforma, executável Python, arquivo de configuração e disponibilidade de dependências externas no `PATH`:

```bash
belt doctor                 # Diagnóstico completo
belt doctor docker          # Verifica dependência específica
belt doctor restic
belt doctor --json          # Exporta o diagnóstico em formato JSON
```

### Catálogo de Ferramentas (`belt list` e `belt run`)

```bash
# Listar ferramentas compatíveis com o sistema operacional atual
belt list

# Listar todas as ferramentas do catálogo (incluindo incompatíveis com o SO atual)
belt list --all

# Exportar catálogo em formato JSON
belt list --json

# Executar uma ferramenta registrada no catálogo repassando argumentos
belt run system.info

# Executar em modo estritamente não-interativo
belt run system.info --non-interactive
```

### Gerenciamento de Imagens Docker (`belt docker`)

```bash
# Exportar imagens para arquivo .tar com manifesto
belt docker export -i alpine:latest -o ./imagens.tar
belt docker export --all --output ./todas-imagens.tar
belt docker export --all --dry-run                    # Simula a exportação sem gerar arquivo

# Importar imagens a partir de arquivo .tar
belt docker import -i ./imagens.tar
belt docker import -i ./imagens.tar --run             # Oferece iniciar um container após importar
belt docker import -i ./imagens.tar --dry-run         # Inspeciona manifesto sem carregar no Docker
```

### Backups e Restauração com Restic (`belt restic`)

```bash
# Inicializar um novo repositório
belt restic init --repo /caminho/do/repositorio

# Executar backup incremental
belt restic backup --source /origem --repo /caminho/do/repositorio
belt restic backup --profile trabalho                 # Utiliza parâmetros salvos no perfil
belt restic backup --profile trabalho --dry-run

# Listar snapshots existentes no repositório
belt restic snapshots --profile trabalho

# Restaurar arquivos de um snapshot
belt restic restore --snapshot latest --target /destino --profile trabalho
belt restic restore --snapshot abc12345 --target /destino --include "documentos/*.pdf"

# Verificar integridade do repositório
belt restic check --profile trabalho
belt restic check --profile trabalho --read-data     # Conferência profunda lendo todos os blocos de dados

# Migrar configurações legadas do ResticMenu para o config.toml do Utility Belt
belt restic migrate-config
```

### Conversão Markdown (`belt markdown`)

```bash
belt markdown config --output-dir ./markdown-resultados
belt markdown convert ./relatorio.pdf
belt markdown convert https://example.com --output-dir ./saida-temporaria
belt markdown batch ./documentos --non-interactive
belt markdown watch ./entrada --non-interactive
belt markdown clipboard
belt doctor markdown --json
belt doctor clipboard

# Mesmo adaptador em subprocesso; caminhos continuam relativos ao seu cwd
belt run markdown.convert --non-interactive convert ./relatorio.pdf
```

Somente `config` persiste o destino absoluto em `[markdown].output_dir`; preserva perfis e outras preferências. `--output-dir` substitui o destino somente naquela execução. TOML inválido retorna `2` sem sobrescrever o arquivo. CLI direta sem argumento ou destino retorna `2`, sem perguntar; no menu, a configuração ausente pode ser preenchida ou cancelada. `belt markdown` sem subcomando mostra ajuda fora de TTY. `menu` exige TTY.

A instalação inicial do Belt inclui apenas as bibliotecas leves de interface, HTTP, monitoramento e clipboard. **MarkItDown e extras de formatos são adquiridos depois do consentimento**, em outro ambiente: dados do usuário, `markdown/engines/markitdown-0.1.8/py<major.minor>/recipes-<revisão>/core`. No Windows, o diretório de dados padrão é `%LOCALAPPDATA%\utility-belt\utility-belt`; no Linux, `$XDG_DATA_HOME/utility-belt` ou `~/.local/share/utility-belt`. O caminho efetivo aparece em `belt doctor markdown --json`.

O motor fixado é MarkItDown `0.1.8`, em Python **3.11–3.14**; outros comandos do Belt mantêm Python >=3.11. A aquisição requer `uv >=0.12.13` no PATH, acesso ao PyPI e receitas empacotadas com versões/hashes. Não baixa Python nem instala no Python global ou no ambiente do Belt. Primeiro oferece a base e, quando necessário, o grupo específico (PDF, DOCX, PPTX, XLSX, XLS, Outlook ou legendas YouTube). Cada oferta informa finalidade/pacotes/destino e tem padrão negativo `[s/N]`. Responder `n`, cancelar, executar fora de TTY ou usar `--non-interactive` impede a aquisição. Para preparar automação, execute o formato em TTY, confirme as receitas necessárias e depois repita com `--non-interactive`. Requisito já adquirido é reutilizado sem download. Falha de instalação exige nova tentativa e novo consentimento para o que falta; não elimina resultados anteriores. Atualizações compatíveis do Belt reutilizam o runtime; outro Python ou revisão das receitas usa uma pasta distinta e preserva a anterior.

ExifTool `13.59` pode ser adquirido como binário portátil consentido para metadados locais; Linux exige Perl disponível. FFmpeg existente é reutilizado; sua aquisição portátil usa `imageio-ffmpeg==0.6.0` quando necessária para áudio comprimido. Não altera PATH nem instala pacotes do sistema. `doctor` informa grupos disponíveis e limites do clipboard, sem consentimento, instalação ou leitura do conteúdo do clipboard.

Áudio exige **outro consentimento por operação** antes de enviar conteúdo ao Google usado pelo conversor nativo. Lote identifica o conjunto finito, inclusive membros de ZIP; monitor pergunta por cada nova conversão. Autorizar instalação não autoriza transmissão. Fora de TTY, com `--non-interactive` ou após recusa, só são extraídos metadados locais disponíveis. Bibliotecas de transcrição permanecem isoladas em `audio` e sua instalação não concede autorização futura. Não há LLM, OCR por IA, Azure nem plugins habilitados.

| Entrada validada com fixtures próprias | Resultado e limites |
| :-- | :-- |
| Texto, Markdown, JSON/JSONL, CSV, HTML, notebook | Conteúdo textual; Markdown/front matter preservados conforme saída do motor |
| PDF, DOCX, PPTX, XLSX, XLS, EPUB | Texto/tabelas extraíveis; sem garantia de fidelidade visual ou OCR de PDF digitalizado |
| MSG, RSS, ZIP | Mensagens/feed/membros; membro corrompido gera parcialidade e código `1` |
| PNG/JPG, WAV, MP3/M4A/MP4 | Metadados locais; transcrição depende de consentimento e do serviço externo |
| HTTP(S), Wikipedia/Bing, YouTube | Página pública sem autenticação; conversores específicos/legendas testados com snapshots ou cliente controlado, sem promessa de disponibilidade do site |

Não há lista restritiva de extensões: entradas regulares são submetidas aos conversores nativos, inclusive extensão desconhecida ou ausente. Formato não atendido, dependência ausente, conteúdo vazio e falha de conversão têm diagnósticos distintos. O smoke público de `example.com` passou; o único smoke externo de áudio autorizado produziu transcrição incorreta em português. Isso não certifica qualidade para documentos reais, conteúdo dinâmico com JavaScript, imagens digitalizadas ou fala em português.

Saídas são UTF-8 em pasta exclusiva pelo horário local `AAAA-MM-DD_HH-MM-SS` (`_2`, `_3` em colisões), sem sobrescrever resultados. Arquivo/clipboard usa `<nome-com-extensão>.md`; URL usa `web_content.md`. Lote compartilha uma pasta e preserva caminhos relativos, por exemplo `financeiro/relatorio.pdf.md`. Monitor reserva uma pasta por novo arquivo. Sucessos e pastas já reservadas permanecem após falha/cancelamento; não há limpeza automática da origem.

Lote e monitor percorrem subpastas por padrão; excluem a árvore de saída interna, links/junctions e ciclos. Raízes de entrada/saída iguais são recusadas. Monitor roda em primeiro plano: não converte estoque inicial nem edições posteriores; novos arquivos criados/movidos e pastas movidas para a árvore são alcançados. Exclusão/recriação inicia novo ciclo. Aguarda duas observações iguais de identidade/tamanho/mtime separadas por 1 segundo e leitura possível, até 30 segundos desde o evento. Mudança antes da publicação descarta o resultado e exige estabilização dentro desse prazo. **Estabilidade é aproximação:** pausas na escrita não garantem que a cópia terminou. Timeout informa falha; conversão manual posterior é possível. Ctrl+C libera o observador e mostra o resumo.

Clipboard aceita um caminho de arquivo existente (com um par de aspas externas opcional) ou URL HTTP(S). Texto livre, vazio, diretório ou backend indisponível retorna `2`. Windows depende da sessão; Linux requer sessão gráfica com `xclip`/`xsel` ou `wl-copy`/`wl-paste`, instalados pelo usuário. Sessões headless podem não ter clipboard.

| Código | Significado |
| :-- | :-- |
| `0` | Operação finita com resultados e nenhuma falha |
| `1` | Conversão vazia/falha, instalação consentida falhou ou lote parcial |
| `2` | Entrada/configuração/requisito ausente ou recusado; nenhum candidato elegível |
| `130` | Cancelamento; monitor encerrado por Ctrl+C, resultados preservados |

### Ferramentas de Desenvolvimento (`belt dev`)

O módulo `belt dev` fornece utilitários dedicados ao dia a dia de desenvolvimento de software, com suporte a simulação (`--dry-run`), execução direta scriptável e interface interativa com checklists guiados (TUI MS-DOS).

```bash
# Abrir menu interativo de desenvolvimento em TTY (ou apenas 'belt dev')
belt dev menu

# Janitor: varredura e faxina de dependências e caches de compilação
belt dev janitor                              # Varre o diretório atual (.)
belt dev janitor ./meu-projeto                # Varre pasta específica
belt dev janitor --dry-run                    # Simula a exclusão sem remover arquivos
belt dev janitor --days 60                    # Define limiar para considerar projeto ativo (padrão: 30)
belt dev janitor --yes                        # Confirma exclusão sem confirmação interativa

# Git-Tidy: higienização segura de branches locais e remotas
belt dev git-tidy                             # Higieniza branches locais órfãs ou mergeadas
belt dev git-tidy --dry-run                   # Simula os comandos git de deleção
belt dev git-tidy --remote                    # Higieniza branches remotas em origin
belt dev git-tidy --all                       # Higieniza ambas (locais e remotas)
belt dev git-tidy --yes                       # Confirma exclusão sem confirmação interativa

# Diagnóstico de integridade para Git
belt doctor git                               # Avalia se o Git está instalado e funcional
```

#### Faxineiro de Caches e Dependências (`belt dev janitor`)
- **Alvos detectados:** diretórios de dependências pesadas e caches de compilação como `node_modules`, `target`, `.venv`, `.pytest_cache`, `.next`, `__pycache__`, `.turbo`, `.gradle`, entre outros.
- **Interatividade:** na TUI, todos os diretórios encontrados vêm pré-selecionados por padrão (`checked=True`), permitindo confirmação rápida ou ajuste via `<Espaço>` (marcar/desmarcar) e tecla `a` (todos).
- **Segurança operacional:** confirmação final obrigatória com padrão negativo (`default=False`), exibindo o total de bytes e contagem de pastas a serem excluídas.
- **Códigos de retorno:**
  - `0`: varredura concluída com sucesso ou nenhum cache descartável encontrado.
  - `1`: concluído com falhas parciais de remoção de arquivos.
  - `2`: caminho informado não é um diretório válido ou comando chamado sem `--yes`/`--dry-run` em ambiente sem TTY.
- **Identificador no catálogo:** `dev.janitor` (classificação: `destructive`, suporta `--dry-run`).

#### Higienizador Git (`belt dev git-tidy`)
- **Sincronização prévia:** executa preventivamente `git fetch --prune` antes da análise de branches.
- **Detecção de órfãs:** identifica branches locais cuja contraparte remota foi excluída no servidor (comum após *Squash & Merge* no GitHub), além de branches mescladas via `git branch --merged`.
- **Proteção inviolável:** as branches canônicas (`main`, `master`, `dev`, `development`, `staging`, `prod`, `production`) e a branch corrente (`HEAD`) são protegidas contra qualquer exclusão.
- **Remoção remota:** branches em `origin` requerem `--remote` ou `--all` com aviso de segurança explícito antes do envio de `git push origin --delete`.
- **Códigos de retorno:**
  - `0`: higienização concluída com sucesso.
  - `2`: Git ausente do `PATH` ou diretório corrente não é um repositório Git.
- **Identificador no catálogo:** `dev.git-tidy` (classificação: `destructive`, suporta `--dry-run`).

### Autocompletar no Shell (`belt show-completion`)

Exibe instruções nativas para habilitar autocompletar de comandos sem modificar perfis de usuário de forma invasiva:

```bash
belt show-completion powershell
belt show-completion bash
belt show-completion zsh
belt show-completion fish
```

---

## Configuração e Perfis

O Utility Belt salva suas configurações de forma atômica no diretório padrão do sistema operacional gerenciado pelo [`platformdirs`](https://github.com/tox-dev/platformdirs):

- **Windows:** `%APPDATA%\utility-belt\config.toml`
- **Linux:** `~/.config/utility-belt/config.toml`

### Exemplo de estrutura do `config.toml`:

```toml
[general]
confirm_destructive = true
default_log_level = "INFO"

[restic.profiles.padrao]
repository = "D:/Backups/Geral"
exclude_file = ""

[restic.profiles.projetos]
repository = "/mnt/backup/projetos"
exclude_file = "/mnt/backup/projetos/excludes.txt"
```

---

## Desenvolvimento e Governança

Para clonar e executar o projeto localmente em modo de desenvolvimento:

```bash
# Clonar repositório
git clone https://github.com/EuThiagoAndrade/utility-belt.git
cd utility-belt

# Sincronizar dependências no ambiente virtual
uv sync

# Executar a CLI em desenvolvimento
uv run belt --help
```

### Gates de Qualidade e Testes

Antes de submeter alterações, execute a suíte de testes e validações:

```bash
# Executar a suíte de testes unitários (pytest)
uv run pytest

# Verificação de estilo e linting (ruff)
uv run ruff check

# Validador canônico de governança do projeto
uv run python scripts/validate_governance.py

# Checagem de quebras de linha e formatação git
git diff --check
```

### Governança e Contribuição

Este projeto adota um modelo de governança desacoplado e agnóstico de ferramentas proprietárias. Para compreender o ciclo de vida de desenvolvimento, padrões de branches, decomposição de issues, tasks persistentes e tomadas de decisão:

- Consulte o guia de contribuição em [**`CONTRIBUTING.md`**](CONTRIBUTING.md).
- Consulte a política de segurança em [**`SECURITY.md`**](SECURITY.md).
- Consulte a governança do repositório em [**`_project/README.md`**](_project/README.md).
- Consulte o registro de ciclos em [**`_project/cycles.md`**](_project/cycles.md).
- Consulte o comportamento canônico de agentes em [**`.agent/ai_behavior.md`**](.agent/ai_behavior.md).

---

## Licença

Este projeto é software livre distribuído sob os termos da licença [MIT](LICENSE). Consulte o arquivo [LICENSE](LICENSE) para maiores detalhes.
