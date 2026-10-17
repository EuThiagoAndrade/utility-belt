# Lições aprendidas

Registro de aprendizados comprovados e reutilizáveis do repositório `utility-belt`. Não use este arquivo como backlog, task corrente ou histórico de conversa.

## Registros

### 2026-09-11 — Subprocess cwd deve sempre apontar para o diretório do usuário

No ciclo `000`, a análise da execução de ferramentas CLI isoladas via `uv tool` evidenciou que mudar o `cwd` do subprocesso para o diretório interno do script faz com que caminhos relativos passados pelo usuário (ex.: `--output ./imagens.tar`) sejam gravados dentro do ambiente virtual em `site-packages`. O runner deve sempre fixar `cwd = Path.cwd()` no diretório corrente de invocação do usuário e injetar a pasta da ferramenta no `PYTHONPATH` do processo filho.

### 2026-09-11 — Subprocessos PowerShell no Windows exigem ExecutionPolicy Bypass

No Windows padrão, a política de execução de scripts PowerShell é frequentemente `Restricted`. Para que scripts `.ps1` empacotados funcionem de forma transparente sem que o usuário precise alterar a política global da sua máquina, a invocação do runner deve passar `-NoProfile -ExecutionPolicy Bypass -File` como argumentos diretos do subprocesso.

### 2026-09-11 — tomllib nativo é somente leitura; escrita atômica exige tomli-w

No Python 3.11+, o módulo nativo `tomllib` provê apenas deserialização (leitura) de TOML. Para edição e gravação de perfis em `config.toml`, deve-se utilizar `tomli-w` com escrita atômica em arquivo temporário seguida de substituição para garantir que falhas de E/S ou interrupções não corrompam o arquivo de configuração do usuário.

### 2026-09-13 — Menus interativos devem ser condicionais ao TTY

No ciclo `001`, a inclusão de menus interativos guiados via `questionary` exigiu a distinção estrita entre chamadas interativas e não-interativas. Comandos executados sem argumentos abrem menus interativos apenas quando conectados a um terminal interativo (`sys.stdin.isatty()`). Em ambientes não-interativos (scripts, CI, cron) ou com `--non-interactive`, a CLI deve manter o comportamento padrão de exibir ajuda ou abortar com código de saída 2, nunca travando à espera de entrada do usuário.

### 2026-10-12 — Seleção de clipboard deve considerar a sessão local

No ciclo `006`, Pyperclip 1.11.0 detectou kernel Microsoft em container Linux e escolheu o backend WSL antes do X11 disponível, tentando executar `powershell.exe` ausente. Priorizar o backend gráfico disponível da sessão local evita essa escolha; leitura não exige escrever no clipboard. Validar também a ausência de backend em headless e preservar o clipboard rico do usuário ao testar.

### 2026-10-12 — Resolver symlink de Python pode escapar da venv

No smoke distribuído do ciclo `006`, `Path.resolve()` no Python da venv Linux apontou para o intérprete base e perdeu os pacotes instalados. Ao executar uma venv por seu Python, preservar o caminho absoluto de invocação e seu symlink, em vez de resolvê-lo para o binário global. Comprovar imports fora do checkout com modo isolado do Python.

### 2026-10-12 — Suítes concorrentes podem disputar runtime compartilhado

No ciclo `006`, duas suítes completas simultâneas disputaram o lock do mesmo ambiente do motor e excederam o prazo do harness do monitor. Rodar serialmente quando compartilham runtime; paralelismo requer ambientes independentes. Distinguir falha do harness de falha de produção sem relaxar estabilidade, assertivas ou timeout de produção.

### 2026-09-13 — Handoffs estáveis e rastreabilidade pós-merge

Em rotinas de governança com múltiplos agentes e revisões, a identidade do handoff (`handoff_id`) deve ser derivada deterministicamente de repositório, ciclo, workflow, alvo lógico e revisão de origem, e nunca de timestamps voláteis ou UUIDs arbitrários. Reexecuções compatíveis devem ser reconciliadas sem duplicação documental.

### 2026-10-17 — Testes de CLI com Rich/Typer devem sanitizar sequências de escape ANSI

No ciclo `009`, a suíte de testes de CLI (`tests/test_dev_cli.py`) comparando substrings em saídas de `--help` falhou no runner Ubuntu do GitHub Actions porque o Rich/Typer renderizou estilos de terminal com sequências ANSI mesmo quando invocado via `CliRunner`. A sanitização prévia via regex (`re.compile(r"\x1b\[[0-9;]*[mK]")`) garante asserções determinísticas e portáveis entre plataformas Windows e Linux.
