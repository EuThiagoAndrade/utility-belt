# Plano revisado do projeto `utility-belt`

Revisão crítica: 11/09/2026. Status: proposta de arquitetura e execução, ainda não implementada. Os comandos `belt` abaixo descrevem a interface a construir.

## 1. Objetivo e decisão central

Ter um canivete suíço pessoal de terminal: adicionar uma ferramenta ao repositório, distribuí-la em uma versão e atualizar cada máquina Windows ou Linux com um comando, tornando os novos comandos disponíveis de qualquer diretório.

A unidade de distribuição inicial será um pacote completo, instalado por usuário. Não será necessário copiar scripts individualmente, ativar um ambiente virtual ou manter um checkout de trabalho nas máquinas de uso. Atualizar trará ferramentas novas e correções; ferramentas retiradas da versão deixarão de aparecer. Configurações, senhas, backups e arquivos do usuário não fazem parte dessa sincronização.

**Prioridade: CLI e distribuição primeiro; menu como interface opcional.** O núcleo será Python, mas as ferramentas poderão ser Python, PowerShell, Bash ou executáveis externos, respeitando a compatibilidade declarada de cada uma.

## 2. Análise crítica do plano anterior e do código atual

Esta avaliação combina leitura estática dos três scripts Docker/Restic e referências técnicas. Não houve execução de backups, importações ou validação real no Linux.

| Ponto cego | Evidência ou consequência | Melhoria proposta |
| --- | --- | --- |
| Distribuição só na fase final | A necessidade principal é atualizar várias máquinas; um menu local não resolve isso | Entregar pacote instalável e ensaio de atualização na primeira fase funcional |
| Uso direto confundido com abrir um script | Os dois scripts Docker usam `input()` e pausas obrigatórias; Restic também é interativo | Separar parâmetros de execução e interação; preservar menus legados explicitamente até a migração |
| Portabilidade presumida | Restic tem padrões `C:\Programas`, `D:\Restic-Programas` e armazenamento baseado em `LOCALAPPDATA` | Perfis locais, diretórios por SO e testes reais em Windows/Linux |
| Atualização acoplada ao checkout | Verificar alterações locais faz sentido para desenvolvimento, mas não deveria ser rotina da máquina de uso | Instalação isolada, origem conhecida e atualização pelo gerenciador |
| Catálogo insuficiente | Não define plataforma, runtime, modo não interativo ou inclusão dos arquivos no pacote | Manifesto validado e teste do wheel instalado fora do repositório |
| Dependência encontrada confundida com funcional | Docker pode estar no PATH com daemon indisponível; HD Restic pode estar ausente ou trocado | Diagnóstico separado de executável, serviço, acesso e identidade do repositório |
| Códigos de saída não preservados de ponta a ponta | Docker converte falhas em `1`; Restic transforma falhas em `ValueError` no menu | Adaptadores CLI devem conservar o código do processo filho, incluindo backup incompleto |
| Importação Docker faz duas coisas | `importar_imagens_docker.py` carrega imagens e oferece executar container | Separar `docker import` de `docker run`; execução deve continuar explícita |
| Segurança descrita só como confirmação | Perguntar sempre impede automação, mas um `--yes` indiscriminado enfraquece proteções | Política por operação e validações obrigatórias mesmo sem interação |
| Falhas parciais pouco especificadas | Exportação escreve direto no `.tar` final e depois cria manifesto | Arquivo temporário, promoção após sucesso e tratamento explícito de manifesto ausente/falha |
| Reprodutibilidade ausente | Mesmo código pode receber dependências distintas em instalações posteriores | Versões identificáveis, lock no desenvolvimento e limites claros para instalação final |
| Testes deixados para depois | Empacotamento pode omitir scripts; cancelamento pode deixar processos rodando | Testar instalação, execução e atualização desde o primeiro incremento |
| Resolução de `cwd` vs. arquivos do pacote | Se o runner mudar o `cwd` para a pasta do script, caminhos relativos do usuário (`--output ./meu.tar`) gravam dentro de `site-packages` | Fixar `cwd` no diretório corrente do usuário; resolver scripts e manifestos via `importlib.resources`; injetar pasta da ferramenta no `PYTHONPATH` |
| PowerShell bloqueado por política padrão do Windows | No Windows padrão a `ExecutionPolicy` é `Restricted`; invocar `-File` sem bypass falha | Adicionar `-ExecutionPolicy Bypass` ao nível de processo do subprocesso PowerShell, sem alterar a política do sistema |
| `tomllib` não escreve TOML | Python 3.11+ tem `tomllib` apenas para leitura; migração e novos perfis exigem serialização | Adicionar `tomli-w` como dependência explícita de runtime para escrita atômica do `config.toml` |
| Omissão de arquivos não-Python no Wheel | Build backends (como Hatchling/setuptools) podem omitir `tool.toml`, `.ps1` e `.sh` se não configurados | Configurar inclusão explícita de `package-data`/artefatos no `pyproject.toml` e validar wheel limpo |
| Escopo inflado com legados não utilizados | Pastas `Conda/` e `Utilitarios/` estavam no repositório mas não serão utilizadas | Descartar/remover `Conda/` e `Utilitarios/`, focando o MVP estritamente em Docker, Restic e na infraestrutura CLI |

