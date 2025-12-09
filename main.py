from src.app import create_app
from src.dev.models import *  # importar todos los modelos

# Crear la app con dependencias inyectadas (como en JS)
app = create_app()

# Si se ejecuta directamente
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run("main:app", host="0.0.0.0", port=4000, reload=True)

if __name__ == "__main__":
    import os

    import uvicorn

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    print(BASE_DIR)
    # Dev environment: use HTTP by default
    # To enable HTTPS, set USE_SSL=1 before running
    use_ssl = os.getenv("USE_SSL", "0") == "1"
    
    uvicorn_kwargs = {
        "app": "main:app",
        "host": "0.0.0.0",
        "port": 4000,
        "reload": True,
    }
    
    if use_ssl:
        CERT_DIR = os.path.join(BASE_DIR, "certs")
        SSL_CERT = os.path.join(CERT_DIR, "localhost+2.pem")
        SSL_KEY = os.path.join(CERT_DIR, "localhost+2-key.pem")
        if os.path.exists(SSL_CERT) and os.path.exists(SSL_KEY):
            uvicorn_kwargs["ssl_certfile"] = SSL_CERT
            uvicorn_kwargs["ssl_keyfile"] = SSL_KEY
    
    uvicorn.run(**uvicorn_kwargs)
