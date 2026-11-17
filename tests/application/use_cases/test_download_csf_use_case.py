import asyncio
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

from src.application.dtos import CsfPdfDto
from src.application.use_cases import DownloadCsfUseCase
from src.domain.errors import InvalidCertificateError

_PASSWORD = "super-secret"
_RFC = "DIM8701081LA"


class _FakeDownloader:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.result = CsfPdfDto(b"%PDF-1.7 constancia", "constancia.pdf")

    async def download(
        self,
        *,
        certificate: bytes,
        private_key: bytes,
        pass_phrase: str,
    ) -> CsfPdfDto:
        self.calls.append(
            {
                "certificate": certificate,
                "private_key": private_key,
                "pass_phrase": pass_phrase,
            }
        )
        return self.result


def _build_material() -> SimpleNamespace:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name(
        [
            x509.NameAttribute(
                NameOID.X500_UNIQUE_IDENTIFIER, f"{_RFC}/DIMX870108HDFXXX01"
            )
        ]
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

    return SimpleNamespace(
        key=key,
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


@pytest.mark.parametrize("as_pem", [False, True])
def test_execute_validates_and_forwards_der_credentials(
    material: SimpleNamespace, as_pem: bool
) -> None:
    certificate = (
        material.certificate_pem if as_pem else material.certificate_der
    )
    private_key = (
        material.private_key_pem if as_pem else material.private_key_der
    )
    downloader = _FakeDownloader()
    use_case = DownloadCsfUseCase(downloader=downloader)

    result = asyncio.run(
        use_case.execute(
            certificate=certificate,
            private_key=private_key,
            pass_phrase=_PASSWORD,
        )
    )

    assert result == downloader.result
    assert len(downloader.calls) == 1

    call = downloader.calls[0]
    assert call["pass_phrase"] == _PASSWORD

    forwarded_certificate = x509.load_der_x509_certificate(
        call["certificate"]  # type: ignore[arg-type]
    )
    forwarded_private_key = load_der_private_key(
        call["private_key"],  # type: ignore[arg-type]
        _PASSWORD.encode(),
    )

    assert (
        forwarded_certificate.public_bytes(Encoding.DER)
        == material.certificate_der
    )
    assert (
        forwarded_private_key.public_key().public_numbers()
        == material.key.public_key().public_numbers()
    )


def test_execute_rejects_invalid_credentials_before_downloading(
    material: SimpleNamespace,
) -> None:
    downloader = _FakeDownloader()
    use_case = DownloadCsfUseCase(downloader=downloader)

    with pytest.raises(InvalidCertificateError):
        asyncio.run(
            use_case.execute(
                certificate=b"not a certificate",
                private_key=material.private_key_der,
                pass_phrase=_PASSWORD,
            )
        )

    assert downloader.calls == []
