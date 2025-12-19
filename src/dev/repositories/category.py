from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.dev.config.db import async_session_maker
from src.dev.models.category import Category
from src.dev.models.product import Product


class CategoryRepository:

    # CHECK: Verifica si la categoría existe (por nombre)

    @staticmethod
    async def check(
        data: dict, poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        name = data["name"]

        async with poolDB() as session:
            query = select(Category).where(Category.name == name)
            result = await session.execute(query)

        category = result.first()
        return category is not None

    # GET ALL: Lista de categorías activas

    @staticmethod
    async def get_all(poolDB: async_sessionmaker[AsyncSession] = async_session_maker):
        async with poolDB() as session:
            query = (
                select(Category)
                .join(Product, Category.id == Product.category_id)
                .where(Category.is_active == True)
                .where(Product.is_active == True)
                .distinct()
            )
            result = await session.execute(query)

        categories = result.scalars().all()
        categories_list = []

        for category in categories:
            categories_list.append(
                {
                    "id": category.id,
                    "name": category.name,
                }
            )

        return categories_list

    # GET BY ID: Una sola categoría

    @staticmethod
    async def get_byId(
        category_id: int,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ):
        async with poolDB() as session:
            query = select(Category).where(Category.id == category_id)
            result = await session.execute(query)

        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(404, "Categoría no encontrada")

        return {
            "id": category.id,
            "name": category.name,
        }

    # CREATE: Crear categoría
    @staticmethod
    async def create(
        category_data: dict,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ):
        try:
            new_category = Category(
                name=category_data["name"],
            )

            async with poolDB() as session:
                session.add(new_category)
                await session.commit()
                await session.refresh(new_category)

                return {"status": True}

        except IntegrityError:
            raise HTTPException(400, "La categoría ya existe")

        except SQLAlchemyError:
            raise HTTPException(500, "Error en la base de datos")

    # MODIFY: Modificar categoría
    @staticmethod
    async def modify(
        category_id: int,
        new_data: dict,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ):
        async with poolDB() as session:
            try:
                category = await session.get(Category, category_id)

                if not category:
                    raise HTTPException(404, "La categoría no existe")

                for key, value in new_data.items():
                    if hasattr(category, key):
                        setattr(category, key, value)

                await session.commit()
                await session.refresh(category)

                return {"status": True}

            except SQLAlchemyError:
                await session.rollback()
                raise HTTPException(500, "Error en la base de datos")

    # DELETE: Soft delete
    @staticmethod
    async def delete(
        category_id: int,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ):
        async with poolDB() as session:
            try:
                category = await session.get(Category, category_id)

                if not category:
                    raise HTTPException(404, "Categoría no encontrada")

                if not category.is_active:
                    raise HTTPException(400, "La categoría ya está eliminada")

                category.is_active = False
                category.deleted_at = datetime.utcnow()

                await session.commit()

                return {"status": True, "message": "Categoría eliminada"}

            except SQLAlchemyError:
                await session.rollback()
                raise HTTPException(500, "Error en la base de datos")
