from fastapi import UploadFile

from src.shared.errors.base_exception import BadRequestError

#: Tamaño máximo aceptado para cada archivo de la FIEL.
MAX_FIEL_FILE_SIZE = 1 * 1024 * 1024


async def read_fiel_file(file: UploadFile, label: str) -> bytes:
    """Lee el archivo y valida que no esté vacío ni exceda el límite."""
    content = await file.read(MAX_FIEL_FILE_SIZE + 1)

    if not content:
        raise BadRequestError(
            f"El {label} está vacío.",
            error_code="EMPTY_FIEL_FILE",
        )

    if len(content) > MAX_FIEL_FILE_SIZE:
        raise BadRequestError(
            f"El {label} supera el tamaño máximo permitido "
            f"({MAX_FIEL_FILE_SIZE // (1024 * 1024)} MB).",
            error_code="FIEL_FILE_TOO_LARGE",
        )

    return content
