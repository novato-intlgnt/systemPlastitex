from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from src.dev.controllers.categories import CategoryController
from src.dev.middlewares.auth import only_user
from src.dev.repositories.category import CategoryRepository

categoryRouter = APIRouter(prefix="/category", tags=["Category"])

# Inyección de dependencias
category_model = CategoryRepository()
category_controller = CategoryController(category_model)


async def get_current_role(user: dict = Depends(only_user)) -> str:
    """
    Dependencia para obtener el rol del usuario autenticado.
    Args:
        user: Diccionario del usuario decodificado del token.
    Returns:
        El rol del usuario.
    """
    return user.get("role", "")


@categoryRouter.get(
    "/",
    summary="List all categories",
    response_class=JSONResponse,
)
async def get_allCategories(user_role: str = Depends(get_current_role)):
    """
    Obtiene una lista de todas las categorías registradas
    **Roles permitidos:** Auxiliar de almacén, Jefe de almacén
    **Returns:**
    - **id:** ID de la categoría
    - **name:** Nombre de la categoría
    - **is_active:** Estado de la categoría (activo/inactivo)
    """
    return await category_controller.get_all(user_role)


@categoryRouter.get(
    "/{category_id}",
    summary="Get category by ID",
    response_class=JSONResponse,
)
async def get_categoryById(category_id: int, user_role=Depends(get_current_role)):
    """
    Obtiene una categoría según su **id**
    **Roles permitidos:** Auxiliar de almacén, Jefe de almacén
    **Returns:**
    - **id:** ID de la categoría
    - **name:** Nombre de la categoría
    - **is_active:** Estado de la categoría
    """
    return await category_controller.get_byId(user_role, category_id)


@categoryRouter.post(
    "/",
    summary="Add a new category",
)
async def create_category(data: dict, user_role: str = Depends(get_current_role)):
    """
    Registrar una nueva categoría
    **Roles permitidos:** Auxiliar de almacén
    **Args:**
    - **name:** Nombre de la categoría
    - **is_active:** Estado (opcional, por defecto True)
    """
    return await category_controller.create(user_role, data)


@categoryRouter.put(
    "/{category_id}",
    summary="Modify category data",
)
async def modify_category(
    category_id: int, new_data: dict, user_role: str = Depends(get_current_role)
):
    """
    Modificar una categoría existente
    **Roles permitidos:** Auxiliar de almacén, Jefe de almacén
    **Args:**
    - **name:?** Nombre de la categoría
    - **is_active:?** Estado (activo/inactivo)
    """
    return await category_controller.modify(user_role, category_id, new_data)


@categoryRouter.delete(
    "/{category_id}",
    summary="Delete a category",
)
async def delete_category(category_id: int, user_role: str = Depends(get_current_role)):
    """
    Eliminar una categoría (soft delete)
    **Roles permitidos:** Jefe de almacén
    **Args:**
    - **category_id:** ID de la categoría
    """
    return await category_controller.delete(user_role, category_id)
