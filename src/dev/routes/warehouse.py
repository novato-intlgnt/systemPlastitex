"""
Rutas del módulo de Almacén (Warehouse).
Define los endpoints para notas de ingreso (inbound) y salida (outbound).
"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from src.dev.controllers.warehouse import WarehouseController
from src.dev.middlewares.auth import only_user
from src.dev.repositories.warehouse import WarehouseRepository

# Crear el router con prefijo /warehouse
warehouseRouter = APIRouter(prefix="/warehouse", tags=["Warehouse"])

# Inyección de dependencias
warehouse_repository = WarehouseRepository()
warehouse_controller = WarehouseController(warehouse_repository)


async def get_current_user(user: dict = Depends(only_user)) -> dict:
    """
    Dependencia para obtener los datos del usuario autenticado.
    
    Args:
        user: Diccionario del usuario decodificado del token.
        
    Returns:
        Diccionario completo del usuario.
    """
    return user


async def get_current_role(user: dict = Depends(only_user)) -> str:
    """
    Dependencia para obtener el rol del usuario autenticado.
    
    Args:
        user: Diccionario del usuario decodificado del token.
        
    Returns:
        El rol del usuario.
    """
    return user.get("role", "")


# ==============================================================================
# SECCIÓN A: NOTAS DE INGRESO (INBOUND)
# ==============================================================================

@warehouseRouter.post(
    "/inbound",
    summary="Crear nota de ingreso",
    response_class=JSONResponse,
    status_code=201,
)
async def create_entry_note(
    data: dict,
    user: dict = Depends(get_current_user),
):
    """
    Crea una nueva nota de ingreso (cabecera).
    
    **Roles permitidos:** aux_almacen, admin
    
    **Request Body:**
    - **supplier_id** (int, requerido): ID del proveedor
    - **reference** (str, opcional): Referencia o número de documento
    
    **Returns:**
    - **id**: ID de la nota creada
    - **supplier_id**: ID del proveedor
    - **supplier_name**: Nombre del proveedor
    - **date**: Fecha de creación
    - **reference**: Referencia del documento
    """
    return await warehouse_controller.create_entry_note(
        current_role=user.get("role", ""),
        user_id=user.get("id"),
        data=data,
    )


@warehouseRouter.get(
    "/inbound",
    summary="Listar notas de ingreso",
    response_class=JSONResponse,
)
async def get_all_entry_notes(
    user_role: str = Depends(get_current_role),
):
    """
    Obtiene todas las notas de ingreso activas.
    
    **Roles permitidos:** aux_almacen, admin
    
    **Returns:**
    Lista de notas de ingreso con:
    - **id**: ID de la nota
    - **supplier_name**: Nombre del proveedor
    - **date**: Fecha de la nota
    - **reference**: Referencia del documento
    - **items_count**: Cantidad de items
    """
    return await warehouse_controller.get_all_entry_notes(user_role)


@warehouseRouter.get(
    "/inbound/{entry_id}",
    summary="Ver detalle de nota de ingreso",
    response_class=JSONResponse,
)
async def get_entry_note_by_id(
    entry_id: int,
    user_role: str = Depends(get_current_role),
):
    """
    Obtiene una nota de ingreso con todos sus detalles.
    
    **Roles permitidos:** aux_almacen, admin
    
    **Path Parameters:**
    - **entry_id**: ID de la nota de ingreso
    
    **Returns:**
    Datos de la nota con lista de detalles (productos y cantidades).
    """
    return await warehouse_controller.get_entry_note_by_id(user_role, entry_id)


@warehouseRouter.post(
    "/inbound/{entry_id}/items",
    summary="Agregar producto a nota de ingreso",
    response_class=JSONResponse,
    status_code=201,
)
async def add_entry_note_item(
    entry_id: int,
    data: dict,
    user_role: str = Depends(get_current_role),
):
    """
    Agrega un producto al detalle de una nota de ingreso.
    
    **IMPORTANTE:** Esta operación incrementará automáticamente el stock del producto.
    
    **Roles permitidos:** aux_almacen, admin
    
    **Path Parameters:**
    - **entry_id**: ID de la nota de ingreso
    
    **Request Body:**
    - **product_id** (int, requerido): ID del producto
    - **quantity** (int, requerido): Cantidad a ingresar (debe ser > 0)
    
    **Returns:**
    - **id**: ID del item creado
    - **product_name**: Nombre del producto
    - **quantity**: Cantidad ingresada
    - **new_stock**: Nuevo stock del producto
    """
    return await warehouse_controller.add_entry_note_item(user_role, entry_id, data)


@warehouseRouter.put(
    "/inbound/{entry_id}/items/{item_id}",
    summary="Actualizar item de nota de ingreso",
    response_class=JSONResponse,
)
async def update_entry_note_item(
    entry_id: int,
    item_id: int,
    data: dict,
    user_role: str = Depends(get_current_role),
):
    """
    Actualiza un item de una nota de ingreso.
    
    **IMPORTANTE:** El stock se ajustará según la diferencia de cantidad.
    
    **Roles permitidos:** aux_almacen, admin
    
    **Path Parameters:**
    - **entry_id**: ID de la nota de ingreso
    - **item_id**: ID del item a actualizar
    
    **Request Body:**
    - **product_id** (int, opcional): Nuevo ID del producto
    - **quantity** (int, opcional): Nueva cantidad (debe ser > 0)
    
    **Returns:**
    - **id**: ID del item
    - **product_name**: Nombre del producto
    - **quantity**: Nueva cantidad
    - **new_stock**: Nuevo stock del producto
    """
    return await warehouse_controller.update_entry_note_item(
        user_role, entry_id, item_id, data
    )


@warehouseRouter.delete(
    "/inbound/{entry_id}/items/{item_id}",
    summary="Eliminar item de nota de ingreso",
    response_class=JSONResponse,
)
async def delete_entry_note_item(
    entry_id: int,
    item_id: int,
    user_role: str = Depends(get_current_role),
):
    """
    Elimina un item de una nota de ingreso (soft delete).
    
    **IMPORTANTE:** El stock del producto se revertirá automáticamente.
    
    **Roles permitidos:** aux_almacen, admin
    
    **Path Parameters:**
    - **entry_id**: ID de la nota de ingreso
    - **item_id**: ID del item a eliminar
    
    **Returns:**
    Confirmación de eliminación con el nuevo stock del producto.
    """
    return await warehouse_controller.delete_entry_note_item(user_role, entry_id, item_id)


# ==============================================================================
# SECCIÓN B: NOTAS DE SALIDA (OUTBOUND)
# ==============================================================================

@warehouseRouter.post(
    "/outbound",
    summary="Crear nota de salida",
    response_class=JSONResponse,
    status_code=201,
)
async def create_exit_note(
    data: dict,
    user: dict = Depends(get_current_user),
):
    """
    Crea una nueva nota de salida (cabecera).
    
    **Roles permitidos:** aux_almacen, admin
    
    **Request Body:**
    - **customer_id** (int, requerido): ID del cliente
    - **total** (decimal, opcional): Total de la venta
    - **reference** (str, opcional): Referencia o número de documento
    
    **Returns:**
    - **id**: ID de la nota creada
    - **customer_id**: ID del cliente
    - **customer_name**: Nombre del cliente
    - **date**: Fecha de creación
    - **total**: Total de la venta
    - **reference**: Referencia del documento
    """
    return await warehouse_controller.create_exit_note(
        current_role=user.get("role", ""),
        user_id=user.get("id"),
        data=data,
    )


@warehouseRouter.get(
    "/outbound",
    summary="Listar notas de salida",
    response_class=JSONResponse,
)
async def get_all_exit_notes(
    user_role: str = Depends(get_current_role),
):
    """
    Obtiene todas las notas de salida activas.
    
    **Roles permitidos:** aux_almacen, admin
    
    **Returns:**
    Lista de notas de salida con:
    - **id**: ID de la nota
    - **customer_name**: Nombre del cliente
    - **date**: Fecha de la nota
    - **total**: Total de la venta
    - **reference**: Referencia del documento
    - **items_count**: Cantidad de items
    """
    return await warehouse_controller.get_all_exit_notes(user_role)


@warehouseRouter.get(
    "/outbound/{exit_id}",
    summary="Ver detalle de nota de salida",
    response_class=JSONResponse,
)
async def get_exit_note_by_id(
    exit_id: int,
    user_role: str = Depends(get_current_role),
):
    """
    Obtiene una nota de salida con todos sus detalles.
    
    **Roles permitidos:** aux_almacen, admin
    
    **Path Parameters:**
    - **exit_id**: ID de la nota de salida
    
    **Returns:**
    Datos de la nota con lista de detalles (productos y cantidades).
    """
    return await warehouse_controller.get_exit_note_by_id(user_role, exit_id)


@warehouseRouter.get(
    "/outbound/validate-stock",
    summary="Validar stock antes de salida",
    response_class=JSONResponse,
)
async def validate_stock(
    product_id: int = Query(..., description="ID del producto"),
    quantity: int = Query(..., description="Cantidad a validar"),
    user_role: str = Depends(get_current_role),
):
    """
    Valida si hay stock suficiente para una salida.
    
    **Roles permitidos:** aux_almacen, admin
    
    **Query Parameters:**
    - **product_id**: ID del producto
    - **quantity**: Cantidad solicitada
    
    **Returns:**
    - **is_valid**: true si hay stock suficiente
    - **current_stock**: Stock actual del producto
    - **requested_quantity**: Cantidad solicitada
    - **message**: Mensaje descriptivo
    """
    return await warehouse_controller.validate_stock(user_role, product_id, quantity)


@warehouseRouter.post(
    "/outbound/{exit_id}/items",
    summary="Agregar producto a nota de salida",
    response_class=JSONResponse,
    status_code=201,
)
async def add_exit_note_item(
    exit_id: int,
    data: dict,
    user_role: str = Depends(get_current_role),
):
    """
    Agrega un producto al detalle de una nota de salida.
    
    **REQUISITO CRÍTICO:** Antes de insertar, se validará que haya stock suficiente.
    Si la validación pasa, el stock se decrementará automáticamente.
    
    **Roles permitidos:** aux_almacen, admin
    
    **Path Parameters:**
    - **exit_id**: ID de la nota de salida
    
    **Request Body:**
    - **product_id** (int, requerido): ID del producto
    - **quantity** (int, requerido): Cantidad a sacar (debe ser > 0)
    
    **Returns:**
    - **id**: ID del item creado
    - **product_name**: Nombre del producto
    - **quantity**: Cantidad registrada
    - **new_stock**: Nuevo stock del producto
    
    **Errores:**
    - **400**: Stock insuficiente para la cantidad solicitada
    """
    return await warehouse_controller.add_exit_note_item(user_role, exit_id, data)


@warehouseRouter.put(
    "/outbound/{exit_id}/items/{item_id}",
    summary="Actualizar item de nota de salida",
    response_class=JSONResponse,
)
async def update_exit_note_item(
    exit_id: int,
    item_id: int,
    data: dict,
    user_role: str = Depends(get_current_role),
):
    """
    Actualiza un item de una nota de salida.
    
    **IMPORTANTE:** Se validará el stock antes de actualizar.
    El stock se ajustará según la diferencia.
    
    **Roles permitidos:** aux_almacen, admin
    
    **Path Parameters:**
    - **exit_id**: ID de la nota de salida
    - **item_id**: ID del item a actualizar
    
    **Request Body:**
    - **product_id** (int, opcional): Nuevo ID del producto
    - **quantity** (int, opcional): Nueva cantidad (debe ser > 0)
    
    **Returns:**
    - **id**: ID del item
    - **product_name**: Nombre del producto
    - **quantity**: Nueva cantidad
    - **new_stock**: Nuevo stock del producto
    
    **Errores:**
    - **400**: Stock insuficiente para la nueva cantidad
    """
    return await warehouse_controller.update_exit_note_item(
        user_role, exit_id, item_id, data
    )


@warehouseRouter.delete(
    "/outbound/{exit_id}/items/{item_id}",
    summary="Eliminar item de nota de salida",
    response_class=JSONResponse,
)
async def delete_exit_note_item(
    exit_id: int,
    item_id: int,
    user_role: str = Depends(get_current_role),
):
    """
    Elimina un item de una nota de salida (soft delete).
    
    **IMPORTANTE:** El stock del producto se revertirá automáticamente
    (se sumará la cantidad que se había restado).
    
    **Roles permitidos:** aux_almacen, admin
    
    **Path Parameters:**
    - **exit_id**: ID de la nota de salida
    - **item_id**: ID del item a eliminar
    
    **Returns:**
    Confirmación de eliminación con el nuevo stock del producto.
    """
    return await warehouse_controller.delete_exit_note_item(user_role, exit_id, item_id)
