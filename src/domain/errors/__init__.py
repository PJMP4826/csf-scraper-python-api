"""Excepciones de dominio."""

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
from src.domain.errors.invalid_credentials_error import (
    CertificateKeyMismatchError,
    EmptyCredentialsError,
    InvalidCertificateError,
    InvalidCredentialsError,
    InvalidPrivateKeyError,
    InvalidRfcInCertificateError,
    PrivateKeyExportError,
    RfcNotFoundError,
)

__all__ = [
    "CertificateKeyMismatchError",
    "ConstanciaDownloadError",
    "ConstanciaNotAvailableError",
    "EmptyCredentialsError",
    "FielCredentialsDownloadError",
    "InvalidCertificateError",
    "InvalidConstanciaPdfError",
    "InvalidCredentialsError",
    "InvalidPrivateKeyError",
    "InvalidRfcInCertificateError",
    "PrivateKeyExportError",
    "RfcNotFoundError",
    "SatFormNotFoundError",
    "SatLoginError",
    "SatNetworkError",
    "SatSsoError",
]
