from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class CategoryController:
    def __init__(self, category_model):
        self.category_model = category_model

    @staticmethod
    def _check_role(current_role: str, allowed_roles: list[str]) -> None:
        """
        Verifica que el rol tenga acceso permitido.
        """
        if current_role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Acceso no autorizado.")

    async def get_all(self, current_role: str):
        self._check_role(current_role, ["aux_almacen", "jefe_almacen", "admin"])
        try:
            categories = await self.category_model.get_all()
            if not categories:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status_code": 400,
                        "message": "There is some problem",
                    },
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status_code": 200, "categories": categories},
            )

        except Exception as e:
            print("Error in get_all:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_byId(self, current_role: str, category_id: int):
        self._check_role(current_role, ["aux_almacen", "jefe_almacen", "admin"])
        try:
            category = await self.category_model.get_byId(category_id)
            if not category:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status_code": 400,
                        "message": "There is some problem",
                    },
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status_code": 200, "category": category},
            )

        except Exception as e:
            print("Error in get_byId:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    async def create(self, current_role: str, data: dict):
        """
        Roles permitidos:
        - aux_almacen
        - jefe_almacen
        - admin
        """
        self._check_role(current_role, ["aux_almacen", "jefe_almacen", "admin"])
        try:
            is_category_exist = await self.category_model.check(data)
            if is_category_exist is True:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status": "error",
                        "message": "The category already exists",
                    },
                )

            new_category = await self.category_model.create(data)
            if new_category:
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "status": "success",
                        "message": "The category was created correctly",
                    },
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "error",
                    "message": "Category could not be created",
                },
            )

        except Exception as e:
            print("Error in create:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    async def modify(self, current_role: str, category_id: int, new_data: dict):
        self._check_role(current_role, ["aux_almacen", "jefe_almacen", "admin"])
        try:
            is_category_exist = await self.category_model.get_byId(category_id)
            if not is_category_exist:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status_code": 400,
                        "message": "The category does not exist",
                    },
                )

            category_changed = await self.category_model.modify(category_id, new_data)
            if category_changed:
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "status": "success",
                        "message": "The category was modified correctly",
                    },
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "error",
                    "message": "Category could not be modified",
                },
            )

        except Exception as e:
            print("Error in modify:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    async def delete(self, current_role: str, category_id: int):
        self._check_role(current_role, ["aux_almacen", "jefe_almacen", "admin"])
        try:
            category_deleted = await self.category_model.delete(category_id)
            if not category_deleted:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status_code": 400,
                        "message": "Category could not be deleted",
                    },
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status_code": 200,
                    "message": "Category deleted correctly",
                },
            )

        except Exception as e:
            print("Error in delete:", e)
            raise HTTPException(status_code=500, detail="Internal server error")
