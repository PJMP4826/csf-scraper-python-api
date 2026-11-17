from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, Field, SecretStr


class CsfDownloadRequest(BaseModel):
    """Credenciales FIEL para descargar la Constancia de Situación Fiscal."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    certificate: UploadFile
    private_key: UploadFile
    pass_phrase: SecretStr = Field(min_length=1)
