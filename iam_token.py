import os
import time
import jwt
import httpx

# переменные окружения
SERVICE_ACCOUNT_ID = os.getenv("YANDEX_SERVICE_ACCOUNT_ID")
KEY_ID = os.getenv("YANDEX_KEY_ID")
PRIVATE_KEY = os.getenv("YANDEX_PRIVATE_KEY")

IAM_URL = "https://iam.api.cloud.yandex.net/iam/v1/tokens"

_cached_token = None
_cached_expire = 0


def _create_jwt():
    now = int(time.time())
    payload = {
        "aud": IAM_URL,
        "iss": SERVICE_ACCOUNT_ID,
        "iat": now,
        "exp": now + 3600
    }

    token = jwt.encode(
        payload,
        PRIVATE_KEY,
        algorithm="PS256",
        headers={"kid": KEY_ID}
    )
    return token


async def get_iam_token():
    global _cached_token, _cached_expire

    now = time.time()
    if _cached_token and now < _cached_expire - 60:
        return _cached_token

    jwt_token = _create_jwt()

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(IAM_URL, json={"jwt": jwt_token})
        resp.raise_for_status()
        data = resp.json()

    _cached_token = data["iamToken"]
    _cached_expire = data["expiresAt"]  # строка, но сравнивать не нужно

    return _cached_token
