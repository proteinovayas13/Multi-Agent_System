import os
from dotenv import load_dotenv
from langchain_gigachat import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Загрузка переменных окружения
load_dotenv()

# НАСТРОЙКА GIGACHAT

class GigaChatAgent:
    """
    Простой агент на базе GigaChat.
    """
    
    def __init__(self, verify_ssl=False):
        """
        Инициализация агента.
        
        Args:
            verify_ssl: Отключать ли проверку SSL-сертификатов
                        (только для локальной разработки!)
        """
        # Получаем credentials из переменных окружения
        credentials = os.getenv("GIGACHAT_CREDENTIALS")
        
        if not credentials:
            raise ValueError(
                "GIGACHAT_CREDENTIALS не найдены в .env файле!\n"
                "Создай файл .env и добавь туда: GIGACHAT_CREDENTIALS=твой_ключ"
            )
        
        # Инициализация клиента GigaChat
        try:
            self.llm = GigaChat(
                credentials=credentials,
                scope=os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS"),
                model="GigaChat",           # можно указать другую модель
                temperature=0.7,             # креативность (0-1)
                max_tokens=500,              # максимальная длина ответа
                verify_ssl_certs=verify_ssl,  # отключаем проверку для разработки
                timeout=60.0,
                verbose=False,               # отключаем отладку
            )
            print("✅ GigaChat клиент успешно создан")
        except Exception as e:
            print(f"❌ Ошибка при создании клиента GigaChat: {e}")
            raise
        
        # Системный промпт — задает поведение агента
        self.system_prompt = SystemMessage(
            content="""Ты — полезный AI-ассистент. 
            Отвечай кратко, по делу и дружелюбно.
            Если не знаешь ответа, так и скажи."""
        )
        
        # История диалога (для памяти)
        self.chat_history = []
    
    def chat(self, user_message: str) -> str:
        """
        Отправить сообщение агенту и получить ответ.
        """
        try:
            # Добавляем сообщение пользователя в историю
            self.chat_history.append(HumanMessage(content=user_message))
            
            # Формируем полный список сообщений
            messages = [self.system_prompt] + self.chat_history
            
            # Отправляем запрос к GigaChat
            response = self.llm.invoke(messages)
            
            # Добавляем ответ ассистента в историю
            self.chat_history.append(response)
            
            return response.content
        except Exception as e:
            print(f"❌ Ошибка при обращении к GigaChat: {e}")
            return f"Извините, произошла ошибка: {str(e)}"
    
    def stream_chat(self, user_message: str):
        """
        Стриминговая версия — ответ приходит по токенам
        """
        try:
            self.chat_history.append(HumanMessage(content=user_message))
            messages = [self.system_prompt] + self.chat_history
            
            full_response = ""
            print("🤖 Ассистент: ", end="", flush=True)
            
            for chunk in self.llm.stream(messages):
                content = chunk.content
                if content:
                    print(content, end="", flush=True)
                    full_response += content
            
            print()  # перевод строки
            
            # Сохраняем полный ответ в историю
            self.chat_history.append(AIMessage(content=full_response))
            
            return full_response
        except Exception as e:
            print(f"\n❌ Ошибка при стриминге: {e}")
            return f"Извините, произошла ошибка: {str(e)}"
    
    def clear_history(self):
        """Очистить историю диалога."""
        self.chat_history = []
        print("🗑️ История диалога очищена")


# СОЗДАНИЕ ФАЙЛА .env (ЕСЛИ ЕГО НЕТ)


def create_env_file():
    """Создает пример файла .env, если он не существует."""
    env_path = ".env"
    if not os.path.exists(env_path):
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("""# GigaChat credentials
GIGACHAT_CREDENTIALS=вставь_свой_ключ_здесь
GIGACHAT_SCOPE=GIGACHAT_API_PERS
""")
        print(f"📝 Создан файл {env_path}")
        print("⚠️ Не забудь вставить свой авторизационный ключ GigaChat!")
        return False
    return True


# ДЕМОНСТРАЦИЯ РАБОТЫ


