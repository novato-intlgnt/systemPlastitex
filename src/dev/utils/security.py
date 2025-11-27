import json
import os

import bcrypt
import jwt
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRATION = os.getenv("JWT_EXPIRATION")  # segundos
JWT_COOKIE_EXPIRATION = os.getenv("JWT_COOKIE_EXPIRATION")  # días


def getPassHashed(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verifyPassHashed(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def sign(data: dict):
    payload = {**data}

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm="HS256",
    )
    return token


def decode(token):
    return jwt.decode(token, JWT_SECRET, algorithms="HS256")
