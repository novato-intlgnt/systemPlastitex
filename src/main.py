from app import create_app
from dev.models.user import UserModel

# Crear la app con dependencias inyectadas (como en JS)
app = create_app(user_model=UserModel)

# Si se ejecuta directamente
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=4000, reload=True)
