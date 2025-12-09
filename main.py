from src.app import create_app
from src.dev.models import *  # importar todos los modelos

# Crear la app con dependencias inyectadas (como en JS)
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=4000, reload=True)
