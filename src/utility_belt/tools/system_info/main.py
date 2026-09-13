#!/usr/bin/env python3
"""Ferramenta Piloto: Informações do Sistema."""

import json
import os
import platform
import sys
from pathlib import Path


def main() -> int:
    info = {
        "sistema": platform.system(),
        "versao_so": platform.version(),
        "release": platform.release(),
        "arquitetura": platform.machine(),
        "processador": platform.processor() or "N/A",
        "python": sys.version.split()[0],
        "interpretador": sys.executable,
        "diretorio_trabalho": str(Path.cwd()),
        "usuario": os.environ.get("USERNAME") or os.environ.get("USER") or "N/A",
    }

    if "--json" in sys.argv:
        print(json.dumps(info, indent=2, ensure_ascii=False))
        return 0

    print("===================================================")
    print("  INFORMAÇÕES DO SISTEMA (Utility Belt)")
    print("===================================================")
    print(f" Sistema Operacional : {info['sistema']} ({info['release']})")
    print(f" Arquitetura         : {info['arquitetura']}")
    print(f" Versão do Python    : {info['python']}")
    print(f" Usuário Atual       : {info['usuario']}")
    print(f" Diretório de Execução: {info['diretorio_trabalho']}")
    print("===================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
