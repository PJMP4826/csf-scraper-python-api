import asyncio
from dataclasses import dataclass

import pytest
from opinion_scraper import (
    AuthenticationException,
    FederationException,
    FielCredentialsException,
    InvalidOpinionResponseException,
    InvalidPdfException,
    InvalidRfcException,
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
from src.infrastructure.adapters import (
    pdf_opinion_cumplimiento_downloader as adapter_module,
)
from src.infrastructure.adapters.pdf_opinion_cumplimiento_downloader import (
    PdfOpinionCumplimientoDownloader,
)

_CERTIFICATE = b"certificate"
_PRIVATE_KEY = b"private-key"
_PASS_PHRASE = "pass-phrase"


@dataclass
class _FakePdf:
    content: bytes
    filename: str | None

    def as_bytes(self) -> bytes:
        return self.content


def _patch_downloader(
    monkeypatch: pytest.MonkeyPatch,
    *,
    pdf: _FakePdf | None = None,
    error: Exception | None = None,
) -> None:
    class _FakeOpinionDownloader:
        async def __aenter__(self) -> "_FakeOpinionDownloader":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def download(self) -> _FakePdf:
            if error is not None:
                raise error
            assert pdf is not None
            return pdf

    class _FakeOpinionDownloaderFactory:
        @classmethod
        def create(cls, *, credentials: object) -> _FakeOpinionDownloader:
            return _FakeOpinionDownloader()

    monkeypatch.setattr(
        adapter_module, "OpinionDownloader", _FakeOpinionDownloaderFactory
    )


def _download() -> OpinionCumplimientoPdfDto:
    return asyncio.run(
        PdfOpinionCumplimientoDownloader().download(
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
        pdf=_FakePdf(b"%PDF-1.7 opinion", "opinion_sat.pdf"),
    )

    result = _download()

    assert result == OpinionCumplimientoPdfDto(
        pdf_contents=b"%PDF-1.7 opinion",
        file_name="opinion_sat.pdf",
    )


def test_download_uses_default_filename_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_downloader(
        monkeypatch,
        pdf=_FakePdf(b"%PDF-1.7 opinion", None),
    )

    result = _download()

    assert result.file_name == "opinion_cumplimiento.pdf"


@pytest.mark.parametrize(
    ("library_exception", "domain_exception", "http_status"),
    [
        (
            FielCredentialsException("invalid credentials"),
            OpinionFielCredentialsError,
            422,
        ),
        (
            SatNetworkException("https://sat.example"),
            OpinionSatNetworkError,
            503,
        ),
        (
            SatLoginException("login rejected"),
            OpinionSatLoginError,
            502,
        ),
        (
            FederationException("federation failed"),
            OpinionSatFederationError,
            502,
        ),
        (
            AuthenticationException("bootstrap", "auth failed"),
            OpinionSatAuthenticationError,
            502,
        ),
        (
            SatFormNotFoundException("form not found"),
            OpinionSatFormNotFoundError,
            502,
        ),
        (
            OpinionNotAvailableException("404", "not available"),
            OpinionNotAvailableError,
            404,
        ),
        (
            InvalidPdfException("invalid pdf"),
            InvalidOpinionPdfError,
            502,
        ),
        (
            InvalidOpinionResponseException("invalid response"),
            InvalidOpinionResponseError,
            502,
        ),
        (
            InvalidRfcException("invalid rfc"),
            InvalidOpinionRfcError,
            422,
        ),
        (
            OpinionScraperException("unexpected"),
            OpinionCumplimientoDownloadError,
            500,
        ),
    ],
)
def test_download_maps_library_exceptions(
    monkeypatch: pytest.MonkeyPatch,
    library_exception: Exception,
    domain_exception: type[OpinionCumplimientoDownloadError],
    http_status: int,
) -> None:
    _patch_downloader(monkeypatch, error=library_exception)

    with pytest.raises(domain_exception) as exc_info:
        _download()

    assert exc_info.value.http_status == http_status
    assert exc_info.value.__cause__ is library_exception


def test_sat_network_error_keeps_request_url_and_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_downloader(
        monkeypatch,
        error=SatNetworkException("https://sat.example/login", 500),
    )

    with pytest.raises(OpinionSatNetworkError) as exc_info:
        _download()

    assert exc_info.value.details["url"] == "https://sat.example/login"
    assert exc_info.value.details["status_code"] == 500


def test_opinion_not_available_keeps_sat_codes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_downloader(
        monkeypatch,
        error=OpinionNotAvailableException("404", "sin opinion"),
    )

    with pytest.raises(OpinionNotAvailableError) as exc_info:
        _download()

    assert exc_info.value.details["codigo"] == "404"
    assert exc_info.value.details["mensaje"] == "sin opinion"
