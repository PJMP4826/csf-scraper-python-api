from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.http.responses import error_response
from config.logger import logger
from src.shared.errors.base_exception import BaseAppException

_INTERNAL_MESSAGE = (
    "Ocurrió un error interno. Intenta nuevamente más tarde."
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BaseAppException)
    async def handle_base_app_exception(
        request: Request, exc: BaseAppException
    ) -> JSONResponse:
        payload = exc.to_http_dict()
        status_code = payload["status"]

        if status_code >= 500:
            logger.error(
                "Error %s en %s %s | code=%s",
                status_code,
                request.method,
                request.url.path,
                exc.error_code,
                exc_info=exc,
            )
        else:
            logger.warning(
                "Error %s en %s %s | code=%s | %s",
                status_code,
                request.method,
                request.url.path,
                exc.error_code,
                exc.get_message(),
            )

        return error_response(
            status_code=status_code,
            title=payload["title"],
            message=payload["message"],
            error_code=payload["error_code"],
            details=payload["details"],
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "Error no controlado en %s %s", request.method, request.url.path
        )
        return error_response(
            status_code=500,
            message=_INTERNAL_MESSAGE,
            error_code="INTERNAL_ERROR",
        )
