"""Telegram‑бот із інтеграцією ШІ‑агента.

Цей модуль містить точки входу Telegram‑бота (команди та хендлери повідомлень),
діалогову логіку для кількох сценаріїв (звичайні питання до ChatGPT, «побачення
із зіркою», допомога з листуванням, генерація профілю та «опенер» для першого
повідомлення), а також реєстрацію хендлерів у застосунку `python-telegram-bot`.

Основні команди:
- /start — головне меню та скидання режиму
- /gpt — питання до ChatGPT
- /date — сценарій «побачення з селебриті» (кнопки)
- /message — допомога з перепискою (кнопки + збір історії)
- /profile — генерація профілю
- /opener — генерація першого повідомлення

Примітка: модуль покладається на глобальні об’єкти `dialog` (стан діалогу) та
`chatgpt` (сервіс взаємодії з OpenAI), визначені наприкінці файлу. Логіка коду не
змінюється — додано лише докстрінги.
"""
print(">>> bot.py LOADED")
import os
import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from dotenv import load_dotenv

from gpt import *
from util import *

# Завантажуємо змінні середовища з .env та читаємо токен бота
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError(
        "Не знайдено TELEGRAM_BOT_TOKEN у змінних середовища або файлі .env"
    )

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
if not OPENAI_API_KEY:
    raise RuntimeError("Не знайдено OPENAI_API_KEY у змінних середовища або файлі .env")

async def start(update, context):
  """Обробник команди /start: показує головне меню та вимикає режим ChatGPT.

  Args:
      update: Об’єкт `telegram.Update` з інформацією про вхідну подію.
      context: Об’єкт контексту `ContextTypes.DEFAULT_TYPE` бібліотеки
          `python-telegram-bot`.

  Side Effects:
      - Оновлює глобальний стан `dialog.mode` на `None`.
      - Надсилає фото та кілька текстових повідомлень у чат.
      - Встановлює команди бота та відображає головне меню з кнопками.
  """
  dialog.mode = None
  await send_text(update, context, "Режим ChatGPT вимкнено. Ви у головному меню ✅")

  msg = load_message("main")
  await send_photo(update, context, "main")
  await send_text(update, context, msg)
  await show_main_menu(update, context, {
      # Замість сурогатних пар треба використовувати повні Unicode‑кодпоінти у форматі \UXXXXXXXX (8 hex цифр)
      "start": "Головне меню",
      "profile": "Генерація Tinder-профіля \U0001F60E",
      "opener": "Повідомлення для знайомства \U0001F970",
      "message": "Переписка від вашого імені \U0001F608",
      "date": "Спілкування з зірками \U0001F525",
      "gpt": "Задати питання ChatGPT \U0001F9E0",
  })

async def gpt(update, context):
    """Активує режим «gpt» і показує інструкції користувачу.

    Args:
        update: Об’єкт `telegram.Update`.
        context: Об’єкт контексту `ContextTypes.DEFAULT_TYPE`.

    Side Effects:
        - Встановлює `dialog.mode = "gpt"`.
        - Надсилає зображення та текст із ресурсу `messages/gpt.txt`.
    """
    dialog.mode = "gpt"
    await send_photo(update, context, "gpt")
    msg = load_message("gpt")
    await send_text(update, context, msg)

async def gpt_dialog(update, context):
    """Діалоговий хендлер для режиму «gpt» — надсилає питання до ChatGPT.

    Береться вхідний текст повідомлення користувача, зчитується промпт `gpt`
    із ресурсів і відправляється запит через `ChatGptService`.

    Args:
        update: Об’єкт `telegram.Update` (очікується текстове повідомлення).
        context: Об’єкт контексту `ContextTypes.DEFAULT_TYPE`.

    Side Effects:
        - Відповідає у чаті текстом, згенерованим ШІ.
    """
    text = update.message.text
    prompt = load_prompt("gpt")
    answer = await chatgpt.send_question(prompt, text)
    await send_text(update, context, answer)

async def date(update, context):
    """Активує режим «date» і показує вибір персонажу для діалогу.

    Args:
        update: Об’єкт `telegram.Update`.
        context: Об’єкт контексту `ContextTypes.DEFAULT_TYPE`.

    Side Effects:
        - Встановлює `dialog.mode = "date"`.
        - Надсилає фото та повідомлення з кнопками вибору (callback data
          `date_*`).
    """
    dialog.mode = "date"
    msg = load_message("date")
    await send_photo(update, context, "date")
    await send_text_buttons(update, context, msg,{
        "date_grande":"Аріана Гранде",
        "date_robbie":"Марго Роббі",
        "date_zendaya":"Зендея",
        "date_gosling":"Райан Гослінг",
        "date_hardy":"Том Харді",
    })

