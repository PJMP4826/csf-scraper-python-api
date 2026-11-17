from typing import Any

from api.http.schemas.base import ErrorEnvelope

ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {
        "model": ErrorEnvelope,
        "description": "Archivo inválido o no soportado.",
    },
    422: {
        "model": ErrorEnvelope,
        "description": "El archivo no pudo procesarse.",
    },
    500: {
        "model": ErrorEnvelope,
        "description": "Error interno o de configuración.",
    },
    502: {
        "model": ErrorEnvelope,
        "description": "Fallo del SAT o del lector externo.",
    },
}

DOWNLOAD_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    **ERROR_RESPONSES,
    404: {
        "model": ErrorEnvelope,
        "description": "La constancia no está disponible en el SAT.",
    },
    503: {
        "model": ErrorEnvelope,
        "description": "No fue posible conectar con el SAT.",
    },
}
