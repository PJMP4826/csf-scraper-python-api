from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse

from api.http.controllers.tax_payer_info_extractor_controller import (
    TaxPayerInfoExtractorController,
    get_tax_payer_info_extractor_controller,
)
from api.http.openapi_responses import ERROR_RESPONSES
from api.http.schemas import TaxPayerInfoResponse

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
