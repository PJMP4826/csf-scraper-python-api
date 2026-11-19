from src.application.dtos import OpinionCumplimientoPdfDto
from src.domain.ports import PdfOpinionCumplimientoDownloaderPort
from src.domain.value_objects.sat_fiel_credentials import SatFielCredentials


class DownloadOpinionCumplimientoUseCase:
    """Valida las credenciales FIEL y descarga la Opinión de Cumplimiento."""

    def __init__(
        self, downloader: PdfOpinionCumplimientoDownloaderPort
    ) -> None:
        self._downloader = downloader

    async def execute(
        self,
        certificate: bytes,
        private_key: bytes,
        pass_phrase: str,
    ) -> OpinionCumplimientoPdfDto:
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
