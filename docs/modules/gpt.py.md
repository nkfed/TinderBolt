### Модуль: gpt.py — сервіс взаємодії з OpenAI (Chat Completions)

#### Призначення модуля
Модуль надає обгортку над OpenAI Chat Completions API для побудови розмови у форматі «system + user + assistant». Він інкапсулює:
- створення клієнта OpenAI з вказаним `base_url` та API‑ключем;
- ведення списку повідомлень чату (`message_list`);
- відправку чергового запиту до моделі та отримання відповіді;
- зручні методи для встановлення початкового промпта та для одноразових запитів «prompt + question».

У проєкті використовується у `bot.py` для генерації відповідей у сценаріях діалогу з користувачем (команди `/gpt`, `/date`, `/message`, `/profile`, `/opener`).

---

#### Класи

1) Клас: `ChatGptService`
- Відповідальність: єдиний сервіс доступу до Chat Completions API; зберігає контекст діалогу та формує запити до моделі.
- Внутрішній стан:
  - `client: OpenAI` — інстанс клієнта з бібліотеки `openai` (SDK v1‑стилю).
  - `message_list: list` — список повідомлень контексту чату у форматі словників: `{ "role": "system|user|assistant", "content": str }`.

Конструктор:
```
__init__(self, token: str) -> None
```
- Параметри:
  - `token: str` — API‑ключ для OpenAI сумісного ендпоїнта.
- Дія: ініціалізує `self.client = openai.OpenAI(base_url=..., api_key=token)` та порожній `message_list`.

Методи:
```
async def send_message_list(self) -> str
```
- Призначення: надіслати поточний `message_list` у Chat Completions і повернути контент відповіді.
- Поведінка:
  - Викликає `self.client.chat.completions.create(model="gpt-4o", messages=self.message_list, max_tokens=3000, temperature=0.9)`.
  - Берe першу відповідь: `completion.choices[0].message`.
  - Додає відповідь у `message_list` (як чергове `assistant`‑повідомлення) та повертає `message.content` (рядок).
- Повертає: `str` — текст відповіді моделі.

```
def set_prompt(self, prompt_text: str) -> None
```
- Призначення: встановити «системний» промпт (скидає контекст).
- Дія: `message_list.clear()` і додає `{"role": "system", "content": prompt_text}`.
- Повертає: `None`.

```
async def add_message(self, message_text: str) -> str
```
- Призначення: додати чергове `user`‑повідомлення в поточний контекст і отримати відповідь моделі.
- Дія: додає `{"role": "user", "content": message_text}` у `message_list` та викликає `send_message_list()`.
- Повертає: `str` — текст відповіді моделі.

```
async def send_question(self, prompt_text: str, message_text: str) -> str
```
- Призначення: одноразовий запит «system prompt + user message» без збереження попереднього контексту.
- Дія: очищує `message_list`, додає `system` і `user`, викликає `send_message_list()`.
- Повертає: `str` — текст відповіді моделі.

---

#### Функції
Окремих вільних функцій у модулі немає — весь API зосереджений у класі `ChatGptService`.

---

#### Параметри, типи, повертаємі значення
- Усі текстові параметри (`token`, `prompt_text`, `message_text`) — тип `str`.
- `message_list` — `list[dict]` із ключами `role` (`"system"|"user"|"assistant"`) та `content` (`str`).
- Усі методи, що виконують запит (`send_message_list`, `add_message`, `send_question`) — оголошені як `async` і повертають `str` (контент відповіді).
- `set_prompt` — синхронний, повертає `None`.

Примітка: хоча методи оголошені як асинхронні, виклик SDK `self.client.chat.completions.create(...)` є синхронним. Це може блокувати потік подій під час мережевого запиту. Якщо неблокуюча поведінка критична, розгляньте використання окремого пулу або асинхронного клієнта, якщо він стане доступним.

---

