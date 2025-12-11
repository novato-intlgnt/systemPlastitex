from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.dev.controllers.reports import ReportController
from src.dev.middlewares.auth import only_user
from src.dev.repositories.report import ReportRepositorie

reportRouter = APIRouter(prefix="/reports", tags=["Reports"])

# Inyección de dependencias
report_repositorie = ReportRepositorie()
report_controller = ReportController(report_repositorie)


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
# REPORTES EXISTENTES
# ==============================================================================


# ==============================================================================
# REPORTES PARA AUXILIAR DE COMPRA (aux_compra)
# ==============================================================================


@reportRouter.get(
    "/aux-compra/low-stock",
    summary="R1. Productos Bajo Stock - Productos con stock menor al umbral",
    tags=["Reports - Aux Compra"],
)
async def get_low_stock_aux_compra(
    threshold: int = Query(10, description="Umbral mínimo de stock (default: 10)"),
    user_role: str = Depends(get_current_role),
):
    """
    Lista productos donde `stock < threshold`.

    Ideal para identificar productos que necesitan reabastecimiento.

    - **threshold**: Umbral mínimo de stock. Productos con stock menor a este valor serán listados.

    **Roles permitidos**: aux_compra, admin

    **Returns:**
    - Lista de productos con bajo stock incluyendo:
      - product_id, product_name
      - category_name, unit_name
      - current_stock, threshold, deficit
      - purchase_price
    """
    return await report_controller.get_low_stock_aux_compra(user_role, threshold)


@reportRouter.get(
    "/aux-compra/purchase-history",
    summary="R2. Historial de Compras - Órdenes de compra por proveedor",
    tags=["Reports - Aux Compra"],
)
async def get_purchase_history_filtered(
    supplier_id: Optional[int] = Query(None, description="ID del proveedor (opcional)"),
    start_date: Optional[str] = Query(
        None, description="Fecha inicio YYYY-MM-DD (opcional)"
    ),
    end_date: Optional[str] = Query(
        None, description="Fecha fin YYYY-MM-DD (opcional)"
    ),
    user_role: str = Depends(get_current_role),
):
    """
    Obtiene el historial de compras con filtros opcionales.

    Todos los parámetros son opcionales. Si no se especifican, retorna todas las compras.

    - **supplier_id**: ID del proveedor (opcional - si no se especifica, retorna todos).
    - **start_date**: Fecha de inicio (opcional, formato: YYYY-MM-DD).
    - **end_date**: Fecha de fin (opcional, formato: YYYY-MM-DD).

    **Roles permitidos**: aux_compra, admin

    **Returns:**
    - Lista de órdenes de compra con:
      - order_id, order_date
      - supplier_id, supplier_name
      - total, status
      - created_by
    """
    return await report_controller.get_purchase_history_filtered(
        user_role, supplier_id, start_date, end_date
    )


# ==============================================================================
# REPORTES PARA AUXILIAR DE ALMACÉN (aux_almacen)
# ==============================================================================


@reportRouter.get(
    "/aux-almacen/kardex/{product_id}",
    summary="R3. Kardex Físico - Movimientos de entrada y salida de un producto",
    tags=["Reports - Aux Almacén"],
)
async def get_kardex_by_product(
    product_id: int,
    start_date: Optional[str] = Query(
        None, description="Fecha inicio YYYY-MM-DD (opcional)"
    ),
    end_date: Optional[str] = Query(
        None, description="Fecha fin YYYY-MM-DD (opcional)"
    ),
    user_role: str = Depends(get_current_role),
):
    """
    Obtiene el kardex (movimientos de entrada y salida) de un producto específico.

    El product_id es obligatorio. Las fechas son opcionales.

    - **product_id**: ID del producto a consultar (REQUERIDO).
    - **start_date**: Fecha de inicio (opcional, formato: YYYY-MM-DD).
    - **end_date**: Fecha de fin (opcional, formato: YYYY-MM-DD).

    **Roles permitidos**: aux_almacen, admin

    """
    return await report_controller.get_kardex_by_product(
        user_role, product_id, start_date, end_date
    )


@reportRouter.get(
    "/aux-almacen/stock/{product_id}",
    summary="R4. Stock Actual - Stock de productos por categoría",
    tags=["Reports - Aux Almacén"],
)
async def get_stock_by_product_id(
    product_id: int,
    category_id: Optional[int] = Query(
        None, description="ID de la categoría (opcional)"
    ),
    user_role: str = Depends(get_current_role),
):
    """
    Obtiene el stock actual de productos, opcionalmente filtrado por categoría.

    - **product_id**: ID del producto a consultar.
    - **category_id**: ID de la categoría (opcional).

    **Roles permitidos**: aux_almacen, admin

    **Returns:**
    - Información del producto con:
      - product_id, product_name
      - category_id, category_name
      - unit_id, unit_name
      - stock, sale_price, purchase_price
      - total_entries (total de entradas)
      - total_exits (total de salidas)
    """
    return await report_controller.get_stock_aux_almacen(user_role, product_id)


@reportRouter.get(
    "/aux-almacen/stock",
    summary="R5. Stock de productos para Aux Almacén",
    tags=["Reports - Aux Almacén"],
)
async def get_stock_aux_almacen(
    product_id: Optional[int] = Query(None, description="ID del producto (opcional)"),
    user_role: str = Depends(get_current_role),
):
    """
    Obtiene información detallada de stock.

    Si se proporciona product_id, retorna solo ese producto.
    Si no se proporciona, retorna todos los productos.

    - **product_id**: ID del producto (opcional - si no se especifica, retorna todos).

    **Roles permitidos**: aux_almacen, admin

    **Returns:**
    - Lista de productos con:
      - product_id, product_name
      - category_id, category_name
      - unit_id, unit_name
      - stock, sale_price, purchase_price
      - total_entries (total de entradas)
      - total_exits (total de salidas)
    """
    return await report_controller.get_stock_aux_almacen(user_role, product_id)


@reportRouter.get(
    "/top_selling",
    summary="R6. Productos Más Vendidos - Top de productos por cantidad vendida",
)
async def get_top_selling(
    limit: int = Query(10, description="Número máximo de productos a retornar"),
    user_role: str = Depends(get_current_role),
):
    """
    Obtiene los productos más vendidos.

    - **limit**: Número máximo de productos a retornar (default: 10).

    **Roles permitidos**: aux_almacen, admin
    """
    return await report_controller.get_top_selling(user_role, limit)
