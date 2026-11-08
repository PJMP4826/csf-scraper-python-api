from typing import Any, Dict, Optional

from fastapi.responses import JSONResponse

_TITLES: Dict[int, str] = {
    200: "OK",
    201: "CREATED",
    400: "BAD REQUEST",
    404: "NOT FOUND",
    422: "UNPROCESSABLE ENTITY",
    500: "INTERNAL SERVER ERROR",
    502: "BAD GATEWAY",
    503: "SERVICE UNAVAILABLE",
}


def _title_for(status_code: int) -> str:
    return _TITLES.get(status_code, "ERROR")


def success_response(
    *,
    status_code: int,
    message: str,
    data: Any = None,
) -> JSONResponse:
    """Envelope único de respuesta exitosa."""
    return JSONResponse(
        status_code=status_code,
        content={
            "status": status_code,
            "title": _title_for(status_code),
            "message": message,
            "data": data,
            "error_code": None,
            "details": None,
        },
    )


def error_response(
    *,
    status_code: int,
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """Envelope único de respuesta de error."""
    return JSONResponse(
        status_code=status_code,
        content={
            "status": status_code,
            "title": _title_for(status_code),
            "message": message,
            "data": None,
            "error_code": error_code,
            "details": details,
        },
    )