async def date_button(update, context):
    """Обробляє натискання кнопок у режимі «date».

    Залежно від callback‑даних показує відповідне зображення, інформує
    користувача та встановлює системний промпт для наступних повідомлень.

    Args:
        update: Об’єкт `telegram.Update` з `callback_query`.
        context: Об’єкт контексту `ContextTypes.DEFAULT_TYPE`.

    Side Effects:
        - Відповідає на `callback_query`.
        - Надсилає фото.
        - Встановлює промпт у `chatgpt` через `set_prompt()`.
    """
    query = update.callback_query.data
    await update.callback_query.answer()
    await send_photo(update, context, query)
    await send_text(update, context, "Гарний вибір. \U0001F60E Ваша задача - запросити дівчину,хлопця за п'ять повідомлень ! \U0001F525")
    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt)


async def date_dialog(update, context):
    """Діалог у режимі «date» — передає повідомлення користувача до ШІ.

    Показує службове повідомлення «набирає повідомлення», відправляє введений
    текст у `ChatGptService.add_message()` (використовуючи встановлений раніше
    системний промпт), після чого редагує службове повідомлення відповіддю.

    Args:
        update: Об’єкт `telegram.Update` з текстом повідомлення.
        context: Об’єкт контексту `ContextTypes.DEFAULT_TYPE`.
    """
    text = update.message.text
    my_message = await send_text(update, context, "набирає повідомлення")
    answer = await chatgpt.add_message(text)
    await my_message.edit_text(answer)

async def message(update, context):
    """Активує режим «message» — підготовка до генерації реплік.

    Args:
        update: Об’єкт `telegram.Update`.
        context: Об’єкт контексту `ContextTypes.DEFAULT_TYPE`.

    Side Effects:
        - Встановлює `dialog.mode = "message"`.
        - Надсилає фото та повідомлення з кнопками (`message_next`,
          `message_date`).
        - Очищає `dialog.list` — тимчасову історію чату користувача.
    """
    dialog.mode = "message"
    msg = load_message("message")
    await send_photo(update, context, "message")
    await send_text_buttons(update, context, msg,{
        "message_next": "Написати повідомлення",
        "message_date": "Запросити на побачення",
    })
    dialog.list.clear()

async def message_dialog(update, context):
    """Агрегує повідомлення користувача у режимі «message».

    Args:
        update: Об’єкт `telegram.Update` з текстом.
        context: Об’єкт контексту `ContextTypes.DEFAULT_TYPE`.

    Side Effects:
        - Додає текст повідомлення до списку `dialog.list`.
    """
    text = update.message.text
    dialog.list.append(text)

async def message_button(update, context):
    """Обробляє кнопки у режимі «message» і генерує відповідь ШІ.

    Формує промпт на основі вибраної кнопки та передає агреговану історію
    повідомлень користувача до `ChatGptService.send_question()`.

    Args:
        update: Об’єкт `telegram.Update` із `callback_query`.
        context: Об’єкт контексту `ContextTypes.DEFAULT_TYPE`.

    Side Effects:
        - Відповідає на `callback_query`.
        - Показує службове повідомлення «Думаю над варіантами...», яке далі
          редагується відповіддю ШІ.
    """
    query = update.callback_query.data
    await update.callback_query.answer()

    prompt = load_prompt(query)
    user_chat_history = "\n\n".join(dialog.list)

    my_message = await send_text(update, context, "Думаю над варіантами...")
    answer = await chatgpt.send_question(prompt, user_chat_history)
    await my_message.edit_text(answer)

async def profile(update, context):
    """Активує режим «profile» — збір даних для генерації профілю.

    Args:
        update: Об’єкт `telegram.Update`.
        context: Об’єкт контексту `ContextTypes.DEFAULT_TYPE`.

    Side Effects:
        - Встановлює `dialog.mode = "profile"`.
        - Надсилає фото та початкове повідомлення.
        - Очищає `dialog.user` і скидає лічильник `dialog.counter`.
        - Запитує перше поле анкети (вік).
    """
    dialog.mode = "profile"
    msg = load_message("profile")
    await send_photo(update, context, "profile")
    await send_text(update, context, msg)

    dialog.user.clear()
    dialog.counter = 0
    await send_text(update, context, "Скільки вам років ?")


