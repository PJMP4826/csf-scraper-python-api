import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WINDOWS_DIR = Path(__file__).resolve().parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
ENTRY_POINT = PROJECT_ROOT / "run.py"
ICON_PATH = WINDOWS_DIR / "assets" / "app.ico"

APP_NAME = "csf-scraper-api"

POPPLER_VERSION = "26.09.0-0"
POPPLER_ZIP_NAME = f"Release-{POPPLER_VERSION}.zip"
POPPLER_URL = (
    "https://github.com/oschwartz10612/poppler-windows/releases/download/"
    f"v{POPPLER_VERSION}/{POPPLER_ZIP_NAME}"
)
POPPLER_SHA256 = "7a6f256a0ddf7536182246a5733331bf4677cbcc34f4663774947ad34556c8d0"
POPPLER_CACHE_DIR = WINDOWS_DIR / ".cache" / "poppler"

PYINSTALLER_ARGS = [
    "--onefile",
    "--noconfirm",
    "--clean",
    "--name",
    APP_NAME,
    "--collect-all",
    "csf_scraper",
    "--collect-all",
    "uvicorn",
    "--hidden-import",
    "python_multipart",
    "--hidden-import",
    "multipart",
    "--hidden-import",
    "tiktoken_ext.openai_public",
    "--hidden-import",
    "csf_scraper.image_readers.adapters.cpu.open_cv_image_reader",
    "--hidden-import",
    "anyio._backends._asyncio",
]


def clean_build() -> None:
    if BUILD_DIR.exists():
        print(f"--- Eliminando {BUILD_DIR}... ---")
        shutil.rmtree(BUILD_DIR)

    BUILD_DIR.mkdir(parents=True, exist_ok=True)


def _download(url: str, destination: Path) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "csf-scraper-python-api-build"},
    )
    temporary_path = destination.with_suffix(destination.suffix + ".part")

    try:
        with urllib.request.urlopen(request) as response:
            with temporary_path.open("wb") as output:
                shutil.copyfileobj(response, output, length=1024 * 1024)
        temporary_path.replace(destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def _verify_sha256(file_path: Path, expected: str) -> None:
    digest = hashlib.sha256()
    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    actual = digest.hexdigest()
    if actual != expected:
        file_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"El SHA256 de {file_path.name} no coincide. "
            "El archivo se eliminó; vuelve a ejecutar el script."
        )


def _find_poppler_bin(root: Path) -> Path | None:
    if root.is_file():
        return root.parent if root.name.lower() == "pdftotext.exe" else None

    if not root.exists():
        return None

    for candidate in root.rglob("pdftotext.exe"):
        if candidate.is_file():
            return candidate.parent

    return None


def ensure_poppler(download: bool) -> Path:
    override = os.getenv("POPPLER_DIR")
    if override:
        bin_dir = _find_poppler_bin(Path(override))
        if bin_dir is None:
            raise RuntimeError(
                f"POPPLER_DIR no contiene pdftotext.exe: {override}"
            )
        print(f"--- Usando Poppler de POPPLER_DIR: {bin_dir} ---")
        return bin_dir

    extraction_dir = POPPLER_CACHE_DIR / "extracted"
    cached_bin = _find_poppler_bin(extraction_dir)
    if cached_bin is not None:
        print(f"--- Usando Poppler en cache: {cached_bin} ---")
        return cached_bin

    if not download:
        raise RuntimeError(
            "No hay Poppler en cache y se indicó --no-download. "
            "Define POPPLER_DIR o ejecuta sin --no-download."
        )

    POPPLER_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = POPPLER_CACHE_DIR / POPPLER_ZIP_NAME

    if zip_path.exists():
        print(f"--- Usando archivo en cache: {zip_path} ---")
    else:
        print(f"--- Descargando Poppler {POPPLER_VERSION}... ---")
        _download(POPPLER_URL, zip_path)

    _verify_sha256(zip_path, POPPLER_SHA256)

    if extraction_dir.exists():
        shutil.rmtree(extraction_dir)
    extraction_dir.mkdir(parents=True, exist_ok=True)

    print("--- Extrayendo Poppler... ---")
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(extraction_dir)

    bin_dir = _find_poppler_bin(extraction_dir)
    if bin_dir is None:
        raise RuntimeError(
            "No se encontró pdftotext.exe dentro del paquete de Poppler."
        )

    return bin_dir


