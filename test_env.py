# test_env.py
from dotenv import load_dotenv
import os

# Пытаемся загрузить переменные окружения
load_dotenv()

# Получаем значение BOT_TOKEN
token_value = os.getenv("BOT_TOKEN")

print(f"Путь к текущей директории: {os.getcwd()}")
print(f"Значение BOT_TOKEN: {token_value}")
print(f"Тип BOT_TOKEN: {type(token_value)}")

if token_value is None:
    print("❌ Ошибка: Переменная BOT_TOKEN не загружена. Проверьте .env!")
elif len(token_value) < 10:
    print("❌ Ошибка: Токен слишком короткий. Возможно, он неверен.")
else:
    print("✅ Успех: Токен загружен и выглядит корректно!")

# Запустите этот файл, чтобы увидеть результат.