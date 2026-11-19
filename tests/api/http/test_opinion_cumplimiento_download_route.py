from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from main import app
from src.application.dtos import OpinionCumplimientoPdfDto
from src.bootstraps.application_bootstrap_services import (
    get_download_opinion_cumplimiento_use_case,
)

_URL = "/api/fiscal-info/opinion-cumplimiento/download"
_FILES = {
    "certificate": ("fiel.cer", b"certificate", "application/octet-stream"),
    "private_key": ("fiel.key", b"private-key", "application/octet-stream"),
}


class _FakeUseCase:
    def __init__(self, result: OpinionCumplimientoPdfDto) -> None:
        self.result = result
        self.calls: list[dict[str, object]] = []

    async def execute(
        self,
        certificate: bytes,
        private_key: bytes,
        pass_phrase: str,
    ) -> OpinionCumplimientoPdfDto:
        self.calls.append(
            {
                "certificate": certificate,
                "private_key": private_key,
                "pass_phrase": pass_phrase,
            }
        )
        return self.result


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _override_use_case(use_case: _FakeUseCase) -> None:
    app.dependency_overrides[
        get_download_opinion_cumplimiento_use_case
    ] = lambda: use_case


def test_download_returns_pdf_response(client: TestClient) -> None:
    use_case = _FakeUseCase(
        OpinionCumplimientoPdfDto(
            b"%PDF-1.7 opinion", "opinion_cumplimiento.pdf"
        )
    )
    _override_use_case(use_case)

    response = client.post(
        _URL,
        files=_FILES,
        data={"pass_phrase": "super-secret"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == (
        'attachment; filename="opinion_cumplimiento.pdf"'
    )
    assert response.content == b"%PDF-1.7 opinion"

    assert use_case.calls == [
        {
            "certificate": b"certificate",
            "private_key": b"private-key",
            "pass_phrase": "super-secret",
        }
    ]


def test_download_rejects_empty_certificate(client: TestClient) -> None:
    use_case = _FakeUseCase(
        OpinionCumplimientoPdfDto(b"%PDF", "opinion.pdf")
    )
    _override_use_case(use_case)

    response = client.post(
        _URL,
        files={
            "certificate": ("fiel.cer", b"", "application/octet-stream"),
            "private_key": _FILES["private_key"],
        },
        data={"pass_phrase": "super-secret"},
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "EMPTY_FIEL_FILE"
    assert use_case.calls == []


def test_download_requires_pass_phrase(client: TestClient) -> None:
    use_case = _FakeUseCase(
        OpinionCumplimientoPdfDto(b"%PDF", "opinion.pdf")
    )
    _override_use_case(use_case)

    response = client.post(
        _URL,
        files=_FILES,
        data={"pass_phrase": ""},
    )

    assert response.status_code == 422
    assert use_case.calls == []
