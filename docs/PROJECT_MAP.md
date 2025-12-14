 # Карта проєкту TinderBolt

 Цей документ описує структуру Python‑проєкту, призначення директорій і файлів, а також коротко пояснює, як вони взаємодіють.

 ## Огляд
 - Призначення: Telegram‑бот із декількома режимами (GPT‑чат, поради щодо побачень, генерація повідомлень, профіль, «opener») з інтеграцією OpenAI Chat Completions API.
 - Основні компоненти:
   - `bot.py` — точка входу та логіка обробки команд/повідомлень Telegram.
   - `gpt.py` — сервіс взаємодії з OpenAI (чат‑контекст, відправлення запитів).
   - `util.py` — допоміжні утиліти для повідомлень/кнопок/меню/завантаження ресурсів.
   - `resources/` — статичні ресурси: зображення, тексти повідомлень та промпти.
   - `requirements.txt` — залежності проєкту.

 ## Дерево файлів

 ```
 .
 ├── PROJECT_STRUCTURE.md                 # Існуючий опис структури (коротка форма)
 ├── bot.py                               # Головний файл бота: реєстрація хендлерів і режими діалогу
 ├── gpt.py                               # Клас ChatGptService для роботи з OpenAI Chat Completions
 ├── util.py                              # Утиліти для Telegram (повідомлення, кнопки, меню) і завантаження ресурсів
 ├── requirements.txt                     # Перелік Python‑залежностей
 ├── docs/
 │   └── PROJECT_MAP.md                   # Ця детальна карта проєкту
 └── resources/
     ├── images/                          # Зображення для візуального супроводу в боті
     │   ├── avatar_main.jpg
     │   ├── date.jpg
     │   ├── date_gosling.jpg
     │   ├── date_grande.jpg
     │   ├── date_hardy.jpg
     │   ├── date_robbie.jpg
     │   ├── date_zendaya.jpg
     │   ├── gpt.jpg
     │   ├── main.jpg
     │   ├── message.jpg
     │   ├── message_date.jpg
     │   ├── message_next.jpg
     │   ├── opener.jpg
     │   └── profile.jpg
     ├── messages/                        # Готові текстові повідомлення для різних розділів/режимів
     │   ├── date.txt
     │   ├── gpt.txt
     │   ├── main.txt
     │   ├── message.txt
     │   ├── opener.txt
     │   └── profile.txt
     └── prompts/                         # Тексти промптів для OpenAI (системні інструкції та шаблони)
         ├── date_gosling.txt
         ├── date_grande.txt
         ├── date_hardy.txt
         ├── date_robbie.txt
         ├── date_zendaya.txt
         ├── gpt.txt
         ├── main.txt
         ├── message_date.txt
         ├── message_next.txt
         ├── opener.txt
         └── profile.txt
 ```

 ## Опис ключових файлів

 ### bot.py
 - Відповідає за ініціалізацію Telegram‑бота через `ApplicationBuilder` та реєстрацію хендлерів:
   - Команди: `/start`, `/gpt`, `/date`, `/message`, `/profile`, `/opener` (через `CommandHandler`).
   - Обробник текстових повідомлень без команди — маршрутизація на активний режим (через `MessageHandler`).
   - Обробники callback‑кнопок для режимів `date` і `message` (через `CallbackQueryHandler`).
 - Логіка діалогів реалізована функціями типу `gpt_dialog`, `date_dialog`, `message_dialog`, `profile_dialog`, `opener_dialog` та перемикачем `hello()` залежно від `dialog.mode`.
 - Для генерації текстів використовує `ChatGptService` з `gpt.py` і промпти/повідомлення з `resources/` через утиліти з `util.py`.
 - Зверніть увагу: у файлі присутні явні токени (API‑ключі). Для безпеки їх варто винести у змінні оточення/конфіги.

 ### gpt.py
 - Містить клас `ChatGptService` — тонкий клієнт до OpenAI Chat Completions API:
   - Зберігає чат‑контекст у `message_list`.
   - `set_prompt(prompt_text)` — встановлює системне повідомлення (скидає контекст).
   - `add_message(message_text)` — додає повідомлення користувача та відправляє запит.
   - `send_question(prompt_text, message_text)` — одноразове питання з системним промптом і повідомленням користувача.
   - Внутрішній метод `send_message_list()` викликає `client.chat.completions.create(...)` з моделлю за замовчуванням `gpt-4o` і параметрами `max_tokens`, `temperature`.

 ### util.py
 - Набір допоміжних функцій для роботи з Telegram API та ресурсами:
   - `send_text(...)`, `send_html(...)` — відправлення текстів із коректною обробкою кодувань і режимів розмітки.
   - `send_text_buttons(...)` — відправлення тексту з inline‑кнопками (`InlineKeyboardMarkup`).
   - `send_photo(...)` — відправка фото з каталогу `resources/images/`.
   - `show_main_menu(...)` / `hide_main_menu(...)` — керування командами та кнопкою меню для поточного чату.
   - `load_message(name)` / `load_prompt(name)` — завантаження відповідних `.txt` із `resources/messages/` та `resources/prompts/`.
   - `dialog_user_info_to_str(user)` — перетворює словник параметрів користувача у читабельний текст українською.
   - Порожній клас‑контейнер `Dialog` — використовується в `bot.py` для зберігання стану діалогу.

 ### requirements.txt
 - Містить Python‑пакети, необхідні для роботи бота (наприклад, `python-telegram-bot`, `openai` тощо). Фактичний перелік див. у файлі.

 ### PROJECT_STRUCTURE.md
 - Вихідний короткий перелік файлів/папок проєкту. Цей документ (`docs/PROJECT_MAP.md`) надає більш деталізований опис.

 ## Директорія resources/
 - `images/` — ілюстрації для різних режимів і екранів бота (аватар, основні екрани, теми «date/ message/ opener/ profile» тощо).
 - `messages/` — текстові шаблони повідомлень, що можуть відображатися користувачеві без звернення до моделі.
 - `prompts/` — системні інструкції та шаблони промптів для OpenAI. Наприклад, окремі варіанти для відомих персон або різних етапів діалогу (`message_next`, `message_date`, `opener`, `profile`).

 ## Логічні зв’язки
 - `bot.py` викликає:
   - `util.py` для відправлення текстів/кнопок/зображень і завантаження ресурсів.
   - `gpt.py` для генерації відповідей через OpenAI.
   - `.txt` з `resources/messages/` і `resources/prompts/` як джерела контенту/інструкцій.

 ## Примітки з безпеки/конфігурації
 - Рекомендовано зберігати секретні токени (Telegram Bot Token, OpenAI API Key) у змінних середовища або конфіг‑файлі, не в репозиторії.
 - Для локалізації бажано тримати всі тексти, що відображаються користувачеві, у ресурсах (`resources/messages/`).

 ## Як розвивати далі
 - Додати обробку помилок мережі/квот у `gpt.py`.
 - Виділити модулі за режимами діалогу замість великого `bot.py` (за потреби).
 - Додати логику збереження стану діалогу між перезапусками (наприклад, у БД чи файловому сховищі).