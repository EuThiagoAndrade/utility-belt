<div align="center">
  
# Coleção de Scripts Python para Windows

<p>
  <strong>Um repositório com diversos scripts úteis para automação de tarefas Windows do dia a dia.</strong>
</p>

</div>

---

## Sobre o Projeto

Este repositório serve como uma coleção centralizada de scripts Python práticos para facilitar a sua vida com o Windows. O objetivo é fornecer soluções simples e eficientes para tarefas comuns, que podem ser facilmente adaptadas e utilizadas por qualquer pessoa com conhecimentos básicos de Python.

Os scripts aqui presentes, na medida do possível, serão criados com o mínimo de dependências externas, priorizando o uso de bibliotecas padrão do Python para garantir a portabilidade e facilidade de execução.

## Navegação

Abaixo está a lista de scripts disponíveis neste repositório. Clique no nome para ir diretamente para a sua descrição.

1.  Organizador de Downloads
2.  *(Próximo script a ser adicionado)*
3.  *(Próximo script a ser adicionado)*

---

## Scripts Disponíveis

Aqui você encontrará a documentação detalhada de cada script.

### 1. Organizador de Downloads

#### **Resumo**
-   Varre a pasta "Downloads" do usuário.
-   Classifica arquivos por extensão e move para subpastas (ex.: `PDFs`, `Imagens`, etc.).
-   Evita mover arquivos ainda em download (ex.: `.crdownload`, `.part`) ou recém-modificados.
-   Resolve colisões de nomes gerando `arquivo (1).ext`, `arquivo (2).ext`, etc.
-   Gera logs detalhados no console e em um arquivo (`Downloads/organizador.log`).
-   Não depende de PowerShell, usa apenas bibliotecas padrão do Python.

> **Por que não usar PowerShell aqui?**
>
> `shutil.move()` faz *rename* quando no mesmo volume (operação extremamente rápida) e cópia+remoção caso o destino seja em um volume diferente, sem a necessidade de invocar processos externos. Isso torna o comportamento mais previsível e simplifica o tratamento de erros.

#### **Requisitos**
-   Python 3.10+
-   Windows 10/11
-   Nenhuma biblioteca externa necessária.

#### **Como Executar**
1.  Salve o código do script como `organizador_downloads.py`.
2.  Abra um terminal (CMD ou PowerShell).
3.  Navegue até a pasta onde salvou o arquivo e execute o comando:
    ```sh
    python organizador_downloads.py
    ```
4.  Verifique o arquivo `Downloads/organizador.log` para ver o histórico de ações e o console para o log em tempo real.

<br>

---
---

## Como Contribuir

Contribuições são o que tornam a comunidade de código aberto um lugar incrível para aprender, inspirar e criar. Qualquer contribuição que você fizer será **muito apreciada**.

1.  Faça um *Fork* do projeto.
2.  Crie uma *Branch* para sua Feature (`git checkout -b feature/AmazingFeature`).
3.  Faça o *Commit* de suas mudanças (`git commit -m 'Add some AmazingFeature'`).
4.  Faça o *Push* para a Branch (`git push origin feature/AmazingFeature`).
5.  Abra um *Pull Request*.

## Licença

Distribuído sob a licença MIT.
