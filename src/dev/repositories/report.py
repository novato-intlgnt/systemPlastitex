from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.dev.config.db import async_session_maker


class ReportRepositorie:
    """
    Repositorio para reportes que utiliza Procedimientos Almacenados (SP).
    Todos los métodos delegan la lógica de consulta compleja a los SP de la base de datos.
    """

    @staticmethod
    async def _execute_sp(
        sp_name: str,
        params: dict[str, Any],
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        Método auxiliar para ejecutar un Procedimiento Almacenado.

        Args:
            sp_name: Nombre del procedimiento almacenado.
            params: Diccionario de parámetros a pasar al SP.
            poolDB: Pool de conexiones a la base de datos.

        Returns:
            Lista de diccionarios con los resultados del SP.
        """
        # Construir la lista de parámetros para la sentencia CALL
        param_placeholders = ", ".join([f":{key}" for key in params.keys()])
        sql_statement = text(f"CALL {sp_name}({param_placeholders})")

        async with poolDB() as session:
            result = await session.execute(sql_statement, params)
            rows = result.fetchall()

            # Convertir las filas a lista de diccionarios
            if rows:
                columns = result.keys()
                return [dict(zip(columns, row)) for row in rows]
            return []

    @staticmethod
    async def get_kardex_data(
        product_id: int,
        start_date: str,
        end_date: str,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        R1. Kardex Físico - Obtiene los movimientos de entrada y salida de un producto.

        El SP utiliza UNION ALL para combinar:
        - entry_note_detail (saldo positivo)
        - exit_note_detail (saldo negativo)

        Args:
            product_id: ID del producto.
            start_date: Fecha de inicio (formato: YYYY-MM-DD).
            end_date: Fecha de fin (formato: YYYY-MM-DD).

        Returns:
            Lista de movimientos del kardex.
        """
        params = {
            "p_product_id": product_id,
            "p_start_date": start_date,
            "p_end_date": end_date,
        }
        return await ReportRepositorie._execute_sp(
            "SP_GET_KARDEX_FISICO", params, poolDB
        )

    @staticmethod
    async def get_current_stock(
        category_id: Optional[int] = None,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        R2. Stock Actual - Obtiene el stock actual de productos por categoría.

        El SP utiliza JOIN entre products, categories y units.
        Filtra por category_id si se proporciona.

        Args:
            category_id: ID de la categoría (opcional).

        Returns:
            Lista de productos con su stock actual.
        """
        params = {"p_category_id": category_id}
        return await ReportRepositorie._execute_sp(
            "SP_GET_STOCK_CATEGORIA", params, poolDB
        )

    @staticmethod
    async def get_purchase_history(
        supplier_id: int,
        start_date: str,
        end_date: str,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        R3. Historial de Compras - Obtiene las órdenes de compra por proveedor.

        El SP filtra purchase_order por fechas y supplier_id,
        incluyendo el monto total.

        Args:
            supplier_id: ID del proveedor.
            start_date: Fecha de inicio (formato: YYYY-MM-DD).
            end_date: Fecha de fin (formato: YYYY-MM-DD).

        Returns:
            Lista de órdenes de compra.
        """
        params = {
            "p_supplier_id": supplier_id,
            "p_start_date": start_date,
            "p_end_date": end_date,
        }
        return await ReportRepositorie._execute_sp(
            "SP_GET_PURCHASE_HISTORY", params, poolDB
        )

    @staticmethod
    async def get_top_selling(
        limit: int = 10,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        R4. Productos Más Vendidos - Obtiene los productos con mayor cantidad vendida.

        El SP utiliza SUM(quantity) en exit_note_detail,
        agrupa por product_id y ordena de forma descendente.

        Args:
            limit: Número máximo de productos a retornar (default: 10).

        Returns:
            Lista de productos más vendidos.
        """
        params = {"p_limit": limit}
        return await ReportRepositorie._execute_sp(
            "SP_GET_TOP_SELLING", params, poolDB
        )

    @staticmethod
    async def get_low_stock(
        threshold: int = 10,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        R5. Productos Bajo Stock - Obtiene productos con stock menor al umbral.

        El SP filtra products WHERE stock < p_stock_threshold.

        Args:
            threshold: Umbral mínimo de stock (default: 10).

        Returns:
            Lista de productos con bajo stock.
        """
        params = {"p_stock_threshold": threshold}
        return await ReportRepositorie._execute_sp(
            "SP_GET_LOW_STOCK", params, poolDB
        )
