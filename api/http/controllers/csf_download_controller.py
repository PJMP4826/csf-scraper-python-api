from fastapi import Depends, Response, status

from api.http.fiel_file_reader import read_fiel_file
from api.http.schemas import CsfDownloadRequest
from src.application.use_cases import DownloadCsfUseCase
from src.bootstraps.application_bootstrap_services import (
    get_download_csf_use_case,
)


class CsfDownloadController:
    """Descarga la CSF autenticándose con las credenciales FIEL."""

    def __init__(self, use_case: DownloadCsfUseCase) -> None:
        self._use_case = use_case

    async def handle(self, request: CsfDownloadRequest) -> Response:
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


def get_csf_download_controller(
    use_case: DownloadCsfUseCase = Depends(get_download_csf_use_case),
) -> CsfDownloadController:
    return CsfDownloadController(use_case=use_case)
