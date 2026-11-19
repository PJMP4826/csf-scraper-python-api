from fastapi import Depends, Response, UploadFile, status

from api.http.schemas import OpinionCumplimientoDownloadRequest
from src.application.use_cases import DownloadOpinionCumplimientoUseCase
from src.bootstraps.application_bootstrap_services import (
    get_download_opinion_cumplimiento_use_case,
)
from src.shared.errors.base_exception import BadRequestError

#: Tamaño máximo aceptado para cada archivo de la FIEL.
MAX_FIEL_FILE_SIZE = 1 * 1024 * 1024


class OpinionCumplimientoDownloadController:
    """Descarga la Opinión de Cumplimiento autenticándose con la FIEL."""

    def __init__(self, use_case: DownloadOpinionCumplimientoUseCase) -> None:
        self._use_case = use_case

    async def handle(
        self, request: OpinionCumplimientoDownloadRequest
    ) -> Response:
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


def get_opinion_cumplimiento_download_controller(
    use_case: DownloadOpinionCumplimientoUseCase = Depends(
        get_download_opinion_cumplimiento_use_case
    ),
) -> OpinionCumplimientoDownloadController:
    return OpinionCumplimientoDownloadController(use_case=use_case)
