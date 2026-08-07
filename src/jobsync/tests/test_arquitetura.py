"""Testes de arquitetura: garantem a conformidade com os contratos do import-linter.

Esses testes complementam a execução do `lint-imports` no CI, permitindo que
a suíte de testes do pytest também falhe em caso de violações arquiteturais.
"""
import os
import subprocess
import sys
from pathlib import Path


def _caminho_lint_imports() -> Path:
    """Resolve o executável do import-linter a partir do interpretador em uso."""
    bin_dir = Path(sys.executable).parent
    executavel = bin_dir / "lint-imports"
    if executavel.exists():
        return executavel
    executavel = bin_dir / "lint-imports.exe"
    if executavel.exists():
        return executavel
    raise FileNotFoundError("Comando 'lint-imports' não encontrado junto ao interpretador Python.")


def test_import_linter_passa():
    """O import-linter deve aprovar todos os contratos configurados."""
    lint_imports = _caminho_lint_imports()
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    result = subprocess.run(
        [str(lint_imports)],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "import-linter encontrou violações arquiteturais.\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
