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
2.  Listar os Python.exe do ambiente CONDA
3.  *(Próximo script a ser adicionado)*

---

## Scripts Disponíveis

Aqui você encontrará a documentação detalhada de cada script.

### 1. Organizador de Downloads

#### **Resumo**
-   Varre a pasta "Downloads" do usuário.
-   Classifica arquivos por extensão e move para subpastas (ex.: `PDFs`, `Imagens`, etc.).
-   Move as pastas que estejam diretamente dentro de "Downloads" e que NÃO sejam as pastas predefinidas (PASTAS_POR_TIPO) para uma pasta especial chamada "Pastas_Diversas".
-   Evita mover arquivos ainda em download (ex.: `.crdownload`, `.part`) ou recém-modificados.
-   Resolve colisões de nomes gerando `arquivo (1).ext`, `arquivo (2).ext`, etc.
-   Gera logs detalhados no console e em um arquivo (`Downloads/organizador.log`).
-   Não depende de PowerShell, usa apenas bibliotecas padrão do Python.

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


### 2. Listar os Python.exe do ambiente CONDA

#### **Resumo**
-   Listar todos os ambientes Conda disponíveis na máquina e exibir, em formato de tabela, o nome de cada ambiente e o caminho absoluto do executável Python correspondente (python.exe no Windows, bin/python em Linux/macOS).

#### **Como Funciona**
1)  Invoca "conda info --json" para obter metadados do Conda em formato JSON.
2)  Extrai o "root_prefix" (ambiente base) e a lista de "envs" (prefixos).
3)  Garante que o ambiente base apareça junto dos demais.
4)  Para cada prefixo (caminho de um ambiente Conda), constrói o caminho do executável de Python e verifica se existe.
5)  Ordena a saída colocando "base" no topo e o restante em ordem alfabética.
6)  Imprime uma tabela alinhada: coluna "Env" e coluna "Python".

#### **Observações**
- Não é necessário ativar nenhum ambiente: o script consulta o Conda diretamente.
- Se algum ambiente estiver corrompido ou incompleto, o executável pode não existir; nesse caso, a tabela indicará "(não encontrado)".
- O script foi pensado para Windows, mas também funciona em Linux/macOS.

#### **Exemplo de uso**
- python listar_pythons_conda.py

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
