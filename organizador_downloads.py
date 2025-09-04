import time
import shutil
import logging
from pathlib import Path


# ==============================
#  CONFIGURAÇÕES (edite à vontade)
# ==============================

# Pasta base a organizar (Downloads do usuário atual)
DOWNLOADS = Path.home() / "Downloads"

# Nome da pasta onde serão guardadas as pastas "não-predefinidas"
PASTA_PASTAS_DIVERSAS = "Pastas_Diversas"
DIVERSAS_DIR = DOWNLOADS / PASTA_PASTAS_DIVERSAS

# Mapeamento de pastas de destino -> extensões (todas em minúsculas)
# Observação: acrescente/remova extensões conforme sua realidade.
PASTAS_POR_TIPO = {
    # --- MÍDIA E DESIGN ---
    "Imagens_Raster": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".heic", ".avif"],
    "Imagens_Vetor_e_Design": [".svg", ".ai", ".eps", ".psd", ".fig", ".sketch", ".xd"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mpg", ".mpeg"],
    "Audio": [".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma"],
    "Modelos_3D": [".obj", ".fbx", ".stl", ".blend", ".dae", ".3ds"],
    "Fontes": [".ttf", ".otf", ".woff", ".woff2"],

    # --- DOCUMENTOS E ESCRITÓRIO ---
    "Documentos_de_Texto": [".docx", ".doc", ".txt", ".rtf", ".odt", ".pages", ".md", ".markdown"],
    "PDFs": [".pdf"],
    "Planilhas": [".xlsx", ".xls", ".csv", ".ods", ".numbers"],
    "Apresentacoes": [".pptx", ".ppt", ".odp", ".key"],
    "eBooks": [".epub", ".mobi", ".azw3"],

    # --- SISTEMA E EXECUTÁVEIS ---
    "Executaveis_e_Instaladores": [".exe", ".msi", ".bat", ".cmd", ".app", ".dmg", ".deb", ".rpm", ".AppImage", ".apk"],
    "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz"],
    "Imagens_de_Disco": [".iso", ".img", ".vhd", ".vmdk"],
    
    # --- DESENVOLVIMENTO E CÓDIGO (CATEGORIA REESTRUTURADA) ---
    "Codigo_Fonte": [".py", ".java", ".c", ".cpp", ".cs", ".go", ".rs", ".kt", ".swift", ".rb", ".pl", ".scala", ".pas", ".m"],
    "Web_FrontEnd": [".html", ".htm", ".css", ".js", ".ts", ".jsx", ".tsx"],
    "Estilos_e_Preprocessadores": [".scss", ".sass", ".less", ".styl"],
    "Scripts_de_Automacao": [".sh", ".ps1", ".vbs"],
    "Dados_e_Configuracao": [".json", ".xml", ".yaml", ".yml", ".ini", ".toml", ".env"],
    "Banco_de_Dados": [".sql", ".db", ".sqlite", ".sqlite3", ".mdb"],
    "Notebooks_e_Analise": [".ipynb", ".r"] # Específico para ciência de dados
}

# Conjunto com os nomes de pastas "reservadas"/predefinidas que NÃO devem ser movidas
PREDEFINIDAS = set(PASTAS_POR_TIPO.keys()) | {PASTA_PASTAS_DIVERSAS}

# Extensões que caracterizam arquivo "incompleto" de download (não mover)
INCOMPLETOS = {".crdownload", ".part", ".tmp"}

# Arquivos temporários comuns do Office/Windows começam com "~$"
TMP_PREFIXES = ("~$",)

