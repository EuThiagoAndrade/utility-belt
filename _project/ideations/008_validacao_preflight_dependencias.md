# Ideação — 008: Validação prévia de dependências externas (preflight guard)

> **Ciclo:** `008`
> **Estado:** `Ideação`
> **Criado em:** 2026-10-14
> **Última atualização:** 2026-10-14

## Problema

O Utility Belt integra utilitários de terceiros (como Restic e Docker), mas atualmente não valida a presença desses softwares quando o usuário entra em seus respectivos submenus. O sistema abre os menus normalmente e a ausência do binário só é detectada reativamente no momento da execução de uma ação (ex.: realizar backup ou exportar imagens), resultando em exceções `FileNotFoundError` com mensagens de erro técnicas que não oferecem ao usuário orientações sobre como obter o software, onde baixá-lo ou como instalá-lo no sistema operacional em uso.

## Contexto e evidências

- Baseline: commit `cf44c9076875b51e2806b4a6236d3fa8e969e5a9` na branch `main`.
- Arquitetura atual:
  - `src/utility_belt/doctor.py`: implementa checagens de executáveis (`check_restic`, `check_docker`, etc.) e informa se estão no `PATH` ou se o daemon do Docker está ativo, mas é consultado apenas via comando `belt doctor` ou na tela `Sistema > Verificar ambiente`.
  - `src/utility_belt/ui/restic_menu.py`: a função `show_restic_menu()` não realiza validação preliminar; comandos em `run_restic()` capturam `FileNotFoundError` apenas durante a execução da tarefa.
  - `src/utility_belt/ui/docker_menu.py`: a função `show_docker_menu()` exibe o menu sem checagem de preflight; falhas de executável são tratadas apenas ao tentar listar ou carregar imagens.
  - `src/utility_belt/ui/screen.py`: autoridade visual da interface terminal do Utility Belt, com paleta de cores consistente (cyan, amarelo para avisos, verde para sucessos), `render_header`, `_line`, `message`, `prompt`, `menu_separator` e `menu_footer`.
- Consulta com o responsável em 2026-10-14:
  - O responsável escolheu a abordagem de checagem prévia na entrada do submenu (Preflight / Guard).
  - Aprovou as opções:
    1. Ver instruções de instalação no terminal;
    2. Abrir a página de download no navegador;
    3. Voltar ao menu principal.
  - Exigiu expressamente o cuidado de manter rigorosamente a interface visual e gráfica canônica do Utility Belt / Restic (`src/utility_belt/ui/screen.py`), sem molduras desconexas ou estilos dissonantes.

## Resultado desejado

1. **Preflight Guard nos submenus**: Ao selecionar Restic ou Docker no menu principal, o sistema executa um preflight rápido.
2. **Tela de Requisito Ausente (Onboarding)**: Caso o executável não esteja presente no sistema:
   - A tela mantém a identidade visual canônica de `screen.py` (`render_header`, `message("AVISO", ...)`, `prompt(questionary.select, ...)`).
   - Apresenta explicação clara da finalidade da ferramenta e a razão da dependência.
   - Oferece menu com três opções canônicas:
     - `[1] Ver instruções de instalação no terminal`: exibe comandos recomendados para o SO detectado (Windows: `winget`, `scoop`, links diretos; Linux: `apt`, `dnf`, etc.);
     - `[2] Abrir página de download no navegador`: utiliza `webbrowser.open` para abrir o site oficial ou repositório de releases e exibe a URL no terminal caso o ambiente seja headless ou a abertura falhe;
     - `[0] Voltar ao menu principal`: retorna de forma limpa ao menu raiz.
3. **Tratamento de Docker Daemon**: Se o binário do Docker estiver presente mas o daemon estiver desligado, apresentar mensagem e orientações específicas para inicializar o serviço/Docker Desktop.
4. **Enriquecimento do `doctor`**: No comando `belt doctor` e na tela `Sistema > Verificar ambiente`, exibir links e comandos de instalação sugeridos para itens marcados como `[FALTA]`.

## Hipóteses

- A reutilização direta de `check_restic()` e `check_docker()` de `doctor.py` evita duplicidade e assegura coerência entre o diagnóstico e a navegação.
- O uso de `screen.py` (`render_header`, `message`, `prompt`, `menu_options`, `menu_footer`) garante fidelidade visual e consistência imediata com a experiência do usuário existente.
- A biblioteca padrão `webbrowser` e `platform` atende à abertura de URLs e detecção de plataforma sem introduzir novas dependências no `pyproject.toml`.

## Alternativas

