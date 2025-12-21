"""Сервіс взаємодії з OpenAI Chat Completions.

Цей модуль надає клас `ChatGptService` для роботи з чат‑моделями OpenAI
через SDK `openai`. Сервіс підтримує як короткі одноразові запити з системним
промптом, так і діалоговий режим із накопиченням історії повідомлень.

Використання (псевдокод):

    service = ChatGptService(token="<OPENAI_API_KEY>")
    service.set_prompt("You are helpful assistant")
    await service.add_message("Hello!")
    # або одноразове питання
    await service.send_question("You are helpful assistant", "Explain TCP/IP in simple terms")

Примітка: методи, що звертаються до API, є асинхронними (`async`) і
очікують виклику через `await` усередині асинхронного контексту.
"""

import openai
from openai import OpenAI
from util import normalize_text


class ChatGptService:
    """Тонкий клієнт для OpenAI Chat Completions API.

    Зберігає внутрішній список повідомлень у форматі, сумісному з Chat
    Completions (`{"role": "system|user|assistant", "content": str}`) і надає
    допоміжні методи для оновлення промпта, додавання повідомлень і надсилання
    запиту до моделі.

    Атрибути:
        client (OpenAI): Ініціалізований клієнт OpenAI SDK.
        message_list (list): Поточна історія повідомлень для Chat Completions.
    """
    client: OpenAI = None
    message_list: list = None

    def __init__(self, token):
        """Ініціалізує сервіс OpenAI.

        Args:
            token (str): API‑ключ OpenAI. Використовується для автентифікації
                запитів. Базова URL адреса встановлена на
                "https://openai.javarush.com/v1".
        """
        self.client = openai.OpenAI(base_url="https://openai.javarush.com/v1", api_key=token)
        self.message_list = []

    async def send_message_list(self) -> str:
        """Надсилає поточну історію повідомлень до Chat Completions.

        Після отримання відповіді додає повідомлення асистента до
        `message_list` і повертає його текстовий вміст.

        Returns:
            str: Вміст відповіді асистента (`message.content`).

        Raises:
            Exception: Будь‑які помилки мережі/квот/автентифікації з боку SDK
                `openai` будуть проброшені вгору.
        """
        completion = self.client.chat.completions.create(
            model="gpt-4o",  # gpt-4o,  gpt-4-turbo,    gpt-3.5-turbo
            messages=self.message_list,
            max_tokens=3000,
            temperature=0.9
        )
        message = completion.choices[0].message
        message.content = normalize_text(message.content)
        self.message_list.append(message)
        return message.content

    def set_prompt(self, prompt_text: str) -> None:
        """Очищає історію і встановлює системний промпт.

        Args:
            prompt_text (str): Текст системного повідомлення (`role="system"`).
        """
        prompt_text = normalize_text(prompt_text)
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})

    async def add_message(self, message_text: str) -> str:
        """Додає повідомлення користувача й отримує відповідь моделі.

        Args:
            message_text (str): Текст користувача, що додається з роллю `user`.

        Returns:
            str: Текст відповіді асистента після звернення до API.
        """
        message_text = normalize_text(message_text)
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list()

    async def send_question(self, prompt_text: str, message_text: str) -> str:
        """Виконує одноразовий запит із вказаним системним промптом.

        Очищає історію, додає системний промпт і повідомлення користувача, після
        чого надсилає запит до моделі.

        Args:
            prompt_text (str): Текст системного промпта (`role="system").
            message_text (str): Повідомлення користувача (`role="user").

        Returns:
            str: Текст відповіді асистента.
        """
        prompt_text = normalize_text(prompt_text)
        message_text = normalize_text(message_text)
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list()
