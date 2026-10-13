# Task — Issue #17: Lote, monitoramento e clipboard

> **Ciclo:** `006`
> **Estado:** `Em andamento`
> **Tipo:** `feature`
> **Issue:** [#17](https://github.com/EuThiagoAndrade/utility-belt/issues/17)
> **Plano:** `_project/drafts/006_conversao_markdown_nativa/006_plan.md`
> **Branch:** `feature/issue-17`
> **Worktree:** `C:/Programas/utility-belt`
> **PR:** [#20](https://github.com/EuThiagoAndrade/utility-belt/pull/20) — aberta em rascunho
> **Integração:** `Pendente`
> **Início:** 2026-10-12
> **Última atualização:** 2026-10-12
> **handoff_schema_version:** `1`
> **handoff_id:** utility-belt/006/implementar_issue/issue-17/13b4719af643747b679e87602ac5ff414b35d716

## Objetivo

Implementar Item 2 da v4 aprovada, após integrar A. Autorização humana atual: “Autorizo integrar a PR #19 para continuar com a #17”.

## Escopo autorizado

Lote sequencial recursivo com pasta compartilhada/resumo; monitor em primeiro plano para novos arquivos e pastas, estabilidade 1 s/timeout 30 s, deduplicação por ciclo de vida; clipboard arquivo/URL. Reutilizar núcleo, excluir saídas/links e preservar consentimentos. CLI/catálogo/menu/distribuição pertencem à #18.

## Execução

- [x] Ler autoridades/workflow/templates/gate e plano; confirmar issue #17 aberta e autorização.
- [x] Aceitar handoff de A: 138 testes/gates documentados, head remoto intacto `e523fb0`, PR sem conflitos/revisões impeditivas, nenhum status/run CI disponível (não inferir sucesso de CI).
- [x] Marcar PR #19 pronta e integrar com SHA esperado; GitHub confirmou merge `13b4719af643747b679e87602ac5ff414b35d716` e issue #16 fechada.
- [x] Atualizar main via fast-forward; base da #17 é o merge verificado. Branch/PR/task anteriores de #17 não encontradas; criar branch canônica.
- [x] Implementar Item 2 e testes: lote compartilhado, enumeração finita, monitor/estabilidade/lifecycle, clipboard e consentimentos.
- [x] Executar gates e smokes Windows/Linux.
- [x] Publicar PR #20 após staging seletivo; anexar ao chat e conferir estado remoto.

## Evidências

| Gate | Resultado |
| :-- | :-- |
| Testes | `uv run pytest`: código 0, 175 testes, 240,04 s; `BELT_MARKDOWN_TEST_DATA` aponta para aquisições reais e `PYTEST_ADDOPTS=-p no:cacheprovider`; sem envios externos |
| Validação | `uv run python scripts/validate_governance.py`: código 0, 31 OK, aviso conhecido 006/007, nenhuma falha; `uv run ruff check`: código 0 |
| `git diff --check` | Código 0; `git diff --cached --check` também limpo; staging com somente os dez arquivos de B/rastreabilidade |
| Checks remotos | Para commit `35c3e003d8bac4723ae75af1fa36f878f3b5022a`: zero statuses e zero workflow runs observados; ausência de CI não é aprovação de check |

Commit de implementação validada: `35c3e003d8bac4723ae75af1fa36f878f3b5022a`. PR #20 aberta/draft, não integrada, base main no merge verificado de A. Ajuste documental posterior registra vínculos e estados, sem alterar código ou testes validados.

## Decisões incidentais e desvios

### Matriz e smokes

- Windows x64/Python 3.13.7: suíte completa final com 175 testes passando, incluindo os 37 cenários B. Windows x64/Python 3.11.16: 34 testes B iniciais em 65,64 s, dois cenários adicionais de clipboard em 0,35 s e novo teste de falha de leitura de diretório em 0,38 s; total 37 testes, sem skips.
- Linux x64/Python 3.11.13: 36 testes B em 47,10 s e novo cenário de falha de diretório em 0,49 s; Linux x64/Python 3.13.15: 36 testes em 48,23 s e novo cenário em 0,63 s. Total 37 cenários por combinação; testes complementares registram a última correção sem repetir aquisições de formatos.
- Smokes Linux usam containers descartáveis `mcr.microsoft.com/devcontainers/python:1-3.11-bullseye`, checkout montado somente leitura e dados em `/tmp/belt-smoke`. Python 3.13.15 foi obtido exclusivamente para desenvolvimento em `/tmp/interpreters`; instalador de produção continua sem download de intérprete. Windows reutiliza `.venv-cycle-006-smoke`/Python 3.11 e 3.13.
- Comando de preparação/validação: `python tests/markdown_modes_smoke.py --data-dir <dados-isolados> --consent-install`. Adquire somente base/PDF/DOCX, ambiente audio para provar isolamento mesmo quando instalado e ExifTool; nunca autoriza áudio externo. Windows usa receitas já adquiridas na entrega A.
- Observador watchdog real nas duas plataformas: estoque/edições ignorados, arquivo em dois níveis de novas pastas, movimento de pasta externa com subpastas, remoção/recriação, cópia lenta, exclusão da saída interna e cancelamento que libera observador. Timeout real de 30 s usa observador/relógio reais e leitura indisponível injetada na fronteira, sem mudar ACL/permissões do sistema. Testes controlados complementam estabilidade, deduplicação, revalidação antes/depois do motor, timeout sem loop e falhas individuais.
- Integração real do núcleo: lote PDF/DOCX/WAV/ZIP parcial em subpastas, pasta única, caminhos relativos, sucesso parcial preservado, metadados de áudio sem envio; monitor com motor real e arquivo novo conhecido; clipboard com fixture própria via reader controlado. Clipboard Windows nativo foi lido sem mostrar conteúdo ou alterar formatos existentes; os formatos observados incluem formatos adicionais, por isso a área de transferência do usuário não foi substituída. Linux headless provou erro de backend útil/código 2, sem instalar utilitários de sistema.

### Escolhas incidentais e limites

Smoke adicional com resultados persistidos em dados de desenvolvimento próprios (Windows 3.13, sem aquisição/envio externo):

- Lote: código `0`, dois sucessos e nenhuma falha, `.venv-cycle-006-smoke/modes-demo-source/output/2026-10-12_21-23-56/`, contendo `docs/deep/sample.txt.md` e `docs/sample.pdf.md`.
- Monitor: novo arquivo convertido com código `0`, `.venv-cycle-006-smoke/modes-demo-source/output/2026-10-12_21-24-04/new-file.txt.md`; encerramento cooperativo `130`, um sucesso, nenhuma reconversão de estoque/saída.
- Clipboard com reader controlado de caminho de fixture: código `0`, `.venv-cycle-006-smoke/modes-demo-clipboard-output/2026-10-12_21-24-08/sample.txt.md`. Backend nativo foi validado separadamente por leitura sem alteração de conteúdo/formatos existentes.

- Monitor em `markdown_watch.py` separa somente observação/lifecycle; conversão, saídas, dependências e consentimentos continuam no núcleo compartilhado `markdown.py`. Não há serviço de fundo ou worker paralelo de conversão.
- Lote calcula o conjunto finito de áudio no preflight e pede uma confirmação por conjunto, incluindo membros identificados de ZIP. Hashes vinculam autorização às entradas; mudança depois do aceite impede envio. Monitor confirma áudio por nova conversão; não-TTY/`non_interactive` mantém fallback local. Nenhum novo envio ao Google foi realizado nesta entrega.
- Consentimento de aquisição é consumido uma vez por grupo/ambiente na operação. Se instalação falhar, os demais arquivos independentes continuam; a mesma confirmação não provoca novos downloads para outros arquivos. Uma nova operação exige novo consentimento para o requisito que ainda falta.
- Links simbólicos são excluídos no Linux; Windows valida junctions reais sem privilégio administrativo, com proteção por `FILE_ATTRIBUTE_REPARSE_POINT` também no Python 3.11. Toda a raiz resolvida de saída é excluída; raízes iguais são rejeitadas.
- Duas observações iguais de identidade/tamanho/mtime, separadas por 1 s, são uma aproximação. Pausas de escrita podem parecer estabilidade; não há garantia de término definitivo. Mudança antes da publicação descarta resultado e restabiliza dentro do prazo original; edição depois da publicação é edição de arquivo concluído e não gera reconversão.
- Rodadas completas concorrentes usaram o mesmo ambiente de motor. Uma delas falhou apenas no limite de espera de 30 s do harness do smoke nativo (173 passaram, um falhou); cenário dirigido posterior passou em 5,98 s e a rodada final passou com 175 testes. A falha inicial não foi contada como aprovação; nenhuma alteração de timeout de produção ou relaxamento de assertivas foi usada para obter o gate final.

Reutilizar ambiente `.venv-cycle-006` e aquisições isoladas do ciclo; preservar `.venv` e cache alheios. Não há autorização para repetir o envio externo de áudio da entrega A. Mocks de serviço externo podem validar consentimento sem enviar dados. Reconciliação documental de A acompanha B, sem alterar seu código fora das adaptações necessárias ao Item 2.

## Resultado

A integrada; B implementada, validada e publicada na PR #20 em rascunho. Revisão e autorização de integração B pendentes; C não iniciada. Sem mudanças de CLI/menu/catálogo ou encerramento do ciclo.

### Handoff de execução

- `handoff_schema_version`: `1`
- `handoff_id`: `utility-belt/006/implementar_issue/issue-17/13b4719af643747b679e87602ac5ff414b35d716`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`
- `effect_class`: `remote_mutation`
- `state_before`: A publicada na PR #19, não integrada; #17 aberta, v4 Em Execução e autorização humana para integrar A/implementar B.
- `state_after`: PR #19 integrada/issue #16 fechada, B implementada na branch publicada #17 e PR #20 aberta/draft, 175 testes/gates locais e matriz passando; nenhuma integração B.
- `next_transition`: revisar PR #20 -> integração autorizada de B -> implementar C (#18).
- `preconditions`: critérios Item 2, gates reais e staging seletivo para publicar; autorização própria para integrar B; B integrada antes de C.
- `authority`: responsável autorizou merge de A e execução de B; GitHub comprova merge/issue/PR; autoridades locais regem gates.
- `evidence`: PR #19 integrada, merge `13b4719af643747b679e87602ac5ff414b35d716`, issue #16 fechada, issue #17 aberta, PR #20, commit `35c3e003d8bac4723ae75af1fa36f878f3b5022a`, base atualizada e gates/smokes desta task; zero statuses/runs CI observados.
- `acceptance`: escopo B completo, testes/smokes reais, consentimentos preservados e PR rastreável.
- `blockers`: revisão e autorização de integração B pendentes; nenhum bloqueio local de testes/lint/governança e nenhum check remoto disponível na consulta.
- `result`: `executed`
- `next_workflow_recommended`: revisar PR #20 e integrar somente após autorização; depois implementar #18.
- `next_workflow_authorized`: implementar_issue #17, incluindo publicação validada; #18 somente após B integrada.
- `actions_prohibited`: integrar B sem autorização, iniciar C antes de B integrada, encerrar ciclo, descontinuar File2MD, reutilizar consentimento externo de A.
- `rejection_rule`: recusar divergência ou ausência de evidência material/autorização.
- `logical_key`: `utility-belt/006/implementar_issue/issue-17/13b4719af643747b679e87602ac5ff414b35d716`
- `check_before_mutation`: autoridades/templates/plano e issue lidos; branch/task/PR duplicadas não encontradas; merge de A verificado antes de criar branch B.
- `reconcile_existing`: retomar esta unidade canônica sem duplicar artefatos.
- `ambiguous_state`: parar em concorrência/divergência de issue, task, branch, PR ou plano.
