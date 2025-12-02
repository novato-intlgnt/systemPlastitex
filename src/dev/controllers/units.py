from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class UnitController:
    def __init__(self, unit_model):
        self.unit_model = unit_model

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
            units = await self.unit_model.get_all()
            if not units:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status_code": 400,
                        "message": "There is some problem",
                    },
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status_code": 200, "units": units},
            )

        except Exception as e:
            print("Error in get_all:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_byId(self, current_role: str, unit_id: int):
        self._check_role(current_role, ["aux_almacen", "jefe_almacen", "admin"])
        try:
            unit = await self.unit_model.get_byId(unit_id)
            if not unit:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status_code": 400,
                        "message": "There is some problem",
                    },
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status_code": 200, "unit": unit},
            )

        except Exception as e:
            print("Error in get_byId:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    async def create(self, current_role: str, data: dict):
        """
        Roles permitidos:
        - aux_almacen
        - admin
        """
        self._check_role(current_role, ["aux_almacen", "admin"])
        try:
            is_unit_exist = await self.unit_model.check(data)
            if is_unit_exist is True:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status": "error",
                        "message": "The unit already exists",
                    },
                )

            new_unit = await self.unit_model.create(data)
            if new_unit:
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "status": "success",
                        "message": "The unit was created correctly",
                    },
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "error",
                    "message": "Unit could not be created",
                },
            )

        except Exception as e:
            print("Error in create:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    async def modify(self, current_role: str, unit_id: int, new_data: dict):
        self._check_role(current_role, ["aux_almacen", "admin"])
        try:
            is_unit_exist = await self.unit_model.get_byId(unit_id)
            if not is_unit_exist:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status_code": 400,
                        "message": "The unit does not exist",
                    },
                )

            unit_changed = await self.unit_model.modify(unit_id, new_data)
            if unit_changed:
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "status": "success",
                        "message": "The unit was modified correctly",
                    },
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "error",
                    "message": "Unit could not be modified",
                },
            )

        except Exception as e:
            print("Error in modify:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    async def delete(self, current_role: str, unit_id: int):
        self._check_role(current_role, ["aux_almacen", "admin"])
        try:
            unit_deleted = await self.unit_model.delete(unit_id)
            if not unit_deleted:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status_code": 400,
                        "message": "Unit could not be deleted",
                    },
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status_code": 200,
                    "message": "Unit deleted correctly",
                },
            )

        except Exception as e:
            print("Error in delete:", e)
            raise HTTPException(status_code=500, detail="Internal server error")