Há boas decisões a preservar: execução inicial por subprocessos, lógica fora do menu, código separado de dados e atualização explícita. O Restic já verifica ID de repositório, bloqueia sobreposição de caminhos, usa senha em memória e evita recriação silenciosa de repositório ausente. A migração precisa preservar essas proteções.

Estado local observado: `PLANO_UTILITY_BELT.md` e `restic/` estão não rastreados no Git. Não há `pyproject.toml`, README nem testes no inventário atual. As pastas `Conda/` e `Utilitarios/` serão descartadas/removidas conforme decisão de escopo, mantendo o projeto concentrado nas ferramentas essenciais (`Docker` e `Restic`).

## 3. Escolhas técnicas e alternativas

| Tema | Recomendação | Motivo e limite |
| --- | --- | --- |
| Distribuição | Pacote Python com `pyproject.toml`, wheel e layout `src/` | Instalação e comandos padronizados; scripts e manifestos precisam entrar no artefato |
| Gerenciador principal | `uv tool install` / `uv tool upgrade` | Ambiente isolado e executável no PATH do usuário |
| Alternativa suportada | `pipx` | Mesmo modelo de ferramenta isolada; evitar gerenciar a mesma instalação pelos dois |
| CLI | Typer | Subcomandos, ajuda e completion; manter dependências pequenas |
| Manifesto e configuração nova | TOML (`tomllib` para leitura, `tomli-w` para escrita) | `tomllib` nativo no 3.11+ é apenas leitura; `tomli-w` é puro Python, leve e permite escrita atômica de `config.toml` |
| Localização de assets | `importlib.resources` e build backend com inclusão explícita | Acessa `tool.toml` e scripts dentro do wheel instalado sem depender de caminhos de desenvolvimento |
| Diretórios locais | `platformdirs`, com nome/autoria fixados | Respeita convenções Windows e XDG no Linux |
| Execução | Subprocessos com argumentos em lista | Mantém isolamento dos scripts legados; não é sandbox de segurança |
| Testes e qualidade | pytest, Ruff e CI Windows/Linux | Validar contratos e artefatos, além do código-fonte |

Python 3.11 será o mínimo proposto, sujeito à matriz validada antes da primeira versão. Fixar no projeto as versões das ferramentas de desenvolvimento e registrar as versões testadas de runtimes externos. Definir bounds semânticos estritos no `pyproject.toml` (ex.: `typer>=0.12,<1.0`, `tomli-w>=1.0,<2.0`) para assegurar paridade entre máquinas que instalam via Git.

