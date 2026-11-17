import re
from dataclasses import dataclass

from cryptography import x509
from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes
from cryptography.hazmat.primitives.serialization import (
    BestAvailableEncryption,
    Encoding,
    PrivateFormat,
    PublicFormat,
    load_der_private_key,
    load_pem_private_key,
)
from cryptography.x509.oid import NameOID
from csf_scraper import InvalidRfcFormatException, Rfc
from pydantic import SecretStr

from src.domain.errors.invalid_credentials_error import (
    CertificateKeyMismatchError,
    EmptyCredentialsError,
    InvalidCertificateError,
    InvalidPrivateKeyError,
    InvalidRfcInCertificateError,
    PrivateKeyExportError,
    RfcNotFoundError,
)
from src.domain.value_objects.credentials import Credentials

_CERTIFICATE_PEM_MARKER = b"CERTIFICATE-----"
_PRIVATE_KEY_PEM_MARKER = b"PRIVATE KEY-----"


@dataclass(frozen=True, slots=True, init=False)
class SatFielCredentials(Credentials):
    """Certificado, llave privada y contraseña de la FIEL del SAT.

    Los archivos del SAT suelen venir en DER (``.cer`` y ``.key``); el value
    object los normaliza a PEM y valida que la llave corresponda al
    certificado. La contraseña se guarda como ``SecretStr`` para no filtrarla
    en ``repr``, logs ni mensajes de error.
    """

    certificate_pem: str
    private_key_pem: str
    pass_phrase: SecretStr
    _rfc: Rfc

    def __init__(
        self,
        certificate: bytes | str,
        private_key: bytes | str,
        pass_phrase: str | SecretStr,
    ) -> None:
        secret = (
            pass_phrase
            if isinstance(pass_phrase, SecretStr)
            else SecretStr(pass_phrase)
        )

        self._ensure_not_empty(certificate, private_key, secret)

        password = secret.get_secret_value().encode("utf-8")
        certificate_pem = self._normalize_certificate(certificate)
        private_key_pem = self._normalize_private_key(private_key, password)

        parsed_certificate = self._load_certificate(certificate_pem)
        parsed_private_key = self._load_private_key(private_key_pem, password)

        self._ensure_certificate_matches_private_key(
            parsed_certificate, parsed_private_key
        )
        rfc = self._extract_rfc(parsed_certificate)

        object.__setattr__(self, "certificate_pem", certificate_pem)
        object.__setattr__(self, "private_key_pem", private_key_pem)
        object.__setattr__(self, "pass_phrase", secret)
        object.__setattr__(self, "_rfc", rfc)

    @property
    def rfc(self) -> Rfc:
        return self._rfc

    @staticmethod
    def _as_bytes(value: bytes | str) -> bytes:
        return value if isinstance(value, bytes) else value.encode("utf-8")

    @staticmethod
    def _as_text(value: bytes | str) -> str:
        return value if isinstance(value, str) else value.decode("utf-8")

    @classmethod
    def _has_pem_marker(cls, value: bytes | str, marker: bytes) -> bool:
        return marker in cls._as_bytes(value)

    @staticmethod
    def _is_empty(value: bytes | str | SecretStr) -> bool:
        if isinstance(value, SecretStr):
            return not value.get_secret_value().strip()
        if isinstance(value, bytes):
            return not value.strip()
        return not value.strip()

    @classmethod
    def _ensure_not_empty(
        cls,
        certificate: bytes | str,
        private_key: bytes | str,
        pass_phrase: SecretStr,
    ) -> None:
        if (
            cls._is_empty(certificate)
            or cls._is_empty(private_key)
            or cls._is_empty(pass_phrase)
        ):
            raise EmptyCredentialsError()

    def _normalize_certificate(self, certificate: bytes | str) -> str:
        if self._has_pem_marker(certificate, _CERTIFICATE_PEM_MARKER):
            return self._as_text(certificate)

        try:
            parsed = x509.load_der_x509_certificate(self._as_bytes(certificate))
        except (ValueError, TypeError, UnsupportedAlgorithm) as exception:
            raise InvalidCertificateError(
                details={"reason": str(exception)}
            ) from exception

        return parsed.public_bytes(Encoding.PEM).decode("ascii")

    def _normalize_private_key(
        self, private_key: bytes | str, password: bytes
    ) -> str:
        if self._has_pem_marker(private_key, _PRIVATE_KEY_PEM_MARKER):
            return self._as_text(private_key)

        parsed = self._load_key(
            self._as_bytes(private_key), password, der=True
        )

        try:
            pem = parsed.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=BestAvailableEncryption(password),
            )
        except (ValueError, TypeError, UnsupportedAlgorithm) as exception:
            raise PrivateKeyExportError(
                details={"reason": str(exception)}
            ) from exception

        return pem.decode("ascii")

    @staticmethod
    def _load_key(
        data: bytes, password: bytes | None, *, der: bool
    ) -> PrivateKeyTypes:
        loader = load_der_private_key if der else load_pem_private_key
        first_error: Exception | None = None

        if password:
            try:
                return loader(data, password)
            except (ValueError, TypeError, UnsupportedAlgorithm) as exception:
                first_error = exception

        try:
            return loader(data, None)
        except (ValueError, TypeError, UnsupportedAlgorithm) as exception:
            reason = first_error or exception
            raise InvalidPrivateKeyError(
                details={"reason": str(reason)}
            ) from exception

    def _load_certificate(self, certificate_pem: str) -> x509.Certificate:
        try:
            return x509.load_pem_x509_certificate(
                certificate_pem.encode("ascii")
            )
        except (ValueError, TypeError, UnsupportedAlgorithm) as exception:
            raise InvalidCertificateError(
                details={"reason": str(exception)}
            ) from exception

    def _load_private_key(
        self, private_key_pem: str, password: bytes
    ) -> PrivateKeyTypes:
        return self._load_key(
            private_key_pem.encode("ascii"), password, der=False
        )

    @staticmethod
    def _ensure_certificate_matches_private_key(
        certificate: x509.Certificate, private_key: PrivateKeyTypes
    ) -> None:
        certificate_key = certificate.public_key().public_bytes(
            encoding=Encoding.DER,
            format=PublicFormat.SubjectPublicKeyInfo,
        )
        private_key_public = private_key.public_key().public_bytes(
            encoding=Encoding.DER,
            format=PublicFormat.SubjectPublicKeyInfo,
        )

        if certificate_key != private_key_public:
            raise CertificateKeyMismatchError()

    @staticmethod
    def _extract_rfc(certificate: x509.Certificate) -> Rfc:
        attributes = certificate.subject.get_attributes_for_oid(
            NameOID.X500_UNIQUE_IDENTIFIER
        )
        identifier = str(attributes[0].value).strip() if attributes else ""
        candidate = (
            re.split(r"[ /]+", identifier, maxsplit=1)[0].strip().upper()
            if identifier
            else ""
        )

        if not candidate:
            serial_attributes = certificate.subject.get_attributes_for_oid(
                NameOID.SERIAL_NUMBER
            )
            candidate = (
                str(serial_attributes[0].value).strip().upper()
                if serial_attributes
                else ""
            )

        if not candidate:
            raise RfcNotFoundError()

        try:
            return Rfc(candidate)
        except InvalidRfcFormatException as exception:
            raise InvalidRfcInCertificateError(
                details={"reason": str(exception), "rfc": candidate}
            ) from exception
