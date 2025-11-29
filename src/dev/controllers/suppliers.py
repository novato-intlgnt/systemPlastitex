import os
import pathlib
from typing import Optional

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# Ruta base del proyecto
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
print(BASE_DIR)

templates = Jinja2Templates(directory=BASE_DIR / "views")


class SupplierController:
    def __init__(self, supplier_model):
        self.supplier_model = supplier_model

    async def create(self, data: dict):
        try:
            is_user_exist = await self.supplier_model.check(data)
            if is_user_exist is True:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status": "error",
                        "message": "Some of the data entered is already registered",
                    },
                )

            # Enviar correo de verificación
            new_user = await self.supplier_model.create_worker(data)
            if new_user:
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "status": "success",
                        "message": "User successfully created",
                    },
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "error",
                    "message": "User could not be created",
                },
            )

        except Exception as e:
            print("Error in create:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    async def auth(self, data: dict):
        try:
            auth_user = await self.supplier_model.auth(data)
            if auth_user["status"] is False:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status": "error",
                        "message": "There is some problem with the data entered",
                    },
                )

            response = RedirectResponse(
                url=f"/user/{auth_user['name']}/dashboard",
                status_code=302,
            )

            response.set_cookie(
                key="user",
                value=auth_user["auth"],
                httponly=True,
                samesite="lax",
                secure=False,
                path="/",
                max_age=int(os.getenv("JWT_COOKIE_EXPIRATION", "3600")),
            )
            return response

        except Exception as e:
            print("Error in auth:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    # 🧩 ACCESS (dashboard by role)
    async def access(self, name: str, user: dict, request: Request):
        try:
            if user.get("user") != name:
                return RedirectResponse(url="/", status_code=302)
            return FileResponse(
                path=BASE_DIR / "public" / "dash_aux_compra.html",
                media_type="text/html",
            )
            # return templates.TemplateResponse(
            #     "dashboard.html", {"request": request}  # "user": user}
            # )
        except Exception as e:
            print("Error accessing dashboard:", e)
            raise HTTPException(status_code=500, detail="Internal server error")
