@echo off
REM Pyrogram User Client - Запусковий скрипт для Windows

echo.
echo 🚀 Pyrogram Post Formatter (User Client)
echo =========================================
echo.

REM Перевіряємо наявність Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не встановлено. Встановіть Python 3.8+
    pause
    exit /b 1
)

echo ✓ Python знайдено

REM Перевіряємо наявність .env
if not exist ".env" (
    echo ⚠️  Файл .env не знайдено
    echo 📋 Копіюю .env.example в .env...
    copy .env.example .env
    echo ✓ Файл .env створено. Будь ласка, редагуйте його з вашими значеннями!
    echo.
    echo 📝 Необхідно встановити такі значення у .env:
    echo    - API_ID: отримайте на https://my.telegram.org/apps
    echo    - API_HASH: отримайте на https://my.telegram.org/apps
    echo    - CHANNEL_ID: ID вашого каналу (-100123456789 або @channel_username)
    echo.
    pause
    exit /b 1
)

echo ✓ Файл .env знайдено

REM Перевіряємо віртуальне середовище
if not exist "venv" (
    echo 📦 Створюю віртуальне середовище...
    python -m venv venv
    echo ✓ Віртуальне середовище створено
)

echo ✓ Віртуальне середовище готово

REM Активуємо віртуальне середовище
call venv\Scripts\activate.bat

REM Встановлюємо залежності
echo 📥 Встановлюю залежності...
pip install -q -r requirements.txt
echo ✓ Залежності встановлено

echo.
echo 🔐 Перша авторизація:
echo Вам буде запропоновано ввести номер телефону та код підтвердження.
echo Після цього сесія буде збережена в папці 'sessions'.
echo.
echo 🚀 Запускаю клієнту...
echo.

REM Запускаємо клієнту
python user_client.py

pause