def main():
    print("=" * 50)
    print("GigaChat Agent Demo")
    print("=" * 50)
    
    # Проверяем наличие .env файла
    if not create_env_file():
        print("\n🔧 Пожалуйста, отредактируй файл .env и добавь свой ключ GigaChat")
        print("   Затем запусти программу снова.")
        return
    
    # Загружаем переменные окружения
    load_dotenv()
    
    # Проверяем наличие ключа
    credentials = os.getenv("GIGACHAT_CREDENTIALS")
    if not credentials or credentials == "вставь_свой_ключ_здесь":
        print("\n❌ GIGACHAT_CREDENTIALS не настроен!")
        print("   Открой файл .env и вставь свой авторизационный ключ.")
        print("\n📌 Как получить ключ:")
        print("   1. Зарегистрируйся на https://developers.sber.ru/")
        print("   2. Перейди в раздел GigaChat")
        print("   3. Создай проект и получи авторизационный ключ")
        return
    
    # Создаем агента (verify_ssl=False только для локальной разработки!)
    print("\n🔧 Создание агента...")
    try:
        agent = GigaChatAgent(verify_ssl=False)  # временно отключаем SSL для разработки
    except Exception as e:
        print(f"❌ Не удалось создать агента: {e}")
        return
    
    # Проверяем, что все настроено корректно
    print("\n🔧 Проверка подключения...")
    try:
        test_response = agent.chat("Привет! Как дела?")
        print(f"✅ GigaChat работает!")
        print(f"   Ответ: {test_response[:100]}...")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        print("\nПроверь:")
        print("1. Правильность GIGACHAT_CREDENTIALS в .env")
        print("2. Доступность интернета")
        print("3. Для локальной разработки используй verify_ssl=False")
        return
    
    # Интерактивный режим
    print("\n💬 Введите 'exit' для выхода, 'clear' для очистки истории")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n👤 Вы: ").strip()
            
            if user_input.lower() == "exit":
                print("До свидания! 👋")
                break
            elif user_input.lower() == "clear":
                agent.clear_history()
                continue
            elif not user_input:
                continue
            
            # Используем стриминг для более интерактивного опыта
            agent.stream_chat(user_input)
        except KeyboardInterrupt:
            print("\n\nДо свидания! 👋")
            break
        except Exception as e:
            print(f"\n❌ Неожиданная ошибка: {e}")


# ПРИМЕР ИСПОЛЬЗОВАНИЯ ФУНКЦИЙ (TOOLS)


def example_with_tools():
    """
    Пример использования function calling
    """
    from langchain_core.tools import tool
    import json
    
    @tool
    def get_weather(city: str) -> str:
        """
        Получить текущую погоду в городе.
        В реальном проекте здесь был бы API-запрос.
        """
        # Это имитация — в реальности нужно вызывать API погоды
        weather_data = {
            "Москва": "солнечно, +15°C",
            "Санкт-Петербург": "облачно, +10°C",
            "Казань": "дождь, +12°C"
        }
        return weather_data.get(city, f"данные о погоде для {city} не найдены")
    
    print("\n" + "=" * 50)
    print("Демонстрация Function Calling")
    print("=" * 50)
    
    # Создаем агента
    credentials = os.getenv("GIGACHAT_CREDENTIALS")
    if not credentials:
        print("❌ Нет credentials для демонстрации tools")
        return
    
    try:
        llm = GigaChat(
            credentials=credentials,
            verify_ssl_certs=False,  # только для локальной разработки
            temperature=0.1,
        )
        
        # Привязываем инструменты
        llm_with_tools = llm.bind_tools([get_weather])
        
        # Пример запроса
        response = llm_with_tools.invoke("Какая погода в Москве?")
        
        print(f"Ответ: {response.content}")
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print("\n🔧 Вызов инструмента!")
            for tool_call in response.tool_calls:
                print(f"   Инструмент: {tool_call.get('name')}")
                print(f"   Аргументы: {tool_call.get('args')}")
        else:
            print("(Инструменты не вызывались)")
            
    except Exception as e:
        print(f"❌ Ошибка в демонстрации tools: {e}")

if __name__ == "__main__":
    main()
    
    # Раскомментируй для демонстрации tools:
    # example_with_tools()