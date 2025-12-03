import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.dev.utils.security import decode

# Esquema de seguridad Bearer
security = HTTPBearer()


async def only_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Obtiene y valida el token JWT del header Authorization Bearer.
    
    Args:
        credentials: Credenciales extraídas del header Authorization.
        
    Returns:
        dict: Datos decodificados del usuario (id, role, user, etc.)
        
    Raises:
        HTTPException: 401 si el token es inválido o ha expirado.
    """
    token = credentials.credentials
    
    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionado")

    try:
        decoded = decode(token)
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Middleware que requiere rol admin.
    Valida el token Bearer y verifica que el usuario sea admin.
    """
    user = await only_user(credentials)
    
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Se requiere rol de administrador"
        )
    return user


def require_role(*allowed_roles):
    """
    Middleware que requiere uno de los roles especificados
    Uso: Depends(require_role("admin", "auxiliar_compra"))
    """
    async def check_role(user: dict = Depends(only_user)):
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Acceso denegado"
            )
        return user
    return check_role