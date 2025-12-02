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


@reportRouter.get(
    "/kardex",
    summary="R1. Kardex Físico - Movimientos de entrada y salida de un producto",
)
async def get_kardex(
    product_id: int,
    start_date: str,
    end_date: str,
    user_role: str = Depends(get_current_role),
):
    """
    Obtiene el kardex físico de un producto en un rango de fechas.

    - **product_id**: ID del producto a consultar.
    - **start_date**: Fecha de inicio (formato: YYYY-MM-DD).
    - **end_date**: Fecha de fin (formato: YYYY-MM-DD).

    **Roles permitidos**: aux_almacen, admin
    """
    return await report_controller.get_kardex(
        user_role, product_id, start_date, end_date
    )


@reportRouter.get(
    "/stock/current",
    summary="R2. Stock Actual - Stock de productos por categoría",
)
async def get_current_stock(
    category_id: Optional[int] = Query(None, description="ID de la categoría (opcional)"),
    user_role: str = Depends(get_current_role),
):
    """
    Obtiene el stock actual de productos, opcionalmente filtrado por categoría.

    - **category_id**: ID de la categoría (opcional).

    **Roles permitidos**: aux_almacen, admin
    """
    return await report_controller.get_current_stock(user_role, category_id)


@reportRouter.get(
    "/purchases/history",
    summary="R3. Historial de Compras - Órdenes de compra por proveedor",
)
async def get_purchase_history(
    supplier_id: int,
    start_date: str,
    end_date: str,
    user_role: str = Depends(get_current_role),
):
    """
    Obtiene el historial de compras de un proveedor en un rango de fechas.

    - **supplier_id**: ID del proveedor a consultar.
    - **start_date**: Fecha de inicio (formato: YYYY-MM-DD).
    - **end_date**: Fecha de fin (formato: YYYY-MM-DD).

    **Roles permitidos**: aux_compra, admin
    """
    return await report_controller.get_purchase_history(
        user_role, supplier_id, start_date, end_date
    )


@reportRouter.get(
    "/top_selling",
    summary="R4. Productos Más Vendidos - Top de productos por cantidad vendida",
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


@reportRouter.get(
    "/stock/low",
    summary="R5. Productos Bajo Stock - Productos con stock menor al umbral",
)
async def get_low_stock(
    threshold: int = Query(10, description="Umbral mínimo de stock"),
    user_role: str = Depends(get_current_role),
):
    """
    Obtiene los productos con stock menor al umbral especificado.

    - **threshold**: Umbral mínimo de stock (default: 10).

    **Roles permitidos**: aux_compra, admin
    """
    return await report_controller.get_low_stock(user_role, threshold)
