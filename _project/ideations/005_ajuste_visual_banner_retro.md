# Ideação — 005: Ajuste Visual do Banner Retrô e Cinto Utilitário

> **Ciclo:** `005`
> **Estado:** `Ideação`
> **Criado em:** 2026-09-17
> **Última atualização:** 2026-09-17

## Problema

O banner de abertura retrô introduzido no Ciclo 004 apresentou problemas estéticos e ortográficos identificados pelo usuário:
1. **Arte ASCII inadequada:** A ilustração anterior com um canivete suíço à esquerda e divisor vertical ficou visualmente desbalanceada e desajeitada no terminal.
2. **Tipografia com erro de grafia:** O título "UTILITY-BELT" desenhado em blocos no banner anterior ficou confuso e com letras incorretas (o caractere "I" foi desenhado idêntico ao "T", resultando em leitura truncada/errônea).
3. **Subtítulo desalinhado:** O subtítulo *"Sistema de Ferramentas para Desenvolvedores"* precisa ser substituído pelo novo posicionamento de produto: *"Sistema de ferramentas para simplificar sua vida"*.

## Contexto e evidências

- **Feedback do usuário (2026-09-17):**
  - Excluir o desenho ASCII anterior do canivete.
  - Excluir o nome truncado e substituí-lo por tipografia em fonte grande para diferenciar, em estilo de blocos sólidos preenchidos (`█`) com ortografia 100% correta ("UTILITY-BELT").
  - Inserir o desenho do cinto utilitário estilizado: `|==[■]==[■]==[■]==[████]==[■]==[■]==[■]==|`.
  - Manter a moldura MS-DOS com linhas duplas `═══` na cor ciano original (`\033[1;36m`).
  - Manter o item `v0.1.0 • O Canivete Suíço de Terminal`.
  - Substituir o texto *"Sistema de Ferramentas para Desenvolvedores"* por *"Sistema de ferramentas para simplificar sua vida"*.
  - Centralizar todos os elementos vertical e horizontalmente dentro da moldura.
  - Escopo cirúrgico: modificar apenas esta tela/banner, preservando integralmente todo o restante da CLI e dos menus.

## Resultado desejado

1. Atualização do método `render_banner()` em `src/utility_belt/ui/screen.py`:
   - Moldura dupla MS-DOS `╔═══╗` preservada em Ciano (`\033[1;36m`).
   - Cinto utilitário ASCII `|==[■]==[■]==[■]==[████]==[■]==[■]==[■]==|` centralizado no topo.
   - Tipografia de grande porte preenchida em blocos maciços `█` para "UTILITY-BELT" (Estilo A selecionado pelo usuário), perfeitamente legível e centralizada.
   - Linha `v0.1.0 • O Canivete Suíço de Terminal` centralizada em branco brilhante.
   - Linha `Sistema de ferramentas para simplificar sua vida` centralizada em tom cinza retrô.
2. Atualização dos testes unitários em `tests/test_screen.py` para validar o novo conteúdo e layout.
3. Zero regressões nos gates de testes (`uv run pytest`), linter (`uv run ruff check`) e governança (`python scripts/validate_governance.py`).

## Hipóteses

- **H1:** A centralização vertical e horizontal com o cinto utilitário e tipografia em blocos sólidos `█` proporciona uma identidade limpa, marcante e alinhada ao nome "Utility Belt", sem o ruído gráfico do desenho anterior.
- **H2:** A manutenção das dimensões seguras (largura interna 74, total 76 colunas) garante que o banner não quebre nem sofra overflow em terminais padrão de 80 colunas.

## Alternativas

- **Alternativa A (Selecionada) — Estilo A (Bloco Maciço 5 Linhas em `█`):**
  - Letras maiúsculas sólidas e proporção imponente, 100% nítida e aprovada pelo usuário.
- **Alternativa B — Estilo B (Bloco Meio-Tamanho 3 Linhas com `▀` e `▄`):**
  - Compacto, mas o usuário manifestou preferência explícita pelo Estilo A.\n