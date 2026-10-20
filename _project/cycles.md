# Registro de ciclos

> **Próximo ciclo:** `010`
> **Última atualização:** 2026-10-20

| Ciclo | Assunto | Estado | Ideação | Plano | Issues | Encerramento |
| :---- | :------ | :----- | :------ | :---- | :----- | :----------- |
| `000` | Fundação CLI e Distribuição | `Concluído` | — (bootstrap do projeto) | `_project/executed/000_fundacao_cli_distribuicao/000_plan.md` | — | Commit `8d8a028` |
| `001` | Menus Interativos com Questionary | `Concluído` | — | `_project/executed/001_menus_interativos/001_plan.md` | — | [PR #3](https://github.com/EuThiagoAndrade/utility-belt/pull/3) — integrada em `f613ae8` |
| `002` | Bootstrap da Governança Canônica | `Concluído` | — | `_project/executed/002_bootstrap_governanca_canonica/002_plan.md` | — | [PR #4](https://github.com/EuThiagoAndrade/utility-belt/pull/4) — integrada em `2e201e3` |
| `003` | Atualização do README com a CLI Real | `Concluído` | — | `_project/executed/003_atualizacao_readme/003_plan.md` | [#5](https://github.com/EuThiagoAndrade/utility-belt/issues/5) | [PR #7](https://github.com/EuThiagoAndrade/utility-belt/pull/7) — integrada em `26f4fa1` |
| `004` | Interface Retrô MS-DOS e Identidade Visual | `Concluído` | `_project/ideations/004_interface_retro_e_telas_msdos.md` | `_project/executed/004_interface_retro_e_telas_msdos/004_plan.md` | [#8](https://github.com/EuThiagoAndrade/utility-belt/issues/8), [#9](https://github.com/EuThiagoAndrade/utility-belt/issues/9) | [PR #12](https://github.com/EuThiagoAndrade/utility-belt/pull/12) |
| `005` | Ajuste Visual do Banner Retrô e Cinto Utilitário | `Concluído` | `_project/ideations/005_ajuste_visual_banner_retro.md` | `_project/executed/005_ajuste_visual_banner_retro/005_plan.md` | [#13](https://github.com/EuThiagoAndrade/utility-belt/issues/13) | [PR #14](https://github.com/EuThiagoAndrade/utility-belt/pull/14) — integrada em `ccf07b4` |
| `006` | Conversão Markdown Nativa no Utility Belt | `Concluído` | `_project/ideations/006_conversao_markdown_nativa.md` | `_project/executed/006_conversao_markdown_nativa/006_plan.md` | [#16](https://github.com/EuThiagoAndrade/utility-belt/issues/16), [#17](https://github.com/EuThiagoAndrade/utility-belt/issues/17), [#18](https://github.com/EuThiagoAndrade/utility-belt/issues/18) | [PR #22](https://github.com/EuThiagoAndrade/utility-belt/pull/22) — conclusão efetiva após integração verificável |
| `007` | Interface CLI e Versionamento Automático | `Concluído` | `_project/ideations/007_interface_cli_e_versionamento.md` | `_project/executed/007_interface_cli_e_versionamento/007_plan.md` | [#23](https://github.com/EuThiagoAndrade/utility-belt/issues/23) | [PR #25](https://github.com/EuThiagoAndrade/utility-belt/pull/25) — efetivo após integração verificável |
| `008` | Validação Prévia de Dependências Externas | `Concluído` | `_project/ideations/008_validacao_preflight_dependencias.md` | `_project/executed/008_validacao_preflight_dependencias/008_plan.md` | [#26](https://github.com/EuThiagoAndrade/utility-belt/issues/26) | [PR #27](https://github.com/EuThiagoAndrade/utility-belt/pull/27) — integrada em `b99d47b`; release v0.3.0 |
| `009` | Ferramentas Dev: Janitor e Git-Tidy | `Concluído` | `_project/ideations/009_ferramentas_dev_janitor_git_tidy.md` | `_project/executed/009_ferramentas_dev_janitor_git_tidy/009_plan.md` | [#29](https://github.com/EuThiagoAndrade/utility-belt/issues/29) | [PR #30](https://github.com/EuThiagoAndrade/utility-belt/pull/30) — integrada em `f7d5e11`; release v0.4.0 |
| `010` | Compatibilidade e Padronização Visual de Menus | `Planejamento` | `_project/ideations/010_correcoes_e_padronizacao_menus.md` | `_project/drafts/010_correcoes_e_padronizacao_menus/010_plan.md` | — | — |

O ciclo `010` trata da correção de incompatibilidade de parâmetros entre `menu_options()` e `questionary.checkbox`, bem como da padronização de linha separadora (`menu_separator()`) antes da opção `[0]` nos submenus de Markdown e Desenvolvimento.

O ciclo `009` implementa as ferramentas de desenvolvimento (`belt dev`), reunindo o faxineiro de caches (`janitor`) e o higienizador de branches locais e remotas (`git-tidy`), integrado na [PR #30](https://github.com/EuThiagoAndrade/utility-belt/pull/30) após autorização do responsável e release automática v0.4.0 publicada em `d2d0c50`. Encerramento Concluído nesta branch é proposta, efetiva após merge da PR documental. Próximo ciclo 010 preservado.

O ciclo `008` implementa a validação prévia de dependências externas (preflight guard) e onboarding assistido para Restic e Docker, integrado na [PR #27](https://github.com/EuThiagoAndrade/utility-belt/pull/27) após autorização do responsável e release automática v0.3.0 publicada em `bdcbd9e`. Encerramento Concluído nesta branch é proposta, efetiva após merge da PR documental. Próximo ciclo 009 preservado.

O ciclo `007` entrega o conjunto completo autorizado em 2026-10-13 na [PR #24](https://github.com/EuThiagoAndrade/utility-belt/pull/24), com workflow autoaprovado até a PR por exceção pontual registrada no plano; merge e integração posteriormente autorizados pelo responsável. PR #24 integrada em 328e515 após autorização humana; release automática v0.2.0 publicada em 74e772f. Encerramento Concluído nesta branch é proposta, efetiva após merge da PR documental. Próximo ciclo 008 preservado.

O ciclo `000` não possui ideação separada, correspondendo ao bootstrap e fundação técnica do Utility Belt.
O ciclo `001` originou-se do refinamento interativo de experiência de usuário e foi concluído na PR #3.
O ciclo `002` estabeleceu o modelo de governança canônica agnóstica, adaptação de agentes e gates automatizados em Python.
O ciclo `003` atualiza o README para refletir a interface real, comandos de adaptadores, configuração e governança.
O ciclo `004` reformulou a experiência visual dos menus com telas dedicadas estilo MS-DOS, navegação por atalhos numéricos, banner híbrido retrô com canivete suíço e tipografia 3D isométrica.
O ciclo `005` ajusta o banner retrô com novo cinto utilitário ASCII, tipografia em blocos sólidos 'UTILITY-BELT' centralizada e novo subtítulo institucional.
O ciclo `006` entregou as cinco capacidades Markdown, com A/B/C integradas nas PRs #19/#20/#21 e issues #16/#17/#18 fechadas. Encerramento documental autorizado em 2026-10-12, consolidado em `_project/executed/006_conversao_markdown_nativa/006_task_closure.md`; estado Concluído nesta branch é proposta, com efeito canônico somente após integração verificável da PR documental. Próximo ciclo `007` preservado. File2MD não foi descontinuado.
