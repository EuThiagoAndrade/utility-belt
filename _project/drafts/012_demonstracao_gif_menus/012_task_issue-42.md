# Task — Issue #42: Demonstração dos menus em GIF

> **Ciclo:** `012`
> **Estado:** `Em andamento`
> **Tipo:** `chore`
> **Issue:** `#42`
> **Plano:** `_project/drafts/012_demonstracao_gif_menus/012_plan.md`
> **Branch:** `chore/issue-42`
> **Worktree:** `C:/Programas/utility-belt`
> **PR:** —
> **Integração:** `Pendente`
> **Início:** 2026-10-21
> **Última atualização:** 2026-10-21
> **handoff_schema_version:** `1`
> **handoff_id:** `EuThiagoAndrade/utility-belt+012+implementar_issue+42-demonstracao-gif-menus+98e02a2`

## Objetivo

Entregar GIF de navegação pelos cinco submenus reais, gerador reproduzível e referência no README, sem executar operações do programa.

## Escopo autorizado

Plano v1 aprovado após parecer `APTO COM RESSALVAS`, incluindo R1–R3. Autorização humana preservada: “vamos implementar isso”, “Pode revisar.” e “Aprovado” após apresentação do parecer. Uma issue e uma PR de entrega; merge e closure não autorizados automaticamente.

## Execução

