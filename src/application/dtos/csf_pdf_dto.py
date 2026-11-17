from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CsfPdfDto:
    """PDF de la Constancia de Situación Fiscal descargada."""

    pdf_contents: bytes
    file_name: str