#### Залежності
- `openai` (SDK у стилі v1): використовується `openai.OpenAI` для створення клієнта. У коді також є імпорт `from openai import OpenAI`, але фактичне створення клієнта йде через `openai.OpenAI(...)`.
- Мережевий доступ до сумісного ендпоїнта, заданого `base_url="https://openai.javarush.com/v1"`.
- Python 3.10+ (узгоджено з асинхронними хендлерами в `python-telegram-bot`).

---

#### Приклади використання (псевдокод усередині async‑хендлерів)

1) Одноразове запитання з промптом:
```
# у файлі bot.py ініціалізація сервісу (реальний токен має бути секретом)
chatgpt = ChatGptService(token="<OPENAI_API_KEY>")

# у тілі async-хендлера
prompt = "Ти — асистент для написання привітання. Відповідай коротко."
user_info = "Ім'я: Олена\nМета: знайомство"
answer = await chatgpt.send_question(prompt, user_info)
# далі відправити answer у чат
```

2) Багатокроковий діалог із накопиченням контексту:
```
chatgpt.set_prompt("Ти — корисний чат‑помічник українською мовою.")

reply1 = await chatgpt.add_message("Привіт! Допоможи скласти опис профілю.")
reply2 = await chatgpt.add_message("Ось додаткові дані про мене...")
# контекст зберігається у message_list і розширюється відповідями assistant
```

3) Інтеграція в сценарій `opener` (спрощено в дусі наявного коду):
```
prompt = load_prompt("opener")              # з util.py
user_info = dialog_user_info_to_str(user)    # з util.py
msg = await send_text(update, context, "ChatGPT генерує ваше повідомлення...")
answer = await chatgpt.send_question(prompt, user_info)
await msg.edit_text(answer)
```

---

#### Можливі edge cases та ризики
- Невалідний або прострочений токен: отримаєте помилку автентифікації під час виклику `create(...)`.
- Недоступний `base_url` або мережеві збої: виклики можуть кидати винятки/тайм‑аути; бажано обгорнути запити у `try/except` і повідомляти користувача про помилки.
- Ліміти і квоти: можливі помилки 429 (rate limit) — варто додати повторні спроби з backoff.
- Переповнення контексту: великий `message_list` + `max_tokens=3000` може спричинити `context length exceeded`. Періодично стискайте/обрізайте історію.
- Формат повідомлень: `message_list` має містити коректні пари `role/content`; сторонні типи або невалідні ролі призведуть до помилок API.
- Асинхронність vs синхронний SDK: методи оголошені `async`, але всередині використовують синхронний виклик — у високому навантаженні це може блокувати цикл подій (варто винести у `run_in_executor` або застосувати сумісний async‑клієнт, якщо з’явиться).
- Багатопоточність/конкурентний доступ: одночасні виклики до одного екземпляра `ChatGptService` можуть змагатися за спільний `message_list`. Рекомендується або синхронізувати доступ, або створювати окремий інстанс на користувача/чат.
- Валідація довжини відповіді: `max_tokens=3000` — доволі велике значення; перевіряйте, чи воно сумісне з обраною моделлю та бюджетом.

---

#### Нотатки з інтеграції та покращення
- Секрети: не зберігайте токени в коді; використовуйте змінні оточення або секретні сховища.
- Обробка помилок: додати централізовану обробку винятків і дружні повідомлення користувачу в боті.
- Конфігурація: винести `model`, `temperature`, `max_tokens`, `base_url` у конфіг/ENV.
- Тестування: можна замінити `OpenAI` на тестовий подвійник для модульних тестів, щоб не робити реальні мережеві запити.

---

#### Посилання на код (актуальні фрагменти)
```
class ChatGptService:
    client: OpenAI = None
    message_list: list = None

    def __init__(self, token):
        self.client = openai.OpenAI(base_url="https://openai.javarush.com/v1", api_key=token)
        self.message_list = []

    async def send_message_list(self) -> str:
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.message_list,
            max_tokens=3000,
            temperature=0.9
        )
        message = completion.choices[0].message
        self.message_list.append(message)
        return message.content

    def set_prompt(self, prompt_text: str) -> None:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})

    async def add_message(self, message_text: str) -> str:
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list()

    async def send_question(self, prompt_text: str, message_text: str) -> str:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list()
```
