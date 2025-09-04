"""
Organizador de Downloads (Windows) — Versão Python-puro e robusta, com comentários

Resumo:
- Varre a pasta "Downloads" do usuário.
- Classifica arquivos por extensão e move para subpastas (ex.: PDFs, Imagens, etc.).
- Evita mover arquivos ainda em download (ex.: .crdownload, .part) ou recém-modificados.
- Resolve colisões de nomes gerando "arquivo (1).ext", "arquivo (2).ext", etc.
- Gera logs detalhados em console e em arquivo (Downloads/organizador.log).
- Não depende de PowerShell — usa apenas bibliotecas padrão do Python.

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
"""

import time
import shutil
import logging
from pathlib import Path


# ==============================
#  CONFIGURAÇÕES (edite à vontade)
# ==============================

# Pasta base a organizar (por padrão, Downloads do usuário atual)
DOWNLOADS = Path.home() / "Downloads"

# Mapeamento de pastas de destino -> extensões (todas em minúsculas)
# Observação: acrescente/remova extensões conforme sua realidade.
PASTAS_POR_TIPO = {
    "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documentos": [".docx", ".doc", ".txt", ".rtf", ".odt"],
    "PDFs": [".pdf"],
    "Aplicativos": [".exe", ".msi"],
    "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Planilhas": [".xlsx", ".xls", ".csv"],
    "Apresentacoes": [".pptx", ".ppt"],
    # Extras (opcionais):
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Audio": [".mp3", ".wav", ".flac", ".m4a"],
}

# Extensões que caracterizam arquivo "incompleto" de download (não mover)
INCOMPLETOS = {".crdownload", ".part", ".tmp"}

# Arquivos temporários comuns do Office/Windows começam com "~$"
TMP_PREFIXES = ("~$",)

# Critérios de estabilidade:
# - idade mínima desde a última modificação (segundos)
# - e confirmação de tamanho estável em sondagens sucessivas
IDADE_MIN_SEG = 60          # Exige pelo menos 60s sem alteração
SONDAGENS = 2               # Quantidade de leituras de tamanho (2 já confirma uma vez)
INTERVALO_SONDAGEM = 2.0    # Pausa em segundos entre leituras de tamanho



# ======================
#  FUNÇÕES AUXILIARES
# ======================

def pasta_destino_para(ext: str) -> Path | None:
    """
    Dada uma extensão (ex.: ".pdf"), retorna a subpasta de destino (Path)
    correspondente em DOWNLOADS, ou None se não houver mapeamento.
    """
    for pasta, exts in PASTAS_POR_TIPO.items():
        if ext.lower() in exts:
            return DOWNLOADS / pasta
    return None


def caminho_unico(dest: Path) -> Path:
    """
    Se 'dest' (arquivo de destino) já existir, gera um novo nome único com sufixo incremental:
    "arquivo.ext" -> "arquivo (1).ext", "arquivo (2).ext", ...
    Caso contrário, retorna o próprio 'dest'.
    """
    if not dest.exists():
        return dest

    i = 1
    stem, suf = dest.stem, dest.suffix
    while True:
        candidato = dest.with_name(f"{stem} ({i}){suf}")
        if not candidato.exists():
            return candidato
        i += 1


def mover_seguro(src: Path, dst_dir: Path) -> Path:
    """
    Move 'src' para a pasta 'dst_dir', garantindo que:
    - a pasta de destino existe (mkdir com parents=True, exist_ok=True)
    - o nome final não colide (usa caminho_unico)
    Retorna o caminho final do arquivo movido.
    """
    dst_dir.mkdir(parents=True, exist_ok=True)
    destino_final = caminho_unico(dst_dir / src.name)
    # shutil.move:
    # - no mesmo volume: operação é rename (muito rápida)
    # - em volume diferente: copia+remove (mais lenta, porém confiável)
    shutil.move(str(src), str(destino_final))
    return destino_final


