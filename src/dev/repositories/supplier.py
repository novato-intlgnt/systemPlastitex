from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.dev.config.db import async_session_maker
from src.dev.models.supplier import Supplier


class SupplierRepository:
    @staticmethod
    async def check(
        data: dict, poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        name = data["name"]
        phone = data["phone"]
        async with poolDB() as session:
            query = select(Supplier).where(
                (Supplier.name == name) & (Supplier.phone == phone)
            )
            result = await session.execute(query)
        supplier = result.first()
        return supplier is not None

    @staticmethod
    async def get_all(poolDB: async_sessionmaker[AsyncSession] = async_session_maker):
        async with poolDB() as session:
            query = select(Supplier).where(Supplier.is_active == True)
            result = await session.execute(query)
        suppliers = result.scalars().all()
        suppliers_list = []
        for supplier in suppliers:
            suppliers_list.append(
                {
                    "id": supplier.id,
                    "name": supplier.name,
                    "phone": supplier.phone,
                    "address": supplier.address,
                }
            )
        return suppliers_list

    @staticmethod
    async def get_byId(
        idSupp: int, poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        async with poolDB() as session:
            query = select(Supplier).where((Supplier.id == idSupp))
            result = await session.execute(query)
        supplier = result.scalar_one_or_none()
        return {
            "id": supplier.id,
            "name": supplier.name,
            "phone": supplier.phone,
            "address": supplier.address,
        }

    @staticmethod
    async def create(
        supplier_data: dict,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ):
        name = supplier_data["name"]
        phone = supplier_data["phone"]
        address = supplier_data["address"]

        new_supplier = Supplier(name=name, phone=phone, address=address)
        async with poolDB() as session:
            try:
                session.add(new_supplier)
                await session.commit()
                await session.refresh(new_supplier)
                return {"status": True}

            except IntegrityError:
                await session.rollback()
                raise HTTPException(400, "El proveedor ya existe")

            except SQLAlchemyError:
                await session.rollback()
                raise HTTPException(500, "Error en la base de datos")

    @staticmethod
    async def modify(
        supp_id: int,
        new_data: dict,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ):
        async with poolDB() as session:
            try:
                supplier = await session.get(Supplier, supp_id)
                if not supplier:
                    raise HTTPException(404, "The supplier is not exists")

                for key, value in new_data.items():
                    if hasattr(supplier, key):
                        setattr(supplier, key, value)

                await session.commit()
                await session.refresh(supplier)

                return {"status": True}
            except SQLAlchemyError:
                await session.rollback()
                raise HTTPException(500, "Error en la base de datos")

    @staticmethod
    async def delete(
        supp_id: int, poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        async with poolDB() as session:
            try:
                supplier = await session.get(Supplier, supp_id)

                if not supplier:
                    raise HTTPException(404, "Proveedor no encontrado")

                if not supplier.is_active:
                    raise HTTPException(400, "El proveedor ya está eliminado")

                supplier.is_active = False
                supplier.deleted_at = datetime.utcnow()

                await session.commit()

                return {"status": True, "message": "Proveedor eliminado"}

            except SQLAlchemyError:
                await session.rollback()
                raise HTTPException(500, "Error en la base de datos")
