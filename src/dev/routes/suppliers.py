from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from src.dev.controllers.users import UserController
from src.dev.middlewares.auth import only_user
from src.dev.repositories.user import UserRepositorie

supplierRouter = APIRouter(prefix="/supplier", tags=["Supplier"])

# Inyección de dependencias
supplier_model = UserRepositorie()
supplier_controller = UserController(supplier_model)


# Rutas equivalentes
@supplierRouter.post("/signup", summary="Register an user")
async def stall_signup(data: dict):
    return await supplier_controller.create(data)


@supplierRouter.post("/signin", summary="Enter to user's account")
async def stall_signin(data: dict):
    return await supplier_controller.auth(data)


@supplierRouter.get(
    "/{name}/dashboard",
    summary="Show the user's dashboard",
    response_class=HTMLResponse,
)
async def access_dashboard(name: str, request: Request, user=Depends(only_user)):
    return await supplier_controller.access(name, user, request)
