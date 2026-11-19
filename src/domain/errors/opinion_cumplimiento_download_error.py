from typing import Any, Dict, Optional

from src.shared.errors.infrastructure_exceptions import InfrastructureException


class OpinionCumplimientoDownloadError(InfrastructureException):
    """Fallo al descargar la Opinión de Cumplimiento desde el SAT."""

    http_status = 500
    default_error_code = "OPINION_CUMPLIMIENTO_DOWNLOAD_FAILED"
    default_title = "Opinion Cumplimiento Download Failed"
    is_public = False

    def __init__(
        self,
        message: str = (
            "No fue posible descargar la Opinión de Cumplimiento."
        ),
        *,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message,
            error_code=error_code or self.default_error_code,
            details=details,
            **kwargs,
        )


class OpinionFielCredentialsError(OpinionCumplimientoDownloadError):
    """Las credenciales FIEL no pudieron usarse para autenticarse."""

    http_status = 422
    default_error_code = "OPINION_FIEL_CREDENTIALS_ERROR"
    default_title = "Opinion FIEL Credentials Error"
    is_public = True

    def __init__(
        self,
        message: str = (
            "Las credenciales FIEL no pudieron utilizarse para descargar la "
            "Opinión de Cumplimiento."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class OpinionSatNetworkError(OpinionCumplimientoDownloadError):
    """Una petición HTTP al SAT falló por un error de red o transporte."""

    http_status = 503
    default_error_code = "OPINION_SAT_NETWORK_ERROR"
    default_title = "Opinion SAT Network Error"
    is_public = True

    def __init__(
        self,
        message: str = (
            "No fue posible conectar con el SAT. Intenta nuevamente más tarde."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class OpinionSatLoginError(OpinionCumplimientoDownloadError):
    """El SAT rechazó el inicio de sesión con la FIEL."""

    http_status = 502
    default_error_code = "OPINION_SAT_LOGIN_ERROR"
    default_title = "Opinion SAT Login Error"
    is_public = True

    def __init__(
        self,
        message: str = (
            "El SAT rechazó el inicio de sesión con las credenciales FIEL."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class OpinionSatFederationError(OpinionCumplimientoDownloadError):
    """El flujo de autenticación federada del SAT no se completó."""

    http_status = 502
    default_error_code = "OPINION_SAT_FEDERATION_ERROR"
    default_title = "Opinion SAT Federation Error"
    is_public = True

    def __init__(
        self,
        message: str = (
            "El flujo de autenticación federada del SAT no se completó "
            "correctamente."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class OpinionSatAuthenticationError(OpinionCumplimientoDownloadError):
    """La autenticación con el SAT no llegó a una sesión válida."""

    http_status = 502
    default_error_code = "OPINION_SAT_AUTHENTICATION_ERROR"
    default_title = "Opinion SAT Authentication Error"
    is_public = True

    def __init__(
        self,
        message: str = (
            "La autenticación con el SAT no se completó correctamente."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class OpinionSatFormNotFoundError(OpinionCumplimientoDownloadError):
    """No se encontró el formulario esperado en la respuesta del SAT."""

    http_status = 502
    default_error_code = "OPINION_SAT_FORM_NOT_FOUND"
    default_title = "Opinion SAT Form Not Found"
    is_public = True

    def __init__(
        self,
        message: str = (
            "El SAT devolvió una página sin el formulario esperado para "
            "descargar la Opinión de Cumplimiento."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class OpinionNotAvailableError(OpinionCumplimientoDownloadError):
    """El SAT no devolvió la Opinión de Cumplimiento solicitada."""

    http_status = 404
    default_error_code = "OPINION_NOT_AVAILABLE"
    default_title = "Opinion Not Available"
    is_public = True

    def __init__(
        self,
        message: str = (
            "El SAT no tiene disponible la Opinión de Cumplimiento "
            "solicitada."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class InvalidOpinionPdfError(OpinionCumplimientoDownloadError):
    """Los bytes recibidos del SAT no corresponden a un PDF válido."""

    http_status = 502
    default_error_code = "INVALID_OPINION_PDF"
    default_title = "Invalid Opinion PDF"
    is_public = True

    def __init__(
        self,
        message: str = (
            "El SAT devolvió un documento inválido en lugar de la Opinión de "
            "Cumplimiento en PDF."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class InvalidOpinionResponseError(OpinionCumplimientoDownloadError):
    """La respuesta del portal 32-D no tiene la estructura esperada."""

    http_status = 502
    default_error_code = "INVALID_OPINION_RESPONSE"
    default_title = "Invalid Opinion Response"
    is_public = True

    def __init__(
        self,
        message: str = (
            "El SAT devolvió una respuesta con una estructura inesperada."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class InvalidOpinionRfcError(OpinionCumplimientoDownloadError):
    """El RFC obtenido de la FIEL no cumple el formato esperado."""

    http_status = 422
    default_error_code = "INVALID_OPINION_RFC"
    default_title = "Invalid Opinion RFC"
    is_public = True

    def __init__(
        self,
        message: str = (
            "El RFC contenido en las credenciales FIEL no tiene un formato "
            "válido."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
