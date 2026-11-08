def get_tax_payer_info_extractor():
    """Extractor de datos fiscales a partir de una CSF (PDF, JPG o PNG)."""
    from csf_scraper import OpenCvImageReader

    from src.infrastructure.adapters.tax_payer_info_extractor import (
        TaxPayerInfoExtractor,
    )

    image_reader = OpenCvImageReader()
    return TaxPayerInfoExtractor(image_reader=image_reader)
