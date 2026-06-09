from __future__ import annotations

import subprocess
from pathlib import Path


def run_nougat(pdf_path: Path, output_dir: Path) -> str:
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "nougat",
        str(pdf_path),
        "-o",
        str(output_dir),
        "-m",
        "0.1.0-base",
        "--no-skipping",
    ]

    subprocess.run(cmd, check=True)

    output_file = output_dir / (pdf_path.stem + ".mmd")

    if output_file.exists():
        return output_file.read_text(encoding="utf-8")

    return ""
