---
name: doc-updater
description: "Atualiza a menor autoridade documental correta a partir de fatos verificados, preservando proveniência e histórico."
---

# Doc Updater

Pode ser usado diretamente para uma atualização pedida pelo responsável ou orquestrado por um workflow. Exige como entrada o fato verificado, sua fonte e o escopo documental autorizado.

1. Classifique o fato pela matriz de autoridade em `.agent/ai_behavior.md`.
2. Verifique a fonte: Git, GitHub, resultado de teste, plano aprovado, ADR ou URL fixada.
3. Edite somente o documento canônico responsável e os índices que necessariamente apontem para ele.
4. Não replique políticas em adapters, workflows, templates, skills ou CI.
5. Preserve datas, links imutáveis, autoria, ciclo de origem e estados históricos.
6. Rode o gate de governança e apresente o diff para revisão.

## Handoff estruturado

Retorne: fonte consultada, autoridade escolhida, arquivos alterados, validações executadas, pendências e qualquer decisão humana ainda necessária.
