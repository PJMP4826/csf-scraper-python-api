from fastapi import Depends, UploadFile, status
from fastapi.responses import JSONResponse

from api.http.responses import success_response
from src.bootstraps.infrastructure_bootstrap_services import (
    get_tax_payer_info_extractor,
)
from src.infrastructure.adapters.tax_payer_info_extractor import TaxPayerInfoExtractor
from src.shared.errors.base_exception import BadRequestError

#: Tamaño máximo aceptado para una Constancia de Situación Fiscal.
MAX_FILE_SIZE = 10 * 1024 * 1024


class TaxPayerInfoExtractorController:
    """Registra la info fiscal leyéndola de una Constancia de Situación Fiscal."""

    def __init__(self, extractor: TaxPayerInfoExtractor) -> None:
        self._extractor = extractor

    async def handle(self, file: UploadFile) -> JSONResponse:
        content = await self._read_file(file)

        data = await self._extractor.extract(
            file_bytes=content,
            mime_type=file.content_type or "",
        )

        return success_response(
            status_code=status.HTTP_200_OK,
            message="Información fiscal extraída exitosamente",
            data=data,
        )

    async def _read_file(self, file: UploadFile) -> bytes:
        """Lee el archivo una sola vez y valida tamaño/contenido."""
        content = await file.read(MAX_FILE_SIZE + 1)

        if not content:
            raise BadRequestError(
                "El archivo está vacío.",
                error_code="EMPTY_FILE",
            )

        if len(content) > MAX_FILE_SIZE:
            raise BadRequestError(
                "El archivo supera el tamaño máximo permitido "
                f"({MAX_FILE_SIZE // (1024 * 1024)} MB).",
                error_code="FILE_TOO_LARGE",
            )

        return content


def get_tax_payer_info_extractor_controller(
    extractor: TaxPayerInfoExtractor = Depends(get_tax_payer_info_extractor),
) -> TaxPayerInfoExtractorController:
    return TaxPayerInfoExtractorController(extractor=extractor)
