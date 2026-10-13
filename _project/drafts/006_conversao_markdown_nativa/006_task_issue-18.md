# Task — Issue #18: CLI, menus, catálogo e distribuição Markdown

> **Ciclo:** `006`
> **Estado:** `Em andamento`
> **Tipo:** `feature`
> **Issue:** [#18](https://github.com/EuThiagoAndrade/utility-belt/issues/18)
> **Plano:** `_project/drafts/006_conversao_markdown_nativa/006_plan.md`
> **Branch:** `feature/issue-18`
> **Worktree:** `C:/Programas/utility-belt`
> **PR:** [#21](https://github.com/EuThiagoAndrade/utility-belt/pull/21) — aberta em rascunho
> **Integração:** `Pendente`
> **Início:** 2026-10-12
> **Última atualização:** 2026-10-12
> **handoff_schema_version:** `1`
> **handoff_id:** `utility-belt/006/implementar_issue/issue-18/044605f6e7e44e4a2802aabdee2f163428a66406`

## Objetivo

Expor as cinco capacidades pela CLI, catálogo e menu nativos, diagnosticar sem aquisição e validar a distribuição fora do checkout.

## Escopo autorizado

Item 3 da v4 aprovada, issue #18 e pedido humano “Autorizado integrar a PR #20 para continuar com a #18”. A PR #20 foi integrada em `044605f6e7e44e4a2802aabdee2f163428a66406`, issue #17 fechada; main atualizada por fast-forward. Não autoriza integração de C, encerramento ou descontinuação do File2MD.

## Execução

- [x] Preflight remoto/local; nenhuma branch, task ou PR anterior para #18.
- [x] Adaptador, catálogo, propagação não interativa, menu e doctor.
- [x] Testes, smokes distribuídos na matriz e documentação.
- [x] Gates e publicação revisável na PR #21, vinculada a #18 e anexada ao chat.

## Evidências

| Gate | Resultado |
| :-- | :-- |
| Testes | Rodada completa final: **207 passed em 206,97 s**, Windows x64 Python 3.13.7, motor/observador reais, sem skips. Rodada anterior: 204 passed em 205,52 s; correção do backend gráfico: 51 passed (CLI/lote). Python 3.11.16: 41 passed em 3,28 s, depois 32 casos da interface final passed em 0,86 s. |
| Validação | Ruff passou; governança: 31 OK, aviso conhecido 006/007, zero falhas; wheel/sdist construídos, 17 recursos do worker/receitas/ferramenta/manifesto inspecionados nos dois arquivos. |
| `git diff --check` | Limpo |
| Checks remotos | PR #21 aberta/draft e mergeable; zero statuses e zero workflow runs no commit de implementação consultado. Ausência de CI não significa aprovação remota. |

## Decisões incidentais e desvios

O consentimento anterior para um único envio de áudio foi consumido em A. Nenhum novo áudio foi enviado. Clipboard rico do Windows preservado; clipboard real exercitado somente em sessão X11 descartável.

- A revisão de receitas agora participa do caminho do runtime (SHA-256 dos arquivos empacotados, prefixo `2959f9f80f2b7a67`). Isso atende a separação prevista em P04 para mudanças de receita; o runtime anterior de A/B é preservado, sem migração automática. Somente os ambientes descartáveis de teste foram movidos para a nova pasta para repetir regressões. Reinstalação compatível do pacote reutiliza o mesmo intérprete sem mudança do mtime; outro Python/receita tem teste de identidade distinto.
- Aquisição Python consentida falha/import inválido retorna `1`, separada de ausência/recusa `2`; teste simula falha, resultados não publicados e nova confirmação na tentativa seguinte. Nenhuma receita ou versão do motor foi modificada.
- Harness Windows inicialmente herdou stdin TTY, e `NUL` também reportou isatty; não-TTY real foi exercitado com pipe vazio. Harness Linux inicialmente resolveu o symlink do Python e escapou da venv; corrigido para preservar o caminho absoluto do intérprete instalado. Não houve mudança de produção por essas falhas de harness.
- Imagem Bullseye antiga não conseguiu instalar dependências de teste X11 (Yarn com chave ausente e URLs Debian 404). Smoke gráfico passou para imagem oficial Bookworm, digest `sha256:a1165e272e578941b84abc79e4ab38a0305cd12803a5c4247979ac7655f4d641`, Python 3.13.16 verificado. Pacotes de sistema somente no container descartável do harness, nunca pelo Belt.
- Bind de pasta Windows no container não emitiu evento do observador; repetição usa filesystem Linux nativo `/tmp`. Evidência dos resultados é copiada após o smoke, sem substituir o observador por um mock ou aumentar timeout de produção.
- Pyperclip 1.11.0 detectava `/proc/version` Microsoft antes de X11 e tentava `powershell.exe` inexistente no container. Núcleo prioriza backend disponível da sessão local X11/Wayland pelo `set_clipboard` da própria biblioteca; restaura os callbacks da biblioteca após leitura, sem escrever clipboard. Regressões cobrem xclip/xsel/wl-clipboard.

### Matriz de pacote instalado fora do checkout

Todos usam `tests/markdown_distribution_smoke.py --python <python-instalado> --artifact <wheel-ou-sdist> --fixture-dir tests/fixtures/markdown --work-dir <pasta-descartável> --consent-install`; driver pywinpty 3.0.2 em Windows e pexpect 4.9.0 em Linux, separados do ambiente inicial do Belt. TTY efetivo via PTY/ConPTY, sem substituir isatty ou consentimento de produção. Receitas empacotadas adquiridas após respostas `s` específicas para base e PDF; antes disso não-TTY, flag em TTY e recusa `n` retornam `2` sem lock/runtime. Pacote inicial inspecionado com `-I`, sem MarkItDown/pdfplumber.

| Plataforma/Python | Artefato e execução | Resultado |
| :-- | :-- | :-- |
| Windows x64 3.13.7 | wheel; `C:/Users/thiag/AppData/Local/Temp/belt006-c-py313/app`; work-final | CLI/catálogo/conversão PDF/lote/monitor, aquisição e reuso/upgrade passaram; menu TTY sucesso/erro/cancelamento retornam ao submenu; URL pública example.com pela CLI instalada retornou `0`. |
| Windows x64 3.11.16 | sdist construído/instalado por uv; `C:/Users/thiag/AppData/Local/Temp/belt006-c-py311/app` | Instalação mínima, TTY recusa/consentimento, PDF, lote e monitor real com Ctrl+C `130`, catálogo e reuso após reinstalação passaram. |
| Linux x64 3.11.13 | sdist; imagem `mcr.microsoft.com/devcontainers/python:1-3.11-bullseye`, app `/tmp/belt-app`, cwd `/tmp/belt-work` | Todos os passos do harness passaram, incluindo aquisição real base/PDF e monitor; clipboard headless indisponível `2`; sem dependência de cwd do checkout. |
| Linux x64 3.13.16 | wheel; Bookworm + Xvfb/xclip, app `/tmp/belt-app`, cwd `/tmp/belt-work` | Passou: base/PDF com consentimento, reuso/upgrade, paridade de conteúdo/códigos CLI/catálogo, lote, monitor Ctrl+C `130`, clipboard X11 real `0` e menu TTY com sucesso/erro/cancelamento retornando ao submenu. |

Config temporária pelos caminhos platformdirs (Windows `WIN_PD_OVERRIDE_LOCAL_APPDATA`, Linux XDG), nenhuma preferência do responsável alterada. Saídas reais, não Markdown esperado fabricado. Fixtures próprias; Google não foi chamado. Aquisição reutiliza PyPI/cache uv conforme disponibilidade, com versões/hashes da receita. “Upgrade compatível” exercitado por reinstalação do mesmo artefato 0.1.0: demonstra persistência, sem alegar lançamento de nova versão.

Artefatos finais locais: wheel SHA-256 `8fe5d6d17e36dba01060625b3b44815fe0db958f6732603de1aac72cae12a8e2`; sdist `7761aee0388a1da5e96bff8780ee2853a991cafcabd1c64ca10e77bbb7e548e6`. Inspeção confirmou igualdade de bytes dos 43 arquivos Python/receitas/manifestos do pacote com o checkout final. Wheel/sdist e dados de smoke permanecem ignorados; nenhuma venv entra no commit.

## Resultado

Implementação e matriz concluídas; commit `1a66fb24cd3013478f13bc3cdc4e10f857411855` publicado em `feature/issue-18`, PR #21 aberta/draft e anexada ao chat. Nenhum merge C, encerramento ou descontinuação do File2MD executados. Python 3.11.16 repetiu todos os 32 testes da interface final: 32 passed em 0,86 s.

### Cinco usos reais apresentados para aceite

Arquivos preservados no workspace (ignorados pelo Git) após copiar os resultados do container Linux; origem real `/tmp/belt-work/central`. Destino central persistido em `C:/Programas/utility-belt/.venv-cycle-006-smoke/distribution-linux313/final-config.toml` como evidência de `[markdown].output_dir = /tmp/belt-work/central`; não é configuração do responsável. A pasta de resultados locais é `C:/Programas/utility-belt/.venv-cycle-006-smoke/distribution-linux313/final-central/`.

| Uso | Resultado/destino relativo à pasta local de resultados |
| :-- | :-- |
| Individual de arquivo | `0`, `2026-10-13_01-48-52/sample.pdf.md`, texto do PDF fixture; individual de URL example.com `0` em `C:/Users/thiag/AppData/Local/Temp/belt006-c-py313/work-final/url-output/2026-10-12_21-47-01/web_content.md`. |
| Lote recursivo | `0`, `2026-10-13_01-48-55/deep/file.txt.md`, um sucesso, estrutura relativa preservada. |
| Monitor | Arquivo novo `0`, `2026-10-13_01-48-59/deep/new.txt.md`; Ctrl+C `130`, observador liberado, sucesso preservado. |
| Clipboard | Caminho textual lido de X11/xclip real, `0`, `2026-10-13_01-49-01/sample.txt.md`; clipboard Windows não alterado. |
| Configuração central | CLI `config --output-dir central` retornou `0`; arquivo `final-config.toml` preservado; execuções seguintes sem `--output-dir` gravaram nessa central; override temporário manteve TOML idêntico. |

`final-evidence.json` na mesma raiz registra Python/pacote/runtime/saídas e clipboard real. Destinos Windows adicionais estão nos `evidence.json` de cada work da matriz. Aceite humano desses usos e integração da PR C continuam pendentes; nenhuma evidência autoriza descontinuar File2MD.

### Handoff de execução

- `handoff_schema_version`: `1`
- `handoff_id`: `utility-belt/006/implementar_issue/issue-18/044605f6e7e44e4a2802aabdee2f163428a66406`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`.
- `effect_class`: `remote_mutation`.
- `state_before`: #18 aberta/autorizada, B integrada, main limpa na revisão de origem.
- `state_after`: escopo C implementado, validado e documentado; branch publicada, PR #21 aberta/draft, issue #18 aberta.
- `next_transition`: implementação -> gates -> publicação -> revisão/checks -> integração autorizada.
- `preconditions`: manter escopo da v4 e satisfazer critérios da #18 antes de publicar.
- `authority`: responsável autorizou execução; plano e issue delimitam aceite; GitHub governa estado remoto.
- `evidence`: PR #20 integrada/#17 fechada, base `044605f6e7e44e4a2802aabdee2f163428a66406`, commit `1a66fb24cd3013478f13bc3cdc4e10f857411855`, PR #21, 207 testes, gates, matriz instalada e cinco usos registrados nesta task.
- `acceptance`: cinco capacidades acessíveis, distribuição e consentimento comprovados, gates aprovados e PR rastreável.
- `blockers`: nenhum local; revisão/aceite e autorização de integração C pendentes.
- `result`: `executed`.
- `next_workflow_recommended`: revisão/checks, aceite dos usos e integração somente após autorização própria.
- `next_workflow_authorized`: implementar/publicar #18; merge exige decisão própria.
- `actions_prohibited`: integrar C, encerrar ciclo, descontinuar File2MD, ampliar escopo.
- `rejection_rule`: recusar handoff ausente, incompatível, contraditório ou sem evidência material.
- `logical_key`: `utility-belt/006/implementar_issue/issue-18/044605f6e7e44e4a2802aabdee2f163428a66406`.
- `check_before_mutation`: branch/task/PR pesquisadas antes da criação; repetir antes de publicar.
- `reconcile_existing`: retomar esta unidade sem duplicação.
- `ambiguous_state`: parar se surgirem unidades concorrentes ou divergência de autorização/escopo/base.
