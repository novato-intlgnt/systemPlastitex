from typing import Any, Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.dev.config.db import async_session_maker
from src.dev.models.category import Category
from src.dev.models.product import Product
from src.dev.models.unit import Unit


class ReportRepositorie:
    """
    Repositorio para reportes que utiliza Procedimientos Almacenados (SP).
    Todos los métodos delegan la lógica de consulta compleja a los SP de la base de datos.
    También incluye métodos con queries dinámicas para filtros opcionales.
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
    async def _execute_dynamic_query(
        query: str,
        params: dict[str, Any],
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        Método auxiliar para ejecutar queries dinámicas con parámetros opcionales.

        Args:
            query: Query SQL con placeholders.
            params: Diccionario de parámetros.
            poolDB: Pool de conexiones a la base de datos.

        Returns:
            Lista de diccionarios con los resultados.
        """
        async with poolDB() as session:
            result = await session.execute(text(query), params)
            rows = result.fetchall()

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

    # ==========================================================================
    # NUEVOS MÉTODOS PARA REPORTES EXTENDIDOS
    # ==========================================================================

    @staticmethod
    async def get_low_stock_dynamic(
        threshold: int = 10,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        R5 Alternativo. Productos Bajo Stock con query dinámica.
        
        Útil cuando no se tiene el SP configurado en la base de datos.
        Lista productos donde stock < threshold.

        Args:
            threshold: Umbral mínimo de stock (default: 10).

        Returns:
            Lista de productos con bajo stock incluyendo déficit calculado.
        """
        async with poolDB() as session:
            query = (
                select(
                    Product.id,
                    Product.name,
                    Category.name.label("category_name"),
                    Unit.name.label("unit_name"),
                    Product.stock,
                    Product.purchase_price,
                )
                .join(Category, Product.category_id == Category.id)
                .join(Unit, Product.unit_id == Unit.id)
                .where(Product.is_active == True)
                .where(Product.stock < threshold)
                .order_by(Product.stock.asc())
            )
            
            result = await session.execute(query)
            rows = result.all()
            
            return [
                {
                    "product_id": row.id,
                    "product_name": row.name,
                    "category_name": row.category_name,
                    "unit_name": row.unit_name,
                    "current_stock": row.stock,
                    "threshold": threshold,
                    "deficit": threshold - row.stock,
                    "purchase_price": float(row.purchase_price) if row.purchase_price else 0,
                }
                for row in rows
            ]

    @staticmethod
    async def get_purchase_history_dynamic(
        supplier_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        R3 Extendido. Historial de Compras con filtros opcionales.
        
        Construye una query dinámica que soporta parámetros nulos.
        Si supplier_id es None, retorna todas las compras.
        Si start_date/end_date son None, no aplica filtro de fecha.

        Args:
            supplier_id: ID del proveedor (opcional, None para todos).
            start_date: Fecha de inicio (opcional, formato: YYYY-MM-DD).
            end_date: Fecha de fin (opcional, formato: YYYY-MM-DD).

        Returns:
            Lista de órdenes de compra filtradas.
        """
        # Construir query base
        query = """
            SELECT 
                po.id AS order_id,
                po.date AS order_date,
                s.id AS supplier_id,
                s.name AS supplier_name,
                po.total,
                po.status,
                u.fullname AS created_by
            FROM purchase_order po
            INNER JOIN suppliers s ON po.supplier_id = s.id
            INNER JOIN users u ON po.user_id = u.id
            WHERE po.is_active = TRUE
        """
        
        params = {}
        
        # Agregar filtros opcionales
        if supplier_id is not None:
            query += " AND po.supplier_id = :supplier_id"
            params["supplier_id"] = supplier_id
        
        if start_date is not None:
            query += " AND po.date >= :start_date"
            params["start_date"] = start_date
        
        if end_date is not None:
            query += " AND po.date <= :end_date"
            params["end_date"] = end_date
        
        query += " ORDER BY po.date DESC"
        
        return await ReportRepositorie._execute_dynamic_query(query, params, poolDB)

    @staticmethod
    async def get_stock_by_product(
        product_id: Optional[int] = None,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        Stock por Producto - Obtiene el stock de un producto específico o todos.
        
        Si product_id es None, retorna el stock de todos los productos.
        Incluye información de entradas y salidas totales.

        Args:
            product_id: ID del producto (opcional, None para todos).

        Returns:
            Lista de productos con información de stock detallada.
        """
        query = """
            SELECT 
                p.id AS product_id,
                p.name AS product_name,
                c.id AS category_id,
                c.name AS category_name,
                u.id AS unit_id,
                u.name AS unit_name,
                p.stock,
                p.sale_price,
                p.purchase_price,
                COALESCE((
                    SELECT SUM(end_detail.quantity)
                    FROM entry_note_detail end_detail
                    INNER JOIN entry_note en ON end_detail.entry_id = en.id
                    WHERE end_detail.product_id = p.id AND end_detail.is_active = TRUE
                ), 0) AS total_entries,
                COALESCE((
                    SELECT SUM(exd.quantity)
                    FROM exit_note_detail exd
                    INNER JOIN exit_note exn ON exd.exit_id = exn.id
                    WHERE exd.product_id = p.id AND exd.is_active = TRUE
                ), 0) AS total_exits
            FROM products p
            INNER JOIN categories c ON p.category_id = c.id
            INNER JOIN units u ON p.unit_id = u.id
            WHERE p.is_active = TRUE
        """
        
        params = {}
        
        if product_id is not None:
            query += " AND p.id = :product_id"
            params["product_id"] = product_id
        
        query += " ORDER BY p.name"
        
        return await ReportRepositorie._execute_dynamic_query(query, params, poolDB)

    @staticmethod
    async def get_kardex_by_product(
        product_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        Kardex por Producto - Obtiene los movimientos de un producto específico.
        
        Combina entradas y salidas en un solo resultado ordenado por fecha.
        Si no se especifican fechas, retorna todos los movimientos.

        Args:
            product_id: ID del producto (requerido).
            start_date: Fecha de inicio (opcional, formato: YYYY-MM-DD).
            end_date: Fecha de fin (opcional, formato: YYYY-MM-DD).

        Returns:
            Lista de movimientos del kardex del producto.
        """
        # Construir filtro de fechas
        date_filter_entry = ""
        date_filter_exit = ""
        params = {"product_id": product_id}
        
        if start_date:
            date_filter_entry += " AND en.date >= :start_date"
            date_filter_exit += " AND exn.date >= :start_date"
            params["start_date"] = start_date
        
        if end_date:
            date_filter_entry += " AND en.date <= :end_date"
            date_filter_exit += " AND exn.date <= :end_date"
            params["end_date"] = end_date
        
        query = f"""
            SELECT * FROM (
                -- Entradas (saldo positivo)
                SELECT 
                    en.date AS movement_date,
                    'ENTRADA' AS movement_type,
                    en.reference,
                    end_detail.quantity,
                    end_detail.quantity AS balance,
                    s.name AS supplier_customer_name,
                    'Proveedor' AS entity_type
                FROM entry_note_detail end_detail
                INNER JOIN entry_note en ON end_detail.entry_id = en.id
                INNER JOIN suppliers s ON en.supplier_id = s.id
                WHERE end_detail.product_id = :product_id
                    AND end_detail.is_active = TRUE
                    {date_filter_entry}
                
                UNION ALL
                
                -- Salidas (saldo negativo)
                SELECT 
                    exn.date AS movement_date,
                    'SALIDA' AS movement_type,
                    exn.reference,
                    exd.quantity,
                    -exd.quantity AS balance,
                    c.name AS supplier_customer_name,
                    'Cliente' AS entity_type
                FROM exit_note_detail exd
                INNER JOIN exit_note exn ON exd.exit_id = exn.id
                INNER JOIN customers c ON exn.customer_id = c.id
                WHERE exd.product_id = :product_id
                    AND exd.is_active = TRUE
                    {date_filter_exit}
            ) AS kardex
            ORDER BY movement_date ASC
        """
        
        return await ReportRepositorie._execute_dynamic_query(query, params, poolDB)
