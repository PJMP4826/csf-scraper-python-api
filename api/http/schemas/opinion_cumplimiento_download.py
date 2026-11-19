from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, Field, SecretStr


class OpinionCumplimientoDownloadRequest(BaseModel):
    """Credenciales FIEL para descargar la Opinión de Cumplimiento."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    certificate: UploadFile
    private_key: UploadFile
    pass_phrase: SecretStr = Field(min_length=1)
