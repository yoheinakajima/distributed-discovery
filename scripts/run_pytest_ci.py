"""Run pytest and expose a compact failure report as a GitHub annotation."""

from __future__ import annotations

import subprocess
import sys


def _annotation_escape(value: str) -> str:
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def main() -> int:
    command = [sys.executable, "-m", "pytest", "--tb=short", *sys.argv[1:]]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    if completed.returncode:
        report = "\n".join((completed.stdout + completed.stderr).splitlines()[-120:])
        print(f"::error title=pytest failure::{_annotation_escape(report)}")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
