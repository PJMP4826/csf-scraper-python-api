import asyncio
from dataclasses import dataclass

import pytest
from csf_scraper import CsfScraperException
from csf_scraper.download import (
    ConstanciaNotAvailableException,
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
from src.infrastructure.adapters import pdf_csf_downloader as adapter_module
from src.infrastructure.adapters.pdf_csf_downloader import PdfCsfDownloader

_CERTIFICATE = b"certificate"
_PRIVATE_KEY = b"private-key"
_PASS_PHRASE = "pass-phrase"


@dataclass
class _FakePdf:
    contents: bytes
    filename: str | None

    def as_bytes(self) -> bytes:
        return self.contents


def _patch_downloader(
    monkeypatch: pytest.MonkeyPatch,
    *,
    pdf: _FakePdf | None = None,
    error: Exception | None = None,
) -> None:
    class _FakeDownloader:
        async def __aenter__(self) -> "_FakeDownloader":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def download(self) -> _FakePdf:
            if error is not None:
                raise error
            assert pdf is not None
            return pdf

    class _FakeConstanciaDownloader:
        @classmethod
        def create(cls, *, credentials: object) -> _FakeDownloader:
            return _FakeDownloader()

    monkeypatch.setattr(
        adapter_module, "ConstanciaDownloader", _FakeConstanciaDownloader
    )


def _download() -> CsfPdfDto:
    return asyncio.run(
        PdfCsfDownloader().download(
            certificate=_CERTIFICATE,
            private_key=_PRIVATE_KEY,
            pass_phrase=_PASS_PHRASE,
        )
    )


def test_download_returns_dto_with_filename(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_downloader(
        monkeypatch,
        pdf=_FakePdf(b"%PDF-1.7 constancia", "constancia_sat.pdf"),
    )

    result = _download()

    assert result == CsfPdfDto(
        pdf_contents=b"%PDF-1.7 constancia",
        file_name="constancia_sat.pdf",
    )


def test_download_uses_default_filename_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_downloader(
        monkeypatch,
        pdf=_FakePdf(b"%PDF-1.7 constancia", None),
    )

    result = _download()

    assert result.file_name == "constancia.pdf"


@pytest.mark.parametrize(
    ("library_exception", "domain_exception", "http_status"),
    [
        (
            FielCredentialsException("invalid credentials"),
            FielCredentialsDownloadError,
            422,
        ),
        (
            SatNetworkException("https://sat.example"),
            SatNetworkError,
            503,
        ),
        (
            SatLoginException("login rejected"),
            SatLoginError,
            502,
        ),
        (
            SatSsoException("sso failed"),
            SatSsoError,
            502,
        ),
        (
            SatFormNotFoundException("form not found"),
            SatFormNotFoundError,
            502,
        ),
        (
            ConstanciaNotAvailableException("not available"),
            ConstanciaNotAvailableError,
            404,
        ),
        (
            InvalidPdfException("invalid pdf"),
            InvalidConstanciaPdfError,
            502,
        ),
        (
            CsfScraperException("unexpected"),
            ConstanciaDownloadError,
            500,
        ),
    ],
)
def test_download_maps_library_exceptions(
    monkeypatch: pytest.MonkeyPatch,
    library_exception: Exception,
    domain_exception: type[ConstanciaDownloadError],
    http_status: int,
) -> None:
    _patch_downloader(monkeypatch, error=library_exception)

    with pytest.raises(domain_exception) as exc_info:
        _download()

    assert exc_info.value.http_status == http_status
    assert exc_info.value.__cause__ is library_exception


def test_sat_network_error_keeps_request_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_downloader(
        monkeypatch,
        error=SatNetworkException("https://sat.example/login"),
    )

    with pytest.raises(SatNetworkError) as exc_info:
        _download()

    assert exc_info.value.details["url"] == "https://sat.example/login"
