from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from src.dev.controllers.products import ProductsController
from src.dev.middlewares.auth import only_user
from src.dev.repositories.product import ProductRepositorie

productRouter = APIRouter(prefix="/product", tags=["Product"])

# Inyección de dependencias
product_model = ProductRepositorie()
products_controller = ProductsController(product_model)


# Rutas equivalentes
@productRouter.post("/signup", summary="Register an user")
async def stall_signup(data: dict):
    return await products_controller.create(data)


@productRouter.post("/signin", summary="Enter to user's account")
async def stall_signin(data: dict):
    return await products_controller.auth(data)


@productRouter.get(
    "/{name}/dashboard",
    summary="Show the user's dashboard",
    response_class=HTMLResponse,
)
async def access_dashboard(name: str, request: Request, user=Depends(only_user)):
    return await products_controller.access(name, user, request)
