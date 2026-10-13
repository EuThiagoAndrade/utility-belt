# Plano de Implementação — Interface CLI e versionamento automático

> **Ciclo:** `007`
> **Status:** `Em Execução`
> **Versão:** `v1`
> **Data de criação:** 2026-10-13
> **Última atualização:** 2026-10-13
> **Tipo:** `feature`
> **Prioridade:** `P2`
> **Revisão formal:** `Concluída`
> **Veredito da revisão:** `APTO COM RESSALVAS`
> **Aprovação humana pós-revisão:** `Pendente`

## Objetivo

Entregar o conjunto completo discutido com o responsável: visual principal inspirado no conceito aprovado, mensagens claras, submenu Sistema e incremento automático da versão após integração de features/fixes. Final desta execução: PR pronta para avaliação, sem merge.

## Contexto e baseline

`main`/`origin/main`: `e9f375fd2f11259fa5b7b9bd981363d91e7fcd5b`. Git inicialmente limpo, sem tags e sem workflows. Interface atual usa Questionary/Typer; versões repetidas; estados Markdown apresentados em inglês. Ideação: `_project/ideations/007_interface_cli_e_versionamento.md`.

## Escopo

### Dentro do escopo

Cabeçalhos e navegação compactos, cores cyan/âmbar com fallback, descrições das ferramentas, seleção destacada, instruções consistentes; submenu Sistema com diagnóstico, informações e sobre; apresentação de mensagens e resultados, separação entre saída/perguntas, preparação/conversão visíveis; versão canônica no pacote consumida pelo build e UI; CI e release automático com changelog e tag.

### Fora do escopo

Novo framework TUI, IA, comandos em linguagem natural, motores Markdown, novas capacidades Docker/Restic, alteração permanente da governança, instalação global, merge, deploy/PyPI e release remoto durante esta execução.

## Decisões e autoridades

- Autoridades: `.agent/ai_behavior.md`, `_project/README.md`, `_project/cycles.md`.
- Templates lidos: ideação, plano, task, Issue Form feature e PR; workflows idear, rascunhar, revisar, criar issues e implementar.
- Exceção pontual solicitada pelo responsável em 2026-10-13: "todo o workflow, autoaprovado, até ... a PR"; escopo confirmado como "Conjunto completo". A instrução humana mais recente prevalece conforme ai_behavior. Ela autoriza ideação, rascunho, revisão, prosseguimento após parecer apto, issue, implementação, validação e publicação da PR. Não será registrada uma aprovação humana posterior fictícia; a exceção será registrada separadamente após o parecer. Não se altera a política permanente.
- Uma issue e uma PR para este pacote coerente de experiência e identidade de versão. Itens descritos separadamente no aceite; não publicar PRs documentais intermediárias nem integrar automaticamente.
- Versão fonte: `src/utility_belt/__init__.py`; Hatchling usa versão dinâmica desse arquivo. Bot incrementa feat -> minor, fix -> patch; breaking -> minor em 0.x e major em >=1.x. Docs/chore não incrementam por si. Features e fixes na mesma janela usam o maior incremento, uma vez.
- Release usa GitHub Actions após push em main, checks e build; commit de versão/changelog e tag enviados atomicamente sem force. Baseline histórico fixado em e9f375f para o primeiro release; depois tags delimitam mudanças. Reexecução reconcilia release existente, sem tags duplicadas. Escrita remota limitada a versão, changelog, tag e GitHub Release. Falha de proteção ou corrida não autoriza bypass.

## Estratégia de testes

Gates: `uv run python scripts/validate_governance.py`, `uv run ruff check`, `uv run pytest`, `git diff --check` e status/staging seletivo. Ambiente separado `.venv-cycle007` por venv preexistente inválida; pytest/ruff por uv --with quando necessário. Testar menu Sistema e retornos, TTY/non-interactive, terminais estreitos e sem cor, traduções/resultados, limites entre prompts e saída, consentimentos e códigos de saída. Testar cálculo, baseline, tags, changelog e retries de release em repositórios temporários, sem publicação. Verificar wheel/sdist e versão instalada fora do checkout. Smoke de terminal real/simulado sem executar operações destrutivas ou downloads de conversores. CI Windows/Linux; integrações externas mantêm requisitos explícitos.

## Itens de implementação

### Item 1 — Interface e navegação

