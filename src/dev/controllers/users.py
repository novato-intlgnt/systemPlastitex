import os
import pathlib

from fastapi import HTTPException, status
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent


class UserController:
    def __init__(self, user_model):
        self.user_model = user_model

    async def create(self, data: dict):
        try:
            is_user_exist = await self.user_model.check(data)
            if is_user_exist is True:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status": "error",
                        "message": "Some of the data entered is already registered",
                    },
                )

            new_user = await self.user_model.create_worker(data)
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
        """
        Autentica al usuario y devuelve el token JWT en el body.
        El frontend debe guardar el token y enviarlo en el header Authorization.
        """
        try:
            auth_user = await self.user_model.auth(data)
            if auth_user["status"] is False:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status": "error",
                        "message": "There is some problem with the data entered",
                    },
                )

            # Devolver el token en el body para que el frontend lo guarde
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "success",
                    "message": "Login exitoso",
                    "data": {
                        "access_token": auth_user["auth"],
                        "token_type": "Bearer",
                        "user": {
                            "id": auth_user.get("id"),
                            "name": auth_user["name"],
                            "role": auth_user.get("role"),
                        },
                        "redirect_url": f"/user/{auth_user['name']}/dashboard",
                    },
                },
            )

        except Exception as e:
            print("Error in auth:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    async def access(self, name: str, user: dict):
        try:
            if user.get("user") != name:
                return RedirectResponse(url="/", status_code=302)
            if user.get("role") == "aux_compra":
                return FileResponse(
                    path=BASE_DIR / "public" / "dash_aux_compra.html",
                    media_type="text/html",
                )
            return FileResponse(
                path=BASE_DIR / "public" / "dash_aux_almacen.html",
                media_type="text/html",
            )
        except Exception as e:
            print("Error accessing dashboard:", e)
            raise HTTPException(status_code=500, detail="Internal server error")
