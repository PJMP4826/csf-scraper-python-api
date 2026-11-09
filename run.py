import os
import sys
import multiprocessing
import socket
import uvicorn
from typing import Union

# --- TRUCO CRUCIAL PARA --noconsole ---
# Windows Forms matará el proceso si intenta escribir en una consola inexistente.
# Redireccionamos stdout y stderr a la nada (devnull) solo si no existen.
IS_WINDOWED = sys.stdout is None or sys.stderr is None

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

if __name__ == "__main__":
    # Soporte obligatorio para multiprocesamiento en ejecutables congelados
    multiprocessing.freeze_support()

from main import app


def is_server_running(host: str, port: int) -> bool:
    """Reutilizamos tu lógica de chequeo de puerto para evitar duplicados."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def run_server(host: str, port: Union[str, int]) -> None:
    """Función para ejecutar el servidor FastAPI."""
    default_log_level = "critical" if IS_WINDOWED else "info"
    log_level = os.getenv("LOG_LEVEL", default_log_level)
    access_log = env_bool("ACCESS_LOG", not IS_WINDOWED)

    try:
        uvicorn.run(
            app,  # Pasamos el objeto directo, no el string "main:app"
            host=host,
            port=int(port),
            reload=False,
            workers=1,
            log_level=log_level,
            access_log=access_log,
        )
    except Exception as exception:
        if not IS_WINDOWED:
            print(f"FATAL ERROR: {exception}", file=sys.stderr)
        sys.exit(1)


def run_app() -> None:
    host = os.getenv("HOST_SERVER", "0.0.0.0")
    port = int(os.getenv("PORT_SERVER", 38401))

    # Si el puerto ya está ocupado, cerramos silenciosamente
    if is_server_running(host, port):
        sys.exit(0)

    run_server(host=host, port=port)


if __name__ == "__main__":
    run_app()
