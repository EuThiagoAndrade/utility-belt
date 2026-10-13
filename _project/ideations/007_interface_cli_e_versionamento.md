# Ideação — 007: Interface CLI e versionamento automático

> **Ciclo:** `007`
> **Estado:** `Ideação`
> **Criado em:** 2026-10-13
> **Última atualização:** 2026-10-13

## Problema

Mensagens pouco legíveis, avisos próximos dos prompts, estados técnicos em inglês e uma interface com excesso de molduras. Diagnóstico e informações do computador ocupam entradas separadas no menu principal. A versão continua em 0.1.0 apesar das entregas e é repetida no pacote, metadados e banners.

## Contexto e evidências

Baseline `e9f375fd2f11259fa5b7b9bd981363d91e7fcd5b`, igual a origin/main. Inspeção de `menu.py`, `ui/screen.py`, `ui/markdown_menu.py`, `adapters/markdown.py`, `markdown.py`, `runner.py` e `pyproject.toml`. Nenhuma tag ou workflow de release encontrado. A sobreposição relatada pelo responsável ainda não foi reproduzida interativamente.

O responsável aprovou nesta conversa a direção visual de uma imagem conceitual: fundo escuro, tipografia monoespaçada, título compacto com cinto textual, cyan/âmbar, descrições de ferramentas, seleção destacada e rodapé de navegação. Referência de preview: `C:/Users/thiag/.codex/generated_images/01a135a4-130f-7a61-a294-0748ccc905d2/exec-1605bcec-1842-4342-bad3-d9f03d13b695.png`. A imagem não é uma especificação de pixels ou um novo framework gráfico.

## Resultado desejado

Interface principal próxima do conceito e submenus consistentes, mensagens com resultado e próxima ação claros, diagnóstico/informações/sobre agrupados em Sistema e versão única com incremento automático depois de integrar código validado.

## Hipóteses

Questionary e prompt_toolkit existentes bastam para o visual. Limites de linha, saída de subprocessos e confirmações precisam de separação explícita. Commits convencionais existentes permitem classificar feat/fix sem nova dependência de release.

## Alternativas

1. Manter banner grande e apenas mudar textos: não atende à direção aprovada.
2. Migrar para aplicação de tela inteira: complexidade desnecessária.
3. Refinar a TUI atual e automatizar o release: alternativa escolhida.

## Riscos e restrições

Preservar comandos diretos, códigos de saída, consentimentos de instalação/transcrição e ausência de prompts em automação. Terminais estreitos e sem cor devem permanecer legíveis. Release automático precisa de contents:write e possibilidade de push sem força; proteção da main não será contornada. Não fazer merge desta entrega nem disparar release antes do OK humano.

## Perguntas em aberto

Escopo confirmado pelo responsável: conjunto completo. Fidelidade visual será limitada às capacidades de um terminal de texto. Revisão da PR e integração continuam pendentes.

## Fora do escopo

Agente de IA, entrada em linguagem natural, novas ferramentas, alterações de motores, migração de configurações e mudança permanente da governança.

## Critérios para iniciar o planejamento

Contexto, direção visual e conjunto completo autorizados. Registrar exceção humana ao gate de aprovação pós-revisão somente neste ciclo, mantendo a revisão formal e os checks.

## Handoff de saída

- `handoff_schema_version`: `1`
- `handoff_id`: `EuThiagoAndrade/utility-belt+007+idear+interface-cli-versionamento+e9f375f`
- `identity_source`: `repository + cycle + workflow + logical_target + source_revision`
- `effect_class`: `local_mutation`
- `state_before`: ciclo 007 livre; contexto humano identificado.
- `state_after`: ideação registrada; sem implementação.
- `next_transition`: ideação -> rascunho.
- `preconditions`: escopo e autorização explícitos; templates e autoridades lidos.
- `authority`: responsável, conversa de 2026-10-13, pedido de workflow autoaprovado até a PR e resposta Conjunto completo.
- `evidence`: baseline, inspeção de arquivos e referência visual acima.
- `acceptance`: problema, alternativas, riscos e restrições identificados.
- `blockers`: nenhum para rascunhar.
- `result`: `executed`
- `next_workflow_recommended`: `rascunhar_plano`
- `next_workflow_authorized`: `rascunhar_plano`, pela autorização explícita da conversa.
- `actions_prohibited`: merge, release remoto nesta sessão, ampliar escopo ou eliminar a revisão formal.
- `rejection_rule`: recusar identidade, escopo ou evidência incompatíveis.
- `logical_key`: `EuThiagoAndrade/utility-belt+007+idear+interface-cli-versionamento+e9f375f`
- `check_before_mutation`: ciclo 007 e artefatos ausentes; Git limpo; sem issue/PR correspondente.
- `reconcile_existing`: retomar este artefato sem duplicar ciclo.
- `ambiguous_state`: parar diante de conflitos materiais.
