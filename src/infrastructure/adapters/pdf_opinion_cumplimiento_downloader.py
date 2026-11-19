from opinion_scraper import (
    AuthenticationException,
    FederationException,
    FielCredentials,
    FielCredentialsException,
    InvalidOpinionResponseException,
    InvalidPdfException,
    InvalidRfcException,
    OpinionDownloader,
    OpinionNotAvailableException,
    OpinionScraperException,
    SatFormNotFoundException,
    SatLoginException,
    SatNetworkException,
)

from src.application.dtos import OpinionCumplimientoPdfDto
from src.domain.errors.opinion_cumplimiento_download_error import (
    InvalidOpinionPdfError,
    InvalidOpinionResponseError,
    InvalidOpinionRfcError,
    OpinionCumplimientoDownloadError,
    OpinionFielCredentialsError,
    OpinionNotAvailableError,
    OpinionSatAuthenticationError,
    OpinionSatFederationError,
    OpinionSatFormNotFoundError,
    OpinionSatLoginError,
    OpinionSatNetworkError,
)
from src.domain.ports import PdfOpinionCumplimientoDownloaderPort

#: Nombre usado cuando la librería no informa uno en el PDF descargado.
_DEFAULT_PDF_FILENAME = "opinion_cumplimiento.pdf"


class PdfOpinionCumplimientoDownloader(
    PdfOpinionCumplimientoDownloaderPort
):
    """Descarga la Opinión de Cumplimiento autenticándose con la FIEL."""

    async def download(
        self,
        *,
        certificate: bytes,
        private_key: bytes,
        pass_phrase: str,
    ) -> OpinionCumplimientoPdfDto:
        """Autentica en el SAT y devuelve la Opinión de Cumplimiento.

        Las credenciales llegan ya validadas por ``SatFielCredentials`` desde
        la capa de aplicación; aquí solo se usan para autenticarse.
        """
        try:
            credentials = FielCredentials.from_bytes(
                certificate=certificate,
                key=private_key,
                password=pass_phrase,
            )

            async with OpinionDownloader.create(
                credentials=credentials
            ) as downloader:
                pdf = await downloader.download()
        except FielCredentialsException as exception:
            raise OpinionFielCredentialsError(
                details={"reason": str(exception)}
            ) from exception
        except SatNetworkException as exception:
            raise OpinionSatNetworkError(
                details={
                    "url": exception.url,
                    "status_code": exception.status_code,
                    "reason": str(exception),
                }
            ) from exception
        except SatLoginException as exception:
            raise OpinionSatLoginError(
                details={
                    "stage": exception.stage,
                    "reason": str(exception),
                }
            ) from exception
        except FederationException as exception:
            raise OpinionSatFederationError(
                details={
                    "stage": exception.stage,
                    "reason": str(exception),
                }
            ) from exception
        except AuthenticationException as exception:
            raise OpinionSatAuthenticationError(
                details={
                    "stage": exception.stage,
                    "reason": str(exception),
                }
            ) from exception
        except SatFormNotFoundException as exception:
            raise OpinionSatFormNotFoundError(
                details={"reason": str(exception)}
            ) from exception
        except OpinionNotAvailableException as exception:
            raise OpinionNotAvailableError(
                details={
                    "codigo": exception.codigo,
                    "mensaje": exception.mensaje,
                    "reason": str(exception),
                }
            ) from exception
        except InvalidPdfException as exception:
            raise InvalidOpinionPdfError(
                details={"reason": str(exception)}
            ) from exception
        except InvalidOpinionResponseException as exception:
            raise InvalidOpinionResponseError(
                details={"reason": str(exception)}
            ) from exception
        except InvalidRfcException as exception:
            raise InvalidOpinionRfcError(
                details={"reason": str(exception)}
            ) from exception
        except OpinionScraperException as exception:
            raise OpinionCumplimientoDownloadError(
                details={"reason": str(exception)}
            ) from exception

        return OpinionCumplimientoPdfDto(
            pdf_contents=pdf.as_bytes(),
            file_name=pdf.filename or _DEFAULT_PDF_FILENAME,
        )
