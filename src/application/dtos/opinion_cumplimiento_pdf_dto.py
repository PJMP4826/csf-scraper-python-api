from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OpinionCumplimientoPdfDto:
    """PDF de la Opinión de Cumplimiento descargada."""

    pdf_contents: bytes
    file_name: str
