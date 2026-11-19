def get_download_csf_use_case():
    """Caso de uso para descargar la CSF con credenciales FIEL."""
    from src.application.use_cases.download_csf_use_case import (
        DownloadCsfUseCase,
    )
    from src.bootstraps.infrastructure_bootstrap_services import (
        get_pdf_csf_downloader,
    )

    return DownloadCsfUseCase(downloader=get_pdf_csf_downloader())


def get_download_opinion_cumplimiento_use_case():
    """Caso de uso para descargar la Opinión de Cumplimiento con FIEL."""
    from src.application.use_cases.download_opinion_cumplimiento_use_case import (
        DownloadOpinionCumplimientoUseCase,
    )
    from src.bootstraps.infrastructure_bootstrap_services import (
        get_pdf_opinion_cumplimiento_downloader,
    )

    return DownloadOpinionCumplimientoUseCase(
        downloader=get_pdf_opinion_cumplimiento_downloader()
    )