A PyPA documenta o empacotamento de CLIs e os pontos de entrada que viram executáveis. Essa é a base da distribuição proposta. [Guia de CLI da PyPA](https://packaging.python.org/en/latest/guides/creating-command-line-tools/)

`uv` documenta instalação de ferramentas em ambientes isolados e fontes Git. A escolha é uma recomendação para este projeto, não uma exigência do formato do pacote. [Ferramentas com uv](https://docs.astral.sh/uv/guides/tools/)

Typer já fornece ajuda, subcomandos e completion; verificar a experiência nos shells suportados em vez de implementar essas funções do zero. [Recursos do Typer](https://typer.tiangolo.com/features/)

Não adotar agora um gerenciador próprio de pacotes, marketplace de plugins, banco de dados, serviço residente ou TUI sofisticada. Copiar scripts para o PATH gera colisões e dificulta remoção; `git pull` com aliases exige checkout em toda máquina; tarefas de build de um repositório não substituem a distribuição global pretendida.

## 4. Experiência de terminal

Usar `belt` como comando principal e `utility-belt` como alternativa explícita caso exista colisão de nome. Ambos apontam para o mesmo entry point. Não criar um comando global independente para cada script no MVP.

```text
belt --help
belt --version
belt list
belt list --all
belt doctor
belt doctor docker
belt menu
belt docker export --image alpine:3.22 --output ./imagens.tar
belt docker import --input ./imagens.tar
belt restic backup --profile casa --non-interactive
belt restic restore --profile casa --snapshot ID --target ./restauracao --dry-run
belt run minha-ferramenta -- argumento-do-script
```

Os valores acima são ilustrativos, não recomendações de versões de imagens. O backup não interativo só será habilitado quando existir provedor de credencial protegido configurado; caso contrário, falhará imediatamente com orientação.

Contrato da CLI:

- `belt` sem argumentos mostra ajuda; `belt menu` abre navegação interativa.
- Comandos próprios oferecem `--help`, exemplos e validação antes de efeitos colaterais.
- `belt run ID -- ...` encaminha os argumentos restantes sem reinterpretá-los como shell.
- Sem terminal interativo, nenhum comando deve ficar esperando resposta. Se uma ferramenta declarada `interactive = true` for invocada sem TTY (`not sys.stdin.isatty()`) ou sob `--non-interactive`, o launcher deve abortar antes de iniciar o processo filho, com mensagem explicativa e código de saída 2.
- `--non-interactive` proíbe prompts; não significa consentimento para operações sensíveis.
- `--yes`, quando admitido, aceita somente a confirmação daquela operação; não ignora destino inválido, identidade divergente ou plataforma incompatível.
- Resultado em stdout e diagnóstico em stderr. `--json` começa por `list` e `doctor`; não prometer JSON para saída arbitrária de scripts legados.
- Retornar código original de processos externos quando houver execução; códigos do launcher: `0` (sucesso), `1` (erro operacional/validação), `2` (bloqueio de pré-condição/TTY/incompatibilidade), `130` (interrupção por Ctrl+C).
- Cancelamento por Ctrl+C deve encerrar o trabalho filho e retornar ao shell ou menu sem despejar tracebacks Python. Validar esse comportamento em ambos os SOs.
- Completion será opt-in via comandos informativos (`belt --show-completion [powershell|bash]`). Não usar flags automáticas que editem perfis de shell silenciosamente.

## 5. Instalação e atualização entre máquinas

### 5.1. Fluxo inicial recomendado

Pré-requisitos por máquina: `uv`, acesso à origem e Git quando a instalação usar fonte Git. A instalação deve orientar a obtenção de Python compatível. Docker, Restic, `pwsh` e Bash são dependências apenas das ferramentas que os usam, não pré-requisitos de toda a coleção.

Comandos abaixo são modelos para depois do empacotamento; substituir `ORGANIZACAO` e confirmar a branch real. Não executar contra esses placeholders.

```text
uv tool install "git+https://github.com/ORGANIZACAO/utility-belt.git@main"
uv tool update-shell
```

Reabrir o terminal se o PATH precisar de atualização. Em seguida, `belt --version`, `belt list` e `belt doctor` devem funcionar fora do repositório.

Na máquina já instalada, o comando cotidiano será:

```text
uv tool upgrade utility-belt
```

A atualização segue a origem e as restrições da instalação. O fluxo com branch móvel deve ser validado com dois commits distintos, incluindo nova ferramenta e alteração de versão. Uma instalação fixada em tag/commit não deve ser apresentada como canal que avança automaticamente para a próxima release; para mudar a referência, reinstalar indicando a nova origem. O uv documenta a preservação das restrições durante upgrades. [Versões e atualização de ferramentas](https://docs.astral.sh/uv/concepts/tools/)

Esse comando satisfaz o objetivo de receber os scripts faltantes sem copiar arquivos. Ele atualiza o pacote inteiro; não é sincronização remota de máquinas desligadas. Deve ser executado em cada máquina desejada.

### 5.2. Desenvolvimento e releases

Separar duas modalidades:

- Desenvolvimento: checkout, ambiente do projeto e lock versionado; mudanças locais são tratadas pelo Git.
- Uso: pacote instalado, sem edição interna. Personalizações ficam em configuração externa; mudanças de código voltam ao repositório e entram na próxima versão.

Começar com canal pessoal pela branch validada em CI. Aumentar a versão do pacote a cada entrega. Evoluir para releases identificáveis, wheel e changelog; tag/commit fixo quando for necessário reproduzir o código de uma máquina. Não publicar em índice público sem decisão explícita; nome e disponibilidade ainda precisam ser verificados.

`uv.lock` serve ao ambiente de desenvolvimento/CI, mas não presumir que `uv tool install` reproduz automaticamente esse lock. Para reprodução rigorosa do ambiente distribuído, definir e testar constraints/exportação ou artefato de distribuição apropriado, incluindo dependências por plataforma.

### 5.3. Falha, recuperação e limites

No MVP, usar o gerenciador externo e documentar reinstalação da referência anterior, com teste de recuperação. Não prometer atualização atômica nem rollback automático de configuração. Uma referência antiga deve continuar acessível para recuperação; uso offline completo pode exigir wheel e todas as dependências previamente disponíveis.

Executar atualização sem ferramentas do pacote em atividade, especialmente no Windows. Após atualizar, verificar versão, catálogo e diagnóstico. Falta de rede deve produzir erro sem apagar configurações. Instalação já preparada deve executar ferramentas locais offline, exceto operações que por natureza exigem rede.

Um futuro `belt update` seria somente uma conveniência. Antes de implementá-lo, resolver detecção do gerenciador, execução fora do processo que está sendo substituído, concorrência, validação e recuperação. Não reimplementar instalação dentro do launcher agora.

## 6. Arquitetura e cadastro de novos scripts

```text
utility-belt/
├── pyproject.toml
├── uv.lock
├── src/utility_belt/
│   ├── __init__.py
│   ├── cli.py
│   ├── catalog.py
│   ├── runner.py
│   ├── config.py
│   ├── tools/
│   │   ├── system_info/         # Ferramenta piloto de leitura segura (Fase 1)
│   │   │   ├── tool.toml
│   │   │   └── main.py
│   │   ├── docker_export/
│   │   │   ├── tool.toml
│   │   │   └── main.py
│   │   ├── docker_import/
│   │   │   ├── tool.toml
│   │   │   └── main.py
│   │   └── restic_backup/
│   │       ├── tool.toml
│   │       └── main.py
│   └── adapters/
├── tests/
├── docs/
├── README.md
└── .github/workflows/ci.yml
```

Estrutura alvo, sem autorizar movimentação imediata. Durante a transição, scripts podem continuar nas pastas atuais, mas o build deve incluí-los explicitamente.

Regras fundamentais de resolução e execução do `runner`:
- **Localização de manifestos e scripts**: O catálogo descobre ferramentas exclusivamente inspecionando recursos do pacote instalado via `importlib.resources.files("utility_belt.tools")`, nunca vasculhando pastas arbitrárias no disco do usuário.
- **Diretório de trabalho do processo (`cwd`)**: O `cwd` do subprocesso SEMPRE é o diretório de trabalho corrente do usuário (`Path.cwd()`). Isso é indispensável para que caminhos relativos passados via argumentos (ex.: `--output ./imagens.tar` ou `-- arquivo.txt`) resolvam na pasta do usuário, e não dentro do ambiente virtual em `site-packages`.
- **Isolamento de imports da ferramenta**: Para ferramentas Python compostas por múltiplos arquivos ou utilitários locais na pasta da ferramenta, o runner injeta o diretório da ferramenta no `PYTHONPATH` do processo filho, preservando o `cwd` intacto.
- **Configuração de empacotamento no build backend**: O `pyproject.toml` (ex.: Hatchling) deve declarar expressamente a inclusão de arquivos não-Python dentro de `src/utility_belt/` (`*.toml`, `*.ps1`, `*.sh`), garantindo que o wheel gerado contenha todos os manifestos e scripts de automação.

Manifesto conceitual para um script novo:

```toml
schema_version = 1
id = "texto.contar"
name = "Contar linhas de um arquivo"
description = "Conta linhas sem alterar o arquivo de entrada."
runtime = "python"
entry = "main.py"
platforms = ["windows", "linux"]
interactive = false
risk = "read"
supports_dry_run = false
external_dependencies = []
```

O schema deve definir campos, valores permitidos e versão; rejeitar IDs duplicados, runtime desconhecido, entry ausente ou fora do diretório permitido. Acrescentar restrições de arquitetura e versões de dependências quando aplicáveis. `risk` informa a apresentação, mas não substitui validações no código.

Fluxo de adição:

1. Criar pasta com script e manifesto usando modelo documentado.
2. Declarar plataforma, dependências, efeitos e contrato de argumentos.
3. Acrescentar teste de ajuda e um caso funcional seguro.
4. Validar catálogo e confirmar inclusão no wheel.
5. Integrar a alteração e entregar uma nova versão.
6. Atualizar cada máquina: o script aparece em `belt list` e funciona com `belt run texto.contar -- arquivo.txt`.

O catálogo será descoberto apenas dentro do pacote instalado, sem importar/executar scripts para obter metadados. Não procurar scripts automaticamente no diretório atual. Subcomandos ricos como `belt docker export` usam adaptadores registrados; o caminho genérico `belt run` permite adicionar ferramentas sem editar o núcleo.

Ferramentas incompatíveis não impedem a instalação: `list --all` mostra o motivo; execução falha antes de qualquer alteração. Código não confiável continua não confiável mesmo se executado por subprocesso. Extensões locais e repositórios terceiros ficam fora do MVP.

## 7. Runtimes e dependências

- Python simples: usar `sys.executable` da instalação; nunca presumir que `python` no PATH é o mesmo interpretador.
- Python com dependências comuns pequenas: declarar no pacote inicialmente. Não instalar todas as bibliotecas pesadas de futuras ferramentas no núcleo.
- Python com dependências conflitantes: evolução opcional com metadados inline PEP 723 e ambiente por script. Preparação explícita, lock e diagnóstico devem anteceder uso offline; `list` e `--help` nunca devem baixar bibliotecas.
- PowerShell: declarar `pwsh` ou necessidade específica de Windows PowerShell; invocar o processo com `-NoProfile -ExecutionPolicy Bypass -File`. O `-ExecutionPolicy Bypass` no nível de argumento do processo garante execução mesmo onde a política do sistema é a padrão (`Restricted`), sem modificar a política global da máquina ou do usuário.
- Bash: declarar suporte e executável; não presumir Bash nativo no Windows nem WSL disponível.
- Executáveis externos: localizar, verificar versão suportada e executar por caminho resolvido.

O uv suporta dependências inline e ambientes de scripts, mas essa capacidade adiciona outro ciclo de instalação/cache; adotá-la somente quando surgir necessidade concreta. [Execução de scripts com uv](https://docs.astral.sh/uv/guides/scripts/)

Sempre montar argumentos em lista, com `shell=False`, preservar espaços/Unicode e estabelecer explicitamente o diretório de trabalho (o `cwd` do terminal do usuário). Para subprocessos Python no Windows, injetar `PYTHONIOENCODING=utf-8` no ambiente e tratar E/S com `encoding="utf-8", errors="replace"` para evitar travamentos por caracteres acentuados em consoles legados (CP1252/OEM). Não usar `eval`, interpolação de shell ou download e execução de scripts remotos a cada uso.

`doctor` deve distinguir dependência ausente, versão incompatível, daemon inacessível, configuração incompleta e recurso indisponível. Não instalar Docker/Restic, elevar privilégios nem pedir senha só para listar ferramentas. Diagnósticos devem ter timeout; backups longos não recebem um timeout curto arbitrário.

## 8. Portabilidade, configuração e dados

Alvo inicial: Windows 11 com PowerShell e Ubuntu LTS com Bash, em arquitetura x86_64. Outras distribuições, ARM64 e WSL só serão declarados suportados após validação; WSL é um ambiente separado, com instalação e caminhos próprios.

Usar caminhos de configuração, cache, estado e logs via `platformdirs`. No Linux, respeitar variáveis XDG; no Windows, separar subpastas quando a biblioteca devolver a mesma raiz para diferentes finalidades. [Diretórios por plataforma](https://platformdirs.readthedocs.io/en/latest/platforms.html)

Configuração proposta: `config.toml` com `schema_version` e perfis locais como `casa` e `trabalho`. Precedência: argumentos explícitos, variáveis documentadas e configuração do perfil. Não carregar configuração executável ou de um repositório arbitrário automaticamente.

Caminhos de origem, destino e montagem são locais: a unidade `D:` não equivale automaticamente a `/media/...`. A atualização de código não copia esses valores entre máquinas. Restaurar snapshot de outro SO exige tratar caminhos internos, links e permissões; não prometer equivalência completa.

Migrar `%LOCALAPPDATA%\ResticMenu\config.json` por operação explícita: validar, preservar cópia do original, manter ID do repositório e escrever a nova configuração atomicamente. Não sobrescrever perfil existente nem tentar usar os padrões Windows no Linux. Configuração de schema futuro deve produzir orientação, sem ser sobrescrita por versão antiga.

Senhas não entram em TOML, catálogo, linha de comando ou logs. Manter prompt seguro no modo interativo; automação exige provedor de segredo explicitamente suportado. Registrar operação, versão, duração e resultado, com remoção de credenciais e retenção limitada. Exibir onde os logs ficam, sem capturar indiscriminadamente dados sensíveis dos processos filhos.

## 9. Segurança operacional e migração das ferramentas

Definir política por operação: leitura, escrita e destruição. Confirmação depende do efeito; leitura normal não precisa de pergunta. Simulação deve ser verdadeira e sem escrita; quando só for possível mostrar um plano, chamá-lo de plano, sem alegar validação completa.

Restic: preservar verificação do ID antes da operação, ausência de inicialização automática, bloqueio de sobreposição entre origem/repositório/destino e restauração em destino novo. `--yes` não remove essas barreiras. Testar links simbólicos, junctions e diferenças de maiúsculas no Windows. Repositório ausente ou trocado bloqueia a ação. Backup parcial deve continuar distinguível de sucesso. Exclusão de snapshots e prune permanecem fora do escopo inicial.

Docker: separar importação e execução; importar imagens não restaura volumes, configurações de containers ou toda a aplicação. Exportar para temporário no destino e promover após sucesso; tratar falta de espaço, interrupção e falha do manifesto. Informar que o `.txt` é inventário auxiliar, não verificação criptográfica. Se adotado checksum, validar na importação e distinguir integridade de autenticidade.

Evitar alterar arquivos de instalação durante execução. Definir bloqueios locais para operações concorrentes que disputem o mesmo destino, sem substituir locks próprios do Restic. Nunca remover lock externo automaticamente para contornar erro.

Para origem privada, usar credenciais do Git/gerenciador, sem tokens em exemplos ou manifestos. Alterações integradas ao repositório passarão a executar nas máquinas após atualização: revisão e CI são parte da confiança na distribuição. Assinatura/atestação de releases pode ser evolução quando houver distribuição mais ampla.

## 10. Fases e critérios de conclusão

### Fase 0 — Inventário e contratos

- Confirmar incorporação de `restic/` e `PLANO_UTILITY_BELT.md` ao Git antes de distribuí-lo; decidir renomeação sem torná-la bloqueante.
- Documentar comandos, plataforma alvo, schema do catálogo e política de configuração.
- Registrar comportamentos e proteções existentes dos scripts ativos (`Docker` e `Restic`) antes da adaptação; descartar/excluir pastas não utilizadas (`Conda` e `Utilitarios`).

### Fase 1 — Prova completa de distribuição

- Criar pacote, entry points, catálogo e integrar uma ferramenta piloto segura e sem efeitos colaterais (ex.: `system_info` ou contador de texto) para comprovar a distribuição.
- Configurar build backend com inclusão expressa de dados (`tool.toml`) e testar empacotamento wheel.
- Instalar em Windows/Linux fora do checkout via `uv tool` e disponibilizar `--help`, `list` e `doctor`.
- Entregar segunda versão com ferramenta nova; um upgrade deve fazê-la aparecer em ambas as máquinas.
- Demonstrar reinstalação da versão anterior e preservação da configuração.

### Fase 2 — Docker e Restic

- Adaptar argumentos Docker e separar importação/execução em subcomandos distintos.
- Manter Restic legado identificado como interativo até existir CLI própria que conserve as proteções.
- Migrar configuração Restic para TOML via `tomli-w` com backup do original e testes de caminhos por SO.
- Entregar backup/restauração diretos; modo não interativo só após resolver credenciais e validações.

### Fase 3 — Ergonomia e robustez

- Menu como cliente dos mesmos comandos, completion (`--show-completion`) e exemplos por shell.
- Logs limitados, saída estruturada de diagnóstico, cancelamento por Ctrl+C limpo e tratamento de falhas parciais.
- Documentar cadastro de nova ferramenta, fluxo de atualização, recuperação e desinstalação.

### Fase 4 — Evolução por necessidade

- Releases estáveis e distribuição por wheel/índice escolhido.
- Dependências isoladas por script se surgirem conflitos reais.
- Considerar perfis de seleção, plugins, wrapper de atualização e builds autocontidos somente com casos de uso demonstrados.

## 11. Matriz mínima de aceitação

| Cenário | Resultado obrigatório |
| --- | --- |
| Instalar em Windows e Linux limpos | `belt` acessível fora do checkout, sem ativação manual de venv |
| Atualizar versão A para B com ferramenta nova | Nova ferramenta listada e executável com um comando de atualização |
| Executar atualização novamente | Mesmo catálogo, sem duplicar comandos nem alterar configuração |
| Versão B remove ferramenta | Comando removido do catálogo; dados locais preservados |
| Instalar wheel fora da árvore fonte | Todos os scripts/manifestos presentes, sem dependência do cwd |
| Caminhos relativos passados via CLI (`--output ./x.tar`) | Resolvem a partir do diretório onde o usuário disparou o comando (`Path.cwd()`), nunca dentro de `site-packages` |
| Execução de script PowerShell em Windows limpo | Executa com sucesso via `-ExecutionPolicy Bypass` de processo, sem alterar a política do sistema |
| Caracteres acentuados/Unicode no Windows console | Sem `UnicodeEncodeError`; E/S e logs em UTF-8 com fallback resiliente |
| Sem Docker ou Restic | CLI e ferramentas independentes funcionam; erro localizado na ferramenta afetada |
| Sem rede após preparo | Ferramentas locais executam; atualização relata indisponibilidade |
| Caminhos com espaços, acentos e shell metacharacters | Argumentos preservados, sem interpretação de shell |
| Sem TTY e ferramenta interativa | Erro imediato (código 2); nunca trava esperando `input()` |
| Ctrl+C durante operação | Processo filho tratado, retorno coerente (130) e parcial identificado sem traceback |
| HD ausente/trocado ou destino sobreposto | Operação Restic bloqueada antes da escrita |
| Backup parcialmente concluído | Código e diagnóstico distintos de sucesso |
| Atualização/instalação falha | Configuração preservada e recuperação documentada/testada |
| Duas operações no mesmo destino | Concorrência tratada sem sobrescrita silenciosa |
| Desinstalar | Comando removido; configuração e backups preservados por padrão |

CI deve validar catálogo, lint, contratos, wheel/sdist e testes em ambos os SOs. Usar dublês de executáveis para argumentos, códigos e erros, complementados por integração Restic em diretórios temporários e Docker em ambiente descartável. Dublês sozinhos não provam compatibilidade real. Nunca usar os repositórios de backup pessoais nos testes.

## 12. Definição de sucesso

O projeto estará cumprindo seu objetivo quando adicionar um script exigir apenas seu código, manifesto e teste; uma nova entrega o tornar instalável; e um único comando de atualização em cada máquina o disponibilizar no terminal sem edição do launcher, cópia manual ou perda de configuração.

O menu melhora a descoberta, mas a qualidade do canivete suíço será medida pela facilidade de adicionar ferramentas, pela previsibilidade dos comandos e pela confiança na instalação e atualização entre Windows e Linux.
