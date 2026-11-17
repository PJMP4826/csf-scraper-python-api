from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse, Response

from api.http.controllers.csf_download_controller import (
    CsfDownloadController,
    get_csf_download_controller,
)
from api.http.controllers.tax_payer_info_extractor_controller import (
    TaxPayerInfoExtractorController,
    get_tax_payer_info_extractor_controller,
)
from api.http.openapi_responses import (
    DOWNLOAD_ERROR_RESPONSES,
    ERROR_RESPONSES,
)
from api.http.schemas import CsfDownloadRequest, TaxPayerInfoResponse

router = APIRouter(prefix="/api")


@router.post(
    "/fiscal-info/csf",
    response_class=JSONResponse,
    responses={
        200: {
            "model": TaxPayerInfoResponse,
            "description": "Información fiscal extraída exitosamente.",
        },
        **ERROR_RESPONSES,
    },
)
async def extract_tax_payer_info(
    file: UploadFile = File(...),
    controller: TaxPayerInfoExtractorController = Depends(
        get_tax_payer_info_extractor_controller
    ),
):
    return await controller.handle(file)


@router.post(
    "/fiscal-info/csf/download",
    response_class=Response,
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": (
                "Constancia de Situación Fiscal descargada en PDF."
            ),
        },
        **DOWNLOAD_ERROR_RESPONSES,
    },
)
async def download_csf(
    request: Annotated[
        CsfDownloadRequest, Form(media_type="multipart/form-data")
    ],
    controller: CsfDownloadController = Depends(
        get_csf_download_controller
    ),
) -> Response:
    return await controller.handle(request)
