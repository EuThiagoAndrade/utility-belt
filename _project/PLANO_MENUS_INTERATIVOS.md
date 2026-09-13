# Plano de Implementação: Menus Interativos Guiados no Utility Belt

Implementar uma interface interativa moderna no terminal (com navegação por setas e caixas de seleção via `questionary`), proporcionando o "melhor dos dois mundos":
1. **Uso diário guiado:** `belt`, `belt restic` e `belt docker` abrem menus interativos quando chamados sem argumentos, eliminando a necessidade de digitar parâmetros longos.
2. **Automação via CLI:** comandos diretos como `belt restic backup --dry-run` continuam funcionando plenamente para scripts e agendamentos.

---

## Decisões Definidas na Entrevista (/grill-me)

1. **Acionamento direto sem argumentos:**
   - `belt` -> Menu Principal Central.
   - `belt restic` -> Menu Interativo do Restic.
   - `belt docker` -> Menu Interativo do Docker.
   - Comandos com subcomandos/flags continuam operando normalmente via CLI.
2. **Fidelidade total ao fluxo do Restic:**
   - Assistente guiado passo a passo ("A").
   - Fazer backup com opção de simulação (`--dry-run`).
   - Restauração guiada com listagem de snapshots, seleção de destino, filtro opcional de arquivos e abertura no Explorador de Arquivos do Windows.
   - Verificação rápida da estrutura e verificação completa dos dados (`--read-data`).
   - Navegação/inspeção de arquivos dentro dos snapshots (`ls`).
   - Configuração de caminhos e exclusões com migração transparente da configuração anterior.
3. **Menu Interativo do Docker:**
   - 1. Exportar imagens: lista imagens locais em formato de múltipla escolha (checkbox), pergunta diretório de saída (com autocompletação ou padrão atual) e gera o arquivo `.tar` com manifesto.
   - 2. Importar imagens: lista arquivos `.tar` disponíveis em uma pasta para seleção direta, exibe o manifesto e carrega as imagens no Docker.
4. **Estilo Visual e Navegação:**
   - Menus modernos e limpos com setas do teclado (`↑` / `↓`), barra de espaço para marcar/desmarcar (`[x]`), e máscaras de senha para segurança, utilizando a biblioteca `questionary` (baseada em `prompt_toolkit`, compatível com Windows PowerShell/CMD e Linux).
5. **Persistência de Configurações:**
   - Armazenamento automático dos últimos caminhos usados no `config.toml`, migrando automaticamente as definições legadas do ResticMenu (`%LOCALAPPDATA%\ResticMenu\config.json`).

---

## Proposta de Modificações

### 1. Dependências e Empacotamento
#### [MODIFY] [pyproject.toml](file:///c:/Programas/utility-belt/pyproject.toml)
- Adicionar dependência `questionary>=2.0.0` (para navegação interativa por setas e checkboxes no terminal).

---

### 2. Módulos de Menus Interativos
#### [NEW] [src/utility_belt/ui/restic_menu.py](file:///c:/Programas/utility-belt/src/utility_belt/ui/restic_menu.py)
- Implementar o menu interativo completo do Restic usando `questionary`:
  - Assistente guiado passo a passo (Wizard para novatos).
  - Fazer backup (simulação ou gravação real).
  - Restaurar snapshot (escolha de snapshot em lista navegável, pasta destino, filtro e confirmação de segurança contra sobreposição).
  - Inspeção de arquivos em snapshots (`restic ls`).
  - Verificação de integridade (estrutura e dados completos).
  - Configuração de caminhos e exclusões (salvando no `config.toml`).
  - Histórico de auditoria e logs.
  - Migração automática das configurações antigas.

#### [NEW] [src/utility_belt/ui/docker_menu.py](file:///c:/Programas/utility-belt/src/utility_belt/ui/docker_menu.py)
- Implementar o menu interativo do Docker:
  - Opção 1: Exportar imagens (busca imagens via `docker image ls`, apresenta checklist interativa para marcar com barra de espaço, seleciona pasta de saída e gera `.tar` + manifesto).
  - Opção 2: Importar imagens (procura arquivos `.tar` na pasta informada, exibe manifesto e executa `docker load`).

#### [MODIFY] [src/utility_belt/menu.py](file:///c:/Programas/utility-belt/src/utility_belt/menu.py)
- Atualizar o Menu Principal para usar `questionary` e atalhos diretos:
  - 1. 🛡️ Restic (Backups, Restauração e Integridade) -> aciona `restic_menu`
  - 2. 🐳 Docker (Exportar e Importar Imagens) -> aciona `docker_menu`
  - 3. 🩺 Diagnóstico e Saúde (Doctor) -> roda diagnóstico do ambiente
  - 4. ℹ️ Informações do Sistema (system.info)
  - 0. 🚪 Sair

---

### 3. Integração com Typer CLI
#### [MODIFY] [src/utility_belt/cli.py](file:///c:/Programas/utility-belt/src/utility_belt/cli.py)
- Configurar `@app.callback(invoke_without_command=True)` para que digitar apenas `belt` em um terminal interativo (TTY) abra o Menu Principal.

#### [MODIFY] [src/utility_belt/adapters/restic.py](file:///c:/Programas/utility-belt/src/utility_belt/adapters/restic.py)
- Configurar `@restic_app.callback(invoke_without_command=True)` para que digitar apenas `belt restic` abra o menu interativo do Restic.
- Adicionar comando explícito `belt restic menu`.

#### [MODIFY] [src/utility_belt/adapters/docker.py](file:///c:/Programas/utility-belt/src/utility_belt/adapters/docker.py)
- Configurar `@docker_app.callback(invoke_without_command=True)` para que digitar apenas `belt docker` abra o menu interativo do Docker.
- Adicionar comando explícito `belt docker menu`.

---

## Plano de Verificação

### Testes Automatizados
- Executar a suíte de testes existente com `pytest`:
  ```bash
  pytest
  ```
- Criar novos testes unitários em `tests/test_interactive_menus.py` validando que as callbacks `invoke_without_command` chamam as funções corretas e que a migração de configurações funciona como esperado.

### Verificação Manual
- Testar execução no terminal do Windows:
  1. `belt` -> verificar que abre o menu principal com navegação por setas.
  2. `belt restic` -> verificar abertura do menu do Restic, navegação e opções.
  3. `belt docker` -> verificar abertura do menu do Docker.
  4. `belt restic backup --dry-run` -> verificar que a CLI não-interativa continua funcionando perfeitamente sem abrir menus.
