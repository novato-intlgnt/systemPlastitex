from fastapi import APIRouter, HTTPException, status, Depends

from src.dev.middlewares.auth import only_user, require_role
from src.dev.repositories.purchase_order_repository import PurchaseOrderRepository

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])


@router.get("/")
async def get_all_purchase_orders(user: dict = Depends(only_user)):
    """Listar todas las órdenes de compra"""
    try:
        orders = await PurchaseOrderRepository.get_all()
        return {
            "status": "success",
            "data": orders,
            "user": user.get("name")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener órdenes de compra: {str(e)}"
        )


@router.get("/{order_id}")
async def get_purchase_order_by_id(
    order_id: int,
    user: dict = Depends(only_user)
):
    """Obtener una orden de compra por ID"""
    try:
        order = await PurchaseOrderRepository.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orden de compra no encontrada"
            )
        return {
            "status": "success",
            "data": order
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener orden de compra: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    data: dict,
    user: dict = Depends(require_role("admin", "aux_compra"))
):
    """Crear una nueva orden de compra"""
    try:
        # Validar campos requeridos
        required_fields = ["supplier_id", "total"]
        for field in required_fields:
            if field not in data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El campo '{field}' es requerido"
                )

        # Crear la orden de compra
        result = await PurchaseOrderRepository.create(data, user_id=user.get("id"))
        return {
            "status": "success",
            "message": "Orden de compra creada exitosamente",
            "data": result
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear orden de compra: {str(e)}"
        )


@router.put("/{order_id}")
async def update_purchase_order(
    order_id: int,
    data: dict,
    user: dict = Depends(require_role("admin", "aux_compra"))
):
    """Actualizar una orden de compra"""
    try:
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay datos para actualizar"
            )

        result = await PurchaseOrderRepository.update(order_id, data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orden de compra no encontrada"
            )

        return {
            "status": "success",
            "message": "Orden de compra actualizada exitosamente",
            "data": result
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar orden de compra: {str(e)}"
        )


@router.delete("/{order_id}")
async def delete_purchase_order(
    order_id: int,
    user: dict = Depends(require_role("admin", "aux_compra"))
):
    """Eliminar una orden de compra"""
    try:
        result = await PurchaseOrderRepository.delete(order_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orden de compra no encontrada"
            )

        return {
            "status": "success",
            "message": "Orden de compra eliminada exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar orden de compra: {str(e)}"
        )


@router.post("/{order_id}/recalculate", status_code=status.HTTP_200_OK)
async def recalculate_purchase_order_total(
    order_id: int,
    user: dict = Depends(require_role("admin", "aux_compra"))
):
    """
    Recalcular el total de una orden de compra.
    
    Recalcula el total basándose en la suma de (quantity * unit_price) 
    de todos los detalles activos de la orden.
    
    **Roles permitidos:** admin, aux_compra
    
    **Path Parameters:**
    - **order_id**: ID de la orden de compra a recalcular
    
    **Returns:**
    - **success**: true si se recalculó correctamente
    - **new_total**: Nuevo total calculado
    - **order_id**: ID de la orden
    - **details_count**: Cantidad de detalles incluidos en el cálculo
    - **message**: Mensaje descriptivo
    
    **Errores:**
    - **404**: Orden de compra no encontrada o inactiva
    """
    try:
        result = await PurchaseOrderRepository.recalculate_total(order_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("message", "Orden de compra no encontrada")
            )
        
        return {
            "status": "success",
            "message": result.get("message"),
            "data": {
                "order_id": result.get("order_id"),
                "new_total": result.get("new_total"),
                "details_count": result.get("details_count"),
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al recalcular el total: {str(e)}"
        )
