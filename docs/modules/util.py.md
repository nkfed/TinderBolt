### Модуль `util.py`

#### Призначення
`util.py` — це набір утиліт для Telegram‑бота (на `python-telegram-bot`), що спрощує:
- надсилання текстових і HTML‑повідомлень;
- побудову повідомлень із інлайн‑кнопками;
- відправку фото з локальної папки `resources/images`;
- керування головним меню (списком команд) для конкретного чату;
- завантаження текстів із `resources/messages` і промптів із `resources/prompts`;
- перетворення словника з даними користувача у читабельний текст;
- простий контейнер стану діалогу `Dialog`.

---

#### Залежності
- Бібліотека: `python-telegram-bot` (класи: `Update`, `Message`, `InlineKeyboardButton`, `InlineKeyboardMarkup`, `BotCommand`, `MenuButtonCommands`, `BotCommandScopeChat`, `MenuButtonDefault`, `ParseMode`).
- Стандартна бібліотека Python (`open`, робота з файлами).
- Ресурси проєкту:
  - `resources/images/*.jpg` — для `send_photo()`;
  - `resources/messages/*.txt` — для `load_message()`;
  - `resources/prompts/*.txt` — для `load_prompt()`.

---

### Опис API

#### `dialog_user_info_to_str(user) -> str`
Перетворює словник даних користувача у багато‑рядковий текст українською. Підтримувані ключі: `name`, `sex`, `age`, `city`, `occupation`, `hobby`, `goals`, `handsome`, `wealth`, `annoys`.

- Параметри:
  - `user: dict[str, str]` — значення очікуються рядками; відсутні ключі ігноруються.
- Повертає: `str` — лейбли + значення, кожна пара з нового рядка.
- Можливі помилки: некоректні типи значень (не `str`) можуть спричинити помилки конкатенації.

Приклад:
```python
from util import dialog_user_info_to_str

user = {"name": "Анна", "age": "25", "occupation": "Дизайнер", "goals": "Серйозні стосунки"}
summary = dialog_user_info_to_str(user)
# "Ім'я: Анна\nВік: 25\nПрофесія: Дизайнер\nЦілі знайомства: Серйозні стосунки\n"
```

---

#### `async def send_text(update, context, text) -> telegram.Message`
Надсилає текст у режимі Markdown. Якщо кількість `_` у тексті непарна (ймовірність зламаної розмітки) — надсилається пояснення‑попередження з порадою використати `send_html()`.

- Параметри: `update: Update`, `context: ContextTypes.DEFAULT_TYPE`, `text: str`.
- Повертає: `Message` — об’єкт відправленого повідомлення (або попередження).
- Особливості: перед відправкою текст проходить безпечну нормалізацію UTF-8 з `errors="replace"` для стабільної роботи з будь-якими символами.

Приклад виклику (псевдокод): `send_text(update, context, "Привіт, це _курсив_ і текст.")`
Примітка: виклик робиться всередині асинхронної функції з очікуванням результату.

---

#### `async def send_html(update, context, text) -> telegram.Message`
Надсилає HTML‑повідомлення (`ParseMode.HTML`) з тією ж UTF-8 нормалізацією для стабільності.

- Параметри: як у `send_text`.
- Повертає: `Message`.

Приклад виклику (псевдокод): `send_html(update, context, "<b>Важливо:</b> ...")`

---

#### `async def send_text_buttons(update, context, text, buttons) -> telegram.Message`
Надсилає текст з інлайн‑клавіатурою (кожна кнопка в окремому рядку).

- Параметри:
  - `text: str` — текст (Markdown); буде пропущений через UTF-8 нормалізацію.
  - `buttons: dict` — `{callback_data: label}`; обидва конвертуються у `str`.
- Повертає: `Message`.

Приклад виклику (псевдокод): `send_text_buttons(update, context, "Оберіть дію:", {"date_start": "Почати", "date_stop": "Зупинити"})`

---

#### `async def send_photo(update, context, name) -> telegram.Message`
Надсилає фото `resources/images/{name}.jpg`.

- Параметри: `name: str` — без розширення `.jpg`.
- Повертає: `Message`.
- Помилки: `FileNotFoundError`, якщо файла немає; також застосовні обмеження Telegram за розміром.

Приклад виклику (псевдокод): `send_photo(update, context, "main")`

---

#### `async def show_main_menu(update, context, commands) -> None`
Встановлює специфічні для чату команди та показує кнопку меню.

- Параметри: `commands: dict[str, str]` — `{команда: опис}` (без `/`).
- Повертає: `None`.

Приклад виклику (псевдокод): `show_main_menu(update, context, {"gpt": "Режим GPT", "opener": "Генератор opener"})`

---

#### `async def hide_main_menu(update, context) -> None`
Видаляє команди, встановлені для чату, та повертає стандартну кнопку меню.

- Параметри: як у `show_main_menu` (без `commands`).
- Повертає: `None`.

Приклад виклику (псевдокод): `hide_main_menu(update, context)`

---

#### `def load_message(name) -> str`
Читає файл `resources/messages/{name}.txt` у кодуванні UTF‑8 і повертає вміст.

- Параметри: `name: str`.
- Повертає: `str`.
- Помилки: `FileNotFoundError`, `UnicodeDecodeError` — якщо файл відсутній/пошкоджений.

Приклад виклику (псевдокод): `load_message("main")`

---

#### `def load_prompt(name) -> str`
Читає файл `resources/prompts/{name}.txt` у кодуванні UTF‑8 і повертає вміст.

- Параметри: `name: str`.
- Повертає: `str`.
- Помилки: як у `load_message`.

Приклад виклику (псевдокод): `load_prompt("opener")`

---

### Клас `Dialog`
Порожній клас‑контейнер для стану діалогу. Поля додаються динамічно у коді (див. `bot.py`).

Типові властивості, що встановлюються зовні:
- `mode: str | None` — активний сценарій (`"gpt"`, `"date"`, `"message"`, `"profile"`, `"opener"`).
- `list: list` — проміжні дані/історія.
- `user: dict[str, str]` — анкета користувача.
- `counter: int` — лічильник кроків сценарію.

Приклад ініціалізації (з `bot.py`, псевдокод): `Dialog()` зі встановленням полів `mode`, `list`, `user`, `counter`.

---

### Edge cases та рекомендації
1. Markdown у `send_text`:
   - Непарна кількість `_` вважається помилкою. Навіть при парній кількості можливі хибні інтерпретації; для стабільності використовуйте `send_html()` або екранування.
2. Емодзі/символи:
   - Безпечна нормалізація UTF-8 з `errors="replace"` допомагає коректно пройти будь-яким символам; якщо виникають артефакти — перевіряйте клієнт та вхідні дані.
3. Кнопки (`send_text_buttons`):
   - `callback_data` бажано тримати коротким (Telegram обмежує ~64 байти); не використовуйте довгі тексти.
4. Фото (`send_photo`):
   - Переконайтеся, що `resources/images/{name}.jpg` існує і не перевищує ліміти Telegram.
5. Команди меню:
   - `show_main_menu` застосовує `BotCommandScopeChat` (лише для конкретного чату). Для глобальних команд потрібен інший scope.
6. Завантаження файлів:
   - Додавайте обробку помилок або перевірку на існування перед читанням; синхронізуйте імена файлів та ключі у коді.
7. Типи у `dialog_user_info_to_str`:
   - Якщо значення не рядкові — використовуйте `str()` або нормалізуйте типи на вході.

---

### Версія документа
Відповідає файлу `util.py` (77 рядків) із поточного стану репозиторію.
