from typing import Optional

from fastapi import HTTPException
from fastapi.responses import JSONResponse


class ReportController:
    """
    Controlador de reportes con Control de Acceso Basado en Roles (RBAC).
    Valida el rol del usuario antes de invocar la lógica del repositorio.
    """

    def __init__(self, report_repositorie):
        self.report_repositorie = report_repositorie

    @staticmethod
    def _check_role(current_role: str, allowed_roles: list[str]) -> None:
        """
        Método auxiliar para validar el rol del usuario.

        Args:
            current_role: Rol actual del usuario autenticado.
            allowed_roles: Lista de roles permitidos para la operación.

        Raises:
            HTTPException: 403 si el rol no está permitido.
        """
        if current_role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Acceso no autorizado.")

    async def get_kardex(
        self,
        current_role: str,
        product_id: int,
        start_date: str,
        end_date: str,
    ):
        """
        R1. Kardex Físico - Obtiene los movimientos de entrada y salida de un producto.

        Roles permitidos: aux_almacen, admin

        Args:
            current_role: Rol del usuario autenticado.
            product_id: ID del producto.
            start_date: Fecha de inicio.
            end_date: Fecha de fin.

        Returns:
            JSONResponse con los datos del kardex.
        """
        self._check_role(current_role, ["aux_almacen", "admin"])

        try:
            data = await self.report_repositorie.get_kardex_data(
                product_id, start_date, end_date
            )
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "data": data,
                    "count": len(data),
                },
            )
        except Exception as e:
            print("Error in get_kardex:", e)
            raise HTTPException(status_code=500, detail="Error al obtener el kardex.")

    async def get_current_stock(
        self,
        current_role: str,
        category_id: Optional[int] = None,
    ):
        """
        R2. Stock Actual - Obtiene el stock actual de productos.

        Roles permitidos: aux_almacen, admin

        Args:
            current_role: Rol del usuario autenticado.
            category_id: ID de la categoría (opcional).

        Returns:
            JSONResponse con el stock actual.
        """
        self._check_role(current_role, ["aux_almacen", "admin"])

        try:
            data = await self.report_repositorie.get_current_stock(category_id)
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "data": data,
                    "count": len(data),
                },
            )
        except Exception as e:
            print("Error in get_current_stock:", e)
            raise HTTPException(
                status_code=500, detail="Error al obtener el stock actual."
            )

    async def get_purchase_history(
        self,
        current_role: str,
        supplier_id: int,
        start_date: str,
        end_date: str,
    ):
        """
        R3. Historial de Compras - Obtiene las órdenes de compra por proveedor.

        Roles permitidos: aux_compra, admin

        Args:
            current_role: Rol del usuario autenticado.
            supplier_id: ID del proveedor.
            start_date: Fecha de inicio.
            end_date: Fecha de fin.

        Returns:
            JSONResponse con el historial de compras.
        """
        self._check_role(current_role, ["aux_compra", "admin"])

        try:
            data = await self.report_repositorie.get_purchase_history(
                supplier_id, start_date, end_date
            )
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "data": data,
                    "count": len(data),
                },
            )
        except Exception as e:
            print("Error in get_purchase_history:", e)
            raise HTTPException(
                status_code=500, detail="Error al obtener el historial de compras."
            )

    async def get_top_selling(
        self,
        current_role: str,
        limit: int = 10,
    ):
        """
        R4. Productos Más Vendidos - Obtiene los productos con mayor cantidad vendida.

        Roles permitidos: aux_almacen, admin

        Args:
            current_role: Rol del usuario autenticado.
            limit: Número máximo de productos.

        Returns:
            JSONResponse con los productos más vendidos.
        """
        self._check_role(current_role, ["aux_almacen", "admin"])

        try:
            data = await self.report_repositorie.get_top_selling(limit)
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "data": data,
                    "count": len(data),
                },
            )
        except Exception as e:
            print("Error in get_top_selling:", e)
            raise HTTPException(
                status_code=500, detail="Error al obtener los productos más vendidos."
            )

    async def get_low_stock(
        self,
        current_role: str,
        threshold: int = 10,
    ):
        """
        R5. Productos Bajo Stock - Obtiene productos con stock menor al umbral.

        Roles permitidos: aux_compra, admin

        Args:
            current_role: Rol del usuario autenticado.
            threshold: Umbral mínimo de stock.

        Returns:
            JSONResponse con los productos bajo stock.
        """
        self._check_role(current_role, ["aux_compra", "admin"])

        try:
            data = await self.report_repositorie.get_low_stock(threshold)
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "data": data,
                    "count": len(data),
                },
            )
        except Exception as e:
            print("Error in get_low_stock:", e)
            raise HTTPException(
                status_code=500, detail="Error al obtener los productos bajo stock."
            )

    # ==========================================================================
    # NUEVOS MÉTODOS PARA REPORTES EXTENDIDOS
    # ==========================================================================

    async def get_low_stock_aux_compra(
        self,
        current_role: str,
        threshold: int = 10,
    ):
        """
        Productos Bajo Stock para Aux Compra - Con query dinámica.

        Roles permitidos: aux_compra, admin

        Args:
            current_role: Rol del usuario autenticado.
            threshold: Umbral mínimo de stock (default: 10).

        Returns:
            JSONResponse con productos donde stock < threshold.
        """
        self._check_role(current_role, ["aux_compra", "admin"])

        try:
            data = await self.report_repositorie.get_low_stock_dynamic(threshold)
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "data": data,
                    "count": len(data),
                    "threshold": threshold,
                },
            )
        except Exception as e:
            print("Error in get_low_stock_aux_compra:", e)
            raise HTTPException(
                status_code=500, detail="Error al obtener productos con bajo stock."
            )

    async def get_purchase_history_filtered(
        self,
        current_role: str,
        supplier_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ):
        """
        Historial de Compras con filtros opcionales para Aux Compra.

        Roles permitidos: aux_compra, admin

        Args:
            current_role: Rol del usuario autenticado.
            supplier_id: ID del proveedor (opcional).
            start_date: Fecha de inicio (opcional).
            end_date: Fecha de fin (opcional).

        Returns:
            JSONResponse con el historial filtrado.
        """
        self._check_role(current_role, ["aux_compra", "admin"])

        try:
            data = await self.report_repositorie.get_purchase_history_dynamic(
                supplier_id, start_date, end_date
            )
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "data": data,
                    "count": len(data),
                    "filters": {
                        "supplier_id": supplier_id,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                },
            )
        except Exception as e:
            print("Error in get_purchase_history_filtered:", e)
            raise HTTPException(
                status_code=500, detail="Error al obtener el historial de compras."
            )

    async def get_stock_aux_almacen(
        self,
        current_role: str,
        product_id: Optional[int] = None,
    ):
        """
        Stock para Aux Almacén - Con filtro opcional por producto.

        Roles permitidos: aux_almacen, admin

        Args:
            current_role: Rol del usuario autenticado.
            product_id: ID del producto (opcional, None para todos).

        Returns:
            JSONResponse con información de stock detallada.
        """
        self._check_role(current_role, ["aux_almacen", "admin"])

        try:
            data = await self.report_repositorie.get_stock_by_product(product_id)
            print(data)
            result_list = []
            for product in data:
                result_list.append(
                    {
                        "product_id": product["product_id"],
                        "product_name": product["product_name"],
                        "stock": product["current_stock"],
                        "category_name": product["category_name"],
                        "unit_name": product["unit_name"],
                        "total_entries": product["total_entries"],
                        "total_exits": product["total_exits"],
                        "sale_price": (
                            float(product["sale_price"])
                            if product["sale_price"]
                            else None
                        ),
                        "purchase_price": (
                            float(product["purchase_price"])
                            if product["purchase_price"]
                            else None
                        ),
                    }
                )

            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "data": result_list,
                    "count": len(result_list),
                },
            )
        except Exception as e:
            print("Error in get_stock_aux_almacen:", e)
            raise HTTPException(
                status_code=500, detail="Error al obtener información de stock."
            )

    async def get_kardex_by_product(
        self,
        current_role: str,
        product_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ):
        """
        Kardex por Producto para Aux Almacén.

        Roles permitidos: aux_almacen, admin

        Args:
            current_role: Rol del usuario autenticado.
            product_id: ID del producto (requerido).
            start_date: Fecha de inicio (opcional).
            end_date: Fecha de fin (opcional).

        Returns:
            JSONResponse con los movimientos del kardex.
        """
        self._check_role(current_role, ["aux_almacen", "admin"])

        if not product_id:
            raise HTTPException(status_code=400, detail="El product_id es requerido.")

        try:
            data = await self.report_repositorie.get_kardex_by_product(
                product_id, start_date, end_date
            )
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "data": data,
                    "count": len(data),
                    "product_id": product_id,
                    "filters": {
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                },
            )
        except Exception as e:
            print("Error in get_kardex_by_product:", e)
            raise HTTPException(
                status_code=500, detail="Error al obtener el kardex del producto."
            )
