from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from src.dev.controllers.users import UserController
from src.dev.middlewares.auth import only_user
from src.dev.repositories.user import UserRepository

userRouter = APIRouter(prefix="/user", tags=["User"])

# Inyección de dependencias
user_model = UserRepository()
user_controller = UserController(user_model)


# Rutas equivalentes
@userRouter.post("/signup", summary="Register an user")
async def user_signup(data: dict):
    return await user_controller.create(data)


@userRouter.post("/signin", summary="Enter to user's account")
async def user_signin(data: dict):
    return await user_controller.auth(data)


@userRouter.get(
    "/{name}/dashboard",
    summary="Show the user's dashboard",
    response_class=HTMLResponse,
)
async def access_dashboard(name: str, user=Depends(only_user)):
    return await user_controller.access(name, user)


@userRouter.get(
    "/{name}/",
    summary="Get user's token",
    response_class=HTMLResponse,
)
async def get_token(name: str, user=Depends(only_user)):
    return await user_controller.get_token(name, user)