**Contexto:** conceito aprovado e menus existentes.

**Ação técnica:** refinamento em screen/menu/submenus usando dependências atuais; retirar banner/moldura grandes; textos e cores consistentes; agrupar consultas em Sistema.

**Critérios de aceite:**

- [x] Menu principal: Restic, Docker, Markdown, Sistema e Sair, com descrições e seleção clara.
- [x] Sistema oferece diagnóstico, informações do computador, sobre e voltar; comandos CLI preservados.
- [x] Cabeçalhos cabem em terminais estreitos; sem ANSI em saída redirecionada/NO_COLOR.
- [x] Navegação, cancelamento e retorno mantêm resultado visível até confirmação.

### Item 2 — Mensagens e acompanhamento

**Contexto:** mix de prompts/saídas e estados internos Markdown.

**Ação técnica:** helpers pequenos de mensagem, apresentação de resultado em português, resumos de lote e confirmação em bloco; etapas de conversão/preparação com saída somente em contextos de UI/CLI, sem alterar motor.

**Critérios de aceite:**

- [x] Mensagem/prompt sempre começa numa linha nova; detalhes e pergunta separados.
- [x] Sucesso, erro, aviso e cancelamento identificáveis sem depender de cor.
- [x] Destino e resumo legíveis; sem estados success/failed na apresentação.
- [x] Automação não ganha prompts; consentimentos e exit codes preservados.

### Item 3 — Versão única e release

**Contexto:** 0.1.0 literal em diferentes componentes, sem pipeline de release.

**Ação técnica:** metadados dinâmicos, versão compartilhada e script testado de release convencional; CI e workflow após integração.

**Critérios de aceite:**

- [x] Banner, Sobre, --version e metadados instalados concordam com a fonte única.
- [x] Feat/fix/breaking e docs/chore seguem política; histórico anterior ao baseline não gera incremento.
- [x] Release só publica após checks e build; retries e concorrência não duplicam versão/tag; sem force.
- [x] README explica convenção, atualização da instalação, permissão de bot e limitações.

## Arquivos afetados

`src/utility_belt/ui/*`, `menu.py`, `adapters/markdown.py`, `markdown.py` (apenas apresentação dos consentimentos/etapas), `runner.py` (limite de linha), `__init__.py`, `pyproject.toml`, testes correspondentes, `scripts/release.py`, `.github/workflows/*`, README, changelog e artefatos do ciclo. Lockfile somente se necessário ao build dinâmico.

## Decomposição em issues e PRs

Uma feature issue com os três itens e uma PR de implementação contendo rastreabilidade documental. Release bot futuro produz apenas commit mecânico de versão/changelog após integração autorizada da feature.

## Dependências e blockers

GitHub acessível com permissão de escrita e Actions habilitado. Sem blockers de planejamento. Execução remota de release será verificável somente após merge autorizado; não simular esse resultado.

## Riscos, suposições e rollback

Layout pode variar entre fontes/terminais; usar texto simples e largura medida. Evitar animação quando houver pergunta ativa. Proteger cancelamento e automações com testes. Bot pode ser impedido por proteção da main; reportar falha, nunca bypass. Rollback via revert da PR e desativação do workflow, preservando tags já publicadas. Preview é direção visual, não promessa de pixels idênticos.

## Sequência recomendada

Ideação -> rascunho -> revisão formal e correções -> registrar exceção humana de prosseguimento -> issue -> branch/task -> implementação -> checks/revisão -> PR -> aguardar aprovação humana e merge.

## Referências

- Ideação 007 e conversa de 2026-10-13.
- https://hatch.pypa.io/latest/version/
- https://semver.org/lang/pt-BR/
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow

## Rastreabilidade

