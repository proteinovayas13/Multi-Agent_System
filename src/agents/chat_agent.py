"""
Chat Agent - обычный диалоговый агент
"""
import random
from datetime import datetime

class ChatAgent:
    def __init__(self):
        self.name = "Chat Agent"
        self.greetings = [
            "Привет! Я чат-агент. Чем могу помочь?",
            "Здравствуйте! Рад вас видеть.",
            "Добрый день! Как я могу вам помочь?"
        ]
        self.farewells = [
            "До свидания! Хорошего дня!",
            "Всего хорошего!",
            "Рад был помочь!"
        ]
        self.help_topics = [
            "RAG (поиск информации)",
            "SQL запросы к базам данных",
            "Анализ данных",
            "Генерация отчетов"
        ]
        print(f"✅ {self.name} инициализирован")
    
    def process(self, message: str, context: dict = None) -> str:
        """Обработка сообщения"""
        message = message.encode('utf-8').decode('utf-8')
        message_lower = message.lower()
        
        # Приветствия
        if any(word in message_lower for word in ["привет", "здравствуй", "добрый день", "hi", "hello"]):
            return random.choice(self.greetings)
        
        # Прощания
        if any(word in message_lower for word in ["пока", "до свидания", "goodbye", "bye"]):
            return random.choice(self.farewells)
        
        # Справка
        if any(word in message_lower for word in ["помощь", "help", "что умеешь"]):
            return f"""🤖 Я умею:
{chr(10).join(f'• {topic}' for topic in self.help_topics)}

Также могу:
• Ответить на общие вопросы
• Поддержать разговор
• Рассказать о возможностях системы

Просто напишите, что вас интересует!"""
        
        # Время
        if any(word in message_lower for word in ["время", "time", "час"]):
            current_time = datetime.now().strftime("%H:%M:%S")
            return f"🕐 Текущее время: {current_time}"
        
        # Дата
        if any(word in message_lower for word in ["дата", "date", "число"]):
            current_date = datetime.now().strftime("%d.%m.%Y")
            return f"📅 Сегодня: {current_date}"
        
        # О себе
        if any(word in message_lower for word in ["как дела", "how are you"]):
            responses = ["Отлично! Спасибо что спросили!", "Хорошо, помогаю пользователям!", "Всё отлично, готов помочь!"]
            return random.choice(responses)
        
        # Если ничего не подошло
        return f"""🤔 Я не совсем понял ваш запрос. 
        
💡 Попробуйте:
• Спросить "Что ты умеешь?"
• Задать вопрос по анализу данных
• Попросить помощи с SQL запросом
• Или просто поздороваться!

Ваш запрос: "{message}" """