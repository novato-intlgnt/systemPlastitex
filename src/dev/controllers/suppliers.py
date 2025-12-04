import os
import pathlib
from typing import Optional

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# Ruta base del proyecto
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent

templates = Jinja2Templates(directory=BASE_DIR / "views")


class SupplierController:
    def __init__(self, supplier_model):
        self.supplier_model = supplier_model

    @staticmethod
    def _check_role(current_role: str, allowed_roles: list[str]) -> None:
        """
        Método auxiliar para validar el rol del usuario.

        Args:
            current_role: Rol actual del usuario autenticado.
            allowed_roles: Lista de roles permitidos para la operación.

        Raises:
            HTTPException: 403 si el rol no está permitido.
        """
        if current_role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Acceso no autorizado.")

    async def get_all(self, current_role: str):
        self._check_role(current_role, ["aux_compra", "aux_almacen", "admin"])
        try:
            suppliers = await self.supplier_model.get_all()
            if not suppliers:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status_code": 400,
                        "message": "There is some problem",
                    },
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status_code": 200, "suppliers": suppliers},
            )

        except Exception as e:
            print("Error in get_all:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_byId(self, current_role: str, supp_id: int):
        self._check_role(current_role, ["aux_compra", "admin"])
        try:
            supplier = await self.supplier_model.get_byId(supp_id)
            if not supplier:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status_code": 400,
                        "message": "There is some problem",
                    },
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status_code": 200, "supplier": supplier},
            )

        except Exception as e:
            print("Error in get_byId:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    async def create(self, current_role: str, data: dict):
        self._check_role(current_role, ["aux_compra", "admin"])
        try:
            is_supp_exist = await self.supplier_model.check(data)
            if is_supp_exist is True:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status": "error",
                        "message": "The supplier allready exists",
                    },
                )

            new_supplier = await self.supplier_model.create(data)
            if new_supplier:
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "status": "success",
                        "message": "The supplier was registered correctly",
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

    async def modify(self, current_role: str, supp_id: int, new_data: dict):
        self._check_role(current_role, ["aux_compra", "admin"])
        try:
            is_supp_exist = await self.supplier_model.get_byId(supp_id)
            if not is_supp_exist:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status_code": 400,
                        "message": "The supplier does not exist",
                    },
                )

            supp_changed = await self.supplier_model.modify(supp_id, new_data)
            if supp_changed:
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "status": "success",
                        "message": "The supplier was modified correctly",
                    },
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "error",
                    "message": "Supplier could not be modified",
                },
            )

        except Exception as e:
            print("Error in modify:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    async def delete(self, current_role: str, supp_id: int):
        self._check_role(current_role, ["aux_compra", "admin"])
        try:
            supp_deleted = await self.supplier_model.delete(supp_id)
            if not supp_deleted:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status_code": 400,
                        "message": "Supplier could not be deleted",
                    },
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status_code": 200, "message": "Supplier deleted correctly"},
            )

        except Exception as e:
            print("Error in delete:", e)
            raise HTTPException(status_code=500, detail="Internal server error")
