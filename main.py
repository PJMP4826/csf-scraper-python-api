import warnings
from api.routes import http_api_routes
from api.middlewares.cors import add_cors_middleware
from api.http.exception_handlers import register_exception_handlers
from fastapi import FastAPI
from fastapi.responses import JSONResponse

warnings.filterwarnings("ignore", category=UserWarning)

app = FastAPI(
    title="API de Trámites Fiscales",
    docs_url="/docs",
    description=(
        "API para la lectura y descarga de la Constancia de Situación "
        "Fiscal (CSF) y la descarga de la Opinión de Cumplimiento."
    ),
    version="1.0.0",
)


add_cors_middleware(app)
register_exception_handlers(app)


@app.get("/")
async def root():
    return JSONResponse(
        status_code=200,
        content={"status": 200, "message": "Funcionando"},
    )


# http_api
app.include_router(
    http_api_routes.router,
)
