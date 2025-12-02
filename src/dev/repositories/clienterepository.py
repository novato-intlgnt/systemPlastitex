from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from src.dev.config.db import async_session_maker
from src.dev.models.clients import Client
from src.dev.utils.security import decode, getPassHashed, sign, verifyPassHashed


class ClientRepository:
    
    @staticmethod
    async def check_exists(
        email: str, 
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ) -> bool:
        """Verificar si un cliente ya existe por email"""
        async with poolDB() as session:
            query = select(Client).where(Client.email == email)
            result = await session.execute(query)
            client = result.scalar_one_or_none()
            return client is not None

    @staticmethod
    async def get_all(
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        """Obtener todos los clientes"""
        async with poolDB() as session:
            query = select(Client)
            result = await session.execute(query)
            clients = result.scalars().all()
            
            # Convertir a lista de diccionarios
            return [
                {
                    "id": client.id,
                    "name": client.name,
                    "email": client.email,
                    "phone": client.phone,
                    "address": client.address
                }
                for client in clients
            ]

    @staticmethod
    async def get_by_id(
        client_id: int,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        """Obtener un cliente por ID"""
        async with poolDB() as session:
            query = select(Client).where(Client.id == client_id)
            result = await session.execute(query)
            client = result.scalar_one_or_none()
            
            if not client:
                raise HTTPException(404, "Cliente no encontrado")
            
            return {
                "id": client.id,
                "name": client.name,
                "email": client.email,
                "phone": client.phone,
                "address": client.address
            }

    @staticmethod
    async def create(
        input_data: dict,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        """Crear un nuevo cliente"""
        name = input_data["name"]
        email = input_data["email"]
        phone = input_data.get("phone")
        address = input_data.get("address")

        new_client = Client(
            name=name,
            email=email,
            phone=phone,
            address=address
        )

        async with poolDB() as session:
            try:
                session.add(new_client)
                await session.commit()
                await session.refresh(new_client)
                
                return {
                    "status": True, 
                    "client": {
                        "id": new_client.id,
                        "name": new_client.name,
                        "email": new_client.email,
                        "phone": new_client.phone,
                        "address": new_client.address
                    }
                }

            except IntegrityError:
                await session.rollback()
                raise HTTPException(400, "El email ya está registrado")

            except SQLAlchemyError as e:
                await session.rollback()
                raise HTTPException(500, f"Error en la base de datos: {str(e)}")

    @staticmethod
    async def update(
        client_id: int,
        input_data: dict,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        """Actualizar un cliente"""
        async with poolDB() as session:
            try:
                # Buscar cliente
                query = select(Client).where(Client.id == client_id)
                result = await session.execute(query)
                client = result.scalar_one_or_none()

                if not client:
                    raise HTTPException(404, "Cliente no encontrado")

                # Actualizar solo campos proporcionados
                if "name" in input_data:
                    client.name = input_data["name"]
                if "email" in input_data:
                    client.email = input_data["email"]
                if "phone" in input_data:
                    client.phone = input_data["phone"]
                if "address" in input_data:
                    client.address = input_data["address"]

                await session.commit()
                await session.refresh(client)
                
                return {
                    "status": True, 
                    "client": {
                        "id": client.id,
                        "name": client.name,
                        "email": client.email,
                        "phone": client.phone,
                        "address": client.address
                    }
                }

            except IntegrityError:
                await session.rollback()
                raise HTTPException(400, "El email ya está registrado")

            except SQLAlchemyError as e:
                await session.rollback()
                raise HTTPException(500, f"Error en la base de datos: {str(e)}")

    @staticmethod
    async def delete(
        client_id: int,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker
    ):
        """Eliminar un cliente"""
        async with poolDB() as session:
            try:
                # Buscar cliente
                query = select(Client).where(Client.id == client_id)
                result = await session.execute(query)
                client = result.scalar_one_or_none()

                if not client:
                    raise HTTPException(404, "Cliente no encontrado")

                # Eliminar
                await session.delete(client)
                await session.commit()
                
                return {"status": True, "message": "Cliente eliminado"}

            except SQLAlchemyError as e:
                await session.rollback()
                raise HTTPException(500, f"Error en la base de datos: {str(e)}")