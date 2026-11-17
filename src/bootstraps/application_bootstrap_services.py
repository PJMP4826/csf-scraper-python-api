def get_download_csf_use_case():
    """Caso de uso para descargar la CSF con credenciales FIEL."""
    from src.application.use_cases.download_csf_use_case import (
        DownloadCsfUseCase,
    )
    from src.bootstraps.infrastructure_bootstrap_services import (
        get_pdf_csf_downloader,
    )

    return DownloadCsfUseCase(downloader=get_pdf_csf_downloader())
