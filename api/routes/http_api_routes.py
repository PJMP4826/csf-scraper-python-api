from fastapi import APIRouter, Depends, File, UploadFile

from api.http.controllers.tax_payer_info_extractor_controller import (
    TaxPayerInfoExtractorController,
    get_tax_payer_info_extractor_controller,
)

router = APIRouter(prefix="/api")


@router.post("/fiscal-info/csf")
async def extract_tax_payer_info(
    file: UploadFile = File(...),
    controller: TaxPayerInfoExtractorController = Depends(
        get_tax_payer_info_extractor_controller
    ),
):
    return await controller.handle(file)