async def profile_dialog(update, context):
    """Покроково збирає дані профілю користувача та генерує результат.

    Під час кожного повідомлення збільшує лічильник кроків і заповнює
    відповідні поля у `dialog.user`. На фінальному кроці формує текст профілю
    через `ChatGptService.send_question()` із промптом `profile`.

    Args:
        update: Об’єкт `telegram.Update` з текстом.
        context: Об’єкт контексту `ContextTypes.DEFAULT_TYPE`.

    Side Effects:
        - Модифікує `dialog.user` та `dialog.counter`.
        - Надсилає проміжні підказки.
        - Редагує службове повідомлення з готовим профілем.
    """
    text = update.message.text
    dialog.counter += 1

    if dialog.counter == 1:
        dialog.user["age"] = text
        await send_text(update, context, "Ким ви працюєте ?")
    if dialog.counter == 2:
        dialog.user["occupation"] = text
        await send_text(update, context, "Яке у вас хоббі ?")
    if dialog.counter == 3:
        dialog.user["hobby"] = text
        await send_text(update, context, "Що вам не подобається в людях ?")
    if dialog.counter == 4:
        dialog.user["annoys"] = text
        await send_text(update, context, "Мета знайомства ?")
    if dialog.counter == 5:
        dialog.user["goals"] = text
        prompt = load_prompt("profile")
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update, context, "ChatGPT генерує ваш профіль. Зачекайте декільки секунд.")
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)

async def opener(update, context):
    """Активує режим «opener» — збір даних для першого повідомлення.

    Args:
        update: Об’єкт `telegram.Update`.
        context: Об’єкт контексту `ContextTypes.DEFAULT_TYPE`.

    Side Effects:
        - Встановлює `dialog.mode = "opener"`.
        - Очищає `dialog.user`, скидає `dialog.counter`.
        - Надсилає фото, текст і запитує ім’я партнера.
    """
    dialog.mode = "opener"
    msg = load_message("opener")
    await send_photo(update, context, "opener")
    await send_text(update, context, msg)

    dialog.user.clear()
    dialog.counter = 0
    await send_text(update, context, "Ім'я партнера ?")


async def opener_dialog(update, context):
    """Покроково збирає дані й формує «опенер» через ШІ.

    На кожному кроці заповнює одне поле в `dialog.user`. На фінальному кроці
    викликає `ChatGptService.send_question()` із промптом `opener` і
    редагує службове повідомлення відповіддю.

    Args:
        update: Об’єкт `telegram.Update` з текстом.
        context: Об’єкт контексту `ContextTypes.DEFAULT_TYPE`.
    """
    text = update.message.text
    dialog.counter += 1

    if dialog.counter == 1:
        dialog.user["name"] = text
        await send_text(update, context, "Скільки років партнеру ?")
    if dialog.counter == 2:
        dialog.user["age"] = text
        await send_text(update, context, "Оцініть зовнішність: 1-10 балів ?")
    if dialog.counter == 3:
        dialog.user["handsome"] = text
        await send_text(update, context, "Ким працює ?")
    if dialog.counter == 4:
        dialog.user["occupation"] = text
        await send_text(update, context, "Мета знайомства ?")
    if dialog.counter == 5:
        dialog.user["goals"] = text
        prompt = load_prompt("opener")
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update, context, "ChatGPT генерує ваше повідомлення...")
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)



async def hello(update, context):
  """Роутер текстових повідомлень залежно від активного режиму.

  Визначає, у якому режимі перебуває користувач (`dialog.mode`), та делегує
  обробку у відповідний діалоговий хендлер.

  Args:
      update: Об’єкт `telegram.Update` з текстом.
      context: Об’єкт контексту `ContextTypes.DEFAULT_TYPE`.
  """
  if dialog.mode == "gpt":
    await gpt_dialog(update, context)
  elif dialog.mode == "date":
    await date_dialog(update, context)
  elif dialog.mode == "message":
    await message_dialog(update, context)
  elif dialog.mode == "profile":
    await profile_dialog(update, context)
  elif dialog.mode == "opener":
    await opener_dialog(update, context)

async def buttons_handler(update, context):
    """Демонстраційний обробник довільних кнопок «start/stop».

    Args:
        update: Об’єкт `telegram.Update` із `callback_query`.
        context: Об’єкт контексту `ContextTypes.DEFAULT_TYPE`.

    Side Effects:
        - Відповідає у чаті повідомленням «Started» або «Stopped».
    """
    query = update.callback_query.data
    if query == "start":
        await send_text(update, context, "Started")
    elif query == "stop":
        await send_text(update, context, "Stopped")

dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.user = {}
dialog.counter = 0

chatgpt = ChatGptService(token=OPENAI_API_KEY)

# Глобальний application, створюється один раз
application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

# Реєстрація хендлерів
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("gpt", gpt))
application.add_handler(CommandHandler("date", date))
application.add_handler(CommandHandler("message", message))
application.add_handler(CommandHandler("profile", profile))
application.add_handler(CommandHandler("opener", opener))

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
application.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
application.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))

async def process_update(update_json: dict):
    """Обробка webhook‑апдейту."""
    update = telegram.Update.de_json(update_json, application.bot)

    # Ініціалізуємо application один раз
    if not application.running:
        await application.initialize()
        await application.start()

    await application.process_update(update)

