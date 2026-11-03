"""Helper para diagnóstico acionável e interpretação de erros do Restic."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ResticDiagnostic:
    """Estrutura com resumo e orientação acionável para resultados do Restic."""

    subcommand: str
    returncode: int
    summary: str
    guidance: str
    affected_item: str | None = None
    detail: str | None = None


def _extract_restore_details(stderr: str, stdout: str) -> tuple[str | None, str | None]:
    """Extrai detalhes de erro e caminhos de arquivo reportados pelo Restic na restauração."""
    combined = f"{stderr}\n{stdout}"
    affected_item: str | None = None
    detail: str | None = None

    for line in combined.splitlines():
        line_clean = line.strip()
        if not line_clean:
            continue

        # Exemplo: "ignoring error for /caminho/arquivo.txt: SetFileTime: The system cannot find the path specified."
        # No Windows: "ignoring error for C:\caminho\arquivo.txt: SetFileTime: ..."
        if "ignoring error for " in line_clean:
            rest = line_clean.split("ignoring error for ", 1)[1]
            if len(rest) > 2 and rest[1] == ":" and rest[2] in ("\\", "/"):
                colon_idx = rest.find(":", 2)
                if colon_idx != -1:
                    affected_item = rest[:colon_idx].strip()
                    detail = rest[colon_idx + 1 :].strip()
                    break
                else:
                    affected_item = rest.strip()
                    detail = line_clean
                    break
            elif ":" in rest:
                path_part, reason_part = rest.split(":", 1)
                affected_item = path_part.strip()
                detail = reason_part.strip()
                break
            else:
                affected_item = rest.strip()
                detail = line_clean
                break
        elif "error:" in line_clean.lower() or "failed" in line_clean.lower():
            if not detail:
                detail = line_clean

    return affected_item, detail


def diagnose_restic_result(
    subcommand: str,
    returncode: int,
    stderr: str = "",
    stdout: str = "",
) -> ResticDiagnostic | None:
    """Interpreta códigos de saída e erros conhecidos do Restic em diagnósticos acionáveis."""
    if returncode == 0:
        return None

    # Código 11: Falha ao obter lock do repositório
    if returncode == 11:
        return ResticDiagnostic(
            subcommand=subcommand,
            returncode=11,
            summary="Falha ao obter lock do repositório (código 11).",
            guidance=(
                "Verifique se há outro processo do Restic em execução no repositório.\n"
                "Caso nenhuma operação esteja em andamento (por exemplo, após queda de energia "
                "ou encerramento abrupto), utilize 'belt restic unlock' para remover locks obsoletos após conferência."
            ),
        )

    # Código 3: Backup com arquivos não lidos
    if subcommand == "backup" and returncode == 3:
        return ResticDiagnostic(
            subcommand="backup",
            returncode=3,
            summary="Backup finalizado, mas alguns arquivos não puderam ser lidos (código 3 - incompleto).",
            guidance=(
                "Alguns arquivos não puderam ser lidos durante a execução (ex.: arquivos bloqueados ou sem permissão). "
                "O snapshot foi gerado, mas o backup é considerado incompleto."
            ),
        )

    # Restauração com código de erro não zero
    if subcommand == "restore":
        affected_item, detail = _extract_restore_details(stderr, stdout)
        guidance_text = (
            "A restauração não pôde ser confirmada como completa. "
            "Verifique a integridade e o conteúdo da pasta de destino antes de utilizá-la."
        )
        return ResticDiagnostic(
            subcommand="restore",
            returncode=returncode,
            summary=f"Restauração finalizada com erro (código {returncode}).",
            guidance=guidance_text,
            affected_item=affected_item,
            detail=detail,
        )

    # Falhas desconhecidas ou genéricas
    return ResticDiagnostic(
        subcommand=subcommand,
        returncode=returncode,
        summary=f"A operação '{subcommand}' terminou com código de erro {returncode}.",
        guidance="Consulte as mensagens de saída do Restic exibidas acima para avaliar a causa técnica.",
    )


def format_cli_guidance(diag: ResticDiagnostic) -> str:
    """Formata o diagnóstico complementar para exibição em stderr no modo CLI."""
    lines = [f"\n[DIAGNÓSTICO RESTIC] {diag.summary}"]
    if diag.detail:
        lines.append(f"  Detalhe : {diag.detail}")
    if diag.affected_item:
        lines.append(f"  Item    : {diag.affected_item}")
    lines.append(f"  Ação    : {diag.guidance}")
    return "\n".join(lines)


def format_menu_guidance(diag: ResticDiagnostic) -> str:
    """Formata o diagnóstico complementar para mensagens no menu interativo."""
    parts = [diag.summary]
    if diag.detail:
        parts.append(f"Detalhe: {diag.detail}")
    if diag.affected_item:
        parts.append(f"Item afetado: {diag.affected_item}")
    parts.append(diag.guidance)
    return "\n".join(parts)