def arquivo_estavel(p: Path) -> bool:
    """
    Verifica se um arquivo parece "estável" (não está sendo escrito/baixado).
    Critérios adotados:
    1) O arquivo precisa ser regular (is_file).
    2) Ter idade mínima desde a última modificação (IDADE_MIN_SEG).
    3) Tamanho estável em 'SONDAGENS' leituras com intervalo 'INTERVALO_SONDAGEM'.

    Se qualquer checagem falhar, retorna False.
    """
    try:
        if not p.is_file():
            return False

        # Checa idade mínima desde a última modificação
        idade = time.time() - p.stat().st_mtime
        if idade < IDADE_MIN_SEG:
            return False

        # Checa estabilidade de tamanho em sondagens consecutivas
        tamanho = p.stat().st_size
        for _ in range(SONDAGENS - 1):
            time.sleep(INTERVALO_SONDAGEM)
            novo_tamanho = p.stat().st_size
            if novo_tamanho != tamanho:
                return False  # tamanho mudou: possivelmente ainda em escrita
            tamanho = novo_tamanho

        return True
    except Exception:
        # Em caso de qualquer erro de leitura (permissão, I/O), tratamos como não estável
        return False



# ===============
#  ROTINA PRINCIPAL
# ===============

def main() -> None:
    """
    Executa a organização:
    - Faz um "snapshot" (lista) dos itens em Downloads antes de começar a mover
      (evita iterar em uma pasta que está mudando durante o loop).
    - Ignora temporários e arquivos incompletos.
    - Só move arquivos que estejam estáveis conforme critérios definidos.
    - Registra logs de tudo que foi movido, postergado/ignorado e de eventuais erros.
    """

    # Configuração de logging: imprime no console e salva em arquivo.
    logging.basicConfig(
        level=logging.INFO,  # Mude para DEBUG se quiser ver ainda mais detalhes
        format="%(asctime)s %(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(DOWNLOADS / "organizador.log", encoding="utf-8"),
        ],
    )

    logging.info("Iniciando organização da pasta: %s", DOWNLOADS)

    # Tira um "snapshot" dos itens atuais para evitar efeitos colaterais de mover enquanto itera
    try:
        itens = list(DOWNLOADS.iterdir())
    except FileNotFoundError:
        logging.error("Pasta de Downloads não encontrada: %s", DOWNLOADS)
        return

    movidos = 0   # contador de arquivos efetivamente movidos
    pulados = 0   # contador de arquivos ignorados/postergados
    erros = 0     # contador de falhas ao tentar mover

    for p in itens:
        try:
            # Processa apenas arquivos regulares (ignora pastas, atalhos, etc.)
            if not p.is_file():
                continue

            # Ignora arquivos temporários comuns (prefixos) e extensões de download incompleto
            if p.name.startswith(TMP_PREFIXES) or p.suffix.lower() in INCOMPLETOS:
                pulados += 1
                logging.debug("Ignorando temporário/incompleto: %s", p.name)
                continue

            # Descobre a pasta de destino com base na extensão
            destino_dir = pasta_destino_para(p.suffix.lower())
            if not destino_dir:
                # Extensão não mapeada: não mover (mas também não é erro)
                continue

            # Garante que o arquivo não está em uso e é "antigo" o suficiente
            if not arquivo_estavel(p):
                pulados += 1
                logging.info("Postergando (arquivo instável/recente): %s", p.name)
                continue

            # Tenta mover e registra o caminho final
            final = mover_seguro(p, destino_dir)
            movidos += 1
            logging.info("Movido: %s  ->  %s", p.name, final)

        except PermissionError as e:
            # Permissão negada geralmente indica arquivo aberto/bloqueado por outro processo
            erros += 1
            logging.warning("Arquivo bloqueado, pulando: %s (%s)", p, e)

        except Exception as e:
            # Qualquer outra exceção é logada com stack trace para depuração
            erros += 1
            logging.exception("Erro ao mover %s: %s", p, e)

    # Sumário final da execução
    logging.info("Concluído: movidos=%s | pulados=%s | erros=%s", movidos, pulados, erros)


# Ponto de entrada padrão em scripts Python
if __name__ == "__main__":
    main()