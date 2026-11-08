import json
import asyncio
import os
import tempfile
from collections.abc import Awaitable, Callable
from typing import Final, Any

import puremagic
from csf_scraper import (
    CifDownloadException,
    CifFromImageNotFoundException,
    CifFromPdfNotFoundException,
    CifNotFoundException,
    CsfImageExtractor,
    CsfScraperException,
    EmptyPdfContentException,
    ImageExtractorNotConfiguredException,
    ImageReaderApiException,
    ImageReaderAuthenticationException,
    ImageReaderPort,
    ImageReadingException,
    InvalidIdCifFormatException,
    InvalidImageException,
    InvalidImageFormatException,
    InvalidRfcFormatException,
    PdfToTextConvertException,
    PersonaFisica,
    PersonaMoral,
    RfcFromImageNotFoundException,
    RfcFromPdfNotFoundException,
    Scraper,
)
from csf_scraper.image_readers.adapters.cpu.open_cv.errors import ImageLoadError
from src.shared.errors.base_exception import BadRequestError
from src.shared.errors.infrastructure_exceptions import (
    ConfigurationError,
    InfrastructureException,
    ProcessingError,
    UpstreamServiceError,
)

#: Persona que devuelve cualquier estrategia de lectura.
_Persona = PersonaMoral | PersonaFisica

#: Firma de una estrategia de lectura: (scraper, ruta) -> persona.
_CsfReader = Callable[[Scraper, str], Awaitable[_Persona]]

#: Alias MIME que mandan algunos clientes para formatos que ya soportamos.
#: ``.jpg`` y ``.jpeg`` son el mismo formato, pero el MIME no estándar
#: ``image/jpg`` es común en navegadores y móviles.
_MIME_ALIASES: Final[dict[str, str]] = {
    "image/jpg": "image/jpeg",
    "image/pjpeg": "image/jpeg",
    "image/jfif": "image/jpeg",
    "image/x-png": "image/png",
}

#: Fallos que significan "el archivo no sirve" (entrada inválida del cliente).
_INVALID_INPUT_EXCEPTIONS: Final[tuple[type[Exception], ...]] = (
    InvalidImageException,
    InvalidImageFormatException,
    InvalidRfcFormatException,
    InvalidIdCifFormatException,
    CifFromImageNotFoundException,
    CifFromPdfNotFoundException,
    RfcFromImageNotFoundException,
    RfcFromPdfNotFoundException,
    EmptyPdfContentException,
)

#: El archivo es válido pero no pudo convertirse/procesarse (422).
_PROCESSING_EXCEPTIONS: Final[tuple[type[Exception], ...]] = (
    PdfToTextConvertException,
)

#: Falta configuración del lector (500).
_CONFIGURATION_EXCEPTIONS: Final[tuple[type[Exception], ...]] = (
    ImageExtractorNotConfiguredException,
)

#: Credenciales rechazadas por el proveedor de lectura (500): reintentar con
#: la misma clave daría el mismo resultado.
_AUTHENTICATION_EXCEPTIONS: Final[tuple[type[Exception], ...]] = (
    ImageReaderAuthenticationException,
)

#: Fallo del proveedor externo: SAT u OCR/LLM (502). ``ImageReaderApiException``
#: cubre también ``ImageReaderUnavailableException`` (saturación, caída o red).
_UPSTREAM_EXCEPTIONS: Final[tuple[type[Exception], ...]] = (
    CifDownloadException,
    CifNotFoundException,
    ImageReaderApiException,
)


