from src.dev.models import *  # importar todos los modelos
from src.app import create_app
from src.dev.repositories.user import UserRepositorie

# Crear la app con dependencias inyectadas (como en JS)
app = create_app(user_model=UserRepositorie)

# Si se ejecuta directamente
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=4000, reload=True)
from src.dev.repositories.clienterepository import ClientRepository
from src.dev.routes.Clientes_Gestion import router as client_router
app.include_router(client_router)