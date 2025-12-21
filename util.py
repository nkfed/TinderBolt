"""Утилітарні функції для Telegram‑бота.

Надає допоміжні обгортки для відправлення повідомлень/фото/кнопок, керування
меню команд, а також завантаження текстових ресурсів і простий клас стану
діалогу.

У модулі використано стиль докстрінгів Google. Логіка коду не змінена — додано
лише документацію.
"""

import chardet
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    BotCommand,
    MenuButtonCommands,
    BotCommandScopeChat,
    MenuButtonDefault,
)
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


def dialog_user_info_to_str(user) -> str:
    """Конвертує словник даних користувача у форматований рядок.

    Очікується словник із можливими ключами: `name`, `sex`, `age`, `city`,
    `occupation`, `hobby`, `goals`, `handsome`, `wealth`, `annoys`. Для кожного
    наявного ключа буде додано рядок «Назва: значення» українькою.

    Args:
        user (dict): Словник атрибутів користувача з рядковими значеннями.

    Returns:
        str: Багаторядковий текст із людськими мітками для наявних полів.

    Note:
        Значення беруться як є. Якщо потрібна валідація чи нормалізація —
        виконуйте її до виклику цієї функції.
    """
    result = ""
    map = {"name": "Ім'я", "sex": "Стать", "age": "Вік", "city": "Місто", "occupation": "Професія", "hobby": "Хобі", "goals": "Цілі знайомства",
           "handsome": "Краса, привабливість у балах (максимум 10 балів)", "wealth": "Доход, багатство", "annoys": "У людях дратує"}
    for key, name in map.items():
        if key in user:
            result += name + ": " + user[key] + "\n"
    return result


async def send_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> Message:
    """Надсилає в чат текст у режимі Markdown, із перевіркою підкреслень.

    Якщо кількість символів підкреслення `_` непарна (може зламати Markdown),
    користувачу повертається службове повідомлення з рекомендацією скористатися
    `send_html()`.

    Перед відправкою текст перекодується через UTF‑16 з `surrogatepass`, щоб
    коректно передати сурогатні пари (емодзі тощо).

    Args:
        update (telegram.Update): Апдейт з контекстом чату/повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота.
        text (str): Текст повідомлення.

    Returns:
        telegram.Message: Відправлене повідомлення або службова відповідь.
    """
    if text.count('_') % 2 != 0:
        message = f"Рядок '{text}' є невалідним з погляду markdown. Скористайтеся методом send_html()"
        print(message)
        return await update.message.reply_text(message)
    
    text = text.encode('utf16', errors='surrogatepass').decode('utf-8', errors="replace")
    return await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)

async def send_html(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> Message:
    """Надсилає в чат HTML‑повідомлення.

    Текст попередньо перекодовуємо через UTF‑16 із `surrogatepass` для
    коректної підтримки емодзі та сурогатних пар.

    Args:
        update (telegram.Update): Апдейт з контекстом чату/повідомлення.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота.
        text (str): HTML‑розмітка повідомлення.

    Returns:
        telegram.Message: Відправлене повідомлення.
    """
    text = text.encode('utf16', errors='surrogatepass').decode('utf-8', errors="replace")
    return await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML)


async def send_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, buttons: dict) -> Message:
    """Надсилає текст і додає під ним вертикальний список кнопок.

    Args:
        update (telegram.Update): Апдейт із повідомленням користувача.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота.
        text (str): Текст повідомлення (Markdown).
        buttons (dict): Пара `callback_data -> label` для створення кнопок.

    Returns:
        telegram.Message: Відповідь бота з інлайн‑кнопками.
    """
    text = text.encode('utf16', errors='surrogatepass').decode('utf-8', errors="replace")
    keyboard = []
    for key, value in buttons.items():
        button = InlineKeyboardButton(str(value), callback_data=str(key))
        keyboard.append([button])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)


async def send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str) -> Message:
    """Відправляє фото з директорії `resources/images/` за назвою.

    Args:
        update (telegram.Update): Апдейт із контекстом чату.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота.
        name (str): Ім'я файлу без розширення (jpg).

    Returns:
        telegram.Message: Відправлене фото‑повідомлення.

    Raises:
        FileNotFoundError: Якщо файл зображення відсутній.
    """
    with open('resources/images/' + name + ".jpg", 'rb') as photo:
        return await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, commands: dict):
    """Показує командне меню бота для поточного чату.

    Встановлює команди (`/start`, `/gpt`, тощо) лише в межах поточного чату,
    а також увімкнює кнопку меню типу `MenuButtonCommands`.

    Args:
        update (telegram.Update): Апдейт із контекстом чату.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота.
        commands (dict): Відображення `команда -> опис` для меню.
    """
    command_list = [BotCommand(key, value) for key, value in commands.items()]
    await context.bot.set_my_commands(command_list, scope=BotCommandScopeChat(chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonCommands(), chat_id=update.effective_chat.id)

async def hide_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приховує команди та кнопку меню у поточному чаті.

    Args:
        update (telegram.Update): Апдейт із контекстом чату.
        context (ContextTypes.DEFAULT_TYPE): Контекст бота.
    """
    await context.bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonDefault(), chat_id=update.effective_chat.id)


def load_message(name):
    """Завантажує текст повідомлення з `resources/messages/`.

    Args:
        name (str): Ім'я файлу без розширення (`.txt`).

    Returns:
        str: Вміст файлу.
    """
    path = f"resources/messages/{name}.txt"
    with open(path, "rb") as f:
        raw = f.read()
    encoding = chardet.detect(raw)["encoding"] or "utf-8"
    return raw.decode(encoding, errors="replace")


def load_prompt(name):
    """Завантажує текст промпта з `resources/prompts/`.

    Args:
        name (str): Ім'я файлу без розширення (`.txt`).

    Returns:
        str: Вміст файлу.
    """
    path = f"resources/prompts/{name}.txt"
    with open(path, "rb") as f:
        raw = f.read()
    encoding = chardet.detect(raw)["encoding"] or "utf-8"
    return raw.decode(encoding, errors="replace")


class Dialog:
    """Порожній контейнер для стану діалогу.

    У поточній реалізації клас не має атрибутів та методів. У коді бота йому
    динамічно додаються поля на кшталт `mode`, `list`, `user`, `counter`.

    Приклад використання (псевдокод):

        dialog = Dialog()
        dialog.mode = None
        dialog.list = []
        dialog.user = {}
        dialog.counter = 0
    """
    pass