def _collect_poppler_assets(
    bin_dir: Path,
) -> tuple[list[tuple[Path, str]], list[tuple[Path, str]]]:
    binaries: list[tuple[Path, str]] = []

    pdftotext = bin_dir / "pdftotext.exe"
    if not pdftotext.is_file():
        raise RuntimeError(f"No existe {pdftotext}")

    binaries.append((pdftotext, "poppler/bin"))
    for dll in sorted(bin_dir.glob("*.dll")):
        binaries.append((dll, "poppler/bin"))

    datas: list[tuple[Path, str]] = []
    share_poppler = bin_dir.parent / "share" / "poppler"
    if share_poppler.is_dir():
        datas.append((share_poppler, "poppler/share/poppler"))

    return binaries, datas


def _find_icon() -> Path | None:
    override = os.getenv("APP_ICON")
    candidates = [
        Path(override) if override else None,
        ICON_PATH,
        WINDOWS_DIR / "app.ico",
        PROJECT_ROOT / "app.ico",
    ]

    for candidate in candidates:
        if candidate is not None and candidate.is_file():
            return candidate

    return None


def _check_pyinstaller() -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--version"],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("--- PyInstaller no está instalado en este entorno. ---")
        print("--- Ejecuta: python -m pip install pyinstaller ---")
        return False

    print(f"--- PyInstaller: {result.stdout.strip()} ---")
    return True


def run_compilation(show_console: bool, download_poppler: bool) -> int:
    print(f"--- Usando Python: {sys.executable} ---")

    if not _check_pyinstaller():
        return 1

    bin_dir = ensure_poppler(download=download_poppler)
    binaries, datas = _collect_poppler_assets(bin_dir)

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        *PYINSTALLER_ARGS,
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(BUILD_DIR),
        "--specpath",
        str(BUILD_DIR),
    ]

    if not show_console:
        command.append("--noconsole")

    for source, destination in datas:
        command.extend(["--add-data", f"{source};{destination}"])

    for source, destination in binaries:
        command.extend(["--add-binary", f"{source};{destination}"])

    icon_path = _find_icon()
    if icon_path is not None:
        command.extend(["--icon", str(icon_path)])

    command.append(str(ENTRY_POINT))

    print("--- Iniciando compilación con PyInstaller... ---")
    result = subprocess.run(command, cwd=PROJECT_ROOT, check=False)

    if result.returncode != 0:
        print(f"\n--- ERROR en la compilación (código {result.returncode}) ---")
        return result.returncode

    print("\n--- ¡Compilación exitosa! ---")
    return 0


def _remove_spec_files() -> None:
    if not BUILD_DIR.exists():
        return

    for spec_file in BUILD_DIR.glob("*.spec"):
        spec_file.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genera el ejecutable de Windows con PyInstaller.",
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Genera el ejecutable con consola para depuración.",
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="No descarga Poppler; usa POPPLER_DIR o la cache local.",
    )
    parser.add_argument(
        "--keep-build",
        action="store_true",
        help="Conserva la carpeta build y el archivo .spec.",
    )
    args = parser.parse_args()

    clean_build()

    try:
        exit_code = run_compilation(
            show_console=args.console,
            download_poppler=not args.no_download,
        )
    except Exception as exception:
        print(f"\n--- ERROR: {exception} ---")
        return 1
    finally:
        if not args.keep_build:
            _remove_spec_files()

    if exit_code != 0:
        return exit_code

    exe_path = DIST_DIR / f"{APP_NAME}.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"--- Ejecutable generado: {exe_path} ({size_mb:.1f} MB) ---")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
