import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.user_service import user_service


async def test_registration():
    """Тестируем регистрацию пользователя"""
    test_user_id = 123456789
    test_username = "test_user"
    test_first_name = "Test"

    print("🔄 Регистрируем тестового пользователя...")
    await user_service.register_user(test_user_id, test_username, test_first_name)
    print("✅ Регистрация завершена")

    # Проверим что пользователь в базе
    profile = await user_service.get_user_profile(test_user_id)
    if profile:
        print(f"✅ Пользователь найден в базе: {profile['first_name']} (@{profile['username']})")
    else:
        print("❌ Пользователь не найден в базе")


asyncio.run(test_registration())