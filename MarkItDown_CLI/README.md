# 🚀 MarkItDown CLI - Manual de Utilização

Este script é um "wrapper" em Python para a ferramenta **MarkItDown**, projetado para facilitar a conversão de diversos formatos de arquivos para Markdown de maneira rápida e organizada, com suporte a limpeza de metadados e menu interativo.

---

## 🛠️ Pré-requisitos

Para utilizar este script, você precisa apenas de:
1.  **Python** instalado na sua máquina.
2.  A ferramenta **MarkItDown** instalada em algum lugar (Ambiente Virtual, Global ou Conda).

> [!TIP]
> **Descoberta Automática:** O script é inteligente! Ele tentará encontrar o MarkItDown sozinho no seu sistema ou em pastas `.venv` e `venv` próximas. Se não encontrar, ele solicitará o caminho na primeira execução e salvará a configuração para que você não precise digitar novamente.

---

## 🚀 Como Executar

O script oferece dois modos principais de operação: **Menu Interativo** e **Linha de Comando (CLI)**.

### 1. Modo Menu Interativo (Recomendado)
Execute o script sem argumentos para abrir a interface visual:

```powershell
python markitdown_cli.py
```

**Funcionalidades do Menu:**
*   **1 a 3**: Funções de conversão (Arquivo, Pasta ou URL do YouTube/Web).
*   **4. Cabeçalho YAML**: Alterne entre **REMOVER** (limpeza automática de metadados) ou **MANTER**.
*   **5. Redefinir Caminho**: Use esta opção se você mudar seu ambiente virtual de lugar ou quiser trocar a versão do MarkItDown utilizada.

---

### 2. Modo Linha de Comando (CLI)
Para uso rápido ou em automações.

| Comando | Descrição |
| :--- | :--- |
| `python markitdown_cli.py "arquivo.pdf"` | Converte o arquivo com limpeza de cabeçalho padrão. |
| `python markitdown_cli.py "C:\Pasta" -d` | Processamento inteligente em lote (pasta inteira). |
| `python markitdown_cli.py "doc.docx" --keep-header` | Converte mantendo os metadados originais. |
| `python markitdown_cli.py --set-path "C:\caminho\exe"` | Configura o local do MarkItDown manualmente. |

---

## ✨ Inteligência e Configuração

O script agora gerencia as configurações de forma dinâmica:

*   **Configuração Persistente**: O caminho do executável é salvo no arquivo `markitdown_config.json` no mesmo diretório do script.
*   **Limpeza de Front Matter**: Remove automaticamente aqueles blocos técnicos entre `---` no início do arquivo, comuns em conteúdos do Microsoft Learn.
*   **Flexibilidade Total**: Se o script for movido para outra máquina ou diretório, ele saberá se reajustar ou guiar o usuário na configuração.

---

## 📖 Referência de Parâmetros

Se você preferir não usar o menu e invocar o script diretamente via terminal, aqui estão todos os parâmetros disponíveis:

| Parâmetro | Descrição | Exemplo de Uso |
| :--- | :--- | :--- |
| `input` | (Posicional) O arquivo, pasta ou URL que você deseja converter. | `python markitdown_cli.py "doc.pdf"` |
| `-o`, `--output` | Especifica o nome ou caminho do arquivo de saída. | `python markitdown_cli.py "doc.pdf" -o "final.md"` |
| `-d`, `--directory` | Indica que o input é uma pasta e deve converter tudo nela. | `python markitdown_cli.py "C:\Docs" -d` |
| `--keep-header` | Pula a limpeza automática e mantém o cabeçalho YAML original. | `python markitdown_cli.py "doc.pdf" --keep-header` |
| `--set-path` | Configura ou atualiza o caminho do executável MarkItDown. | `python markitdown_cli.py --set-path "C:\path\to\exe"` |
| `-h`, `--help` | Mostra a ajuda oficial do script com todos os comandos. | `python markitdown_cli.py --help` |

---
**Manual atualizado com suporte a Descoberta Dinâmica e Referência de Parâmetros.** 🚀
