import asyncio
import os
import shutil
import subprocess
import sys
from pathlib import Path

from csf_scraper.exceptions.pdf_reader import PdfToTextConvertException
from csf_scraper.pdf_reader import PdfToText


def resolve_pdftotext() -> str | None:
    """Devuelve la ruta del binario pdftotext disponible."""
    override = os.getenv("PDFTOTEXT_PATH")
    if override:
        return override

    if getattr(sys, "frozen", False):
        bundle_root = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        executable = bundle_root / "poppler" / "bin" / "pdftotext.exe"

        if executable.is_file():
            data_dir = bundle_root / "poppler" / "share" / "poppler"
            if data_dir.is_dir():
                os.environ.setdefault("POPPLER_DATADIR", str(data_dir))
            return str(executable)

    return shutil.which("pdftotext")


class NoWindowPdfToText(PdfToText):
    """Ejecuta pdftotext sin abrir una consola en builds --noconsole."""

    async def extract(self, path: str) -> str:
        command = self.build_command(path)
        extra: dict[str, object] = {}

        if sys.platform == "win32":
            extra["creationflags"] = subprocess.CREATE_NO_WINDOW

        result = await asyncio.to_thread(
            subprocess.run,
            command,
            capture_output=True,
            check=False,
            **extra,
        )

        if result.returncode != 0:
            raise PdfToTextConvertException(
                f"Running pdftotext exit with error (exit code {result.returncode})",
                command,
                result.returncode,
                result.stdout.decode("utf-8", errors="replace"),
                result.stderr.decode("utf-8", errors="replace"),
            )

        return result.stdout.decode("utf-8", errors="replace")
