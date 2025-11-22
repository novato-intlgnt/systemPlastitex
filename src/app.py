import os

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.dev.routes.users import router


def create_app(user_model):
    app = FastAPI(title="Plastitex Dashboard", docs_url="/docs")

    # Directorio base (equivalente a __dirname en JS)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PUBLIC_DIR = os.path.join(BASE_DIR, "public")

    # Archivos estáticos (como express.static)
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

    # Rutas HTML
    @app.get("/")
    async def get_index():
        return FileResponse(os.path.join(PUBLIC_DIR, "index.html"))

    @app.get("/login")
    async def get_login():
        return FileResponse(os.path.join(PUBLIC_DIR, "login.html"))

    @app.get("/loginStail")
    async def get_login_stail():
        return FileResponse(os.path.join(PUBLIC_DIR, "loginStail.html"))

    @app.get("/dash")
    async def get_dash():
        return FileResponse(os.path.join(PUBLIC_DIR, "dash", "dashboardtienda.html"))

    # Rutas dinámicas (como app.use('/user', router))
    # user_router = router(user_model)
    app.include_router(router)
    #
    return app
