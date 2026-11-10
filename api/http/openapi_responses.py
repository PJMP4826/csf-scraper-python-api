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
