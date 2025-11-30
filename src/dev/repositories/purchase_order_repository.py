from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from src.dev.models.purchaseOrder import PurchaseOrder
from src.dev.models.purchaseOrderDetail import PurchaseOrderDetail
from src.dev.config.db import async_session_maker


class PurchaseOrderRepository:

    @staticmethod
    async def get_all():
        """Obtener todas las órdenes de compra"""
        async with async_session_maker() as session:
            query = select(PurchaseOrder).options(
                joinedload(PurchaseOrder.supplier),
                joinedload(PurchaseOrder.details)
            )
            result = await session.execute(query)
            orders = result.unique().scalars().all()
            return [
                {
                    "id": order.id,
                    "user_id": order.user_id,
                    "supplier_id": order.supplier_id,
                    "supplier_name": order.supplier.name if order.supplier else None,
                    "date": order.date,
                    "total": float(order.total),
                    "status": order.status,
                }
                for order in orders
            ]

    @staticmethod
    async def get_by_id(order_id: int):
        """Obtener una orden de compra por ID"""
        async with async_session_maker() as session:
            query = select(PurchaseOrder).where(
                PurchaseOrder.id == order_id
            ).options(
                joinedload(PurchaseOrder.supplier),
                joinedload(PurchaseOrder.details)
            )
            result = await session.execute(query)
            order = result.unique().scalars().first()
            
            if not order:
                return None
            
            return {
                "id": order.id,
                "user_id": order.user_id,
                "supplier_id": order.supplier_id,
                "supplier_name": order.supplier.name if order.supplier else None,
                "date": order.date,
                "total": float(order.total),
                "status": order.status,
                "details": [
                    {
                        "id": detail.id,
                        "product_id": detail.product_id,
                        "quantity": detail.quantity,
                        "unit_price": float(detail.unit_price),
                    }
                    for detail in order.details
                ]
            }

    @staticmethod
    async def create(data: dict, user_id: int):
        """Crear una nueva orden de compra"""
        async with async_session_maker() as session:
            try:
                # Crear la orden de compra
                order = PurchaseOrder(
                    user_id=user_id,
                    supplier_id=data.get("supplier_id"),
                    date=data.get("date"),
                    total=data.get("total", 0),
                    status=data.get("status", "pending")
                )
                session.add(order)
                await session.flush()

                
                details = data.get("details", [])
                for detail in details:
                    order_detail = PurchaseOrderDetail(
                        order_id=order.id,
                        product_id=detail.get("product_id"),
                        quantity=detail.get("quantity"),
                        unit_price=detail.get("unit_price")
                    )
                    session.add(order_detail)

                await session.commit()
                await session.refresh(order)

                return {
                    "id": order.id,
                    "user_id": order.user_id,
                    "supplier_id": order.supplier_id,
                    "date": order.date,
                    "total": float(order.total),
                    "status": order.status,
                }
            except Exception as e:
                await session.rollback()
                raise e

    @staticmethod
    async def update(order_id: int, data: dict):
        """Actualizar una orden de compra"""
        async with async_session_maker() as session:
            try:
                query = select(PurchaseOrder).where(PurchaseOrder.id == order_id)
                result = await session.execute(query)
                order = result.scalars().first()

                if not order:
                    return None

            
                if "date" in data:
                    order.date = data["date"]
                if "total" in data:
                    order.total = data["total"]
                if "status" in data:
                    order.status = data["status"]
                if "supplier_id" in data:
                    order.supplier_id = data["supplier_id"]

                await session.commit()
                await session.refresh(order)

                return {
                    "id": order.id,
                    "user_id": order.user_id,
                    "supplier_id": order.supplier_id,
                    "date": order.date,
                    "total": float(order.total),
                    "status": order.status,
                }
            except Exception as e:
                await session.rollback()
                raise e

    @staticmethod
    async def delete(order_id: int):
        """Eliminar una orden de compra"""
        async with async_session_maker() as session:
            try:
                query = select(PurchaseOrder).where(PurchaseOrder.id == order_id)
                result = await session.execute(query)
                order = result.scalars().first()

                if not order:
                    return False

                await session.delete(order)
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                raise e
