"""Pandoc conversion helpers."""
import shutil
import subprocess
from pathlib import Path


def convert_markdown_to_docx(
    markdown_path: Path, output_path: Path, reference_docx: Path
) -> None:
    """Convert Markdown to DOCX with a reference template."""
    if not shutil.which("pandoc"):
        raise RuntimeError(
            "pandoc is required for DOCX generation; install it in the backend container"
        )

    command = [
        "pandoc",
        str(markdown_path),
        "-o",
        str(output_path),
        "--reference-doc",
        str(reference_docx),
    ]
    subprocess.run(command, check=True)
