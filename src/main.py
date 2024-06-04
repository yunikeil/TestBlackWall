import os
import json
import logging
import secrets
from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from core.settings import config
from core.database.initiator import init_models
from core.redis.client import get_redis_client, pool
from core.logging.handlers import ErrorHandlerTG, WarningHandlerTG
from core.utils.setup import setup_helper
from app.routers.binance import binance_router

# Нужно для корректной работы SetupHelper
from app.scrappers import binance



current_file_path = os.path.abspath(__file__)
locales_path = os.path.join(os.path.dirname(current_file_path), "_locales")
openapi_tags = json.loads(open(f"{locales_path}/tags_metadata.json", "r").read())
docs_development_security = HTTPBasic()


@asynccontextmanager
async def lifespan(app: FastAPI):
    error_tg_handler = ErrorHandlerTG()
    warning_tg_handler = WarningHandlerTG()

    uvi_access_logger = logging.getLogger("uvicorn.access")
    uvi_access_logger.addHandler(warning_tg_handler)

    uvi_logger = logging.getLogger("uvicorn")
    uvi_logger.addHandler(warning_tg_handler)
    uvi_logger.addHandler(error_tg_handler)

    await init_models(drop_all=config.DROP_TABLES)

    async with get_redis_client() as client:
        uvi_logger.info(f"Redis ping returned with: {await client.ping()}.")

    setup_helper.start_setup()

    yield

    await pool.aclose()
    uvi_logger.info("RedisPool closed.")


app = FastAPI(
    debug=config.DEBUG,
    version=config.VERSION,
    title=config.TITLE,
    summary=config.SUMMARY,
    openapi_tags=openapi_tags,
    openapi_url="/openapi.json" if config.DEBUG else None,
    docs_url="/docs" if config.DEBUG else None,
    redoc_url=None,
    lifespan=lifespan,
)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if config.DEBUG:
    from fastapi.responses import RedirectResponse

    @app.get("/", include_in_schema=False)
    async def base_redirect_to_docs():
        return RedirectResponse(url="/docs")


app.include_router(binance_router)


def __temp_get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(docs_development_security)]
):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = bytes(config.DOCS_USERNAME)
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = bytes(config.DOCS_PASSWORD)
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
        
    return credentials.username


@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation(
    _: str = Depends(__temp_get_current_username),
):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/openapi.json", include_in_schema=False)
async def openapi(_: str = Depends(__temp_get_current_username)):
    return get_openapi(
        title=config.TITLE, version=config.VERSION, routes=app.routes, tags=openapi_tags
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="main:app",
        host=config.SERVER_IP,
        port=config.SERVER_PORT,
        reload=config.DEBUG,
        proxy_headers=not config.DEBUG,
    )
