from typing import Any, Dict, Optional

from src.shared.errors.base_exception import BaseAppException


class InfrastructureException(BaseAppException):
    """Fallo interno de infraestructura (500 por defecto)."""

    http_status = 500

    def __init__(
        self,
        message: str,
        *,
        error_code: str = "INFRASTRUCTURE_EXCEPTION",
        details: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ) -> None:
        final_details = {**(details or {})}
        if status_code is not None:
            final_details["status_code"] = status_code
        if response_body is not None:
            final_details["response_body"] = response_body

        super().__init__(
            message, error_code=error_code, details=final_details
        )


class UpstreamServiceError(InfrastructureException):
    """Un servicio externo (SAT, OCR) falló o no está disponible (502)."""

    http_status = 502

    def __init__(
        self,
        message: str,
        *,
        error_code: str = "UPSTREAM_SERVICE_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ) -> None:
        super().__init__(
            message,
            error_code=error_code,
            details=details,
            status_code=status_code,
            response_body=response_body,
        )


class ConfigurationError(InfrastructureException):
    """Falta configuración o una dependencia del sistema (500)."""

    http_status = 500

    def __init__(
        self,
        message: str,
        *,
        error_code: str = "CONFIGURATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, error_code=error_code, details=details)


class ProcessingError(InfrastructureException):
    """El archivo es válido pero no pudo procesarse (422)."""

    http_status = 422

    def __init__(
        self,
        message: str,
        *,
        error_code: str = "PROCESSING_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, error_code=error_code, details=details)


class HttpException(InfrastructureException):
    def __init__(
        self,
        message: str,
        *,
        url: str,
        method: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        response_headers: Optional[Dict[str, str]] = None,
        error_code: str = "HTTP_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        final_details = {**(details or {})}
        final_details["url"] = url
        final_details["method"] = method
        final_details["response_headers"] = response_headers

        super().__init__(
            message,
            error_code=error_code,
            details=final_details,
            status_code=status_code,
            response_body=response_body,
        )


class LLMException(InfrastructureException):
    def __init__(
        self,
        message: str,
        *,
        model: Optional[str] = None,
        error_code: str = "LLM_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        final_details = {**(details or {})}
        if model:
            final_details["model"] = model

        super().__init__(
            message, error_code=error_code, details=final_details
        )
