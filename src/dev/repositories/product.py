from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.dev.config.db import async_session_maker
from src.dev.models.category import Category
from src.dev.models.product import Product
from src.dev.models.unit import Unit


class ProductRepository:

    # CHECK: Verifica si el producto existe (nombre y categoría)
    @staticmethod
    async def check(
        data: dict, poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        async with poolDB() as session:
            try:
                name = data["name"]
                category_id = int(data["category_id"])

                query = select(Product).where(
                    (Product.name == name) & (Product.category_id == category_id)
                )
                result = await session.execute(query)

                product = result.first()
                return product is not None

            except Exception as e:
                await session.rollback()
                print("❌ ERROR EXACTO:", e)
                raise HTTPException(500, "Error en la base de datos")

    # GET ALL: Lista de productos con joins (nombre categoría/unidad)
    @staticmethod
    async def get_all(poolDB: async_sessionmaker[AsyncSession] = async_session_maker):
        async with poolDB() as session:
            query = (
                select(Product, Category.name, Unit.name)
                .join(Category, Product.category_id == Category.id)
                .join(Unit, Product.unit_id == Unit.id)
                .where(Product.is_active == True)
            )

            result = await session.execute(query)

        products = result.all()
        products_list = []

        for product, category_name, unit_name in products:
            products_list.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "category": category_name,
                    "unit": unit_name,
                    "stock": product.stock,
                    "sale_price": float(product.sale_price),
                    "purchase_price": float(product.purchase_price),
                }
            )

        return products_list

    # GET BY ID
    @staticmethod
    async def get_byId(
        prod_id: int, poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        async with poolDB() as session:
            query = (
                select(Product, Category.name, Unit.name)
                .join(Category, Product.category_id == Category.id)
                .join(Unit, Product.unit_id == Unit.id)
                .where(Product.id == prod_id)
            )

            result = await session.execute(query)

        row = result.first()
        if not row:
            raise HTTPException(404, "Producto no encontrado")

        product, category_name, unit_name = row

        return {
            "id": product.id,
            "name": product.name,
            "category": category_name,
            "unit": unit_name,
            "stock": product.stock,
            "sale_price": float(product.sale_price),
            "purchase_price": float(product.purchase_price),
        }

    # CREATE: Crear producto
    @staticmethod
    async def create(
        product_data: dict,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ):
        async with poolDB() as session:
            try:
                print(product_data)
                new_product = Product(
                    name=product_data["name"],
                    category_id=int(product_data["category_id"]),
                    unit_id=int(product_data["unit_id"]),
                    stock=int(product_data.get("stock", 0)),
                    sale_price=float(product_data.get("sale_price", 0)),
                    purchase_price=float(product_data.get("purchase_price", 0)),
                )

                session.add(new_product)
                await session.commit()
                await session.refresh(new_product)

                return {"status": True}

            except Exception as e:
                await session.rollback()
                print("❌ ERROR EXACTO:", e)
                raise HTTPException(500, "Error en la base de datos")

            except IntegrityError:
                raise HTTPException(400, "El producto ya existe")

            except SQLAlchemyError:
                raise HTTPException(500, "Error en la base de datos")

    # MODIFY: Modificar producto
    @staticmethod
    async def modify(
        prod_id: int,
        new_data: dict,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ):
        async with poolDB() as session:
            try:
                product = await session.get(Product, prod_id)

                if not product:
                    raise HTTPException(404, "El producto no existe")

                colums_int = ["id", "category_id", "unit_id", "stock"]
                colums_float = ["purchase_price", "sale_price"]
                for key, value in new_data.items():
                    if hasattr(product, key):
                        if key in colums_int:
                            setattr(product, key, int(value))
                            continue
                        if key in colums_float:
                            setattr(product, key, float(value))
                            continue
                        setattr(product, key, value)

                await session.commit()
                await session.refresh(product)

                return {"status": True}

            except SQLAlchemyError:
                await session.rollback()
                raise HTTPException(500, "Error en la base de datos")

    # DELETE: Soft delete

    @staticmethod
    async def delete(
        prod_id: int, poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        async with poolDB() as session:
            try:
                product = await session.get(Product, prod_id)

                if not product:
                    raise HTTPException(404, "Producto no encontrado")

                if not product.is_active:
                    raise HTTPException(400, "El producto ya está eliminado")

                product.is_active = False
                product.deleted_at = datetime.utcnow()

                await session.commit()

                return {"status": True, "message": "Producto eliminado"}

            except SQLAlchemyError:
                await session.rollback()
                raise HTTPException(500, "Error en la base de datos")
