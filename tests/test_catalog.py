"""Testes para o catálogo de ferramentas do Utility Belt."""


import pytest

from utility_belt.catalog import (
    Catalog,
    load_manifest_from_dict,
)


def test_manifest_validation_success() -> None:
    manifest = load_manifest_from_dict(
        {
            "schema_version": 1,
            "id": "teste.tool",
            "name": "Ferramenta de Teste",
            "description": "Descricao de teste",
            "runtime": "python",
            "entry": "main.py",
            "platforms": ["windows", "linux"],
            "interactive": False,
            "risk": "read",
        }
    )
    assert manifest.id == "teste.tool"
    assert manifest.runtime == "python"
    assert "windows" in manifest.platforms


def test_manifest_validation_missing_id() -> None:
    with pytest.raises(ValueError, match="id"):
        load_manifest_from_dict(
            {
                "schema_version": 1,
                "name": "Sem ID",
                "entry": "main.py",
                "platforms": ["windows"],
            }
        )


def test_manifest_validation_invalid_runtime() -> None:
    with pytest.raises(ValueError, match="runtime"):
        load_manifest_from_dict(
            {
                "schema_version": 1,
                "id": "tool.invalida",
                "name": "Runtime Invalido",
                "runtime": "ruby",
                "entry": "main.py",
                "platforms": ["windows"],
            }
        )


def test_catalog_discovery() -> None:
    cat = Catalog()
    tools = cat.list_tools(all_platforms=True)
    tool_ids = [t.id for t in tools]

    assert "system.info" in tool_ids
    assert "docker.export" in tool_ids
    assert "docker.import" in tool_ids
    assert "restic.backup" in tool_ids


def test_get_tool() -> None:
    cat = Catalog()
    tool = cat.get_tool("system.info")
    assert tool is not None
    assert tool.name == "Informações do Sistema"
    assert tool.entry == "main.py"
