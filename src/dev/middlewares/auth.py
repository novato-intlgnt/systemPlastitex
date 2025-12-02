import jwt
from fastapi import HTTPException, Request, Depends
from fastapi.responses import RedirectResponse

from src.dev.utils.security import decode


async def only_user(request: Request):
    token = request.cookies.get("user")
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        decoded = decode(token)
        return decoded
    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/index.html", status_code=302)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def require_admin(request: Request):
    """
    Middleware que requiere rol admin
    """
    user = await only_user(request)
    
    if isinstance(user, RedirectResponse):
        return user
    
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