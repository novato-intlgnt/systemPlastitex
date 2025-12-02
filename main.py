from src.app import create_app

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
    CERT_DIR = os.path.join(BASE_DIR, "certs")

    SSL_CERT = os.path.join(CERT_DIR, "localhost+2.pem")
    SSL_KEY = os.path.join(CERT_DIR, "localhost+2-key.pem")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=4000,
        reload=True,
        ssl_certfile=SSL_CERT,
        ssl_keyfile=SSL_KEY,
    )
