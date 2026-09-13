"""Catálogo e descoberta de ferramentas do Utility Belt via importlib.resources."""

from __future__ import annotations

import importlib.resources
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CURRENT_PLATFORM = "windows" if sys.platform == "win32" else ("linux" if sys.platform.startswith("linux") else sys.platform)


@dataclass
class ToolManifest:
    id: str
    name: str
    description: str
    runtime: str
    entry: str
    platforms: list[str]
    interactive: bool = False
    risk: str = "read"
    supports_dry_run: bool = False
    external_dependencies: list[str] = field(default_factory=list)
    schema_version: int = 1
    tool_dir: Path | None = None

    @property
    def is_compatible(self) -> bool:
        """Verifica se a ferramenta é suportada na plataforma atual."""
        return CURRENT_PLATFORM in self.platforms

    @property
    def entry_path(self) -> Path | None:
        """Caminho absoluto para o arquivo de entrada da ferramenta."""
        if self.tool_dir:
            return self.tool_dir / self.entry
        return None

    def validate(self) -> None:
        """Valida se o manifesto respeita as regras do schema."""
        if not self.id or not isinstance(self.id, str):
            raise ValueError("O campo 'id' é obrigatório e deve ser uma string.")
        if not self.name or not isinstance(self.name, str):
            raise ValueError(f"Ferramenta '{self.id}': 'name' é obrigatório.")
        if self.runtime not in {"python", "powershell", "bash", "binary"}:
            raise ValueError(f"Ferramenta '{self.id}': runtime inválido '{self.runtime}'.")
        if not self.entry or not isinstance(self.entry, str):
            raise ValueError(f"Ferramenta '{self.id}': 'entry' é obrigatório.")
        if not isinstance(self.platforms, list) or not self.platforms:
            raise ValueError(f"Ferramenta '{self.id}': 'platforms' deve ser uma lista não vazia.")
        if self.risk not in {"read", "write", "destructive"}:
            raise ValueError(f"Ferramenta '{self.id}': 'risk' deve ser read, write ou destructive.")


def load_manifest_from_dict(data: dict[str, Any], tool_dir: Path | None = None) -> ToolManifest:
    """Cria e valida um ToolManifest a partir de um dicionário."""
    manifest = ToolManifest(
        id=str(data.get("id", "")),
        name=str(data.get("name", "")),
        description=str(data.get("description", "")),
        runtime=str(data.get("runtime", "python")),
        entry=str(data.get("entry", "")),
        platforms=list(data.get("platforms", [])),
        interactive=bool(data.get("interactive", False)),
        risk=str(data.get("risk", "read")),
        supports_dry_run=bool(data.get("supports_dry_run", False)),
        external_dependencies=list(data.get("external_dependencies", [])),
        schema_version=int(data.get("schema_version", 1)),
        tool_dir=tool_dir,
    )
    manifest.validate()
    return manifest


def load_manifest_from_file(manifest_file: Path) -> ToolManifest:
    """Carrega um manifesto a partir de um arquivo tool.toml."""
    with manifest_file.open("rb") as f:
        data = tomllib.load(f)
    return load_manifest_from_dict(data, tool_dir=manifest_file.parent)


class Catalog:
    """Catálogo central de ferramentas registradas no pacote."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolManifest] = {}
        self._loaded = False

    def load(self) -> None:
        """Descobre todas as ferramentas em utility_belt.tools."""
        if self._loaded:
            return

        self._tools.clear()
        try:
            tools_resource = importlib.resources.files("utility_belt.tools")
        except Exception:
            self._loaded = True
            return

        # Itera pelas subpastas de utility_belt.tools
        for item in tools_resource.iterdir():
            if item.is_dir():
                manifest_resource = item.joinpath("tool.toml")
                if manifest_resource.is_file():
                    try:
                        # Extrai como arquivo real para suportar qualquer backend
                        with importlib.resources.as_file(manifest_resource) as manifest_path:
                            manifest = load_manifest_from_file(manifest_path)
                            self._tools[manifest.id] = manifest
                    except Exception as err:
                        # Registro de erro sem interromper o carregamento das demais
                        print(f"Aviso: erro ao carregar manifesto em {item.name}: {err}", file=sys.stderr)

        self._loaded = True

    def list_tools(self, all_platforms: bool = False) -> list[ToolManifest]:
        """Retorna as ferramentas registradas, ordenadas por ID."""
        self.load()
        tools = list(self._tools.values())
        if not all_platforms:
            tools = [t for t in tools if t.is_compatible]
        return sorted(tools, key=lambda t: t.id)

    def get_tool(self, tool_id: str) -> ToolManifest | None:
        """Recupera uma ferramenta pelo ID."""
        self.load()
        return self._tools.get(tool_id)


# Instância global do catálogo
catalog = Catalog()
