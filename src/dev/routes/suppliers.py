from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from src.dev.controllers.suppliers import SupplierController
from src.dev.middlewares.auth import only_user
from src.dev.repositories.supplier import SupplierRepository

supplierRouter = APIRouter(prefix="/supplier", tags=["Supplier"])

# Inyección de dependencias
supplier_model = SupplierRepository()
supplier_controller = SupplierController(supplier_model)


async def get_current_role(user: dict = Depends(only_user)) -> str:
    """
    Dependencia para obtener el rol del usuario autenticado.

    Args:
        user: Diccionario del usuario decodificado del token.

    Returns:
        El rol del usuario.
    """
    return user.get("role", "")


@supplierRouter.get(
    "/",
    summary="List all suppliers",
    response_class=JSONResponse,
)
async def get_allSupp(user_role: str = Depends(get_current_role)):
    """
    Obtiene una lista de todos los proveedores registrados
    **Roles permitidos:** Auxiliar de compra
    **Returns:**
    - **id:** ID del proveedor
    - **name:** Nommbre
    - **phone:** Nmro de celular
    - **address:** Direccion
    """
    return await supplier_controller.get_all(user_role)


@supplierRouter.get(
    "/{supplier_id}",
    summary="Get supplier by ID",
    response_class=JSONResponse,
)
async def get_byIdSupp(supplier_id: int, user_role=Depends(get_current_role)):
    """
    Obtiene un determinado proveedor, según su **id**
    **Roles permitidos:** Auxiliar de compra
    **Arg
    **Returns:**
    - **id:** ID del proveedor
    - **name:** Nommbre
    - **phone:** Nmro de celular
    - **address:** Direccion
    """
    return await supplier_controller.get_byId(user_role, supplier_id)


@supplierRouter.post(
    "/",
    summary="Add a new supplier",
)
async def createSupp(data: dict, user_role: str = Depends(get_current_role)):
    """
    Registrar un nuevo proveedor
    **Roles permitidos:** Auxiliar de compra
    **Args:**
    - **name:** Nommbre
    - **phone:** Nmro de celular
    - **address:** Direccion
    """
    return await supplier_controller.create(user_role, data)


@supplierRouter.put(
    "/{supplier_id}",
    summary="Change supplier's data",
)
async def modifySupp(
    supplier_id: int, new_data: dict, user_role: str = Depends(get_current_role)
):
    """
    Modificar un proveedor
    **Roles permitidos:** Auxiliar de compra
    **Args:**
    - **supplier_id:** ID del proveedor
    - **name:?** Nommbre
    - **phone:?** Nmro de celular
    - **address:?** Direccion
    """
    return await supplier_controller.modify(user_role, supplier_id, new_data)


@supplierRouter.delete(
    "/{supplier_id}",
    summary="Delete a supplier",
)
async def deleteSupp(supplier_id: int, user_role: str = Depends(get_current_role)):
    """
    Eliminar un nuevo proveedor
    **Roles permitidos:** Auxiliar de compra
    **Args:**
    - **supplier_id:** ID del proveedor
    """
    return await supplier_controller.delete(user_role, supplier_id)
