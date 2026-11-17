from src.application.dtos import CsfPdfDto
from src.domain.ports import PdfCsfDownloaderPort
from src.domain.value_objects.sat_fiel_credentials import SatFielCredentials


class DownloadCsfUseCase:
    """Valida las credenciales FIEL y descarga la Constancia de Situación Fiscal."""

    def __init__(self, downloader: PdfCsfDownloaderPort) -> None:
        self._downloader = downloader

    async def execute(
        self,
        certificate: bytes,
        private_key: bytes,
        pass_phrase: str,
    ) -> CsfPdfDto:
        credentials = SatFielCredentials(
            certificate=certificate,
            private_key=private_key,
            pass_phrase=pass_phrase,
        )

        return await self._downloader.download(
            certificate=credentials.certificate_der,
            private_key=credentials.private_key_der,
            pass_phrase=credentials.pass_phrase.get_secret_value(),
        )
