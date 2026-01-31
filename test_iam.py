import asyncio
from iam_token import get_iam_token

async def main():
    print("Пробую получить IAM‑токен...")

    try:
        token = await get_iam_token()
        print("\n=== УСПЕХ! IAM‑токен получен ===")
        print(token[:80] + "...")
        print("\nТеперь можно запускать поиск через Yandex Search API.")
    except Exception as e:
        print("\n=== ОШИБКА ПРИ ПОЛУЧЕНИИ IAM‑ТОКЕНА ===")
        print(str(e))
        print("\nПроверь:")
        print("1) SERVICE_ACCOUNT_ID — должен быть ID сервисного аккаунта")
        print("2) KEY_ID — должен быть ID ключа, НЕ ID аккаунта")
        print("3) PRIVATE KEY — должен соответствовать KEY_ID")
        print("4) Формат ключа — BEGIN/END строки, переносы")
        print("5) Установлены PyJWT и cryptography")

asyncio.run(main())
