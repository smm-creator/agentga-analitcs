#!/bin/bash

# Pyrogram User Client - Запусковий скрипт

echo ""
echo "🚀 Pyrogram Post Formatter (User Client)"
echo "========================================="
echo ""

# Перевіряємо наявність Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не встановлено. Встановіть Python 3.8+"
    exit 1
fi

echo "✓ Python 3 знайдено"

# Перевіряємо наявність .env
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не знайдено"
    echo "📋 Копіюю .env.example в .env..."
    cp .env.example .env
    echo "✓ Файл .env створено. Будь ласка, редагуйте його з вашими значеннями!"
    echo ""
    echo "📝 Необхідно встановити такі значення у .env:"
    echo "   - API_ID: отримайте на https://my.telegram.org/apps"
    echo "   - API_HASH: отримайте на https://my.telegram.org/apps"
    echo "   - CHANNEL_ID: ID вашого каналу (-100123456789 або @channel_username)"
    echo ""
    exit 1
fi

echo "✓ Файл .env знайдено"

# Перевіряємо віртуальне середовище
if [ ! -d "venv" ]; then
    echo "📦 Створюю віртуальне середовище..."
    python3 -m venv venv
    echo "✓ Віртуальне середовище створено"
fi

# Активуємо віртуальне середовище
source venv/bin/activate

echo "✓ Віртуальне середовище активовано"

# Встановлюємо залежності
echo "📥 Встановлюю залежності..."
pip install -q -r requirements.txt
echo "✓ Залежності встановлено"

echo ""
echo "🔐 <b>Перша авторизація:</b>"
echo "Вам буде запропоновано ввести номер телефону та код підтвердження."
echo "Після цього сесія буде збережена в папці 'sessions'."
echo ""
echo "🚀 Запускаю клієнту..."
echo ""

# Запускаємо клієнту
python3 user_client.py