1. **Manter o comportamento reativo (status quo)**: Rejeitada, pois expõe o usuário a erros frustrantes após navegar por múltiplos passos de configuração.
2. **Ocultar ou desabilitar ferramentas ausentes no menu principal**: Rejeitada, pois impede que o usuário descubra recursos do Utility Belt e aprenda como habilitá-los.
3. **Instalação automática de dependências em segundo plano**: Rejeitada, pois instalações de Docker e Restic exigem elevação de privilégios (`sudo` / UAC), reinicializações ou gerenciadores de pacotes de sistema, ferindo os princípios de segurança, previsibilidade e consentimento explícito.
4. **Preflight Guard interativo com onboarding assistido (Escolhida)**: Intercepta a navegação no ponto de entrada do submenu, orienta o usuário de forma amigável e preserva a autonomia e integridade do sistema.

## Riscos e restrições

- **Fidelidade visual estrita**: Não adotar estilos ou diagramas arbitrários; utilizar estritamente a API de `utility_belt.ui.screen` para cabeçalhos, avisos e menus.
- **Ambientes não interativos (CLI/Scripts)**: Comandos executados diretamente via linha de comando (`belt restic ...`, `belt docker ...`) quando fora de TTY não devem abrir navegador ou travar em prompts interativos; devem emitir mensagem instrutiva no `stderr` com código de saída adequado.
- **Falha de abertura do navegador**: Ambientes headless (SSH, contêineres, servidores sem GUI) podem falhar em `webbrowser.open()`; a URL deve ser sempre impressa em texto para que o usuário possa copiar ou clicar.
- **Simplicidade de código**: Não criar um subsistema complexo de gerenciamento de pacotes; manter a solução leve, focada em diagnóstico, instruções contextuais e atalhos de navegação.

## Perguntas em aberto

- Para o Docker, quando o binário existir mas o daemon estiver inativo, devemos oferecer tentativa de aguardar o daemon ou apenas orientar o usuário a iniciar o Docker Desktop / daemon? (Orientação inicial é o caminho mais seguro e direto).
- Em terminais compatíveis com hyperlink OSC 8, vale a pena formatar a URL clicável diretamente na mensagem informativa?

## Fora do escopo

- Instalação automática com privilégios administrativos de sistema (`sudo` ou prompt UAC automático).
- Suporte a download de binários não verificados diretamente para diretórios de sistema.
- Alteração do motor Markdown (que possui ciclo de aquisição próprio isolado via ciclo 006).
- Adição de novas ferramentas ou novos adaptadores.

## Critérios para iniciar o planejamento

- Validação da ideia e escopo pelo solicitante.
- Definição formal das mensagens e URLs oficiais de cada ferramenta (Restic: `https://restic.net` / `https://github.com/restic/restic/releases`; Docker: `https://www.docker.com/products/docker-desktop`).
- Confirmação de que o visual segue as convenções já consolidadas em `src/utility_belt/ui/screen.py`.

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+008+idear+validacao-preflight-dependencias+cf44c90`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`
- `effect_class`: `local_mutation`
- `state_before`: ausência de validação prévia na entrada de submenus de dependências externas; erros reativos em tempo de execução.
- `state_after`: ideação do ciclo 008 registrada detalhando problema, preflight guard, fidelidade visual de `screen.py`, alternativas e riscos.
- `next_transition`: `ideia -> rascunho de plano`, dependente de decisão humana.
- `preconditions`: contexto identificado e solicitação explícita do usuário atendida.
- `authority`: solicitante, conversa de 2026-10-14.
- `evidence`: `_project/ideations/008_validacao_preflight_dependencias.md`, `src/utility_belt/doctor.py`, `src/utility_belt/ui/screen.py`.
- `acceptance`: fatos e hipóteses separados, alternativas analisadas, riscos documentados e alinhamento visual com `screen.py` assegurado.
- `blockers`: nenhum para a ideação.
- `result`: `executed`
- `next_workflow_recommended`: `rascunhar_plano`
- `next_workflow_authorized`: nenhum (aguardando aprovação humana da ideação).
- `actions_prohibited`: implementar código de produção, aprovar plano sem revisão formal ou abrir PR sem autorização explícita.
- `rejection_rule`: o receptor recusa handoff ausente, incompatível, sem evidência ou sem autoridade explícita.
- `logical_key`: `EuThiagoAndrade/utility-belt+008+idear+validacao-preflight-dependencias+cf44c90`
- `check_before_mutation`: ciclo 008 livre em `_project/cycles.md`, sem artefatos conflitantes.
- `reconcile_existing`: atualizar este artefato caso haja novos refinamentos sem criar ciclos duplicados.
- `ambiguous_state`: interromper a mutação e solicitar intervenção humana caso haja divergência.
