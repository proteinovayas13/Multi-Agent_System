"""
RAG Agent - Retrieval-Augmented Generation агент
Поиск информации в базе знаний и генерация ответов
"""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

class RAGAgent:
    """
    RAG Agent для поиска информации и ответов на вопросы
    Поддерживает:
    - Поиск по ключевым словам
    - Поиск по категориям
    - Контекстные ответы
    - Сохранение истории
    """
    
    def __init__(self):
        self.name = "RAG Agent"
        self.version = "1.0.0"
        self.history = []  # История запросов
        self.context = {}  # Контекст разговора
        
        # Расширенная база знаний
        self.knowledge_base = self._init_knowledge_base()
        
        print(f"{self.name} v{self.version} инициализирован")
        print(f"Загружено тем: {len(self.knowledge_base)}")
        print(f"Всего документов: {self._count_documents()}")
    
    def _init_knowledge_base(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Инициализация базы знаний
        В реальном проекте здесь будет подключение к Elasticsearch, Pinecone и т.д.
        """
        return {
            "kubernetes": [
                {
                    "title": "Что такое Kubernetes?",
                    "content": "Kubernetes (K8s) - это платформа с открытым исходным кодом для автоматизации развертывания, масштабирования и управления контейнеризированными приложениями.",
                    "tags": ["контейнеры", "оркестрация", "devops"],
                    "source": "Официальная документация",
                    "date": "2024-01-15"
                },
                {
                    "title": "Основные компоненты Kubernetes",
                    "content": "Ключевые компоненты: Pods (минимальная единица), Services (сетевое взаимодействие), Deployments (управление версиями), Ingress (входящий трафик), ConfigMaps (конфигурация), Secrets (секреты).",
                    "tags": ["компоненты", "архитектура"],
                    "source": "Kubernetes Documentation",
                    "date": "2024-02-20"
                },
                {
                    "title": "Minikube для локальной разработки",
                    "content": "Minikube - инструмент для запуска Kubernetes локально. Позволяет тестировать кластер на одной машине, идеален для разработки и обучения.",
                    "tags": ["minikube", "локальная разработка"],
                    "source": "Minikube Docs",
                    "date": "2024-03-01"
                }
            ],
            "langgraph": [
                {
                    "title": "Что такое LangGraph?",
                    "content": "LangGraph - библиотека для создания графовых LLM приложений с управлением состоянием. Позволяет строить сложные агентные системы с циклами, ветвлениями и человеко-машинным взаимодействием.",
                    "tags": ["библиотека", "агенты", "графы"],
                    "source": "LangGraph Documentation",
                    "date": "2024-01-10"
                },
                {
                    "title": "Основные концепции LangGraph",
                    "content": "Ключевые концепции: State (состояние) - данные между узлами; Nodes (узлы) - функции обработки; Edges (связи) - маршрутизация; Conditional Edges (условная маршрутизация); Checkpoints (сохранение состояния).",
                    "tags": ["концепции", "архитектура"],
                    "source": "LangGraph Tutorial",
                    "date": "2024-02-15"
                },
                {
                    "title": "Практическое применение LangGraph",
                    "content": "LangGraph используется для создания мультиагентных систем, RAG приложений, чат-ботов с памятью, автоматизации бизнес-процессов, анализа данных с несколькими этапами.",
                    "tags": ["применение", "use cases"],
                    "source": "LangGraph Examples",
                    "date": "2024-03-05"
                }
            ],
            "docker": [
                {
                    "title": "Что такое Docker?",
                    "content": "Docker - платформа для разработки, доставки и запуска приложений в контейнерах. Контейнеры изолируют приложения от окружения, обеспечивая воспроизводимость.",
                    "tags": ["контейнеры", "виртуализация"],
                    "source": "Docker Documentation",
                    "date": "2024-01-20"
                },
                {
                    "title": "Dockerfile и его инструкции",
                    "content": "Dockerfile описывает инструкции для сборки образа. Основные инструкции: FROM (базовый образ), WORKDIR (рабочая директория), COPY (копирование файлов), RUN (выполнение команд), CMD (команда по умолчанию), EXPOSE (порты).",
                    "tags": ["dockerfile", "сборка"],
                    "source": "Docker Guide",
                    "date": "2024-02-10"
                }
            ],
            "langchain": [
                {
                    "title": "LangChain Framework",
                    "content": "LangChain - фреймворк для разработки приложений на основе LLM. Предоставляет инструменты для работы с моделями, промптами, цепочками вызовов и векторными базами данных.",
                    "tags": ["framework", "llm"],
                    "source": "LangChain Docs",
                    "date": "2024-01-25"
                }
            ],
            "python": [
                {
                    "title": "Python для разработки агентов",
                    "content": "Python - основной язык для разработки AI-агентов. Используются библиотеки: asyncio (асинхронность), typing (типизация), dataclasses (структуры данных), pytest (тестирование).",
                    "tags": ["python", "разработка"],
                    "source": "Python Documentation",
                    "date": "2024-02-28"
                }
            ],
            "fastapi": [
                {
                    "title": "FastAPI для веб-сервисов",
                    "content": "FastAPI - современный веб-фреймворк для Python. Особенности: высокая производительность, автоматическая документация OpenAPI, валидация данных через Pydantic, асинхронная поддержка.",
                    "tags": ["fastapi", "веб-разработка"],
                    "source": "FastAPI Tutorial",
                    "date": "2024-03-10"
                }
            ]
        }
    
    def _count_documents(self) -> int:
        """Подсчет общего количества документов"""
        count = 0
        for category in self.knowledge_base.values():
            count += len(category)
        return count
    
    def _normalize_text(self, text: str) -> str:
        """Нормализация текста для поиска"""
        text = text.lower()
        # Удаляем знаки препинания
        text = re.sub(r'[^\w\s]', ' ', text)
        # Удаляем лишние пробелы
        text = ' '.join(text.split())
        return text
    
    def _search_by_keywords(self, query: str) -> List[Dict[str, Any]]:
        """
        Поиск по ключевым словам
        В реальном проекте здесь будет запрос к Elasticsearch
        """
        normalized_query = self._normalize_text(query)
        query_words = set(normalized_query.split())
        
        results = []
        
        for category, documents in self.knowledge_base.items():
            for doc in documents:
                # Поиск в заголовке и содержимом
                title_normalized = self._normalize_text(doc["title"])
                content_normalized = self._normalize_text(doc["content"])
                
                # Подсчет совпадений
                score = 0
                for word in query_words:
                    if word in title_normalized:
                        score += 3
                    if word in content_normalized:
                        score += 1
                    if any(word in tag for tag in doc.get("tags", [])):
                        score += 2
                
                if score > 0:
                    results.append({
                        "category": category,
                        "title": doc["title"],
                        "content": doc["content"],
                        "tags": doc.get("tags", []),
                        "source": doc.get("source", "Unknown"),
                        "score": score
                    })
        
        # Сортировка по релевантности
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5]  # Возвращаем топ-5 результатов
    
    def _generate_response(self, query: str, results: List[Dict[str, Any]]) -> str:
        """
        Генерация ответа на основе найденных документов
        В реальном проекте здесь будет вызов LLM (GigaChat, OpenAI и т.д.)
        """
        if not results:
            # Если ничего не найдено
            categories = ", ".join(self.knowledge_base.keys())
            return f"""По запросу "{query}" ничего не найдено.

Доступные темы: {categories}

💡 Совет: попробуйте уточнить запрос или спросить о конкретной технологии.
   Например: "Что такое Kubernetes?" или "Как работает LangGraph?" """
        
        # Формируем ответ
        response = f"📚 **Найдена информация по запросу:** \"{query}\"\n\n"
        
        for i, result in enumerate(results, 1):
            response += f"**{i}. {result['title']}** (категория: {result['category']})\n"
            response += f"{result['content']}\n"
            if result.get('tags'):
                response += f"Теги: {', '.join(result['tags'])}\n"
            response += f"Источник: {result['source']}\n\n"
        
        # Добавляем рекомендации
        response += "---\n"
        response += "**Рекомендации:**\n"
        
        # Рекомендуем похожие темы
        top_category = results[0]['category']
        other_categories = [c for c in self.knowledge_base.keys() if c != top_category]
        if other_categories:
            response += f"- Посмотрите также информацию по теме: {', '.join(other_categories[:2])}\n"
        
        response += "- Могу ответить на уточняющие вопросы\n"
        response += "- Могу найти информацию по другим технологиям\n"
        
        # Добавляем статистику
        response += f"\n**Статистика:** Найдено {len(results)} документов"
        
        return response
    
    def _save_to_history(self, query: str, response: str):
        """Сохранение в историю"""
        self.history.append({
            "query": query,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "results_count": len(self._search_by_keywords(query))
        })
        
        # Ограничиваем историю
        if len(self.history) > 100:
            self.history.pop(0)
    
    def _update_context(self, query: str, response: str):
        """Обновление контекста разговора"""
        self.context["last_query"] = query
        self.context["last_response"] = response
        self.context["timestamp"] = datetime.now().isoformat()
        
        # Извлекаем тему из запроса
        for category in self.knowledge_base.keys():
            if category in query.lower():
                self.context["current_topic"] = category
                break
    
    def process(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Основной метод обработки запроса
        
        Args:
            message: Текст запроса
            context: Контекст разговора (опционально)
        
        Returns:
            str: Ответ агента
        """
        # Сохраняем переданный контекст
        if context:
            self.context.update(context)
        
        # Поиск информации
        results = self._search_by_keywords(message)
        
        # Генерация ответа
        response = self._generate_response(message, results)
        
        # Сохраняем в историю
        self._save_to_history(message, response)
        
        # Обновляем контекст
        self._update_context(message, response)
        
        return response
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики работы агента"""
        return {
            "name": self.name,
            "version": self.version,
            "total_queries": len(self.history),
            "knowledge_base_size": len(self.knowledge_base),
            "total_documents": self._count_documents(),
            "categories": list(self.knowledge_base.keys()),
            "last_query": self.context.get("last_query", "Нет запросов"),
            "current_topic": self.context.get("current_topic", "Не определен")
        }
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Получение истории запросов"""
        return self.history[-limit:]
    
    def clear_history(self):
        """Очистка истории"""
        self.history = []
        self.context = {}
        print(f"История {self.name} очищена")


# Пример использования для тестирования
if __name__ == "__main__":
    print("Тестирование RAG Agent")
    
    agent = RAGAgent()
    
    # Тестовые запросы
    test_queries = [
        "Что такое Kubernetes?",
        "Расскажи про LangGraph",
        "Как работает Docker?",
        "Что такое Python?",
        "FastAPI для чего?"
    ]
    
    for query in test_queries:
        print(f"\nЗапрос: {query}")
        response = agent.process(query)
        print(f"Ответ:\n{response}")

    # Показываем статистику
    print("\nСтатистика работы:")
    stats = agent.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")