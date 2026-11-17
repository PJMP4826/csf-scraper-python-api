import re
from pathlib import Path

from fastapi import Depends, Response, UploadFile, status

from api.http.schemas import CsfDownloadRequest
from src.application.use_cases import DownloadCsfUseCase
from src.bootstraps.application_bootstrap_services import (
    get_download_csf_use_case,
)
from src.shared.errors.base_exception import BadRequestError

#: Tamaño máximo aceptado para cada archivo de la FIEL.
MAX_FIEL_FILE_SIZE = 1 * 1024 * 1024


class CsfDownloadController:
    """Descarga la CSF autenticándose con las credenciales FIEL."""

    def __init__(self, use_case: DownloadCsfUseCase) -> None:
        self._use_case = use_case

    async def handle(self, request: CsfDownloadRequest) -> Response:
        certificate = await self._read_file(
            request.certificate, "certificado"
        )
        private_key = await self._read_file(
            request.private_key, "llave privada"
        )

        pdf = await self._use_case.execute(
            certificate=certificate,
            private_key=private_key,
            pass_phrase=request.pass_phrase.get_secret_value(),
        )

        return Response(
            content=pdf.pdf_contents,
            status_code=status.HTTP_200_OK,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{pdf.file_name}"'
                )
            },
        )

    async def _read_file(self, file: UploadFile, label: str) -> bytes:
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


def get_csf_download_controller(
    use_case: DownloadCsfUseCase = Depends(get_download_csf_use_case),
) -> CsfDownloadController:
    return CsfDownloadController(use_case=use_case)
