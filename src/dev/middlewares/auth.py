import jwt
from fastapi import HTTPException, Request
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