| Campo | Valor |
| :-- | :-- |
| Issue(s) | [#23](https://github.com/EuThiagoAndrade/utility-belt/issues/23) |
| PR(s) | [#24](https://github.com/EuThiagoAndrade/utility-belt/pull/24), integração pendente |
| Branch(es) | `feature/issue-23` |
| `handoff_schema_version` | `1` |
| `handoff_id` | EuThiagoAndrade/utility-belt+007+rascunhar_plano+interface-cli-versionamento+e9f375f |
| Destino após conclusão | `_project/executed/007_interface_cli_e_versionamento/007_plan.md` |

## Handoff de saída

Histórico do rascunho, preservado para evidenciar a sequência. Handoffs de revisão/autoridade/issue em `007_handoff_workflow.md`; handoff operacional corrente em `007_task_issue-23.md`.

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+007+rascunhar_plano+interface-cli-versionamento+e9f375f`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`
- `effect_class`: `local_mutation`
- `state_before`: ideação 007 aceita explicitamente, sem implementação.
- `state_after`: rascunho v1 criado.
- `next_transition`: rascunho -> revisão formal.
- `preconditions`: ler plano e verificar escopo, critérios e templates.
- `authority`: autorização humana do workflow completo nesta conversa.
- `evidence`: baseline, ideação, templates/workflows e inspeção de código.
- `acceptance`: completude do plano e revisão formal sem bloqueios.
- `blockers`: nenhum para revisar.
- `result`: `executed`
- `next_workflow_recommended`: `revisar_plano`
- `next_workflow_authorized`: `revisar_plano`, autorizado pelo responsável.
- `actions_prohibited`: implementar antes do parecer apto/issue; merge; release nesta sessão.
- `rejection_rule`: recusar handoff sem escopo, evidência ou autoridade.
- `logical_key`: `EuThiagoAndrade/utility-belt+007+rascunhar_plano+interface-cli-versionamento+e9f375f`
- `check_before_mutation`: nenhum plano/issue/PR 007 existente.
- `reconcile_existing`: este é o único plano canônico do ciclo.
- `ambiguous_state`: parar antes de efeitos se identidade ou escopo conflitarem.

## Revisão crítica

- **Data:** 2026-10-13
- **Versão revisada:** v1, depois de entrar em Em Revisão.
- **Veredito:** `APTO COM RESSALVAS`
- **Bloqueios remanescentes:** nenhum para entrega até a PR.
- **Aprovação humana pós-revisão:** `Pendente`
- **Correções materiais:** decisões sobre baseline de release, push atômico, idempotência, CI e separação de consentimentos já explicitadas no plano antes da implementação.
- **Ressalvas:** pixel fidelity depende do terminal; release remoto somente verificável após merge. Validador passou com 33 OK/0 falhas e um aviso: próximo ciclo 008 versus 007 derivado do último concluído; reserva ativa 007 explica o aviso. Proteção da main não consultável (API 403 por plano do GitHub); não assumir nem contornar proteção. Ambiente preexistente inválido substituído para checks por ambiente isolado.

### Parecer e aceite da revisão

**Autorização excepcional de prosseguimento:** registrada após o parecer em 2026-10-13. Status Aprovado decorre da instrução humana explícita nesta conversa para workflow autoaprovado até a PR, não de uma aprovação humana posterior. O campo canônico de aprovação humana pós-revisão permanece Pendente por precisão histórica; somente este gate foi dispensado pelo responsável neste ciclo. Ideação -> rascunho -> revisão formal ocorreram separadamente. Preflight de criar_issues aceita escopo/template/parecer e esta autoridade excepcional; autoriza somente a issue planejada e implementação subsequente até a PR, sem merge.

Todas as seções do template presentes; objetivo e não-objetivos delimitados; três itens com aceite verificável; issue/PR única justificada; consentimentos e códigos preservados; dependências existentes suficientes. Gate manual visual e testes de publicação em repositórios temporários previstos. Riscos remanescentes não impedem implementar e submeter uma PR, mas impedem declarar release remoto executado nesta sessão.

Handoff de revisão: `EuThiagoAndrade/utility-belt+007+revisar_plano+interface-cli-versionamento+e9f375f`; identidade `repository + cycle + workflow + logical_target + source_revision`; efeito `local_mutation`; estado Em Revisão -> Em Revisão com parecer apto; resultado `executed`; evidências: checklist acima, validator e plano v1. Aceite explícito: plano íntegro e sem bloqueios para escopo autorizado. Próxima transição depende do registro da exceção humana já solicitada; não há aprovação humana posterior fabricada. Handoffs completos complementares em `007_handoff_workflow.md`. Chave lógica igual ao handoff; reexecução reconcilia este parecer; estado ambíguo impede mutação. Merge e release nesta sessão proibidos.

## Pós-mortem

- **Data de conclusão:** —
- **Desvios:** —
- **Lições comprovadas:** —
