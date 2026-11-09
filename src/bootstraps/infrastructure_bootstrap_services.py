def get_tax_payer_info_extractor():
    """Extractor de datos fiscales a partir de una CSF (PDF, JPG o PNG)."""
    from csf_scraper import CsfPdfExtractor, OpenCvImageReader

    from src.infrastructure.adapters.pdftotext import (
        NoWindowPdfToText,
        resolve_pdftotext,
    )
    from src.infrastructure.adapters.tax_payer_info_extractor import (
        TaxPayerInfoExtractor,
    )

    image_reader = OpenCvImageReader()
    pdf_extractor = CsfPdfExtractor(
        text_provider=NoWindowPdfToText(
            executable=resolve_pdftotext() or "pdftotext",
        ),
    )

    return TaxPayerInfoExtractor(
        image_reader=image_reader,
        pdf_extractor=pdf_extractor,
    )
