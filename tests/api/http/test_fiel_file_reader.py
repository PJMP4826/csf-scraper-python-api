import asyncio
import io

import pytest
from starlette.datastructures import UploadFile

from api.http.fiel_file_reader import MAX_FIEL_FILE_SIZE, read_fiel_file
from src.shared.errors.base_exception import BadRequestError


def _file(content: bytes) -> UploadFile:
    return UploadFile(filename="fiel.cer", file=io.BytesIO(content))


def test_returns_file_contents() -> None:
    content = b"certificate"

    assert (
        asyncio.run(read_fiel_file(_file(content), "certificado")) == content
    )


def test_rejects_empty_file() -> None:
    with pytest.raises(BadRequestError) as exc_info:
        asyncio.run(read_fiel_file(_file(b""), "certificado"))

    assert exc_info.value.http_status == 400
    assert exc_info.value.error_code == "EMPTY_FIEL_FILE"


def test_rejects_file_over_limit() -> None:
    content = b"x" * (MAX_FIEL_FILE_SIZE + 1)

    with pytest.raises(BadRequestError) as exc_info:
        asyncio.run(read_fiel_file(_file(content), "llave privada"))

    assert exc_info.value.http_status == 400
    assert exc_info.value.error_code == "FIEL_FILE_TOO_LARGE"


def test_accepts_file_at_limit() -> None:
    content = b"x" * MAX_FIEL_FILE_SIZE

    assert (
        asyncio.run(read_fiel_file(_file(content), "certificado")) == content
    )
