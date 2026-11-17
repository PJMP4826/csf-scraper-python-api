from typing import Any

from src.shared.errors.base_exception import UnprocessableEntityError


class InvalidCredentialsError(UnprocessableEntityError):
    """Base de los errores semánticos de credenciales FIEL."""

    http_status = 422
    default_error_code = "INVALID_FIEL_CREDENTIALS"
    default_title = "Invalid FIEL Credentials"
    is_public = True

    def __init__(
        self,
        message: str = "Las credenciales FIEL no son válidas.",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class EmptyCredentialsError(InvalidCredentialsError):
    """El certificado, la llave o la contraseña están vacíos."""

    default_error_code = "EMPTY_FIEL_CREDENTIALS"
    default_title = "Empty FIEL Credentials"

    def __init__(
        self,
        message: str = "Las credenciales FIEL no pueden estar vacías.",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class InvalidCertificateError(InvalidCredentialsError):
    """El certificado no pudo interpretarse como X.509."""

    default_error_code = "INVALID_FIEL_CERTIFICATE"
    default_title = "Invalid FIEL Certificate"

    def __init__(
        self,
        message: str = "El certificado proporcionado no es válido.",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class InvalidPrivateKeyError(InvalidCredentialsError):
    """La llave privada no pudo cargarse o la contraseña es incorrecta."""

    default_error_code = "INVALID_FIEL_PRIVATE_KEY"
    default_title = "Invalid FIEL Private Key"

    def __init__(
        self,
        message: str = (
            "La contraseña de la llave privada es incorrecta o el archivo "
            "está corrupto."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class CertificateKeyMismatchError(InvalidCredentialsError):
    """La llave privada no corresponde al certificado."""

    default_error_code = "FIEL_CERTIFICATE_KEY_MISMATCH"
    default_title = "FIEL Certificate Key Mismatch"

    def __init__(
        self,
        message: str = (
            "La llave privada no corresponde al certificado proporcionado."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class PrivateKeyExportError(InvalidCredentialsError):
    """La llave cargada no pudo exportarse a PEM."""

    default_error_code = "FIEL_PRIVATE_KEY_EXPORT_FAILED"
    default_title = "FIEL Private Key Export Failed"

    def __init__(
        self,
        message: str = "La llave privada no pudo convertirse a PEM.",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class RfcNotFoundError(InvalidCredentialsError):
    """El certificado no contiene un RFC en su subject."""

    default_error_code = "FIEL_RFC_NOT_FOUND"
    default_title = "FIEL RFC Not Found"

    def __init__(
        self,
        message: str = (
            "No se pudo encontrar el RFC en el certificado proporcionado."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class InvalidRfcInCertificateError(InvalidCredentialsError):
    """El RFC extraído del certificado no cumple el formato esperado."""

    default_error_code = "INVALID_FIEL_RFC"
    default_title = "Invalid FIEL RFC"

    def __init__(
        self,
        message: str = (
            "El RFC contenido en el certificado no tiene un formato válido."
        ),
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
