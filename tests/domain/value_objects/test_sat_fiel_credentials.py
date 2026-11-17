from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    BestAvailableEncryption,
    Encoding,
    PrivateFormat,
    load_der_private_key,
)
from cryptography.x509.oid import NameOID
from csf_scraper import Rfc

from src.domain.errors.invalid_credentials_error import (
    CertificateKeyMismatchError,
    EmptyCredentialsError,
    InvalidCertificateError,
    InvalidCredentialsError,
    InvalidPrivateKeyError,
    InvalidRfcInCertificateError,
    RfcNotFoundError,
)
from src.domain.value_objects.sat_fiel_credentials import SatFielCredentials
from src.shared.errors.base_exception import UnprocessableEntityError

_PASSWORD = "super-secret"
_RFC = "DIM8701081LA"


def _build_material(
    *,
    rfc: str = _RFC,
    unique_identifier: str | None = None,
    use_serial_fallback: bool = False,
) -> SimpleNamespace:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    attributes = [
        x509.NameAttribute(NameOID.COMMON_NAME, "Credenciales FIEL de prueba")
    ]
    if use_serial_fallback:
        attributes.append(
            x509.NameAttribute(NameOID.SERIAL_NUMBER, rfc)
        )
    else:
        attributes.append(
            x509.NameAttribute(
                NameOID.X500_UNIQUE_IDENTIFIER,
                unique_identifier or f"{rfc}/DIMX870108HDFXXX01",
            )
        )

    subject = x509.Name(attributes)
    now = datetime.now(timezone.utc)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=365))
        .sign(key, hashes.SHA256())
    )

    return SimpleNamespace(
        key=key,
        certificate=certificate,
        certificate_der=certificate.public_bytes(Encoding.DER),
        certificate_pem=certificate.public_bytes(Encoding.PEM),
        private_key_der=key.private_bytes(
            Encoding.DER,
            PrivateFormat.PKCS8,
            BestAvailableEncryption(_PASSWORD.encode()),
        ),
        private_key_pem=key.private_bytes(
            Encoding.PEM,
            PrivateFormat.PKCS8,
            BestAvailableEncryption(_PASSWORD.encode()),
        ),
    )


@pytest.fixture(scope="module")
def material() -> SimpleNamespace:
    return _build_material()


def test_der_inputs_are_normalized_to_pem(material: SimpleNamespace) -> None:
    credentials = SatFielCredentials(
        material.certificate_der,
        material.private_key_der,
        _PASSWORD,
    )

    assert credentials.certificate_pem.startswith(
        "-----BEGIN CERTIFICATE-----"
    )
    assert credentials.private_key_pem.startswith(
        "-----BEGIN ENCRYPTED PRIVATE KEY-----"
    )
    assert credentials.rfc == Rfc(_RFC)


def test_pem_inputs_are_accepted(material: SimpleNamespace) -> None:
    credentials = SatFielCredentials(
        material.certificate_pem,
        material.private_key_pem,
        _PASSWORD,
    )

    assert credentials.certificate_pem == material.certificate_pem.decode()
    assert credentials.private_key_pem == material.private_key_pem.decode()
    assert credentials.rfc == Rfc(_RFC)


@pytest.mark.parametrize(
    "unique_identifier",
    [
        f"{_RFC} DIMX870108HDFXXX01",
        f"{_RFC}/DIMX870108HDFXXX01",
    ],
)
def test_rfc_is_extracted_from_x500_unique_identifier(
    unique_identifier: str,
) -> None:
    current = _build_material(unique_identifier=unique_identifier)

    credentials = SatFielCredentials(
        current.certificate_der,
        current.private_key_der,
        _PASSWORD,
    )

    assert credentials.rfc == Rfc(_RFC)


def test_rfc_falls_back_to_serial_number() -> None:
    current = _build_material(use_serial_fallback=True)

    credentials = SatFielCredentials(
        current.certificate_der,
        current.private_key_der,
        _PASSWORD,
    )

    assert credentials.rfc == Rfc(_RFC)


@pytest.mark.parametrize(
    ("certificate", "private_key", "pass_phrase"),
    [
        (b"", b"key", _PASSWORD),
        (b"certificate", b"", _PASSWORD),
        (b"certificate", b"key", ""),
    ],
)
def test_empty_values_raise_empty_credentials_error(
    certificate: bytes,
    private_key: bytes,
    pass_phrase: str,
) -> None:
    with pytest.raises(EmptyCredentialsError):
        SatFielCredentials(certificate, private_key, pass_phrase)


def test_invalid_certificate_raises_semantic_error(
    material: SimpleNamespace,
) -> None:
    with pytest.raises(InvalidCertificateError):
        SatFielCredentials(
            b"not a certificate",
            material.private_key_der,
            _PASSWORD,
        )


def test_wrong_password_raises_semantic_error(
    material: SimpleNamespace,
) -> None:
    with pytest.raises(InvalidPrivateKeyError):
        SatFielCredentials(
            material.certificate_der,
            material.private_key_der,
            "wrong-password",
        )


def test_mismatched_key_raises_semantic_error(
    material: SimpleNamespace,
) -> None:
    other = _build_material()

    with pytest.raises(CertificateKeyMismatchError):
        SatFielCredentials(
            material.certificate_der,
            other.private_key_der,
            _PASSWORD,
        )


def test_missing_rfc_raises_semantic_error() -> None:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, "Sin RFC")]
    )
    now = datetime.now(timezone.utc)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=365))
        .sign(key, hashes.SHA256())
    )
    private_key = key.private_bytes(
        Encoding.DER,
        PrivateFormat.PKCS8,
        BestAvailableEncryption(_PASSWORD.encode()),
    )

    with pytest.raises(RfcNotFoundError):
        SatFielCredentials(
            certificate.public_bytes(Encoding.DER),
            private_key,
            _PASSWORD,
        )


def test_invalid_rfc_raises_semantic_error() -> None:
    current = _build_material(unique_identifier="NO-ES-UN-RFC")

    with pytest.raises(InvalidRfcInCertificateError):
        SatFielCredentials(
            current.certificate_der,
            current.private_key_der,
            _PASSWORD,
        )


def test_der_properties_can_be_loaded_again(
    material: SimpleNamespace,
) -> None:
    credentials = SatFielCredentials(
        material.certificate_der,
        material.private_key_der,
        _PASSWORD,
    )

    certificate = x509.load_der_x509_certificate(credentials.certificate_der)
    private_key = load_der_private_key(
        credentials.private_key_der, _PASSWORD.encode()
    )

    assert certificate.public_bytes(Encoding.DER) == material.certificate_der
    assert (
        private_key.public_key().public_numbers()
        == material.key.public_key().public_numbers()
    )


def test_password_is_hidden_from_repr(material: SimpleNamespace) -> None:
    credentials = SatFielCredentials(
        material.certificate_der,
        material.private_key_der,
        _PASSWORD,
    )

    assert _PASSWORD not in repr(credentials)
    assert credentials.pass_phrase.get_secret_value() == _PASSWORD


def test_semantic_errors_are_public_unprocessable_entities() -> None:
    error = EmptyCredentialsError()

    assert isinstance(error, InvalidCredentialsError)
    assert isinstance(error, UnprocessableEntityError)
    assert error.http_status == 422
    assert error.is_public is True
    assert error.to_http_dict()["status"] == 422
    assert error.to_http_dict()["message"] == error.get_message()
