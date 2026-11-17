from copy import deepcopy
from http import HTTPStatus
from typing import Any, Dict, Optional


def _title_for_status(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return "Error"


class BaseAppException(Exception):
    """Base para excepciones que pueden atravesar el flujo request -> response.

    Cada subclase declara su ``http_status`` y, opcionalmente, si su mensaje y
    detalles pueden exponerse al cliente. Las excepciones internas
    (infraestructura, base de datos, proveedores externos) quedan como
    ``is_public = False``: el handler responde 500 con un mensaje genérico y
    deja el detalle real únicamente en los logs.
    """

    http_status: int = 500
    default_error_code: str = "INTERNAL_ERROR"
    default_title: str = "Internal Server Error"
    is_public: bool = False

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None,
        title: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> None:
        super().__init__(message)

        self.error_code: str = error_code or self.default_error_code
        self.details: Dict[str, Any] = deepcopy(details) if details else {}

        if http_status is not None:
            self.http_status = http_status
        if title is not None:
            self.title = title
        elif http_status is not None:
            self.title = _title_for_status(self.http_status)
        else:
            self.title = self.default_title or _title_for_status(self.http_status)
        if is_public is not None:
            self.is_public = is_public

    @property
    def status_code(self) -> int:
        """Alias de ``http_status`` para consumidores que esperan ese nombre."""
        return self.http_status

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.args[0]}"

    def get_message(self) -> str:
        return self.args[0] if self.args else "Sin error encontrado"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.args[0],
            "error_code": self.error_code,
            "details": deepcopy(self.details),
            "type": self.__class__.__name__,
        }

    def to_http_dict(self) -> Dict[str, Any]:
        """Envelope uniforme de error para respuestas HTTP."""
        if self.is_public:
            message = self.get_message()
            details = deepcopy(self.details)
        else:
            message = "Ocurrió un error interno."
            details = {}

        return {
            "title": self.title,
            "status": self.http_status,
            "error_code": self.error_code,
            "message": message,
            "details": details,
        }


class NotFoundError(BaseAppException):
    http_status = 404
    default_error_code = "NOT_FOUND"
    default_title = "Not Found"
    is_public = True

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message, error_code=error_code, details=details, **kwargs
        )


class BadRequestError(BaseAppException):
    http_status = 400
    default_error_code = "BAD_REQUEST"
    default_title = "Bad Request"
    is_public = True

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message, error_code=error_code, details=details, **kwargs
        )


class ConflictError(BaseAppException):
    http_status = 409
    default_error_code = "CONFLICT"
    default_title = "Conflict"
    is_public = True

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message, error_code=error_code, details=details, **kwargs
        )


class UnprocessableEntityError(BaseAppException):
    http_status = 422
    default_error_code = "UNPROCESSABLE_ENTITY"
    default_title = "Unprocessable Entity"
    is_public = True

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message, error_code=error_code, details=details, **kwargs
        )
