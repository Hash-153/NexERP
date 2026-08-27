"""Local CI quality gate for NexERP source, tests, and configuration.

The command intentionally uses standard-library checks first so it can run in a
fresh checkout before optional formatting tools are installed.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOTS = (ROOT / "backend", ROOT / "alembic")
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache", ".venv", "node_modules", "dist", "build"}


def python_files() -> Iterable[Path]:
    for source_root in SOURCE_ROOTS:
        if not source_root.exists():
            continue
        for path in source_root.rglob("*.py"):
            if not EXCLUDED_PARTS.intersection(path.parts):
                yield path


def validate_python_syntax() -> list[str]:
    failures = []
    for path in python_files():
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as error:
            failures.append(f"{path}: {error}")
    return failures


def validate_json_files() -> list[str]:
    failures = []
    for path in (ROOT / "frontend").glob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            failures.append(f"{path}: {error}")
    return failures


def run_tests() -> int:
    command = [sys.executable, "-m", "pytest", "backend/tests", "-q"]
    completed = subprocess.run(command, cwd=ROOT, check=False)
    return completed.returncode


def source_statistics() -> dict[str, int]:
    files = list(python_files())
    lines = sum(len(path.read_text(encoding="utf-8", errors="ignore").splitlines()) for path in files)
    return {"python_files": len(files), "python_lines": lines}


def main() -> int:
    syntax_failures = validate_python_syntax()
    json_failures = validate_json_files()
    if syntax_failures or json_failures:
        for failure in syntax_failures + json_failures:
            print(failure, file=sys.stderr)
        return 1
    print(f"Syntax and JSON validation passed: {source_statistics()}")
    return run_tests()


if __name__ == "__main__":
    raise SystemExit(main())
