from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.dev.config.db import async_session_maker
from src.dev.models.unit import Unit


class UnitRepository:

    # CHECK: Verifica si la unidad existe (nombre)
    @staticmethod
    async def check(
        data: dict, poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        name = data["name"]

        async with poolDB() as session:
            query = select(Unit).where(Unit.name == name)
            result = await session.execute(query)

        unit = result.first()
        return unit is not None

    # GET ALL: Lista de unidades activas

    @staticmethod
    async def get_all(poolDB: async_sessionmaker[AsyncSession] = async_session_maker):
        async with poolDB() as session:
            query = select(Unit).where(Unit.is_active == True)
            result = await session.execute(query)

        units = result.scalars().all()
        units_list = []

        for unit in units:
            units_list.append(
                {
                    "id": unit.id,
                    "name": unit.name,
                }
            )

        return units_list

    # GET BY ID: Una sola unidad

    @staticmethod
    async def get_byId(
        unit_id: int, poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        async with poolDB() as session:
            query = select(Unit).where(Unit.id == unit_id)
            result = await session.execute(query)

        unit = result.scalar_one_or_none()

        if not unit:
            raise HTTPException(404, "Unidad no encontrada")

        return {
            "id": unit.id,
            "name": unit.name,
        }

    # CREATE: Crear unidad

    @staticmethod
    async def create(
        unit_data: dict,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ):
        try:
            new_unit = Unit(
                name=unit_data["name"],
            )

            async with poolDB() as session:
                session.add(new_unit)
                await session.commit()
                await session.refresh(new_unit)

                return {"status": True}

        except IntegrityError:
            raise HTTPException(400, "La unidad ya existe")

        except SQLAlchemyError:
            raise HTTPException(500, "Error en la base de datos")

    # MODIFY: Modificar unidad

    @staticmethod
    async def modify(
        unit_id: int,
        new_data: dict,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ):
        async with poolDB() as session:
            try:
                unit = await session.get(Unit, unit_id)

                if not unit:
                    raise HTTPException(404, "La unidad no existe")

                for key, value in new_data.items():
                    if hasattr(unit, key):
                        setattr(unit, key, value)

                await session.commit()
                await session.refresh(unit)

                return {"status": True}

            except SQLAlchemyError:
                await session.rollback()
                raise HTTPException(500, "Error en la base de datos")

    # DELETE: Soft delete

    @staticmethod
    async def delete(
        unit_id: int, poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        async with poolDB() as session:
            try:
                unit = await session.get(Unit, unit_id)

                if not unit:
                    raise HTTPException(404, "Unidad no encontrada")

                if not unit.is_active:
                    raise HTTPException(400, "La unidad ya está eliminada")

                unit.is_active = False
                unit.deleted_at = datetime.utcnow()

                await session.commit()

                return {"status": True, "message": "Unidad eliminada"}

            except SQLAlchemyError:
                await session.rollback()
                raise HTTPException(500, "Error en la base de datos")
