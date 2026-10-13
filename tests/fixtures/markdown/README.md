# Fixtures Markdown

Documentos sintéticos próprios, gerados por `generate.py`, sem dados pessoais.
Texto esperado: `Utility Belt fixture`. PDF/DOCX/PPTX/XLSX/XLS/MSG/EPUB,
texto/JSON/JSONL/Markdown/CSV/HTML/RSS/IPYNB/ZIP e imagens contêm apenas dados
de teste. WAV contém silêncio PCM para testar extração local de metadados;
nunca deve ser enviado ao Google pela suíte automatizada.

MP3/M4A/MP4 foram gerados desse mesmo silêncio com o binário do pacote
`imageio-ffmpeg==0.6.0`, usando `-metadata artist=Utility Belt fixture`.
Testes da normalização executam FFmpeg real e substituem o cliente Google
por um mock; não fazem envio externo.

`partial.zip` inclui um PDF deliberadamente inválido. `no-extension` e
`sample.unrecognized` verificam aceitação por conteúdo fora de uma allowlist.
JPEG/PNG validam metadados locais, sem OCR ou descrição de imagem.

As ferramentas de geração são usadas somente no desenvolvimento; os arquivos
versionados podem ser lidos diretamente sem instalá-las no Belt.
