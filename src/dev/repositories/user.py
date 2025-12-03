from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.dev.config.db import async_session_maker
from src.dev.models.user import User
from src.dev.utils.security import getPassHashed, sign, verifyPassHashed


class UserRepository:
    @staticmethod
    async def check(
        input_data: dict, poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        user = input_data["user"]
        rol = input_data["role"]
        async with poolDB() as session:
            query = select(User).where((User.username == user) & (User.role == rol))
            result = await session.execute(query)
        user = result.first()
        return user is not None

    @staticmethod
    async def create_worker(
        input_data: dict, poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        user = input_data["user"]
        name = input_data["name"]
        role = input_data["role"]
        password = getPassHashed(input_data["pass"])

        newUser = User(username=user, password=password, fullname=name, role=role)
        async with poolDB() as session:
            try:
                session.add(newUser)
                await session.commit()
                await session.refresh(newUser)
                return {"status": True}

            except IntegrityError:
                await session.rollback()
                raise HTTPException(400, "El usuario ya existe")

            except SQLAlchemyError:
                await session.rollback()
                raise HTTPException(500, "Error en la base de datos")

    @staticmethod
    async def auth(
        input_data: dict, poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        username = input_data["user"]
        password = input_data["pass"]

        async with poolDB() as session:
            query = select(User.password, User.role, User.id).where(
                User.username == username
            )
            result = await session.execute(query)
        user = result.first()
        
        if user is None:
            return {"status": False}
        
        passHashed = user.password
        roleUser = user.role
        userId = user.id
        
        if verifyPassHashed(password, passHashed) is False:
            return {"status": False}

        # El token incluye: user, role, id
        token = sign({"user": username, "role": roleUser, "id": userId})

        return {
            "auth": token,
            "name": username,
            "role": roleUser,
            "id": userId,
            "status": True,
        }