# Critérios de estabilidade (para arquivos):
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
    Gera um nome único se 'dest' já existir.
    - Para arquivos: "arquivo.ext" -> "arquivo (1).ext", "arquivo (2).ext", ...
    - Para pastas:  "pasta" -> "pasta (1)", "pasta (2)", ...
    Obs.: Funciona para ambos porque usamos Path.exists() e montamos o novo nome.
    """
    if not dest.exists():
        return dest

    i = 1
    stem, suf = dest.stem, dest.suffix  # para pastas, suffix = ""
    while True:
        candidato = dest.with_name(f"{stem} ({i}){suf}")
        if not candidato.exists():
            return candidato
        i += 1


def mover_arquivo_seguro(src: Path, dst_dir: Path) -> Path:
    """
    Move um ARQUIVO 'src' para a pasta 'dst_dir', garantindo que:
    - a pasta de destino existe (mkdir com parents=True, exist_ok=True)
    - o nome final não colide (usa caminho_unico)
    Retorna o caminho final do arquivo movido.
    """
    dst_dir.mkdir(parents=True, exist_ok=True)
    destino_final = caminho_unico(dst_dir / src.name)
    shutil.move(str(src), str(destino_final))
    return destino_final


def mover_pasta_seguro(src_dir: Path, dst_dir: Path) -> Path:
    """
    Move uma PASTA 'src_dir' para dentro de 'dst_dir', garantindo:
    - criação de 'dst_dir' se não existir;
    - resolução de colisão de nomes (sufixo " (1)", " (2)", ...).
    Retorna o caminho final da pasta movida.
    """
    dst_dir.mkdir(parents=True, exist_ok=True)
    destino_final = caminho_unico(dst_dir / src_dir.name)
    shutil.move(str(src_dir), str(destino_final))
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
      (evita iterar numa pasta que está mudando durante o loop).
    - ARQUIVOS: ignora temporários e incompletos; só move se estiverem estáveis.
    - PASTAS: move todas as pastas diretamente dentro de Downloads, exceto:
        * as predefinidas (as chaves de PASTAS_POR_TIPO),
        * a própria "Pastas_Diversas".
      Todas as demais pastas vão para "Downloads/Pastas_Diversas".
    - Loga tudo o que foi movido/postergado/ignorado e eventuais erros.
    """

    # Configuração de logging: imprime no console e salva em arquivo.
    logging.basicConfig(
        level=logging.INFO,  # Mude para DEBUG se quiser mais verbosidade
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

    # Contadores
    movidos_arquivos = 0
    movidos_pastas  = 0
    pulados         = 0
    erros           = 0

    # ============
    # 1) ARQUIVOS
    # ============
    for p in itens:
        try:
            if not p.is_file():
                continue  # Só arquivos nesta primeira etapa

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

            # Move o arquivo
            final = mover_arquivo_seguro(p, destino_dir)
            movidos_arquivos += 1
            logging.info("Arquivo movido: %s  ->  %s", p.name, final)

        except PermissionError as e:
            erros += 1
            logging.warning("Arquivo bloqueado, pulando: %s (%s)", p, e)

        except Exception as e:
            erros += 1
            logging.exception("Erro ao mover arquivo %s: %s", p, e)

    # ==========
    # 2) PASTAS
    # ==========
    for p in itens:
        try:
            if not p.is_dir():
                continue  # Só pastas nesta segunda etapa

            # Não mover pastas "predefinidas" (as chaves de PASTAS_POR_TIPO) nem a "Pastas_Diversas"
            if p.name in PREDEFINIDAS:
                continue

            # Evitar mover links simbólicos (se existirem)
            if p.is_symlink():
                pulados += 1
                logging.info("Ignorando link simbólico: %s", p.name)
                continue

            # Move a pasta para "Downloads/Pastas_Diversas"
            final_dir = mover_pasta_seguro(p, DIVERSAS_DIR)
            movidos_pastas += 1
            logging.info("Pasta movida: %s  ->  %s", p.name, final_dir)

        except PermissionError as e:
            erros += 1
            logging.warning("Pasta bloqueada, pulando: %s (%s)", p, e)

        except Exception as e:
            erros += 1
            logging.exception("Erro ao mover pasta %s: %s", p, e)

    # Sumário final da execução
    logging.info(
        "Concluído: arquivos_movidos=%s | pastas_movidas=%s | pulados=%s | erros=%s",
        movidos_arquivos, movidos_pastas, pulados, erros
    )


# Ponto de entrada padrão em scripts Python
if __name__ == "__main__":
    main()
