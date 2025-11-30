from fastapi import APIRouter, HTTPException, status, Depends

from src.dev.middlewares.auth import only_user, require_admin, require_role
from src.dev.repositories.clienterepository import ClientRepository

router = APIRouter(prefix="/clients", tags=["Clients"])
@router.get("/")
async def get_all_clients(user: dict = Depends(only_user)):

    try:
        clients = await ClientRepository.get_all()
        return {
            "status": "success",
            "data": clients,
            "user": user.get("name")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener clientes: {str(e)}"
        )
@router.get("/{client_id}")
async def get_client_by_id(
    client_id: int,
    user: dict = Depends(only_user)
):
    try:
        client = await ClientRepository.get_by_id(client_id)
        return {
            "status": "success",
            "data": client
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener cliente: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_client(
    data: dict,
    user: dict = Depends(require_role("admin", "auxiliar_almacen"))
):
    try:
        # Validar campos requeridos
        if "name" not in data or "email" not in data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los campos 'name' y 'email' son requeridos"
            )

        # Verificar si el email ya existe
        exists = await ClientRepository.check_exists(data["email"])
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        result = await ClientRepository.create(data)
        return {
            "status": "success",
            "message": "Cliente creado exitosamente",
            "data": result["client"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear cliente: {str(e)}"
        )
@router.put("/{client_id}")
async def update_client(
    client_id: int,
    data: dict,
    user: dict = Depends(require_role("admin", "auxiliar_almacen"))
):
    try:
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay datos para actualizar"
            )

        result = await ClientRepository.update(client_id, data)
        return {
            "status": "success",
            "message": "Cliente actualizado exitosamente",
            "data": result["client"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar cliente: {str(e)}"
        )
@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    user: dict = Depends(require_role("admin", "auxiliar_almacen"))
):
    try:
        await ClientRepository.delete(client_id)
        return {
            "status": "success",
            "message": "Cliente eliminado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar cliente: {str(e)}"
        )