# Utility Belt (`belt`)

Canivete suíço pessoal de terminal para Windows e Linux.

O **Utility Belt** unifica ferramentas de linha de comando em um pacote Python isolado, distribuível e de fácil atualização. Ele organiza scripts e utilitários em um catálogo declarativo baseado em manifestos (`tool.toml`), oferecendo tanto execução direta e scriptável via CLI quanto uma interface interativa de terminal (TUI) rica com navegação guiada.

---

## Recursos Principais

- **Interface Dupla:** Uso via linha de comando direta (scriptável em CI/automações) ou via menus interativos no terminal (TUI orientada a prompts com `questionary`).
- **Catálogo Modular:** Ferramentas registradas de forma declarativa com metadados de plataforma, tempo de execução e classificação de risco (`read`, `write`, `destructive`).
- **Adaptadores de Ferramentas:**
  - **Docker:** Exportação e importação segura de imagens com manifestos e simulação (`--dry-run`).
  - **Restic:** Gerenciamento de repositórios, backups incrementais, restauração de snapshots e conferência de integridade.
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
```

> **Nota:** Em ambientes não interativos (como rotinas de CI ou cron jobs), chamar `belt` sem argumentos exibe a ajuda padrão em vez de aguardar entrada do usuário.

---

## Referência da CLI (Modo Direto)

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

### Governança Canônica

Este projeto adota um modelo de governança desacoplado e agnóstico de ferramentas proprietárias. Para compreender o ciclo de vida de desenvolvimento, padrões de branches, decomposição de issues, tasks persistentes e tomadas de decisão:

- Consulte o guia canônico em [**`_project/README.md`**](_project/README.md).
- Consulte o registro de ciclos em [**`_project/cycles.md`**](_project/cycles.md).
- Consulte o comportamento canônico de agentes em [**`.agent/ai_behavior.md`**](.agent/ai_behavior.md).

---

## Licença

Este projeto é desenvolvido para uso pessoal e sob licença aberta. Consulte o repositório para maiores detalhes.
