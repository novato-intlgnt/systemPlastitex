"""
Controlador para el módulo de Almacén (Warehouse).
Implementa la lógica de negocio y Control de Acceso Basado en Roles (RBAC).
"""

from fastapi import HTTPException
from fastapi.responses import JSONResponse


class WarehouseController:
    """
    Controlador de operaciones de almacén con Control de Acceso Basado en Roles (RBAC).
    
    Roles permitidos:
    - aux_almacen: Auxiliar de almacén
    - admin: Administrador
    
    Valida el rol del usuario antes de invocar la lógica del repositorio.
    """

    # Roles permitidos para operaciones de almacén
    ALLOWED_ROLES = ["aux_almacen", "admin"]

    def __init__(self, warehouse_repository):
        """
        Inicializa el controlador con el repositorio inyectado.
        
        Args:
            warehouse_repository: Instancia del WarehouseRepository.
        """
        self.warehouse_repository = warehouse_repository

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
            raise HTTPException(
                status_code=403,
                detail="Acceso no autorizado. Solo auxiliares de almacén y administradores."
            )

    # ==========================================================================
    # SECCIÓN A: NOTAS DE INGRESO (INBOUND)
    # ==========================================================================

    async def create_entry_note(
        self,
        current_role: str,
        user_id: int,
        data: dict,
    ):
        """
        Crea una nueva nota de ingreso.
        
        Roles permitidos: aux_almacen, admin
        
        Args:
            current_role: Rol del usuario autenticado.
            user_id: ID del usuario que crea la nota.
            data: Datos de la nota (supplier_id, reference).
            
        Returns:
            JSONResponse con los datos de la nota creada.
        """
        self._check_role(current_role, self.ALLOWED_ROLES)
        
        # Validar campos requeridos
        if not data.get("supplier_id"):
            raise HTTPException(
                status_code=400,
                detail="El campo 'supplier_id' es requerido"
            )
        
        try:
            result = await self.warehouse_repository.create_entry_note(data, user_id)
            return JSONResponse(
                status_code=201,
                content={
                    "status": "success",
                    "message": "Nota de ingreso creada correctamente",
                    "data": result,
                },
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in create_entry_note: {e}")
            raise HTTPException(status_code=500, detail="Error al crear la nota de ingreso")

    async def get_all_entry_notes(self, current_role: str):
        """
        Lista todas las notas de ingreso.
        
        Roles permitidos: aux_almacen, admin
        
        Args:
            current_role: Rol del usuario autenticado.
            
        Returns:
            JSONResponse con la lista de notas de ingreso.
        """
        self._check_role(current_role, self.ALLOWED_ROLES)
        
        try:
            data = await self.warehouse_repository.get_all_entry_notes()
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "data": data,
                    "count": len(data),
                },
            )
        except Exception as e:
            print(f"Error in get_all_entry_notes: {e}")
            raise HTTPException(status_code=500, detail="Error al obtener las notas de ingreso")

    async def get_entry_note_by_id(self, current_role: str, entry_id: int):
        """
        Obtiene una nota de ingreso con sus detalles.
        
        Roles permitidos: aux_almacen, admin
        
        Args:
            current_role: Rol del usuario autenticado.
            entry_id: ID de la nota de ingreso.
            
        Returns:
            JSONResponse con los datos de la nota y sus detalles.
        """
        self._check_role(current_role, self.ALLOWED_ROLES)
        
        try:
            data = await self.warehouse_repository.get_entry_note_by_id(entry_id)
            
            if not data:
                raise HTTPException(
                    status_code=404,
                    detail="Nota de ingreso no encontrada"
                )
            
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "data": data,
                },
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in get_entry_note_by_id: {e}")
            raise HTTPException(status_code=500, detail="Error al obtener la nota de ingreso")

    async def add_entry_note_item(
        self,
        current_role: str,
        entry_id: int,
        data: dict,
    ):
        """
        Agrega un producto a una nota de ingreso.
        El stock se incrementará automáticamente.
        
        Roles permitidos: aux_almacen, admin
        
        Args:
            current_role: Rol del usuario autenticado.
            entry_id: ID de la nota de ingreso.
            data: Datos del item (product_id, quantity).
            
        Returns:
            JSONResponse con los datos del item creado.
        """
        self._check_role(current_role, self.ALLOWED_ROLES)
        
        # Validar campos requeridos
        if not data.get("product_id"):
            raise HTTPException(status_code=400, detail="El campo 'product_id' es requerido")
        if not data.get("quantity") or data.get("quantity", 0) <= 0:
            raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")
        
        try:
            result = await self.warehouse_repository.add_entry_note_item(entry_id, data)
            return JSONResponse(
                status_code=201,
                content={
                    "status": "success",
                    "message": "Producto agregado a la nota de ingreso",
                    "data": result,
                },
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in add_entry_note_item: {e}")
            raise HTTPException(status_code=500, detail="Error al agregar el producto")

    async def update_entry_note_item(
        self,
        current_role: str,
        entry_id: int,
        item_id: int,
        data: dict,
    ):
        """
        Actualiza un item de una nota de ingreso.
        
        Roles permitidos: aux_almacen, admin
        
        Args:
            current_role: Rol del usuario autenticado.
            entry_id: ID de la nota de ingreso.
            item_id: ID del item a actualizar.
            data: Datos a actualizar (product_id, quantity).
            
        Returns:
            JSONResponse con los datos del item actualizado.
        """
        self._check_role(current_role, self.ALLOWED_ROLES)
        
        if not data:
            raise HTTPException(status_code=400, detail="No hay datos para actualizar")
        
        if "quantity" in data and data.get("quantity", 0) <= 0:
            raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")
        
        try:
            result = await self.warehouse_repository.update_entry_note_item(
                entry_id, item_id, data
            )
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "Item actualizado correctamente",
                    "data": result,
                },
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in update_entry_note_item: {e}")
            raise HTTPException(status_code=500, detail="Error al actualizar el item")

    async def delete_entry_note_item(
        self,
        current_role: str,
        entry_id: int,
        item_id: int,
    ):
        """
        Elimina un item de una nota de ingreso.
        El stock se revertirá automáticamente.
        
        Roles permitidos: aux_almacen, admin
        
        Args:
            current_role: Rol del usuario autenticado.
            entry_id: ID de la nota de ingreso.
            item_id: ID del item a eliminar.
            
        Returns:
            JSONResponse confirmando la eliminación.
        """
        self._check_role(current_role, self.ALLOWED_ROLES)
        
        try:
            result = await self.warehouse_repository.delete_entry_note_item(entry_id, item_id)
            return JSONResponse(
                status_code=200,
                content=result,
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in delete_entry_note_item: {e}")
            raise HTTPException(status_code=500, detail="Error al eliminar el item")

    # ==========================================================================
    # SECCIÓN B: NOTAS DE SALIDA (OUTBOUND)
    # ==========================================================================

    async def create_exit_note(
        self,
        current_role: str,
        user_id: int,
        data: dict,
    ):
        """
        Crea una nueva nota de salida.
        
        Roles permitidos: aux_almacen, admin
        
        Args:
            current_role: Rol del usuario autenticado.
            user_id: ID del usuario que crea la nota.
            data: Datos de la nota (customer_id, total, reference).
            
        Returns:
            JSONResponse con los datos de la nota creada.
        """
        self._check_role(current_role, self.ALLOWED_ROLES)
        
        # Validar campos requeridos
        if not data.get("customer_id"):
            raise HTTPException(
                status_code=400,
                detail="El campo 'customer_id' es requerido"
            )
        
        try:
            result = await self.warehouse_repository.create_exit_note(data, user_id)
            return JSONResponse(
                status_code=201,
                content={
                    "status": "success",
                    "message": "Nota de salida creada correctamente",
                    "data": result,
                },
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in create_exit_note: {e}")
            raise HTTPException(status_code=500, detail="Error al crear la nota de salida")

    async def get_all_exit_notes(self, current_role: str):
        """
        Lista todas las notas de salida.
        
        Roles permitidos: aux_almacen, admin
        
        Args:
            current_role: Rol del usuario autenticado.
            
        Returns:
            JSONResponse con la lista de notas de salida.
        """
        self._check_role(current_role, self.ALLOWED_ROLES)
        
        try:
            data = await self.warehouse_repository.get_all_exit_notes()
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "data": data,
                    "count": len(data),
                },
            )
        except Exception as e:
            print(f"Error in get_all_exit_notes: {e}")
            raise HTTPException(status_code=500, detail="Error al obtener las notas de salida")

    async def get_exit_note_by_id(self, current_role: str, exit_id: int):
        """
        Obtiene una nota de salida con sus detalles.
        
        Roles permitidos: aux_almacen, admin
        
        Args:
            current_role: Rol del usuario autenticado.
            exit_id: ID de la nota de salida.
            
        Returns:
            JSONResponse con los datos de la nota y sus detalles.
        """
        self._check_role(current_role, self.ALLOWED_ROLES)
        
        try:
            data = await self.warehouse_repository.get_exit_note_by_id(exit_id)
            
            if not data:
                raise HTTPException(
                    status_code=404,
                    detail="Nota de salida no encontrada"
                )
            
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "data": data,
                },
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in get_exit_note_by_id: {e}")
            raise HTTPException(status_code=500, detail="Error al obtener la nota de salida")

    async def validate_stock(
        self,
        current_role: str,
        product_id: int,
        quantity: int,
    ):
        """
        Valida si hay stock suficiente para una salida.
        
        Roles permitidos: aux_almacen, admin
        
        Args:
            current_role: Rol del usuario autenticado.
            product_id: ID del producto.
            quantity: Cantidad solicitada.
            
        Returns:
            JSONResponse con el resultado de la validación.
        """
        self._check_role(current_role, self.ALLOWED_ROLES)
        
        try:
            result = await self.warehouse_repository.validate_stock(product_id, quantity)
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "data": result,
                },
            )
        except Exception as e:
            print(f"Error in validate_stock: {e}")
            raise HTTPException(status_code=500, detail="Error al validar stock")

    async def add_exit_note_item(
        self,
        current_role: str,
        exit_id: int,
        data: dict,
    ):
        """
        Agrega un producto a una nota de salida.
        REQUISITO CRÍTICO: Valida stock antes de insertar.
        El stock se decrementará automáticamente si la validación pasa.
        
        Roles permitidos: aux_almacen, admin
        
        Args:
            current_role: Rol del usuario autenticado.
            exit_id: ID de la nota de salida.
            data: Datos del item (product_id, quantity).
            
        Returns:
            JSONResponse con los datos del item creado.
            
        Raises:
            HTTPException: 400 si no hay stock suficiente.
        """
        self._check_role(current_role, self.ALLOWED_ROLES)
        
        # Validar campos requeridos
        if not data.get("product_id"):
            raise HTTPException(status_code=400, detail="El campo 'product_id' es requerido")
        if not data.get("quantity") or data.get("quantity", 0) <= 0:
            raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")
        
        try:
            # La validación de stock se hace dentro del repositorio
            result = await self.warehouse_repository.add_exit_note_item(exit_id, data)
            return JSONResponse(
                status_code=201,
                content={
                    "status": "success",
                    "message": "Producto agregado a la nota de salida",
                    "data": result,
                },
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in add_exit_note_item: {e}")
            raise HTTPException(status_code=500, detail="Error al agregar el producto")

    async def update_exit_note_item(
        self,
        current_role: str,
        exit_id: int,
        item_id: int,
        data: dict,
    ):
        """
        Actualiza un item de una nota de salida.
        Valida stock antes de actualizar.
        
        Roles permitidos: aux_almacen, admin
        
        Args:
            current_role: Rol del usuario autenticado.
            exit_id: ID de la nota de salida.
            item_id: ID del item a actualizar.
            data: Datos a actualizar (product_id, quantity).
            
        Returns:
            JSONResponse con los datos del item actualizado.
        """
        self._check_role(current_role, self.ALLOWED_ROLES)
        
        if not data:
            raise HTTPException(status_code=400, detail="No hay datos para actualizar")
        
        if "quantity" in data and data.get("quantity", 0) <= 0:
            raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")
        
        try:
            result = await self.warehouse_repository.update_exit_note_item(
                exit_id, item_id, data
            )
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "Item actualizado correctamente",
                    "data": result,
                },
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in update_exit_note_item: {e}")
            raise HTTPException(status_code=500, detail="Error al actualizar el item")

    async def delete_exit_note_item(
        self,
        current_role: str,
        exit_id: int,
        item_id: int,
    ):
        """
        Elimina un item de una nota de salida.
        El stock se revertirá automáticamente.
        
        Roles permitidos: aux_almacen, admin
        
        Args:
            current_role: Rol del usuario autenticado.
            exit_id: ID de la nota de salida.
            item_id: ID del item a eliminar.
            
        Returns:
            JSONResponse confirmando la eliminación.
        """
        self._check_role(current_role, self.ALLOWED_ROLES)
        
        try:
            result = await self.warehouse_repository.delete_exit_note_item(exit_id, item_id)
            return JSONResponse(
                status_code=200,
                content=result,
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in delete_exit_note_item: {e}")
            raise HTTPException(status_code=500, detail="Error al eliminar el item")
