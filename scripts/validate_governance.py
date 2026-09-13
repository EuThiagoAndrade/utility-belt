#!/usr/bin/env python3
"""
Validador de Governança do Utility Belt.

Audita a integridade, estrutura e rastreabilidade documental conforme
definido em .agent/ai_behavior.md e _project/README.md.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class GovernanceValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.successes: list[str] = []

    def log_ok(self, message: str) -> None:
        self.successes.append(message)

    def log_warn(self, message: str) -> None:
        self.warnings.append(message)

    def log_error(self, message: str) -> None:
        self.errors.append(message)

    def validate_canonical_files(self) -> None:
        """Verifica a presença das autoridades canônicas fundamentais."""
        required_files = [
            (".agent/ai_behavior.md", "Autoridade de comportamento de agentes"),
            ("_project/README.md", "Autoridade de ciclo de vida e estrutura"),
            ("_project/cycles.md", "Autoridade de estado de ciclos"),
            (".agent/task.md", "Ponte de tarefas"),
            (".agent/lessons_learned.md", "Registro de lições aprendidas"),
        ]
        for rel_path, desc in required_files:
            file_path = self.root / rel_path
            if file_path.is_file():
                self.log_ok(f"Arquivo canônico presente: {rel_path} ({desc})")
            else:
                self.log_error(f"Arquivo canônico obrigatório ausente: {rel_path} ({desc})")

    def validate_adapters(self) -> None:
        """Verifica os adapters de descoberta agnóstica na raiz."""
        adapters = ["AGENTS.md", "CLAUDE.md", "GEMINI.md"]
        for adapter in adapters:
            adapter_path = self.root / adapter
            if not adapter_path.is_file():
                self.log_error(f"Adapter de descoberta ausente na raiz: {adapter}")
                continue

            content = adapter_path.read_text(encoding="utf-8")
            if ".agent/ai_behavior.md" in content:
                self.log_ok(f"Adapter válido: {adapter} aponta para .agent/ai_behavior.md")
            else:
                self.log_error(f"Adapter {adapter} não faz referência a .agent/ai_behavior.md")

    def validate_templates(self) -> None:
        """Verifica templates da governança e do GitHub."""
        templates = [
            ".agent/templates/adr.md",
            ".agent/templates/ideacao.md",
            ".agent/templates/plano_implementacao.md",
            ".agent/templates/task.md",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/chore.yml",
            ".github/PULL_REQUEST_TEMPLATE/pull_request_template.md",
        ]
        for tmpl in templates:
            tmpl_path = self.root / tmpl
            if tmpl_path.is_file():
                self.log_ok(f"Template presente: {tmpl}")
            else:
                self.log_error(f"Template obrigatório ausente: {tmpl}")

    def validate_decisions(self) -> None:
        """Verifica integridade dos ADRs."""
        decisions_dir = self.root / "_project" / "decisions"
        if not decisions_dir.is_dir():
            self.log_error("Diretório _project/decisions/ ausente.")
            return

        adrs = list(decisions_dir.glob("ADR-*.md"))
        if not adrs:
            self.log_warn("Nenhum ADR encontrado em _project/decisions/.")
            return

        adr_pattern = re.compile(r"^ADR-\d{3}_[\w\-]+\.md$")
        for adr in adrs:
            if not adr_pattern.match(adr.name):
                self.log_error(f"Nome do ADR fora do padrão 'ADR-NNN_assunto.md': {adr.name}")
            else:
                content = adr.read_text(encoding="utf-8")
                if "## Status" in content and "## Decisão" in content:
                    self.log_ok(f"ADR válido: {adr.name}")
                else:
                    self.log_error(f"ADR {adr.name} não contém seções obrigatórias (Status, Decisão).")

    def validate_cycles(self) -> None:
        """Valida coerência de _project/cycles.md e diretórios dos ciclos."""
        cycles_file = self.root / "_project" / "cycles.md"
        if not cycles_file.is_file():
            self.log_error("Arquivo _project/cycles.md ausente.")
            return

        content = cycles_file.read_text(encoding="utf-8")
        next_cycle_match = re.search(r">\s*\*\*Próximo ciclo:\*\*\s*`(\d{3})`", content)
        if not next_cycle_match:
            self.log_error("_project/cycles.md não declara '> **Próximo ciclo:** `NNN`'.")
            declared_next = None
        else:
            declared_next = next_cycle_match.group(1)
            self.log_ok(f"Próximo ciclo declarado: {declared_next}")

        # Parsing das linhas da tabela markdown
        table_lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip().startswith("|") and not line.strip().startswith("| :")
        ]

        if len(table_lines) <= 1:
            self.log_warn("Tabela de ciclos em _project/cycles.md vazia ou sem registros.")
            return

        header = [col.strip() for col in table_lines[0].split("|")[1:-1]]
        expected_cols = ["Ciclo", "Assunto", "Estado", "Ideação", "Plano", "Issues", "Encerramento"]
        if header != expected_cols:
            self.log_warn(
                f"Cabeçalho da tabela de ciclos diverge do canônico. Esperado: {expected_cols}, obtido: {header}"
            )

        executed_cycles: list[str] = []
        valid_states = {"Ideação", "Planejamento", "Em execução", "Concluído", "Cancelado", "Substituído"}

        for row_str in table_lines[1:]:
            cols = [col.strip() for col in row_str.split("|")[1:-1]]
            if len(cols) < 5:
                continue

            cycle_col = cols[0]
            cycle_match = re.search(r"`(\d{3})`", cycle_col)
            if not cycle_match:
                self.log_error(f"Número de ciclo inválido na linha: {row_str}")
                continue

            cycle_id = cycle_match.group(1)
            subject = cols[1]
            state = cols[2].replace("`", "").strip()

            if state not in valid_states:
                self.log_error(f"Ciclo {cycle_id}: estado inválido '{state}'. Válidos: {valid_states}")

            if state == "Concluído":
                executed_cycles.append(cycle_id)
                # Verifica diretório correspondente em executed/
                executed_dir = self.root / "_project" / "executed"
                matching_dirs = list(executed_dir.glob(f"{cycle_id}_*"))
                if not matching_dirs:
                    self.log_error(f"Ciclo {cycle_id} ('{subject}') marcado como Concluído, mas pasta em executed/ não encontrada.")
                else:
                    cycle_folder = matching_dirs[0]
                    plan_file = cycle_folder / f"{cycle_id}_plan.md"
                    closure_file = cycle_folder / f"{cycle_id}_task_closure.md"

                    if not plan_file.is_file():
                        self.log_error(f"Ciclo {cycle_id}: arquivo de plano {plan_file.name} ausente.")
                    else:
                        self.log_ok(f"Ciclo {cycle_id}: plano concluído presente ({plan_file.name})")

                    if not closure_file.is_file():
                        self.log_error(f"Ciclo {cycle_id}: task de encerramento {closure_file.name} ausente.")
                    else:
                        self.log_ok(f"Ciclo {cycle_id}: closure presente ({closure_file.name})")

        # Verifica consistência do próximo ciclo
        if executed_cycles and declared_next:
            highest_cycle = max(int(c) for c in executed_cycles)
            expected_next = f"{highest_cycle + 1:03d}"
            if declared_next != expected_next:
                self.log_warn(
                    f"Próximo ciclo declarado ({declared_next}) diverge do esperado ({expected_next}) baseado no maior ciclo concluído ({highest_cycle:03d})."
                )

    def run(self) -> bool:
        """Executa todas as validações e exibe o relatório."""
        print(f"=== Auditoria de Governança: {self.root.name} ===")
        self.validate_canonical_files()
        self.validate_adapters()
        self.validate_templates()
        self.validate_decisions()
        self.validate_cycles()

        print("\n--- Resultados ---")
        for ok in self.successes:
            print(f"  [OK]   {ok}")
        for warn in self.warnings:
            print(f"  [WARN] {warn}")
        for err in self.errors:
            print(f"  [FAIL] {err}")

        total_checks = len(self.successes) + len(self.warnings) + len(self.errors)
        print(f"\nResumo: {total_checks} verificações | {len(self.successes)} OK | {len(self.warnings)} Avisos | {len(self.errors)} Falhas")

        return len(self.errors) == 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Validador de Governança do Utility Belt")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Diretório raiz do repositório a auditar")
    args = parser.parse_args()

    validator = GovernanceValidator(args.root)
    success = validator.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