- [x] Aceitar handoff da revisão e registrar aprovação humana pós-revisão.
- [x] Buscar duplicatas e criar [issue #42](https://github.com/EuThiagoAndrade/utility-belt/issues/42) com o template chore; consultar novamente e confirmar estado aberto, payload e label.
- [x] Publicar documentação aprovada em [PR #43](https://github.com/EuThiagoAndrade/utility-belt/pull/43), draft, sem merge.
- [x] Criar branch da issue a partir de `98e02a2`, com base atualizada para `main` `69c8b78` antes do commit documental.
- [x] Implementar captura com isolamento e validação de estados, incluindo falhas provocadas.
- [x] Gerar e inspecionar GIF e incluir no README.
- [ ] Executar gates, registrar propriedades e versões e publicar PR de entrega.

## Evidências

| Gate | Resultado |
| :-- | :-- |
| Testes | `uv run pytest -q`: 253 passed, 36 skipped, 1 warning, 51.35 s |
| Validação | Validator: 43 OK, 1 aviso de numeração conhecido, 0 falhas; ruff: All checks passed |
| `git diff --check` | Passou; staging seletivo será conferido antes do commit |
| Checks remotos | Pendente |

### Mídia e reprodução

- Comando executado: `uv run --with pyte --with pillow python scripts/generate_demo.py`.
- Para repetir com as versões opcionais usadas: `uv run --with pyte==0.8.2 --with pillow==13.0.0 python scripts/generate_demo.py`.
- Versões: pyte 0.8.2; Pillow 13.0.0; Questionary 2.1.1; prompt_toolkit 3.0.53; fonte Consolas, 20 px.
- GIF: `docs/assets/demo.gif`, 33.500 ms, 1104 × 776 pixels, 431.643 bytes, 46 quadros codificados e loop infinito.
- Estados validados: main → restic → main → docker → main → markdown → main → dev → main → system → main. Cada submenu permanece inicialmente por 3 segundos, além da navegação até Voltar.
- Tentativas bloqueadas na captura válida: zero. Apenas a disponibilidade de Restic/Docker foi adaptada no harness; nenhuma consulta/inicialização de serviço ou operação de módulo ocorreu.
- `--self-check` passou: tentativa de operação com exceção absorvida ainda invalida a captura; timeout finito; controladores encerrados; restauração de adaptações; GIF inválido não substitui destino anterior nem deixa arquivo parcial.
- Inspeção visual: seis quadros principais extraídos do GIF e examinados, incluindo texto, cores, destaque e rodapés. A animação foi aberta em prévia HTML local e observada no navegador, confirmando mudança de seleção sem quadros acumulados ou cortes. Legibilidade em resolução original conferida; README oferece link para tamanho original em telas estreitas.
- Prévia e capturas auxiliares ficaram em diretório temporário, fora do staging. Nenhuma alteração em `src/`, `pyproject.toml` ou `uv.lock`.
- Aviso do pytest: acesso negado ao cache `.pytest_cache/v/cache/nodeids`; testes sem falha, sem alteração de permissões/limpeza. Aviso do validator: reserva ativa de 012 com próximo disponível 013, já explicado no parecer.

## Decisões incidentais e desvios

- A PR de implementação terá como base `chore/cycle-012-plan` enquanto a PR documental #43 aguarda integração humana. Isso mantém o diff da entrega separado, sem merge automático e sem misturar plano e implementação na mesma PR. Após integração de #43, a entrega poderá ser redirecionada à main.
- `main` avançou apenas com remoção de badge no README; alteração preservada. Nenhum desvio material do escopo.
- O workflow de implementação, template de task, template de PR, autoridades canônicas, lições e skill local governance-check foram lidos no ponto de uso.

## Resultado

Implementação e verificações locais concluídas. GIF e README prontos; publicação da PR de entrega em andamento. Integração continua pendente de autorização humana.

### Handoff de criação da issue (aceito)

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+012+criar_issues+chore-demonstracao-gif-menus+5b0cb559/v1`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision` = `EuThiagoAndrade/utility-belt + 012 + criar_issues + chore-demonstracao-gif-menus + 5b0cb559/v1`.
- `effect_class`: `remote_mutation`
- `state_before`: plano revisado e aprovado, sem issue para a chave lógica; busca retornou zero duplicatas.
- `state_after`: issue #42 aberta com checklist dos itens 1–2 e R1–R3; número, corpo e label chore confirmados em nova consulta ao GitHub.
- `next_transition`: `issue -> implementação autorizada`.
- `preconditions`: plano aprovado, issue aberta, autorização humana de execução e base atualizada.
- `authority`: responsável humano, mensagens acima; GitHub confirma estado da issue.
- `evidence`: URL #42, plano v1, resposta de criação e fetch da issue; PR documental #43.
- `acceptance`: uma issue canônica para a chave, escopo aderente e preflight da implementação satisfeito; handoff aceito.
- `blockers`: nenhum.
- `result`: `executed`
- `next_workflow_recommended`: `implementar_issue`.
- `next_workflow_authorized`: `implementar_issue`, pelo pedido humano de execução e aprovação pós-revisão; não inclui merge.
- `actions_prohibited`: ampliar escopo ou integrar automaticamente.
- `rejection_rule`: recusar divergência entre plano aprovado, issue ou autorização humana.
- `logical_key`: `EuThiagoAndrade/utility-belt+012+chore+demonstracao-gif-menus+5b0cb559/v1`.
- `check_before_mutation`: buscas de issue e PR por ciclo/GIF sem duplicatas.
- `reconcile_existing`: reutilizar #42 e não duplicar issue.
- `ambiguous_state`: interromper se outra issue concorrer pela mesma entrega.

### Handoff de execução

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+012+implementar_issue+42-demonstracao-gif-menus+98e02a2`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision` = `EuThiagoAndrade/utility-belt + 012 + implementar_issue + 42-demonstracao-gif-menus + 98e02a2`.
- `effect_class`: `local_mutation`
- `state_before`: issue #42 aberta, plano aprovado e PR documental #43 publicada; nenhuma branch/task/PR da entrega anterior.
- `state_after`: GIF, gerador e README implementados e validados na branch `chore/issue-42`; publicação da PR em andamento.
- `next_transition`: `PR -> revisão/checks -> integração autorizada`.
- `preconditions`: critérios do plano e R1–R3 atendidos, gates aprovados e diff cirúrgico.
- `authority`: agente executa escopo autorizado; humano decide integração posterior.
- `evidence`: esta task, GIF, gerador, README, saída de geração, self-check e cinco gates registrados acima.
- `acceptance`: GIF válido, README e gerador revisáveis, rastreabilidade e checks comprovados.
- `blockers`: publicação e checks remotos pendentes; integração exige decisão humana própria.
- `result`: `executed`
- `next_workflow_recommended`: publicar PR validada, acompanhar checks e apresentar entrega para revisão.
- `next_workflow_authorized`: implementação e publicação de PR após gates; sem merge.
- `actions_prohibited`: merge, closure, alteração de produto ou operações dos módulos.
- `rejection_rule`: recusar resultado sem GIF válido ou evidências dos controles/gates.
- `logical_key`: `EuThiagoAndrade/utility-belt+012+implementar_issue+42-demonstracao-gif-menus+98e02a2`.
- `check_before_mutation`: issue consultada novamente, branch inexistente e nenhuma PR duplicada identificada.
- `reconcile_existing`: retomar esta branch/task e uma única PR da issue.
- `ambiguous_state`: interromper em divergência entre issue, plano, branch ou PR.
