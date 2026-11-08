import os
import uvicorn
from main import app  # type: ignore
# from dotenv import load_dotenv
# from pathlib import Path


# def get_project_root() -> Path:
#     """raiz del proyecto."""
#     return Path(__file__).resolve().parent


def run_app():
    # root = get_project_root()
    # print(f"ROOT PROJECT PATH: {str(root)}")
    # load_dotenv(root / ".env")

    # reload = os.getenv("DEBUG_MODE", "false").lower() == "true"

    # print("RELOAD", reload)

    # if os.getenv("DEBUG_MODE") == "true":
    #     import debugpy

    #     debugpy.listen(("0.0.0.0", 5678))
    #     print("Waiting for debugger attach on port 5678...")

    host = os.getenv("HOST_SERVER", "0.0.0.0")
    print(f"HOST SERVER: {os.getenv("HOST_SERVER")}")
    port = int(os.getenv("PORT_SERVER", 8000))

    try:

        print("Server started successfully...")
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            # reload=reload,
            workers=1,
            use_colors=False,
            log_config=None,
        )
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")


if __name__ == "__main__":
    run_app()
