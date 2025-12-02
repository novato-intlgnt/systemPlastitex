from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from src.dev.controllers.units import UnitController
from src.dev.middlewares.auth import only_user
from src.dev.repositories.unit import UnitRepository

unitRouter = APIRouter(prefix="/unit", tags=["Unit"])

# Inyección de dependencias
unit_model = UnitRepository()
unit_controller = UnitController(unit_model)


async def get_current_role(user: dict = Depends(only_user)) -> str:
    """
    Dependencia para obtener el rol del usuario autenticado.
    Args:
        user: Diccionario del usuario decodificado del token.
    Returns:
        El rol del usuario.
    """
    return user.get("role", "")


@unitRouter.get(
    "/",
    summary="List all units",
    response_class=JSONResponse,
)
async def get_allUnits(user_role: str = Depends(get_current_role)):
    """
    Obtiene una lista de todas las unidades de medida registradas
    **Roles permitidos:** Auxiliar de almacén, Jefe de almacén
    **Returns:**
    - **id:** ID de la unidad
    - **name:** Nombre de la unidad
    """
    return await unit_controller.get_all(user_role)


@unitRouter.get(
    "/{unit_id}",
    summary="Get unit by ID",
    response_class=JSONResponse,
)
async def get_unitById(unit_id: int, user_role=Depends(get_current_role)):
    """
    Obtiene una unidad de medida según su **id**
    **Roles permitidos:** Auxiliar de almacén, Jefe de almacén
    **Returns:**
    - **id:** ID de la unidad
    - **name:** Nombre de la unidad
    """
    return await unit_controller.get_byId(user_role, unit_id)


@unitRouter.post(
    "/",
    summary="Add a new unit",
)
async def create_unit(data: dict, user_role: str = Depends(get_current_role)):
    """
    Registrar una nueva unidad de medida
    **Roles permitidos:** Auxiliar de almacén
    **Args:**
    - **name:** Nombre de la unidad
    """
    return await unit_controller.create(user_role, data)


@unitRouter.put(
    "/{unit_id}",
    summary="Modify unit data",
)
async def modify_unit(
    unit_id: int, new_data: dict, user_role: str = Depends(get_current_role)
):
    """
    Modificar una unidad de medida existente
    **Roles permitidos:** Auxiliar de almacén, Jefe de almacén
    **Args:**
    - **name:?** Nombre
    """
    return await unit_controller.modify(user_role, unit_id, new_data)


@unitRouter.delete(
    "/{unit_id}",
    summary="Delete a unit",
)
async def delete_unit(unit_id: int, user_role: str = Depends(get_current_role)):
    """
    Eliminar una unidad de medida
    **Roles permitidos:** Auxiliar de almacén
    **Args:**
    - **unit_id:** ID de la unidad
    """
    return await unit_controller.delete(user_role, unit_id)
