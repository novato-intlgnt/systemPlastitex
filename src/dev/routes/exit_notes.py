from fastapi import APIRouter, Depends, HTTPException, status
from src.dev.middlewares.auth import only_user, require_role
from src.dev.controllers.warehouse import WarehouseController
from src.dev.repositories.warehouse import WarehouseRepository

router = APIRouter(prefix="/warehouse/outbound", tags=["Exit Notes"])

# Inyección de dependencias
warehouse_repository = WarehouseRepository()
warehouse_controller = WarehouseController(warehouse_repository)


async def get_current_role(user: dict = Depends(only_user)) -> tuple[str, int]:
    """Obtener rol e ID del usuario autenticado"""
    return user.get("role", ""), user.get("id", 0)


@router.get("/")
async def get_all_exit_notes(role_and_id: tuple[str, int] = Depends(get_current_role)):
    """Listar todas las notas de salida"""
    role, user_id = role_and_id
    return await warehouse_controller.get_all_exit_notes(role)


@router.get("/{note_id}")
async def get_exit_note_by_id(note_id: int, role_and_id: tuple[str, int] = Depends(get_current_role)):
    """Obtener una nota de salida por ID"""
    role, user_id = role_and_id
    return await warehouse_controller.get_exit_note_by_id(role, note_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_exit_note(
    data: dict, role_and_id: tuple[str, int] = Depends(get_current_role)
):
    """Crear una nueva nota de salida"""
    role, user_id = role_and_id
    return await warehouse_controller.create_exit_note(role, user_id, data)


@router.post("/{note_id}/items", status_code=status.HTTP_201_CREATED)
async def add_exit_note_item(
    note_id: int, data: dict, role_and_id: tuple[str, int] = Depends(get_current_role)
):
    """Agregar un producto a una nota de salida"""
    role, user_id = role_and_id
    return await warehouse_controller.add_exit_note_item(role, note_id, data)


@router.put("/{note_id}/items/{item_id}")
async def update_exit_note_item(
    note_id: int, item_id: int, data: dict, role_and_id: tuple[str, int] = Depends(get_current_role)
):
    """Actualizar un producto en una nota de salida"""
    role, user_id = role_and_id
    return await warehouse_controller.update_exit_note_item(role, note_id, item_id, data)


@router.delete("/{note_id}/items/{item_id}")
async def delete_exit_note_item(
    note_id: int, item_id: int, role_and_id: tuple[str, int] = Depends(get_current_role)
):
    """Eliminar un producto de una nota de salida"""
    role, user_id = role_and_id
    return await warehouse_controller.delete_exit_note_item(role, note_id, item_id)


@router.get("/validate-stock")
async def validate_stock(
    product_id: int, quantity: int, role_and_id: tuple[str, int] = Depends(get_current_role)
):
    """Validar si hay stock disponible"""
    role, user_id = role_and_id
    return await warehouse_controller.validate_stock(role, product_id, quantity)