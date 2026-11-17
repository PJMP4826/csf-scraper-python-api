from csf_scraper import CsfScraperException
from csf_scraper.download import (
    ConstanciaDownloader,
    ConstanciaNotAvailableException,
    FielCredentials,
    FielCredentialsException,
    InvalidPdfException,
    SatFormNotFoundException,
    SatLoginException,
    SatNetworkException,
    SatSsoException,
)

from src.application.dtos import CsfPdfDto
from src.domain.errors.constancia_download_error import (
    ConstanciaDownloadError,
    ConstanciaNotAvailableError,
    FielCredentialsDownloadError,
    InvalidConstanciaPdfError,
    SatFormNotFoundError,
    SatLoginError,
    SatNetworkError,
    SatSsoError,
)
from src.domain.ports import PdfCsfDownloaderPort

#: Nombre usado cuando el SAT no informa uno en ``Content-Disposition``.
_DEFAULT_PDF_FILENAME = "constancia.pdf"


class PdfCsfDownloader(PdfCsfDownloaderPort):
    """Descarga la CSF en PDF autenticándose con las credenciales FIEL."""

    async def download(
        self,
        *,
        certificate: bytes,
        private_key: bytes,
        pass_phrase: str,
    ) -> CsfPdfDto:
        """Autentica en el SAT y devuelve la constancia descargada.

        Las credenciales llegan ya validadas por ``SatFielCredentials`` desde
        la capa de aplicación; aquí solo se usan para autenticarse.
        """
        try:
            credentials = FielCredentials.from_bytes(
                certificate=certificate,
                key=private_key,
                password=pass_phrase,
            )

            async with ConstanciaDownloader.create(
                credentials=credentials
            ) as downloader:
                pdf = await downloader.download()
        except FielCredentialsException as exception:
            raise FielCredentialsDownloadError(
                details={"reason": str(exception)}
            ) from exception
        except SatNetworkException as exception:
            raise SatNetworkError(
                details={"url": exception.url, "reason": str(exception)}
            ) from exception
        except SatLoginException as exception:
            raise SatLoginError(
                details={"reason": str(exception)}
            ) from exception
        except SatSsoException as exception:
            raise SatSsoError(
                details={"reason": str(exception)}
            ) from exception
        except SatFormNotFoundException as exception:
            raise SatFormNotFoundError(
                details={"reason": str(exception)}
            ) from exception
        except ConstanciaNotAvailableException as exception:
            raise ConstanciaNotAvailableError(
                details={"reason": str(exception)}
            ) from exception
        except InvalidPdfException as exception:
            raise InvalidConstanciaPdfError(
                details={"reason": str(exception)}
            ) from exception
        except CsfScraperException as exception:
            raise ConstanciaDownloadError(
                details={"reason": str(exception)}
            ) from exception

        return CsfPdfDto(
            pdf_contents=pdf.as_bytes(),
            file_name=pdf.filename or _DEFAULT_PDF_FILENAME,
        )
