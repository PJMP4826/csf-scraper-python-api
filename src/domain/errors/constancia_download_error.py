from typing import Any, Dict, Optional

from src.shared.errors.infrastructure_exceptions import InfrastructureException


class ConstanciaDownloadError(InfrastructureException):
    """Fallo al descargar la Constancia de Situación Fiscal desde el SAT."""

    http_status = 500
    default_error_code = "CONSTANCIA_DOWNLOAD_FAILED"
    default_title = "Constancia Download Failed"
    is_public = False

    def __init__(
        self,
        message: str = (
            "No fue posible descargar la Constancia de Situación Fiscal."
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


class FielCredentialsDownloadError(ConstanciaDownloadError):
    """Las credenciales FIEL no pudieron usarse para autenticarse."""

    http_status = 422
    default_error_code = "FIEL_CREDENTIALS_DOWNLOAD_FAILED"
    default_title = "FIEL Credentials Download Failed"
    is_public = True

    def __init__(
        self,
        message: str = (
            "Las credenciales FIEL no pudieron utilizarse para descargar la "
            "constancia."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class SatNetworkError(ConstanciaDownloadError):
    """Una petición HTTP al SAT falló por un error de red o transporte."""

    http_status = 503
    default_error_code = "SAT_NETWORK_ERROR"
    default_title = "SAT Network Error"
    is_public = True

    def __init__(
        self,
        message: str = (
            "No fue posible conectar con el SAT. Intenta nuevamente más tarde."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class SatLoginError(ConstanciaDownloadError):
    """El SAT rechazó el inicio de sesión con la FIEL."""

    http_status = 502
    default_error_code = "SAT_LOGIN_ERROR"
    default_title = "SAT Login Error"
    is_public = True

    def __init__(
        self,
        message: str = (
            "El SAT rechazó el inicio de sesión con las credenciales FIEL."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class SatSsoError(ConstanciaDownloadError):
    """El flujo SSO/SAML del SAT no llegó a la página esperada."""

    http_status = 502
    default_error_code = "SAT_SSO_ERROR"
    default_title = "SAT SSO Error"
    is_public = True

    def __init__(
        self,
        message: str = (
            "El flujo de autenticación SSO del SAT no se completó "
            "correctamente."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class SatFormNotFoundError(ConstanciaDownloadError):
    """No se encontró el formulario esperado en la respuesta del SAT."""

    http_status = 502
    default_error_code = "SAT_FORM_NOT_FOUND"
    default_title = "SAT Form Not Found"
    is_public = True

    def __init__(
        self,
        message: str = (
            "El SAT devolvió una página sin el formulario esperado para "
            "descargar la constancia."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class ConstanciaNotAvailableError(ConstanciaDownloadError):
    """El SAT no devolvió la constancia en PDF."""

    http_status = 404
    default_error_code = "CONSTANCIA_NOT_AVAILABLE"
    default_title = "Constancia Not Available"
    is_public = True

    def __init__(
        self,
        message: str = (
            "El SAT no tiene disponible la Constancia de Situación Fiscal "
            "solicitada."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class InvalidConstanciaPdfError(ConstanciaDownloadError):
    """Los bytes recibidos del SAT no corresponden a un PDF válido."""

    http_status = 502
    default_error_code = "INVALID_CONSTANCIA_PDF"
    default_title = "Invalid Constancia PDF"
    is_public = True

    def __init__(
        self,
        message: str = (
            "El SAT devolvió un documento inválido en lugar de la constancia "
            "en PDF."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