class TaxPayerInfoExtractor:
    def __init__(self, image_reader: ImageReaderPort) -> None:
        # ``Scraper`` consume un ``RfcCifExtractorPort``: se adapta el motor de
        # lectura (``ImageReaderPort``) con ``CsfImageExtractor``.
        self._image_extractor = CsfImageExtractor(image_reader)

        # Estrategias de lectura: MIME type -> (sufijo del temporal, lector).
        # Agregar un formato soportado es agregar una entrada aquí.
        self._readers: dict[str, tuple[str, _CsfReader]] = {
            "application/pdf": ("pdf", self._read_pdf),
            "image/jpeg": ("jpg", self._read_image),
            "image/png": ("png", self._read_image),
        }

    async def _read_pdf(self, scraper: Scraper, file_path: str) -> _Persona:
        return await scraper.obtain_from_pdf_path(path=file_path)

    async def _read_image(self, scraper: Scraper, file_path: str) -> _Persona:
        return await scraper.obtain_from_image_path(path=file_path)

    async def extract(self, file_bytes: bytes, mime_type: str) -> dict[str, Any]:
        suffix, read = self._readers[self._detect_kind(file_bytes, mime_type)]

        file_path = await asyncio.to_thread(
            self._write_temp_file, file_bytes, f".{suffix}"
        )

        try:
            async with Scraper.create(image_extractor=self._image_extractor) as scraper:
                person = await read(scraper, file_path)
        except _INVALID_INPUT_EXCEPTIONS as exception:
            raise BadRequestError(
                "No se pudieron leer los datos fiscales del archivo. "
                "Verifica que sea una Constancia de Situación Fiscal vigente.",
                error_code="INVALID_CSF_FILE",
                details={"reason": str(exception)},
            ) from exception
        except _PROCESSING_EXCEPTIONS as exception:
            raise ProcessingError(
                "El PDF no pudo interpretarse como una Constancia de "
                "Situación Fiscal.",
                error_code="CSF_PDF_CONVERSION_FAILED",
                details={"reason": str(exception)},
            ) from exception
        except _CONFIGURATION_EXCEPTIONS as exception:
            raise ConfigurationError(
                "El lector de imágenes no está configurado correctamente.",
                error_code="CSF_IMAGE_READER_NOT_CONFIGURED",
                details={"reason": str(exception)},
            ) from exception
        except FileNotFoundError as exception:
            # ``CsfPdfExtractor`` depende del binario ``pdftotext``
            # (paquete ``poppler-utils``); sin él el PDF no se puede leer.
            raise ConfigurationError(
                "Falta la dependencia del sistema para leer PDFs (pdftotext).",
                error_code="CSF_PDF_TOOL_MISSING",
                details={"reason": str(exception)},
            ) from exception
        except _AUTHENTICATION_EXCEPTIONS as exception:
            raise ConfigurationError(
                "El proveedor de lectura de imágenes rechazó las credenciales.",
                error_code="CSF_IMAGE_READER_AUTH_FAILED",
                details={"reason": str(exception)},
            ) from exception
        except _UPSTREAM_EXCEPTIONS as exception:
            raise UpstreamServiceError(
                "El servicio del SAT no está disponible en este momento. "
                "Intenta nuevamente más tarde.",
                error_code="CSF_SERVICE_UNAVAILABLE",
                details={"reason": str(exception)},
            ) from exception
        except ImageReadingException as exception:
            raise ProcessingError(
                "No fue posible leer el codigo QR de la constancia, verifique la calidad de la imagen",
                error_code="CSF_QR_NOT_READABLE",
                details={"reason": str(exception)},
            ) from exception
        except ImageLoadError as exception:
            raise ProcessingError(
                "No fue posible decodificar la imagen de la constancia. "
                "Verifica que el archivo no esté dañado.",
                error_code="CSF_IMAGE_DECODE_FAILED",
                details={"reason": str(exception)},
            ) from exception
        except ValueError as exception:
            # El QR se leyó pero no contiene el patrón RFC/idCIF esperado
            # (``OpenCvImageReader._parse_id_cif_and_rfc``).
            raise ProcessingError(
                "El código QR se leyó, pero no contiene los datos fiscales "
                "esperados. Verifica que sea una Constancia de Situación "
                "Fiscal vigente.",
                error_code="CSF_QR_PAYLOAD_INVALID",
                details={"reason": str(exception)},
            ) from exception
        except CsfScraperException as exception:
            raise InfrastructureException(
                "No fue posible consultar los datos fiscales en el SAT.",
                error_code="CSF_LOOKUP_FAILED",
                details={"reason": str(exception)},
            ) from exception
        finally:
            await asyncio.to_thread(self._remove_temp_file, file_path)

        return json.loads(person.model_dump_json())

    def _detect_kind(self, file_bytes: bytes, mime_type: str) -> str:
        """Determina el tipo real del archivo (magic bytes primero).

        El ``mime_type`` que manda el cliente es solo una pista: puede venir con
        parámetros (``application/pdf; boundary=...``), ser genérico o usar un
        alias no estándar (``image/jpg``).
        """
        try:
            guessed: str | None = puremagic.from_string(file_bytes, mime=True)  # type: ignore
        except (puremagic.PureError, ValueError):
            # ``PureValueError`` hereda de ``ValueError`` y se lanza, por
            # ejemplo, con un archivo vacío.
            guessed = None

        if guessed in self._readers:
            return guessed

        hinted = self._normalize_mime(mime_type)
        if hinted in self._readers:
            return hinted

        raise BadRequestError(
            "Formato no soportado: se espera un PDF, JPG o PNG de la "
            "Constancia de Situación Fiscal.",
            error_code="UNSUPPORTED_CSF_FORMAT",
            details={"mime_type": mime_type, "detected": guessed},
        )

    @staticmethod
    def _normalize_mime(mime_type: str) -> str:
        """Descarta parámetros y resuelve alias (``image/jpg`` -> ``image/jpeg``)."""
        normalized = (mime_type or "").split(";", 1)[0].strip().lower()
        return _MIME_ALIASES.get(normalized, normalized)

    def _write_temp_file(self, file_bytes: bytes, suffix: str) -> str:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        try:
            temp_file.write(file_bytes)
        finally:
            temp_file.close()
        return temp_file.name

    def _remove_temp_file(self, file_path: str) -> None:
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass
