from fastapi import Depends, Response, status

from api.http.fiel_file_reader import read_fiel_file
from api.http.schemas import OpinionCumplimientoDownloadRequest
from src.application.use_cases import DownloadOpinionCumplimientoUseCase
from src.bootstraps.application_bootstrap_services import (
    get_download_opinion_cumplimiento_use_case,
)


class OpinionCumplimientoDownloadController:
    """Descarga la Opinión de Cumplimiento autenticándose con la FIEL."""

    def __init__(self, use_case: DownloadOpinionCumplimientoUseCase) -> None:
        self._use_case = use_case

    async def handle(
        self, request: OpinionCumplimientoDownloadRequest
    ) -> Response:
        certificate = await read_fiel_file(
            request.certificate, "certificado"
        )
        private_key = await read_fiel_file(
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


def get_opinion_cumplimiento_download_controller(
    use_case: DownloadOpinionCumplimientoUseCase = Depends(
        get_download_opinion_cumplimiento_use_case
    ),
) -> OpinionCumplimientoDownloadController:
    return OpinionCumplimientoDownloadController(use_case=use_case)
