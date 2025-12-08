from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class ProductController:
    def __init__(self, product_model):
        self.product_model = product_model

    @staticmethod
    def _check_role(current_role: str, allowed_roles: list[str]) -> None:
        """
        Verifica que el rol tenga acceso permitido.
        """
        if current_role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Acceso no autorizado.")

    async def get_all(self, current_role: str):
        self._check_role(current_role, ["aux_almacen", "aux_compra", "admin"])
        try:
            products = await self.product_model.get_all()
            if not products:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status_code": 400,
                        "message": "There is some problem",
                    },
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status_code": 200, "products": products},
            )

        except Exception as e:
            print("Error in get_all:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_byId(self, current_role: str, product_id: int):
        self._check_role(current_role, ["aux_almacen", "jefe_almacen", "admin"])
        try:
            product = await self.product_model.get_byId(product_id)
            if not product:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status_code": 400,
                        "message": "There is some problem",
                    },
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status_code": 200, "product": product},
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
            is_product_exist = await self.product_model.check(data)
            if is_product_exist is True:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status": "error",
                        "message": "The product already exists",
                    },
                )

            new_product = await self.product_model.create(data)
            if new_product:
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "status": "success",
                        "message": "The product was created correctly",
                    },
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "error",
                    "message": "Product could not be created",
                },
            )

        except Exception as e:
            print("Error in create:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    async def modify(self, current_role: str, product_id: int, new_data: dict):
        self._check_role(current_role, ["aux_almacen", "jefe_almacen", "admin"])
        try:
            is_product_exist = await self.product_model.get_byId(product_id)
            if not is_product_exist:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status_code": 400,
                        "message": "The product does not exist",
                    },
                )

            product_changed = await self.product_model.modify(product_id, new_data)
            if product_changed:
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "status": "success",
                        "message": "The product was modified correctly",
                    },
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "error",
                    "message": "Product could not be modified",
                },
            )

        except Exception as e:
            print("Error in modify:", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    async def delete(self, current_role: str, product_id: int):
        self._check_role(current_role, ["aux_almacen", "jefe_almacen", "admin"])
        try:
            product_deleted = await self.product_model.delete(product_id)
            if not product_deleted:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status_code": 400,
                        "message": "Product could not be deleted",
                    },
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status_code": 200,
                    "message": "Product deleted correctly",
                },
            )

        except Exception as e:
            print("Error in delete:", e)
            raise HTTPException(status_code=500, detail="Internal server error")
