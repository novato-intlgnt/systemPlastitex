from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from src.dev.controllers.products import ProductController
from src.dev.middlewares.auth import only_user
from src.dev.repositories.product import ProductRepository

productRouter = APIRouter(prefix="/product", tags=["Product"])

# Inyección de dependencias
product_model = ProductRepository()
product_controller = ProductController(product_model)


async def get_current_role(user: dict = Depends(only_user)) -> str:
    """
    Dependencia para obtener el rol del usuario autenticado.

    Args:
        user: Diccionario del usuario decodificado del token.

    Returns:
        El rol del usuario.
    """
    return user.get("role", "")


@productRouter.get(
    "/",
    summary="List all products",
    response_class=JSONResponse,
)
async def get_allProducts(user_role: str = Depends(get_current_role)):
    """
    Obtiene una lista de todos los productos registrados
    **Roles permitidos:** Auxiliar de almacén, Jefe de almacén

    **Returns:**
    - **id:** ID del producto
    - **name:** Nombre del producto
    - **description:** Descripción
    - **stock:** Cantidad actual
    - **unit:** Unidad de medida
    """
    return await product_controller.get_all(user_role)


@productRouter.get(
    "/{product_id}",
    summary="Get product by ID",
    response_class=JSONResponse,
)
async def get_productById(product_id: int, user_role=Depends(get_current_role)):
    """
    Obtiene un producto según su **id**
    **Roles permitidos:** Auxiliar de almacén, Jefe de almacén

    **Returns:**
    - **id:** ID del producto
    - **name:** Nombre del producto
    - **description:** Descripción
    - **stock:** Cantidad actual
    - **unit:** Unidad de medida
    """
    return await product_controller.get_byId(user_role, product_id)


@productRouter.post(
    "/",
    summary="Add a new product",
)
async def create_product(data: dict, user_role: str = Depends(get_current_role)):
    """
    Registrar un nuevo producto
    **Roles permitidos:** Auxiliar de almacén

    **Args:**
    - **name:** Nombre del producto
    - **description:** Descripción
    - **stock:** Cantidad inicial
    - **unit:** Unidad de medida
    """
    return await product_controller.create(user_role, data)


@productRouter.put(
    "/{product_id}",
    summary="Modify product data",
)
async def modify_product(
    product_id: int, new_data: dict, user_role: str = Depends(get_current_role)
):
    """
    Modificar un producto existente
    **Roles permitidos:** Auxiliar de almacén, Jefe de almacén

    **Args:**
    - **name:?** Nombre
    - **description:?** Descripción
    - **stock:?** Nuevo stock
    - **unit:?** Unidad
    """
    return await product_controller.modify(user_role, product_id, new_data)


@productRouter.delete(
    "/{product_id}",
    summary="Delete a product",
)
async def delete_product(product_id: int, user_role: str = Depends(get_current_role)):
    """
    Eliminar un producto
    **Roles permitidos:** Jefe de almacén

    **Args:**
    - **product_id:** ID del producto
    """
    return await product_controller.delete(user_role, product_id)
