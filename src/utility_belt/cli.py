"""Ponto de entrada principal da CLI do Utility Belt (belt / utility-belt)."""

from __future__ import annotations

import json

import typer

from utility_belt import __version__
from utility_belt.adapters.docker import docker_app
from utility_belt.adapters.restic import restic_app
from utility_belt.catalog import catalog
from utility_belt.doctor import run_diagnostics
from utility_belt.menu import show_menu
from utility_belt.runner import run_tool

app = typer.Typer(
    name="belt",
    help="Utility Belt (`belt`): Canivete suíço pessoal de terminal para Windows e Linux.",
    no_args_is_help=True,
    add_completion=False,
)

# Adiciona os subcomandos adaptados de Docker e Restic
app.add_typer(docker_app, name="docker")
app.add_typer(restic_app, name="restic")


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"belt (utility-belt) versão {__version__}")
        raise typer.Exit()


@app.callback()
def common_options(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Exibe a versão instalada do Utility Belt.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    pass


@app.command(name="list", help="Lista as ferramentas registradas no catálogo.")
def list_tools(
    all_platforms: bool = typer.Option(
        False, "--all", "-a", help="Lista todas as ferramentas, incluindo incompatíveis com o SO atual."
    ),
    as_json: bool = typer.Option(
        False, "--json", help="Exporta a lista em formato JSON."
    ),
) -> None:
    tools = catalog.list_tools(all_platforms=all_platforms)

    if as_json:
        data = [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "runtime": t.runtime,
                "platforms": t.platforms,
                "compatible": t.is_compatible,
                "interactive": t.interactive,
                "risk": t.risk,
            }
            for t in tools
        ]
        typer.echo(json.dumps(data, indent=2, ensure_ascii=False))
        return

    if not tools:
        typer.echo("Nenhuma ferramenta encontrada no catálogo.")
        return

    typer.secho(f"\nFerramentas registradas ({len(tools)}):", bold=True)
    for tool in tools:
        if tool.is_compatible:
            status = typer.style("[OK]", fg=typer.colors.GREEN, bold=True)
        else:
            status = typer.style("[Incompatível]", fg=typer.colors.YELLOW)

        risk_color = (
            typer.colors.RED
            if tool.risk == "destructive"
            else (typer.colors.YELLOW if tool.risk == "write" else typer.colors.CYAN)
        )
        risk_str = typer.style(f"({tool.risk})", fg=risk_color)

        typer.echo(f"  {status} {tool.id:<20} {risk_str:<15} {tool.name}")
        typer.echo(f"       {tool.description}")


@app.command(name="doctor", help="Verifica saúde do ambiente, dependências e configurações.")
def doctor(
    target: str | None = typer.Argument(
        None, help="Alvo específico para checar (ex.: docker, restic)."
    ),
    as_json: bool = typer.Option(
        False, "--json", help="Exporta o diagnóstico em formato JSON."
    ),
) -> None:
    diag = run_diagnostics()

    if target:
        dep = diag["dependencies"].get(target.lower())
        if not dep:
            typer.secho(f"Dependência '{target}' desconhecida para o doctor.", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)
        if as_json:
            typer.echo(json.dumps({target: dep}, indent=2, ensure_ascii=False))
        else:
            status = typer.style("Instalado", fg=typer.colors.GREEN) if dep.get("installed") else typer.style("Ausente", fg=typer.colors.RED)
            typer.echo(f"{target}: {status} - {dep.get('details', '')}")
        return

    if as_json:
        typer.echo(json.dumps(diag, indent=2, ensure_ascii=False))
        return

    typer.secho("\n=== Diagnóstico do Utility Belt ===", bold=True)
    typer.echo(f" Plataforma : {diag['system']['platform']} ({diag['system']['os_name']} {diag['system']['os_release']})")
    typer.echo(f" Python     : {diag['python']['version']} ({diag['python']['executable']})")
    typer.echo(f" Config     : {diag['config']['path']} ({'Encontrado' if diag['config']['exists'] else 'Padrão em memória'})")

    typer.secho("\n=== Dependências Externas ===", bold=True)
    for name, info in diag["dependencies"].items():
        if info.get("installed"):
            tag = typer.style("[OK]", fg=typer.colors.GREEN, bold=True)
            details = info.get("details") or info.get("path") or "Disponível"
        else:
            tag = typer.style("[FALTA]", fg=typer.colors.YELLOW)
            details = info.get("details") or "Não encontrado no PATH"
        typer.echo(f"  {tag} {name:<12} : {details}")


@app.command(
    name="run",
    help="Executa uma ferramenta registrada pelo ID, repassando argumentos.",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def run_command(
    ctx: typer.Context,
    tool_id: str = typer.Argument(..., help="ID da ferramenta a executar (ex.: system.info)."),
    non_interactive: bool = typer.Option(
        False, "--non-interactive", help="Força execução não interativa sem prompts."
    ),
) -> None:
    tool = catalog.get_tool(tool_id)
    if not tool:
        typer.secho(f"Erro: Ferramenta '{tool_id}' não encontrada no catálogo.", fg=typer.colors.RED, err=True)
        typer.echo("Use 'belt list' para ver as ferramentas disponíveis.")
        raise typer.Exit(code=1)

    exit_code = run_tool(tool, args=ctx.args, non_interactive=non_interactive)
    raise typer.Exit(code=exit_code)


@app.command(name="menu", help="Abre o menu interativo de navegação no terminal.")
def interactive_menu() -> None:
    show_menu()


@app.command(name="show-completion", help="Exibe instruções para autocompletar no shell sem modificar perfis.")
def show_completion_cmd(
    shell: str = typer.Argument("powershell", help="Shell desejado (powershell, bash, zsh, fish)."),
) -> None:
    shell = shell.lower()
    typer.secho(f"=== Instruções de Autocompletar para {shell.upper()} ===", bold=True)
    if shell == "powershell":
        typer.echo(
            'Para habilitar o autocompletar nesta sessão do PowerShell, execute:\n'
            '  Register-ArgumentCompleter -Native -CommandName belt -ScriptBlock {\n'
            '      param($wordToComplete, $commandAst, $cursorPosition)\n'
            '      [System.Environment]::SetEnvironmentVariable("_BELT_COMPLETE", "complete_powershell")\n'
            '  }\n'
            'Para persistir, adicione o comando acima ao seu $PROFILE manualmente.'
        )
    elif shell == "bash":
        typer.echo(
            'Para habilitar o autocompletar no Bash, adicione ao seu ~/.bashrc:\n'
            '  eval "$(_BELT_COMPLETE=complete_bash belt)"'
        )
    else:
        typer.echo(f"Consulte a documentação do Typer/Click para autocompletar em {shell}.")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
