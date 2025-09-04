Todos os scripts tem seu arquivo de leiura obrigatório 

///////////////////////////////////////////
MENU - ABAIXO OS SCRIPTS EM ORDEM DO README
1 - Organizador de Downloads (Windows) 
//////////////////////////////////////////

//////////////////////////////////////
1 - Organizador de Downloads (Windows) 

Versão Python-puro e robusta, com comentários

Resumo:
- Varre a pasta "Downloads" do usuário.
- Classifica arquivos por extensão e move para subpastas (ex.: PDFs, Imagens, etc.).
- Evita mover arquivos ainda em download (ex.: .crdownload, .part) ou recém-modificados.
- Resolve colisões de nomes gerando "arquivo (1).ext", "arquivo (2).ext", etc.
- Gera logs detalhados em console e em arquivo (Downloads/organizador.log).
- Não depende de PowerShell usa apenas bibliotecas padrão do Python.

Por que não usar PowerShell aqui?
- shutil.move() faz rename quando no mesmo volume (rápido) e cópia+remoção em volumes diferentes,
  sem necessidade de invocar processos externos. Isso torna o comportamento mais previsível e 
  simplifica o tratamento de erros.

Requisitos:
- Python 3.10+ em Windows 10/11.
- Sem bibliotecas externas.

Como executar:
- Salve este arquivo como "organizador_downloads.py" (ou nome de sua preferência).
- Execute no terminal:  python organizador_downloads.py
- Verifique o arquivo "Downloads/organizador.log" para ver o histórico de ações.

FIM /////////////////////////
