import os
from datetime import datetime, timedelta

# import bcrypt
# import jwt
# from db import get_pool
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", 3600))  # segundos
JWT_COOKIE_EXPIRATION = int(os.getenv("JWT_COOKIE_EXPIRATION", 7))  # días


class UserModel:

    @staticmethod
    async def check(input_data: dict):
        print("check")
        # urlhost = input_data["urlhost"]
        # user = input_data["user"]
        # email = input_data["email"]
        #
        # pool = await get_pool()
        # async with pool.acquire() as conn:
        #     rows = await conn.fetch(
        #         "SELECT user_id FROM users WHERE name = $1 OR email = $2", user, email
        #     )
        #
        #     if not rows:
        #         payload = {
        #             "name": user,
        #             "mail": email,
        #             "exp": datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION),
        #         }
        #         token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        #
        #         return {"url": urlhost, "name": user, "mail": email, "token": token}
        #
        #     return True

    @staticmethod
    async def create_worker(input_data: dict):
        print("create_worker")
        # user = input_data["user"]
        # email = input_data["email"]
        # role = input_data["role"]
        # password = input_data["pass"]
        #
        # pool = await get_pool()
        # hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(7))
        #
        # async with pool.acquire() as conn:
        #     async with conn.transaction():
        #         await conn.execute(
        #             """
        #             WITH new_user AS (
        #                 INSERT INTO users (email, name, password, created_at, is_verified, status)
        #                 VALUES ($1, $2, $3, NOW(), $4, $5)
        #                 RETURNING user_id
        #             )
        #             INSERT INTO workers (worker_id, role, hire_date, is_active)
        #             SELECT user_id, $6, NOW(), $7 FROM new_user;
        #         """,
        #             email,
        #             user,
        #             hashed.decode(),
        #             False,
        #             "inActive",
        #             role,
        #             False,
        #         )
        #
        # return {"success": True, "message": "Worker created successfully"}

    @staticmethod
    async def verify(input_token: str):
        print("verify")
        # try:
        #     decoder = jwt.decode(input_token, JWT_SECRET, algorithms=["HS256"])
        #     name = decoder.get("name")
        #     mail = decoder.get("mail")
        #
        #     if not name or not mail:
        #         return True
        #
        #     pool = await get_pool()
        #     async with pool.acquire() as conn:
        #         result = await conn.fetch(
        #             "SELECT is_verified FROM users WHERE name = $1 AND email = $2 AND is_verified = true",
        #             name,
        #             mail,
        #         )
        #
        #         if len(result) == 1:
        #             return 1
        #
        #         update = await conn.execute(
        #             """
        #             WITH updated_user AS (
        #                 UPDATE users
        #                 SET is_verified = true
        #                 WHERE name = $1 AND email = $2
        #                 RETURNING user_id
        #             )
        #             UPDATE workers
        #             SET is_active = true
        #             WHERE worker_id IN (SELECT user_id FROM updated_user);
        #         """,
        #             name,
        #             mail,
        #         )
        #
        #         if "UPDATE 1" in update:
        #             token = jwt.encode(
        #                 {
        #                     "user": name,
        #                     "exp": datetime.utcnow()
        #                     + timedelta(seconds=JWT_EXPIRATION),
        #                 },
        #                 JWT_SECRET,
        #                 algorithm="HS256",
        #             )
        #             cookie = {"expiresIn": JWT_COOKIE_EXPIRATION, "path": "/"}
        #             return {"auth": token, "cookie": cookie, "user": name}
        #
        #         return False
        # except Exception as e:
        #     print("Error verifying user:", e)
        #     raise e

    @staticmethod
    async def auth(input_data: dict):
        print("auth")
        # email = input_data["email"]
        # password = input_data["pass"]
        #
        # pool = await get_pool()
        # async with pool.acquire() as conn:
        #     rows = await conn.fetch(
        #         "SELECT password, name FROM users WHERE email = $1 AND is_verified = true",
        #         email,
        #     )
        #
        #     if not rows:
        #         return False
        #
        #     user_row = rows[0]
        #     stored_pass = user_row["password"].encode("utf-8")
        #
        #     if not bcrypt.checkpw(password.encode("utf-8"), stored_pass):
        #         return False
        #
        #     await conn.execute(
        #         "UPDATE users SET status = $1 WHERE email = $2", "Active", email
        #     )
        #
        #     token = jwt.encode(
        #         {
        #             "name": user_row["name"],
        #             "exp": datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION),
        #         },
        #         JWT_SECRET,
        #         algorithm="HS256",
        #     )
        #
        #     cookie = {
        #         "expiresIn": JWT_COOKIE_EXPIRATION * 24 * 60 * 60 * 1000,
        #         "path": "/",
        #     }
        #
        #     return {"auth": token, "cookie": cookie, "name": user_row["name"]}
