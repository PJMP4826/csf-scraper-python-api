from typing import Any, Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class SuccessEnvelope(BaseModel, Generic[DataT]):
    status: int
    title: str
    message: str
    data: DataT
    error_code: None = None
    details: None = None


class ErrorEnvelope(BaseModel):
    status: int
    title: str
    message: str
    data: None = None
    error_code: str | None = None
    details: dict[str, Any] | None = None
