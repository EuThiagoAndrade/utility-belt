# Task — Issue #16: Núcleo de conversão Markdown e destino seguro

> **Ciclo:** `006`
> **Estado:** `Em andamento`
> **Tipo:** `feature`
> **Issue:** [#16](https://github.com/EuThiagoAndrade/utility-belt/issues/16)
> **Plano:** `_project/drafts/006_conversao_markdown_nativa/006_plan.md`
> **Branch:** `feature/issue-16`
> **Worktree:** `C:/Programas/utility-belt`
> **PR:** [#19](https://github.com/EuThiagoAndrade/utility-belt/pull/19) — aberta em rascunho
> **Integração:** `Pendente`
> **Início:** 2026-10-12
> **Última atualização:** 2026-10-12
> **handoff_schema_version:** `1`
> **handoff_id:** utility-belt/006/implementar_issue/issue-16/b36d04396ca0bb7af3dab79e5781b092df06ef12

## Objetivo

Implementar a entrega A, Item 1 da v4 aprovada. Solicitação humana atual autoriza implementar #16, #17 e #18 em sequência; merge continua sujeito a autorização própria.

## Escopo autorizado

Núcleo, configuração segura, arquivo/URL, worker isolado, receitas fixadas, aquisição consentida, consentimento externo de áudio e diagnóstico de ZIP parcial. Sem antecipar entregas B/C.

## Execução

- [x] Ler autoridades, workflow, templates e gate; conferir issues abertas e plano aprovado.
- [x] Atualizar referências remotas: HEAD e origin/main = `b36d04396ca0bb7af3dab79e5781b092df06ef12`; nenhuma PR aberta ou branch da issue existente.
- [x] Criar branch canônica; preservar documentos preexistentes não versionados.
- [x] Criar ambiente de desenvolvimento `.venv-cycle-006` com Python 3.13.7 e uv 0.12.13; preservar `.venv` anterior inválida.
- [x] Implementar núcleo/configuração, worker isolado, receitas/constraints, consentimentos, ZIP parcial e fixtures próprias.
- [x] Validar aquisições reais e 33 cenários de integração em Windows/Linux x64, Python 3.11/3.13.
- [x] Executar um smoke externo de áudio e um de URL com consentimentos humanos específicos.
- [x] Concluir suíte completa final e auditoria antes de publicar.
- [x] Publicar PR #19 após gates; anexá-la ao chat e conferir estado remoto.

## Evidências

| Gate | Resultado |
| :-- | :-- |
| Testes | `uv run pytest`: código 0, 138 testes, 138,86 s; `BELT_MARKDOWN_TEST_DATA` aponta para aquisições reais e `PYTEST_ADDOPTS=-p no:cacheprovider`, sem rede externa na suíte |
| Validação | `uv run python scripts/validate_governance.py`: código 0, 31 OK, aviso conhecido 006/007, nenhuma falha; `uv run ruff check`: código 0, sem erros |
| `git diff --check` | Código 0, sem erros; inspeção manual de novos arquivos/staging antes de commit |
| Checks remotos | Consultados no GitHub para `438647eb401e2f37e16fa615e30a3993d50767a8`: zero statuses e zero workflow runs; ausência de CI não é check aprovado |

Commit de implementação validada: `438647eb401e2f37e16fa615e30a3993d50767a8`. PR #19 aberta/draft, `merged=false`, base `main`/`b36d04396ca0bb7af3dab79e5781b092df06ef12`, head `feature/issue-16`, sem conflito observado (`mergeable=true`). Revisão e integração ainda não realizadas. Ajuste posterior desta task/plano registra somente vínculos e estado, sem mudar código, receitas ou fixtures validados.

### Ambiente e smokes reais

- Ferramentas: uv `0.12.13`; MarkItDown `0.1.8`; ExifTool `13.59`; FFmpeg fornecido por `imageio-ffmpeg==0.6.0`. Python do motor não é baixado pelo instalador de produção.
- Matriz: Windows x64 Python `3.13.7`: 33 testes de integração reais no gate completo (resultado final abaixo); Windows x64 `3.11.16`: 26 testes iniciais em 131,45 s e sete adicionais em 48,76 s; Linux x64 `3.11.13`: 33 testes em 66,33 s; Linux x64 `3.13.15`: 33 testes em 78,77 s. Todos com resultados positivos, sem envio externo pela suíte.
- Windows usa `.venv-cycle-006-smoke/markdown/engines/markitdown-0.1.8/py3.11` e `py3.13`; Linux usa `/tmp/belt-smoke/...` em containers descartáveis da imagem `mcr.microsoft.com/devcontainers/python:1-3.11-bullseye`, com checkout montado somente leitura. Python 3.11 de Windows e 3.13 de Linux foram obtidos **somente para desenvolvimento**, em diretórios isolados, sem registro ou mudança de PATH; produção usa `sys.executable` explícito e `--no-python-downloads`.
- Entrada do smoke: `python tests/markdown_smoke.py --data-dir <diretório-isolado> --consent-install`. A flag autoriza apenas aquisições do teste, nunca envio de áudio. Receitas base/PDF/DOCX/PPTX/XLSX/XLS/Outlook/YouTube e audio/FFmpeg foram adquiridas com hashes e revalidadas. Segunda execução reutilizou os ambientes sem novo download.
- Testes de integração: texto/JSON/JSONL/Markdown/CSV/HTML/RSS/IPYNB/EPUB/PDF/DOCX/PPTX/XLSX/XLS/MSG/ZIP/JPEG/PNG/WAV/MP3/M4A/MP4, arquivo sem extensão e extensão desconhecida, ZIP parcial, Wikipedia/Bing por snapshots próprios, isolamento de áudio inclusive em ZIP e ambiente audio previamente instalado, normalização real FFmpeg e conversor YouTube com cliente de legendas mockado. Serviços de legendas e Google não são dependências da suíte automatizada; não há promessa de disponibilidade/qualidade externa.
- Fixtures em `tests/fixtures/markdown/` são sintéticas próprias, aproximadamente 96 KB, com instruções de geração. Nenhum documento pessoal, checkout File2MD ou áudio externo foi versionado.

### Consentimentos específicos e limites observados

O responsável respondeu nesta conversa **“Autorizar este único teste”** para enviar ao Google áudio sintético dizendo “Teste de conversão Markdown do Utility Belt” e **“Usar example.com”** para a conversão de URL. Esses consentimentos não se tornam preferência persistente nem autorizam outro envio.

- WAV gerado localmente com System.Speech: `.venv-cycle-006-smoke/authorized-transcription.wav`, 195.656 bytes. Conversão real retornou código `0` e metadados (PCM mono, 22.050 Hz, 16 bits). Destino: `.venv-cycle-006-smoke/authorized-output/2026-10-12_20-39-40/authorized-transcription.wav.md`.
- Texto reconhecido: `dance to the conversion market doing today`. **Não corresponde à frase em português.** O motor nativo usa a configuração padrão do serviço; esta integração comprova funcionamento/envio consentido, não qualidade linguística. Não foi acrescentada troca de idioma, excluída pelo plano, nem repetido o envio autorizado.
- `https://example.com`: código `0`, conteúdo HTML não vazio, destino `.venv-cycle-006-smoke/authorized-output/2026-10-12_20-40-24/web_content.md`. URL foi consultada somente na operação consentida e a saída não foi versionada.

### Constraints e binários

Geração: `uv pip compile src/utility_belt/markdown_runtime/constraints.in --universal --python-version 3.11 --generate-hashes --output-file src/utility_belt/markdown_runtime/constraints.txt`; cada grupo foi compilado com essa constraint comum, versão Python 3.11, resolução universal e hashes. Entradas por grupo são derivadas de `recipes.toml`. Produção consome `--constraints constraints.txt --require-hashes --requirements <grupo>.txt`, nunca nomes de pacotes de mensagens de exceção ou `latest`.

| Arquivo | SHA-256 |
| :-- | :-- |
| `constraints.txt` | `d21857148ca59bd5698ca61103bb2c04f9c1c2cfb84ada0c7eff4cb5baed9837` |
| `base.txt` | `4c641558710de33b5e59efa995de9a3c0a2bf1b181ec0a882a97e9bc0d3b4310` |
| `pdf.txt` | `fa75c3423955d7f17d88649eda74e0cc93213421a6e1f7c57900c4e994902a33` |
| `docx.txt` | `5495a8b4b4070ec39308a8e74056ce233bc5c0dcc66ba438c82b7799d8e8bbeb` |
| `pptx.txt` | `ede36cf1a1e38cff1a02227fbd6ae452d33fa569e1e59501e284fd8eae6a1f40` |
| `xlsx.txt` | `d5d3ac25f7f7684c6f238d8d704d29e56dbff756c936b8fc7cb02fabd19646ae` |
| `xls.txt` | `534c374a61b605b1b353066691df7f441b93499dda5e42806d4dd6c0f94d1ad4` |
| `outlook.txt` | `6b907e5db92ea47faddb34d434bfe3c4c6d11a7d009cfb5d81e561614cf77fed` |
| `youtube-transcription.txt` | `12b886577d24194516529e0c4118ea0d65d40b3321da0b21ac0e32d9830ef5f6` |
| `audio-transcription.txt` | `3e0a3c8cd253a35a4c0a4fcd864365a6768735447ef32614d720473387181838` |
| `ffmpeg.txt` | `35727741eb4451e565a88f1b4630b90f71ae9bc4dacd186cc703bbcfee9531f7` |

ExifTool adquirido das distribuições oficiais SourceForge; os hashes publicados foram conferidos durante aquisição, extração portátil e execução `-ver` nas duas plataformas:

- Windows: [exiftool-13.59_64.zip](https://sourceforge.net/projects/exiftool/files/exiftool-13.59_64.zip/download), SHA-256 `44b512b25af500724ba579d0a53c8fc5851628b692dd5e5d94ae4a15c2cba9ec`.
- Linux: [Image-ExifTool-13.59.tar.gz](https://sourceforge.net/projects/exiftool/files/Image-ExifTool-13.59.tar.gz/download), SHA-256 `668ea3acececb7235fbd0f4900e72d5f12c9b07e5c778fd36cb1e9b5828fd65a`. Perl já disponível no container; ausência de Perl testada sem aquisição de pacote do sistema.

## Decisões incidentais e desvios

Ambiente de desenvolvimento separado evita sobrescrever `.venv` preexistente; gates usam `UV_PROJECT_ENVIRONMENT=.venv-cycle-006`. Dependências de geração de fixtures foram instaladas apenas no ambiente de desenvolvimento; não são dependências iniciais do Belt. Houve exatamente uma operação externa de áudio consentida, descrita acima.

`requests>=2.32.0` é a dependência leve para HTTP e aquisição portátil com validação TLS; watchdog/pyperclip fixados conforme P04, sem motor/extras no ambiente inicial. `uv.lock` acrescenta somente essas dependências e transitivas; comparação TOML confirmou nenhuma versão preexistente alterada. Não se altera PATH, Python global ou configurações do usuário durante a aquisição do motor.

ZIP com PDF corrompido revelou que o motor podia retornar texto pelo fallback genérico após falha de PDF; instrumentação registra também tentativas nativas de membros e reporta parcialidade/código 1. YAML/front matter e conteúdo retornado pelo motor são publicados sem pós-processamento.

O cache preexistente de pytest não permite escrita nesta máquina. Os gates finais usam `PYTEST_ADDOPTS=-p no:cacheprovider`, preservando o cache alheio e executando os mesmos testes. Não foi removido nenhum artefato preexistente.

No staging, Git classificou o PDF sintético como texto e sinalizou espaços de sintaxe PDF. `.gitattributes` limita tratamento binário aos PDFs destas fixtures, preservando offsets e bytes diante de `core.autocrlf`; não se modifica o PDF nem a política de outros arquivos.

Plano e ideação aprovados, antes não versionados, serão incluídos integralmente como contexto necessário de rastreabilidade da entrega, com somente a transição para execução e vínculos atualizados. Isso evita PR sem plano acessível; não muda o escopo técnico aprovado nem cria um segundo plano.

## Resultado

Entrega A implementada, validada e publicada na PR #19 em rascunho. Aguardando revisão e autorização de integração; início de B depende de A integrada. Nenhum código de B/C foi iniciado, nenhuma issue foi fechada e o ciclo permanece em execução.

### Handoff de execução

- `handoff_schema_version`: `1`
- `handoff_id`: `utility-belt/006/implementar_issue/issue-16/b36d04396ca0bb7af3dab79e5781b092df06ef12`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`
- `effect_class`: `remote_mutation`
- `state_before`: plano v4 aprovado; issues #16/#17/#18 abertas; main atualizada; documentos preexistentes locais; sem task/branch/PR de #16.
- `state_after`: #16 implementada na branch canônica publicada, PR #19 aberta/draft, 138 testes e gates locais passando, quatro combinações da matriz e smokes específicos registrados; integração não executada.
- `next_transition`: revisão da PR #19 -> integração autorizada -> implementação de #17.
- `preconditions`: cumprir Item 1 e gates A antes da publicação; integrar A antes de B.
- `authority`: solicitação humana atual autoriza implementação/publicação pelo workflow; responsável autoriza integração; GitHub comprova estados remotos.
- `evidence`: issue #16, PR #19, commit `438647eb401e2f37e16fa615e30a3993d50767a8`, plano v4, base atualizada, staging seletivo, gates, hashes, matriz e smokes registrados nesta task; GitHub observou PR não integrada e nenhum status/run de CI.
- `acceptance`: Item 1 completo, gates reais e PR rastreável, sem expansão de escopo.
- `blockers`: revisão e autorização de integração ausentes; nenhum status/run de CI disponível na consulta. Nenhum bloqueio local de testes/lint/governança.
- `result`: `executed`
- `next_workflow_recommended`: revisar PR #19; integrar somente após autorização, então implementar #17.
- `next_workflow_authorized`: implementar_issue para #16; #17/#18 somente após suas dependências integradas.
- `actions_prohibited`: merge, iniciar B antes de A integrada, encerrar ciclo, descontinuar File2MD, envio de áudio sem consentimento próprio.
- `rejection_rule`: recusar inconsistências ou ausência de evidências materiais/autorizações.
- `logical_key`: `utility-belt/006/implementar_issue/issue-16/b36d04396ca0bb7af3dab79e5781b092df06ef12`
- `check_before_mutation`: issues e PRs consultadas no conector; branches/status/base locais e remotos conferidos antes da criação.
- `reconcile_existing`: retomar somente esta branch/task sem duplicações.
- `ambiguous_state`: parar em divergência de issue, task, branch, PR ou plano aprovado.
