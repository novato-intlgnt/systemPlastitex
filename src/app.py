import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from scalar_fastapi import Layout, get_scalar_api_reference

from src.dev.routes.users import userRouter


def create_app(user_model):
    app = FastAPI(title="Plastitex Dashboard", docs_url="/docs")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:4000",
            "http://127.0.0.1:4000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PUBLIC_DIR = os.path.join(BASE_DIR, "public")

    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(PUBLIC_DIR)),
        name="static",
    )
    app.mount("/js", StaticFiles(directory=os.path.join(PUBLIC_DIR, "js")), name="js")
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(PUBLIC_DIR, "assets")),
        name="assets",
    )
    app.mount("/js", StaticFiles(directory=os.path.join(PUBLIC_DIR, "js")), name="js")
    app.mount(
        "/css", StaticFiles(directory=os.path.join(PUBLIC_DIR, "css")), name="css"
    )

    @app.get("/docs-scalar", include_in_schema=False)
    async def scalar_docs():
        return get_scalar_api_reference(
            openapi_url=app.openapi_url,
            title="Documentación Plastitex API",
            layout=Layout.MODERN,
            dark_mode=True,
            show_sidebar=True,
            default_open_all_tags=True,
            hide_download_button=False,
            hide_models=False,
        )

    # Rutas HTML
    @app.get("/")
    async def get_index():
        return FileResponse(os.path.join(PUBLIC_DIR, "index.html"))

    @app.get("/login")
    async def get_login():
        return FileResponse(os.path.join(PUBLIC_DIR, "login.html"))

    app.include_router(userRouter)

    return app
