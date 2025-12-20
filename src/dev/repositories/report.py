from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.dev.config.db import async_session_maker
from src.dev.models.category import Category
from src.dev.models.product import Product
from src.dev.models.unit import Unit


class ReportRepositorie:
    """
    Repositorio para reportes que utiliza Funciones de Base de Datos (DB Functions) en PostgreSQL.
    Todos los métodos delegan la lógica de consulta compleja a las funciones de la base de datos.
    """

    @staticmethod
    async def _execute_sp(
        sp_name: str,
        params: dict[str, Any],
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        MÉTODO AUXILIAR CORREGIDO PARA POSTGRESQL.
        Ejecuta una Función de BD (que retorna tabla) usando SELECT.

        Args:
            sp_name: Nombre de la función de BD (en PostgreSQL).
            params: Diccionario de parámetros a pasar.
            poolDB: Pool de conexiones a la base de datos.

        Returns:
            Lista de diccionarios con los resultados.
        """
        param_placeholders = ", ".join([f":{key}" for key in params.keys()])
        sql_statement = text(f"SELECT * FROM {sp_name}({param_placeholders})")

        async with poolDB() as session:
            result = await session.execute(sql_statement, params)
            rows = result.fetchall()

            if not rows:
                return []

            columns = result.keys()
            final_rows = []

            for row in rows:
                row_dict = dict(zip(columns, row))

                for key, value in row_dict.items():
                    if hasattr(value, "isoformat"):
                        row_dict[key] = value.isoformat()
                    if isinstance(value, Decimal):
                        row_dict[key] = float(value)
                final_rows.append(row_dict)

            return final_rows

    @staticmethod
    async def get_kardex_data(
        product_id: int,
        start_date: str,
        end_date: str,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        R1. Kardex Físico - Obtiene los movimientos de entrada y salida de un producto.
        Delega a la función de BD sp_get_kardex_fisico.
        """
        params = {
            "p_product_id": product_id,
            "p_start_date": datetime.strptime(start_date, "%Y-%m-%d").date(),
            "p_end_date": datetime.strptime(end_date, "%Y-%m-%d").date(),
        }
        # Usa el nombre de la función en minúsculas
        return await ReportRepositorie._execute_sp(
            "sp_get_kardex_fisico", params, poolDB
        )

    @staticmethod
    async def get_current_stock(
        category_id: Optional[int] = None,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        R2. Stock Actual - Obtiene el stock actual de productos por categoría.
        Delega a la función de BD sp_get_stock_categoria.
        """
        params = {"p_category_id": category_id}
        return await ReportRepositorie._execute_sp(
            "sp_get_stock_categoria", params, poolDB
        )

    @staticmethod
    async def get_purchase_history(
        supplier_id: Optional[int] = None,  # Firma actualizada para ser opcional
        start_date: Optional[str] = None,  # Firma actualizada para ser opcional
        end_date: Optional[str] = None,  # Firma actualizada para ser opcional
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        R3. Historial de Compras - Obtiene las órdenes de compra por proveedor.
        Delega a la función de BD sp_get_purchase_history.
        """

        def to_date(value: Optional[str]) -> Optional[date]:
            if value is None:
                return None
            return datetime.strptime(value, "%Y-%m-%d").date()

        start_date_parsed = to_date(start_date)
        end_date_parsed = to_date(end_date)

        params = {
            "p_supplier_id": supplier_id,
            "p_start_date": start_date_parsed,
            "p_end_date": end_date_parsed,
        }
        return await ReportRepositorie._execute_sp(
            "sp_get_purchase_history", params, poolDB
        )

    @staticmethod
    async def get_top_selling(
        limit: int = 10,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        R4. Productos Más Vendidos - Obtiene los productos con mayor cantidad vendida.
        Delega a la función de BD sp_get_top_selling.
        """
        params = {"p_limit": limit}
        return await ReportRepositorie._execute_sp("sp_get_top_selling", params, poolDB)

    @staticmethod
    async def get_low_stock(
        threshold: int = 10,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        R5. Productos Bajo Stock - Obtiene productos con stock menor al umbral.
        Delega a la función de BD sp_get_low_stock (que incluye el último proveedor).
        """
        params = {"p_stock_threshold": threshold}
        return await ReportRepositorie._execute_sp("sp_get_low_stock", params, poolDB)

    @staticmethod
    async def get_low_stock_dynamic(
        threshold: int = 10,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        R5 Alternativo. Redirigido a la función de BD, ya que es más completa.
        (El SP incluye el campo last_supplier que esta query dinámica no incluye).
        """
        # Redirigido al método principal que usa el SP completo.
        return await ReportRepositorie.get_low_stock(threshold, poolDB)

    @staticmethod
    async def get_purchase_history_dynamic(
        supplier_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        R3 Extendido. Historial de Compras con filtros opcionales.
        Redirigido al método principal que usa el SP, ya que el SP ahora soporta
        parámetros opcionales.
        """

        # Redirigido al método principal que usa el SP.
        return await ReportRepositorie.get_purchase_history(
            supplier_id, start_date, end_date, poolDB
        )

    @staticmethod
    async def get_stock_by_product(
        category_id: Optional[int] = None,
        unit_id: Optional[int] = None,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        R2. Stock Actual - Obtiene el stock actual de productos por categoría.
        Delega a la función de BD sp_get_current_stock.
        """
        print(category_id, unit_id)
        params = {
            "p_cat_id": category_id,
            "p_unit_id": unit_id,
        }

        return await ReportRepositorie._execute_sp(
            "sp_get_current_stock", params, poolDB
        )

    @staticmethod
    async def get_kardex_by_product(
        product_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        Kardex por Producto - Obtiene los movimientos de un producto específico.
        Delegando a la función de BD sp_get_kardex_fisico.
        """

        def to_date(value: Optional[str]) -> Optional[date]:
            if value is None:
                return None
            return datetime.strptime(value, "%Y-%m-%d").date()

        start_date_parsed = to_date(start_date)
        end_date_parsed = to_date(end_date)

        params = {
            "p_product_id": product_id,
            "p_start_date": start_date_parsed,
            "p_end_date": end_date_parsed,
        }

        return await ReportRepositorie._execute_sp(
            "sp_get_kardex_fisico", params, poolDB
        )
