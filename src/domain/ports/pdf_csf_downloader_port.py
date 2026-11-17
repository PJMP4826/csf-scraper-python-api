from abc import ABC, abstractmethod

from src.application.dtos import CsfPdfDto


class PdfCsfDownloaderPort(ABC):
    """Contrato de dominio para descargar la CSF autenticándose con la FIEL."""

    @abstractmethod
    async def download(
        self,
        *,
        certificate: bytes,
        private_key: bytes,
        pass_phrase: str,
    ) -> CsfPdfDto:
        """Devuelve la constancia descargada como PDF."""
        raise NotImplementedError
