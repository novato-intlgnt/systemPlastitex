import os
import pathlib
from typing import Optional

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr, ValidationError

# Ruta base del proyecto
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent


class UserController:
    def __init__(self, user_model):
        self.user_model = user_model

    # 🧩 CREATE (signup)
    async def create(self, data: dict):
        try:
            is_user_exist = await self.user_model.check({"input": data})
            if is_user_exist is True:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status": "error",
                        "message": "Some of the data entered is already registered",
                    },
                )

            # Enviar correo de verificación
            if len(is_user_exist.keys()) == 4:
                new_user = await self.user_model.create_worker(
                    {"input": {**data, **role}}
                )
                if new_user:
                    return JSONResponse(
                        status_code=status.HTTP_201_CREATED,
                        content={
                            "status": "success",
                            "message": "User successfully created, check your email to verify your account",
                        },
                    )
                else:
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

    # 🧩 VERIFY (token verification)

    # 🧩 AUTH (signin)
    async def auth(self, data: dict):
        try:
            auth_user = await self.user_model.auth({"input": data})
            if auth_user is False:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status": "error",
                        "message": "There is some problem with the data entered",
                    },
                )

            response = JSONResponse(
                content={
                    "status": "ok",
                    "redirect": f"user/{auth_user['name']}/dashboard",
                }
            )
            response.set_cookie(
                key="user",
                value=auth_user["auth"],
                httponly=True,
                max_age=int(os.getenv("JWT_COOKIE_EXPIRATION", "3600")),
            )
            return response

        except Exception as e:
            print("Error in auth:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    # 🧩 ACCESS (dashboard by role)
    async def access(self, name: str, user: dict):
        try:
            if user.get("role") == "stall":
                return FileResponse(BASE_DIR / "public/dashboard.html")
            elif user.get("role") == "client":
                return FileResponse(BASE_DIR / "public/dashboardCli.html")
            else:
                raise HTTPException(status_code=403, detail="Unauthorized role")
        except Exception as e:
            print("Error accessing dashboard:", e)
            raise HTTPException(status_code=500, detail="Internal server error")
