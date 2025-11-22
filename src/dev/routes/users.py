from fastapi import APIRouter, Depends

from src.dev.controllers.users import UserController

# from dev.middlewares.auth import only_user
# from dev.middlewares.user_handler import assign_role
from src.dev.models.user import UserModel

router = APIRouter(prefix="/user", tags=["User"])

# Inyección de dependencias
user_model = UserModel()
user_controller = UserController(user_model)


# Rutas equivalentes
@router.post("/signup/")
async def stall_signup(data: dict):
    print("helo")
    return await user_controller.create(data)


@router.post("/signin/")
async def stall_signin(data: dict):
    return await user_controller.auth(data)


# @router.get("/{name}/dashboard")
# async def access_dashboard(name: str, user=Depends(only_user)):
#     return await user_controller.access(name, user)
