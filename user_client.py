import os
import re
from typing import Optional
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import logging

# Завантажуємо змінні з .env
load_dotenv()

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Константи
SESSION_NAME = os.getenv('SESSION_NAME', 'my_session')
CHANNEL_ID = os.getenv('CHANNEL_ID')
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH')

if not API_ID or not API_HASH or not CHANNEL_ID:
    raise ValueError("❌ Необхідно встановити API_ID, API_HASH та CHANNEL_ID у файлі .env")

# Словник для автозаміни ключових слів на посилання
KEYWORD_LINKS = {
    "штани": "https://prof1group.ua/pants",
    "взуття": "https://prof1group.ua/shoes",
    "рубашка": "https://prof1group.ua/shirts",
    "шапка": "https://prof1group.ua/hats",
    "жакет": "https://prof1group.ua/jackets",
    # Додавайте свої ключові слова тут
}

# Ініціалізація Pyrogram клієнту
app = Client(
    session_name=SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    workdir="sessions"
)


def format_text_with_links(text: str) -> str:
    """
    Форматує текст, замінюючи ключові слова на HTML-посилання.
    Зберігає оригінальний регістр слова.
    
    Args:
        text: Вихідний текст
        
    Returns:
        Форматований текст з HTML-посиланнями
    """
    result = text
    
    for keyword, url in KEYWORD_LINKS.items():
        # Регулярний вираз для пошуку слова без урахування регістру
        # \b - границя слова, (?i) - без урахування регістру
        pattern = rf'\b({re.escape(keyword)})\b'
        
        def replace_func(match):
            original_word = match.group(1)
            # Екранування HTML-спеціальних символів
            escaped_word = original_word.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            return f'<a href="{url}">{escaped_word}</a>'
        
        result = re.sub(pattern, replace_func, result, flags=re.IGNORECASE)
    
    return result


@app.on_message(filters.text & filters.private)
async def handle_text_message(client: Client, message: Message):
    """
    Обробник текстових повідомлень з приватного чату
    """
    try:
        original_text = message.text
        formatted_text = format_text_with_links(original_text)
        
        # Надсилаємо повідомлення у канал
        await client.send_message(
            chat_id=CHANNEL_ID,
            text=formatted_text,
            parse_mode="html"
        )
        
        # Підтвердження користувачу
        await client.send_message(
            chat_id=message.chat.id,
            text=f"✅ Пост опублікований у канал!\n\n"
                 f"<b>Текст, що був надіслан:</b>\n{formatted_text}",
            parse_mode="html"
        )
        
        logger.info(f"[TEXT] Published: {original_text[:50]}...")
        
    except Exception as e:
        logger.error(f"Error processing text message: {str(e)}")
        await client.send_message(
            chat_id=message.chat.id,
            text=f"❌ Помилка при публікації: {str(e)}"
        )


@app.on_message(filters.photo & filters.private)
async def handle_photo_message(client: Client, message: Message):
    """
    Обробник повідомлень з фото з приватного чату
    """
    try:
        # Отримуємо опис фото (якщо є)
        caption = message.caption or "(без опису)"
        formatted_caption = format_text_with_links(caption)
        
        # Надсилаємо фото у канал
        await client.send_photo(
            chat_id=CHANNEL_ID,
            photo=message.photo.file_id,
            caption=formatted_caption if caption != "(без опису)" else None,
            parse_mode="html"
        )
        
        # Підтвердження користувачу
        confirm_text = f"✅ Фото опублікована у канал!\n\n"
        if caption != "(без опису)":
            confirm_text += f"<b>Опис, що був надіслано:</b>\n{formatted_caption}"
        else:
            confirm_text += "📸 Фото без опису"
        
        await client.send_message(
            chat_id=message.chat.id,
            text=confirm_text,
            parse_mode="html"
        )
        
        logger.info(f"[PHOTO] Published photo with caption: {caption[:50]}...")
        
    except Exception as e:
        logger.error(f"Error processing photo message: {str(e)}")
        await client.send_message(
            chat_id=message.chat.id,
            text=f"❌ Помилка при публікації фото: {str(e)}"
        )


@app.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    """
    Команда /help - показує інструкцію
    """
    help_text = """📖 <b>Інструкція користування:</b>

1️⃣ <b>Текстові повідомлення:</b>
   Просто напишіть текст - я замініню ключові слова на посилання та опублікую у канал
   
   Приклад: "Купіть якісні штани та взуття в нас!"
   Результат: Купіть якісні <a href="https://prof1group.ua/pants">штани</a> та <a href="https://prof1group.ua/shoes">взуття</a> в нас!

2️⃣ <b>Повідомлення з фото:</b>
   Надішліть фото з текстом у полі "Підпис" - опис буде обробленим, і фото опублікується з форматованим текстом

3️⃣ <b>Команди:</b>
   /help - показати цю справку
   /keywords - список всіх ключових слів

💡 <b>Нотатки:</b>
   • Регістр слова зберігається при замініі
   • Пошук здійснюється без урахування регістру
   • Посилання генеруються автоматично
"""
    
    await client.send_message(
        chat_id=message.chat.id,
        text=help_text,
        parse_mode="html"
    )


@app.on_message(filters.command("keywords") & filters.private)
async def keywords_command(client: Client, message: Message):
    """
    Команда /keywords - показує список ключових слів
    """
    keywords_text = "<b>📋 Список ключових слів та посилань:</b>\n\n"
    for i, (keyword, url) in enumerate(KEYWORD_LINKS.items(), 1):
        keywords_text += f"{i}. <code>{keyword}</code> → <a href=\"{url}\">{url}</a>\n"
    
    if not KEYWORD_LINKS:
        keywords_text = "❌ Словник ключових слів порожній!"
    
    await client.send_message(
        chat_id=message.chat.id,
        text=keywords_text,
        parse_mode="html"
    )


@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    """
    Команда /start - вітання
    """
    start_text = """👋 Вітаємо в Post Formatter!

Це приватна версія, яка працює від вашого особистого акаунту.

✨ <b>Основні функції:</b>
• 📝 Надішліть текстове повідомлення - бот автоматично замініть ключові слова на посилання та опублікує у канал
• 📸 Надішліть фото з описом - опис буде обробленим, і фото опублікується з форматованим текстом

🔗 <b>Ключові слова та посилання:</b>
"""
    
    for keyword, url in KEYWORD_LINKS.items():
        start_text += f"\n• <code>{keyword}</code> → {url}"
    
    start_text += "\n\n⚙️ /keywords - показати список\n📖 /help - показати справку"
    
    await client.send_message(
        chat_id=message.chat.id,
        text=start_text,
        parse_mode="html"
    )


async def main():
    """
    Основна функція для запуску клієнту
    """
    logger.info("🚀 Pyrogram Post Formatter запускається...")
    logger.info(f"📱 Session: {SESSION_NAME}")
    logger.info(f"🔗 Channel ID: {CHANNEL_ID}")
    
    async with app:
        logger.info("✅ Клієнт підключився успішно!")
        logger.info("🎧 Чекаю на повідомлення...")
        await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⛔ Бот зупинено")
    except Exception as e:
        logger.error(f"❌ Критична помилка: {str(e)}")
