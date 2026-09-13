import sys
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path para carregar os scripts utilitários
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_governance import GovernanceValidator  # noqa: E402


def test_governance_integrity():
    """Valida que toda a estrutura de governança do Utility Belt está íntegra e sem falhas."""
    validator = GovernanceValidator(REPO_ROOT)
    success = validator.run()

    assert success, f"Falhas de governança detectadas: {validator.errors}"
    assert len(validator.errors) == 0
    assert len(validator.successes) > 0
