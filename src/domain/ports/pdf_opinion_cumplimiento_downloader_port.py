from abc import ABC, abstractmethod

from src.application.dtos import OpinionCumplimientoPdfDto


class PdfOpinionCumplimientoDownloaderPort(ABC):
    """Contrato para descargar la Opinión de Cumplimiento con la FIEL."""

    @abstractmethod
    async def download(
        self,
        *,
        certificate: bytes,
        private_key: bytes,
        pass_phrase: str,
    ) -> OpinionCumplimientoPdfDto:
        """Devuelve la Opinión de Cumplimiento descargada como PDF."""
        raise NotImplementedError
