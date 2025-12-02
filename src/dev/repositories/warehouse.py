"""
Repositorio para el módulo de Almacén (Warehouse).
Maneja las operaciones de base de datos para notas de ingreso y salida.
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import joinedload

from src.dev.config.db import async_session_maker
from src.dev.models.customer import Customer
from src.dev.models.entryNote import EntryNote
from src.dev.models.entryNoteDetail import EntryNoteDetail
from src.dev.models.exitNote import ExitNote
from src.dev.models.exitNoteDetail import ExitNoteDetail
from src.dev.models.product import Product
from src.dev.models.supplier import Supplier


class WarehouseRepository:
    """
    Repositorio para operaciones CRUD de notas de ingreso (Entry Notes) y 
    notas de salida (Exit Notes) del almacén.
    
    Utiliza SQLAlchemy AsyncSession para operaciones asíncronas.
    """

    # ==========================================================================
    # SECCIÓN A: NOTAS DE INGRESO (INBOUND / Entry Notes)
    # ==========================================================================

    @staticmethod
    async def create_entry_note(
        data: dict,
        user_id: int,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> dict:
        """
        Crea una nueva nota de ingreso (cabecera).
        
        Args:
            data: Diccionario con supplier_id y reference (opcional).
            user_id: ID del usuario que crea la nota.
            poolDB: Pool de conexiones a la base de datos.
            
        Returns:
            Diccionario con los datos de la nota creada.
        """
        async with poolDB() as session:
            try:
                # Verificar que el proveedor exista
                supplier = await session.get(Supplier, data.get("supplier_id"))
                if not supplier or not supplier.is_active:
                    raise HTTPException(
                        status_code=404,
                        detail="Proveedor no encontrado o inactivo"
                    )
                
                entry_note = EntryNote(
                    user_id=user_id,
                    supplier_id=data.get("supplier_id"),
                    date=datetime.utcnow(),
                    reference=data.get("reference"),
                    is_active=True,
                )
                
                session.add(entry_note)
                await session.commit()
                await session.refresh(entry_note)
                
                return {
                    "id": entry_note.id,
                    "user_id": entry_note.user_id,
                    "supplier_id": entry_note.supplier_id,
                    "supplier_name": supplier.name,
                    "date": entry_note.date.isoformat() if entry_note.date else None,
                    "reference": entry_note.reference,
                }
                
            except HTTPException:
                raise
            except SQLAlchemyError as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

    @staticmethod
    async def get_all_entry_notes(
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        Obtiene todas las notas de ingreso activas con información del proveedor.
        
        Returns:
            Lista de diccionarios con las notas de ingreso.
        """
        async with poolDB() as session:
            query = (
                select(EntryNote)
                .options(joinedload(EntryNote.supplier), joinedload(EntryNote.details))
                .where(EntryNote.is_active == True)
                .order_by(EntryNote.date.desc())
            )
            
            result = await session.execute(query)
            notes = result.unique().scalars().all()
            
            return [
                {
                    "id": note.id,
                    "user_id": note.user_id,
                    "supplier_id": note.supplier_id,
                    "supplier_name": note.supplier.name if note.supplier else None,
                    "date": note.date.isoformat() if note.date else None,
                    "reference": note.reference,
                    "items_count": len([d for d in note.details if d.is_active]),
                }
                for note in notes
            ]

    @staticmethod
    async def get_entry_note_by_id(
        entry_id: int,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> Optional[dict]:
        """
        Obtiene una nota de ingreso por su ID con todos sus detalles.
        
        Args:
            entry_id: ID de la nota de ingreso.
            
        Returns:
            Diccionario con la nota y sus detalles, o None si no existe.
        """
        async with poolDB() as session:
            query = (
                select(EntryNote)
                .options(
                    joinedload(EntryNote.supplier),
                    joinedload(EntryNote.details).joinedload(EntryNoteDetail.product),
                )
                .where(EntryNote.id == entry_id, EntryNote.is_active == True)
            )
            
            result = await session.execute(query)
            note = result.unique().scalars().first()
            
            if not note:
                return None
            
            return {
                "id": note.id,
                "user_id": note.user_id,
                "supplier_id": note.supplier_id,
                "supplier_name": note.supplier.name if note.supplier else None,
                "date": note.date.isoformat() if note.date else None,
                "reference": note.reference,
                "details": [
                    {
                        "id": detail.id,
                        "product_id": detail.product_id,
                        "product_name": detail.product.name if detail.product else None,
                        "quantity": detail.quantity,
                    }
                    for detail in note.details
                    if detail.is_active
                ],
            }

    @staticmethod
    async def add_entry_note_item(
        entry_id: int,
        data: dict,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> dict:
        """
        Agrega un producto al detalle de una nota de ingreso.
        El trigger TR_STOCK_INCREMENT se encargará de incrementar el stock.
        
        Args:
            entry_id: ID de la nota de ingreso.
            data: Diccionario con product_id y quantity.
            
        Returns:
            Diccionario con los datos del item creado.
        """
        async with poolDB() as session:
            try:
                # Verificar que la nota de ingreso exista
                entry_note = await session.get(EntryNote, entry_id)
                if not entry_note or not entry_note.is_active:
                    raise HTTPException(
                        status_code=404,
                        detail="Nota de ingreso no encontrada"
                    )
                
                # Verificar que el producto exista
                product = await session.get(Product, data.get("product_id"))
                if not product or not product.is_active:
                    raise HTTPException(
                        status_code=404,
                        detail="Producto no encontrado o inactivo"
                    )
                
                # Crear el detalle
                detail = EntryNoteDetail(
                    entry_id=entry_id,
                    product_id=data.get("product_id"),
                    quantity=data.get("quantity", 0),
                    is_active=True,
                )
                
                session.add(detail)
                
                # Incrementar stock manualmente (como alternativa al trigger)
                product.stock = product.stock + data.get("quantity", 0)
                
                await session.commit()
                await session.refresh(detail)
                
                return {
                    "id": detail.id,
                    "entry_id": detail.entry_id,
                    "product_id": detail.product_id,
                    "product_name": product.name,
                    "quantity": detail.quantity,
                    "new_stock": product.stock,
                }
                
            except HTTPException:
                raise
            except SQLAlchemyError as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

    @staticmethod
    async def update_entry_note_item(
        entry_id: int,
        item_id: int,
        data: dict,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> dict:
        """
        Actualiza un item de una nota de ingreso.
        Ajusta el stock según la diferencia de cantidad.
        
        Args:
            entry_id: ID de la nota de ingreso.
            item_id: ID del item a actualizar.
            data: Diccionario con quantity y/o product_id.
            
        Returns:
            Diccionario con los datos del item actualizado.
        """
        async with poolDB() as session:
            try:
                # Obtener el detalle
                query = select(EntryNoteDetail).where(
                    EntryNoteDetail.id == item_id,
                    EntryNoteDetail.entry_id == entry_id,
                    EntryNoteDetail.is_active == True,
                )
                result = await session.execute(query)
                detail = result.scalars().first()
                
                if not detail:
                    raise HTTPException(
                        status_code=404,
                        detail="Item de nota de ingreso no encontrado"
                    )
                
                old_quantity = detail.quantity
                old_product_id = detail.product_id
                
                # Revertir stock del producto anterior
                old_product = await session.get(Product, old_product_id)
                if old_product:
                    old_product.stock = old_product.stock - old_quantity
                
                # Actualizar campos
                if "product_id" in data:
                    detail.product_id = data["product_id"]
                if "quantity" in data:
                    detail.quantity = data["quantity"]
                
                # Aplicar stock al nuevo producto
                new_product = await session.get(Product, detail.product_id)
                if new_product:
                    new_product.stock = new_product.stock + detail.quantity
                
                await session.commit()
                await session.refresh(detail)
                
                return {
                    "id": detail.id,
                    "entry_id": detail.entry_id,
                    "product_id": detail.product_id,
                    "product_name": new_product.name if new_product else None,
                    "quantity": detail.quantity,
                    "new_stock": new_product.stock if new_product else 0,
                }
                
            except HTTPException:
                raise
            except SQLAlchemyError as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

    @staticmethod
    async def delete_entry_note_item(
        entry_id: int,
        item_id: int,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> dict:
        """
        Elimina (soft delete) un item de una nota de ingreso.
        Revierte el stock del producto.
        
        Args:
            entry_id: ID de la nota de ingreso.
            item_id: ID del item a eliminar.
            
        Returns:
            Diccionario confirmando la eliminación.
        """
        async with poolDB() as session:
            try:
                # Obtener el detalle
                query = select(EntryNoteDetail).where(
                    EntryNoteDetail.id == item_id,
                    EntryNoteDetail.entry_id == entry_id,
                    EntryNoteDetail.is_active == True,
                )
                result = await session.execute(query)
                detail = result.scalars().first()
                
                if not detail:
                    raise HTTPException(
                        status_code=404,
                        detail="Item de nota de ingreso no encontrado"
                    )
                
                # Revertir stock
                product = await session.get(Product, detail.product_id)
                if product:
                    product.stock = product.stock - detail.quantity
                
                # Soft delete
                detail.is_active = False
                detail.deleted_at = datetime.utcnow()
                
                await session.commit()
                
                return {
                    "status": "success",
                    "message": "Item eliminado correctamente",
                    "product_new_stock": product.stock if product else 0,
                }
                
            except HTTPException:
                raise
            except SQLAlchemyError as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

    # ==========================================================================
    # SECCIÓN B: NOTAS DE SALIDA (OUTBOUND / Exit Notes)
    # ==========================================================================

    @staticmethod
    async def validate_stock(
        product_id: int,
        requested_quantity: int,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> dict:
        """
        Valida si hay stock suficiente para una salida.
        Equivalente a invocar SP_VALIDATE_STOCK.
        
        Args:
            product_id: ID del producto.
            requested_quantity: Cantidad solicitada.
            
        Returns:
            Diccionario con is_valid, current_stock, y message.
        """
        async with poolDB() as session:
            product = await session.get(Product, product_id)
            
            if not product or not product.is_active:
                return {
                    "is_valid": False,
                    "current_stock": 0,
                    "requested_quantity": requested_quantity,
                    "message": "Producto no encontrado o inactivo",
                }
            
            if product.stock >= requested_quantity:
                return {
                    "is_valid": True,
                    "current_stock": product.stock,
                    "requested_quantity": requested_quantity,
                    "message": f"Stock suficiente para {product.name}",
                }
            else:
                return {
                    "is_valid": False,
                    "current_stock": product.stock,
                    "requested_quantity": requested_quantity,
                    "message": f"Stock insuficiente para {product.name}. Disponible: {product.stock}, Solicitado: {requested_quantity}",
                }

    @staticmethod
    async def create_exit_note(
        data: dict,
        user_id: int,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> dict:
        """
        Crea una nueva nota de salida (cabecera).
        
        Args:
            data: Diccionario con customer_id, total y reference (opcional).
            user_id: ID del usuario que crea la nota.
            
        Returns:
            Diccionario con los datos de la nota creada.
        """
        async with poolDB() as session:
            try:
                # Verificar que el cliente exista
                customer = await session.get(Customer, data.get("customer_id"))
                if not customer or not customer.is_active:
                    raise HTTPException(
                        status_code=404,
                        detail="Cliente no encontrado o inactivo"
                    )
                
                exit_note = ExitNote(
                    user_id=user_id,
                    customer_id=data.get("customer_id"),
                    date=datetime.utcnow(),
                    total=data.get("total", 0),
                    reference=data.get("reference"),
                    is_active=True,
                )
                
                session.add(exit_note)
                await session.commit()
                await session.refresh(exit_note)
                
                return {
                    "id": exit_note.id,
                    "user_id": exit_note.user_id,
                    "customer_id": exit_note.customer_id,
                    "customer_name": customer.name,
                    "date": exit_note.date.isoformat() if exit_note.date else None,
                    "total": float(exit_note.total),
                    "reference": exit_note.reference,
                }
                
            except HTTPException:
                raise
            except SQLAlchemyError as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

    @staticmethod
    async def get_all_exit_notes(
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> list[dict]:
        """
        Obtiene todas las notas de salida activas con información del cliente.
        
        Returns:
            Lista de diccionarios con las notas de salida.
        """
        async with poolDB() as session:
            query = (
                select(ExitNote)
                .options(joinedload(ExitNote.customer), joinedload(ExitNote.details))
                .where(ExitNote.is_active == True)
                .order_by(ExitNote.date.desc())
            )
            
            result = await session.execute(query)
            notes = result.unique().scalars().all()
            
            return [
                {
                    "id": note.id,
                    "user_id": note.user_id,
                    "customer_id": note.customer_id,
                    "customer_name": note.customer.name if note.customer else None,
                    "date": note.date.isoformat() if note.date else None,
                    "total": float(note.total),
                    "reference": note.reference,
                    "items_count": len([d for d in note.details if d.is_active]),
                }
                for note in notes
            ]

    @staticmethod
    async def get_exit_note_by_id(
        exit_id: int,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> Optional[dict]:
        """
        Obtiene una nota de salida por su ID con todos sus detalles.
        
        Args:
            exit_id: ID de la nota de salida.
            
        Returns:
            Diccionario con la nota y sus detalles, o None si no existe.
        """
        async with poolDB() as session:
            query = (
                select(ExitNote)
                .options(
                    joinedload(ExitNote.customer),
                    joinedload(ExitNote.details).joinedload(ExitNoteDetail.product),
                )
                .where(ExitNote.id == exit_id, ExitNote.is_active == True)
            )
            
            result = await session.execute(query)
            note = result.unique().scalars().first()
            
            if not note:
                return None
            
            return {
                "id": note.id,
                "user_id": note.user_id,
                "customer_id": note.customer_id,
                "customer_name": note.customer.name if note.customer else None,
                "date": note.date.isoformat() if note.date else None,
                "total": float(note.total),
                "reference": note.reference,
                "details": [
                    {
                        "id": detail.id,
                        "product_id": detail.product_id,
                        "product_name": detail.product.name if detail.product else None,
                        "quantity": detail.quantity,
                    }
                    for detail in note.details
                    if detail.is_active
                ],
            }

    @staticmethod
    async def add_exit_note_item(
        exit_id: int,
        data: dict,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> dict:
        """
        Agrega un producto al detalle de una nota de salida.
        REQUISITO CRÍTICO: Valida stock antes de insertar.
        El trigger TR_STOCK_DECREMENT se encargará de decrementar el stock.
        
        Args:
            exit_id: ID de la nota de salida.
            data: Diccionario con product_id y quantity.
            
        Returns:
            Diccionario con los datos del item creado.
            
        Raises:
            HTTPException: 400 si no hay stock suficiente.
        """
        async with poolDB() as session:
            try:
                # Verificar que la nota de salida exista
                exit_note = await session.get(ExitNote, exit_id)
                if not exit_note or not exit_note.is_active:
                    raise HTTPException(
                        status_code=404,
                        detail="Nota de salida no encontrada"
                    )
                
                # Verificar que el producto exista
                product = await session.get(Product, data.get("product_id"))
                if not product or not product.is_active:
                    raise HTTPException(
                        status_code=404,
                        detail="Producto no encontrado o inactivo"
                    )
                
                requested_quantity = data.get("quantity", 0)
                
                # VALIDACIÓN CRÍTICA DE STOCK
                if product.stock < requested_quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Stock insuficiente para {product.name}. "
                               f"Disponible: {product.stock}, Solicitado: {requested_quantity}"
                    )
                
                # Crear el detalle
                detail = ExitNoteDetail(
                    exit_id=exit_id,
                    product_id=data.get("product_id"),
                    quantity=requested_quantity,
                    is_active=True,
                )
                
                session.add(detail)
                
                # Decrementar stock manualmente (como alternativa al trigger)
                product.stock = product.stock - requested_quantity
                
                await session.commit()
                await session.refresh(detail)
                
                return {
                    "id": detail.id,
                    "exit_id": detail.exit_id,
                    "product_id": detail.product_id,
                    "product_name": product.name,
                    "quantity": detail.quantity,
                    "new_stock": product.stock,
                }
                
            except HTTPException:
                raise
            except SQLAlchemyError as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

    @staticmethod
    async def update_exit_note_item(
        exit_id: int,
        item_id: int,
        data: dict,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> dict:
        """
        Actualiza un item de una nota de salida.
        Valida stock y ajusta según la diferencia.
        
        Args:
            exit_id: ID de la nota de salida.
            item_id: ID del item a actualizar.
            data: Diccionario con quantity y/o product_id.
            
        Returns:
            Diccionario con los datos del item actualizado.
        """
        async with poolDB() as session:
            try:
                # Obtener el detalle
                query = select(ExitNoteDetail).where(
                    ExitNoteDetail.id == item_id,
                    ExitNoteDetail.exit_id == exit_id,
                    ExitNoteDetail.is_active == True,
                )
                result = await session.execute(query)
                detail = result.scalars().first()
                
                if not detail:
                    raise HTTPException(
                        status_code=404,
                        detail="Item de nota de salida no encontrado"
                    )
                
                old_quantity = detail.quantity
                old_product_id = detail.product_id
                new_product_id = data.get("product_id", old_product_id)
                new_quantity = data.get("quantity", old_quantity)
                
                # Revertir stock del producto anterior
                old_product = await session.get(Product, old_product_id)
                if old_product:
                    old_product.stock = old_product.stock + old_quantity
                
                # Verificar stock del nuevo producto
                new_product = await session.get(Product, new_product_id)
                if not new_product or not new_product.is_active:
                    raise HTTPException(
                        status_code=404,
                        detail="Producto no encontrado o inactivo"
                    )
                
                if new_product.stock < new_quantity:
                    # Revertir el cambio anterior
                    if old_product:
                        old_product.stock = old_product.stock - old_quantity
                    raise HTTPException(
                        status_code=400,
                        detail=f"Stock insuficiente para {new_product.name}. "
                               f"Disponible: {new_product.stock}, Solicitado: {new_quantity}"
                    )
                
                # Actualizar campos
                detail.product_id = new_product_id
                detail.quantity = new_quantity
                
                # Aplicar descuento al nuevo producto
                new_product.stock = new_product.stock - new_quantity
                
                await session.commit()
                await session.refresh(detail)
                
                return {
                    "id": detail.id,
                    "exit_id": detail.exit_id,
                    "product_id": detail.product_id,
                    "product_name": new_product.name,
                    "quantity": detail.quantity,
                    "new_stock": new_product.stock,
                }
                
            except HTTPException:
                raise
            except SQLAlchemyError as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

    @staticmethod
    async def delete_exit_note_item(
        exit_id: int,
        item_id: int,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> dict:
        """
        Elimina (soft delete) un item de una nota de salida.
        Revierte el stock del producto.
        
        Args:
            exit_id: ID de la nota de salida.
            item_id: ID del item a eliminar.
            
        Returns:
            Diccionario confirmando la eliminación.
        """
        async with poolDB() as session:
            try:
                # Obtener el detalle
                query = select(ExitNoteDetail).where(
                    ExitNoteDetail.id == item_id,
                    ExitNoteDetail.exit_id == exit_id,
                    ExitNoteDetail.is_active == True,
                )
                result = await session.execute(query)
                detail = result.scalars().first()
                
                if not detail:
                    raise HTTPException(
                        status_code=404,
                        detail="Item de nota de salida no encontrado"
                    )
                
                # Revertir stock
                product = await session.get(Product, detail.product_id)
                if product:
                    product.stock = product.stock + detail.quantity
                
                # Soft delete
                detail.is_active = False
                detail.deleted_at = datetime.utcnow()
                
                await session.commit()
                
                return {
                    "status": "success",
                    "message": "Item eliminado correctamente",
                    "product_new_stock": product.stock if product else 0,
                }
                
            except HTTPException:
                raise
            except SQLAlchemyError as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

    # ==========================================================================
    # SECCIÓN C: MÉTODOS AUXILIARES PARA SPs
    # ==========================================================================

    @staticmethod
    async def call_sp_validate_stock(
        product_id: int,
        requested_quantity: int,
        poolDB: async_sessionmaker[AsyncSession] = async_session_maker,
    ) -> dict:
        """
        Invoca el procedimiento almacenado SP_VALIDATE_STOCK.
        
        Args:
            product_id: ID del producto.
            requested_quantity: Cantidad solicitada.
            
        Returns:
            Resultado del SP con is_valid, current_stock, message.
        """
        async with poolDB() as session:
            sql = text("CALL SP_VALIDATE_STOCK(:product_id, :quantity)")
            result = await session.execute(
                sql, 
                {"product_id": product_id, "quantity": requested_quantity}
            )
            row = result.fetchone()
            
            if row:
                columns = result.keys()
                return dict(zip(columns, row))
            
            return {
                "is_valid": False,
                "message": "Error al ejecutar validación de stock"
            }
