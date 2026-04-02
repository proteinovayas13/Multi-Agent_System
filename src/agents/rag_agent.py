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
    """
    
    def __init__(self):
        self.name = "RAG Agent"
        self.version = "2.0.0"
        self.history = []
        self.context = {}
        self.knowledge_base = self._init_knowledge_base()
        
        print(f"✅ {self.name} v{self.version} инициализирован")
        print(f"📚 Загружено тем: {len(self.knowledge_base)}")
        print(f"📄 Всего документов: {self._count_documents()}")
    
    def _init_knowledge_base(self) -> Dict[str, List[Dict[str, Any]]]:
        """Инициализация базы знаний"""
        return {
            "how_to_run": [
                {
                    "title": "Как запустить проект локально",
                    "content": "1. Активировать виртуальное окружение: .\\langgraph-env\\Scripts\\Activate.ps1\n2. Запустить API: python src/api.py\n3. Запустить UI: streamlit run streamlit_app.py\n4. Открыть браузер: http://localhost:8000/docs и http://localhost:8501",
                    "tags": ["запуск", "локально", "инструкция", "как", "start", "run"],
                    "source": "Документация проекта"
                },
                {
                    "title": "Как запустить через Docker",
                    "content": "Команды:\n- docker-compose up -d (запуск всех сервисов)\n- docker-compose down -v (остановка)\n- docker ps (проверка статуса)\n\nСервисы:\n- PostgreSQL: порт 5432\n- Elasticsearch: порт 9200\n- Grafana: порт 3000\n- Kibana: порт 5601\n- Prometheus: порт 9090",
                    "tags": ["docker", "запуск", "контейнеры", "как"],
                    "source": "Документация проекта"
                }
            ],
            "commands": [
                {
                    "title": "Полезные команды для разработки",
                    "content": "Команды:\n- Активация окружения: .\\langgraph-env\\Scripts\\Activate.ps1\n- Запуск API: python src/api.py\n- Запуск UI: streamlit run streamlit_app.py\n- Установка зависимостей: pip install -r requirements.txt",
                    "tags": ["команды", "разработка", "dev", "commands"],
                    "source": "Документация проекта"
                },
                {
                    "title": "Kubernetes команды",
                    "content": "Команды:\n- Просмотр подов: kubectl get pods -n langgraph\n- Логи: kubectl logs -f -l app=langgraph-agent -n langgraph\n- Перезапуск: kubectl rollout restart deployment langgraph-agent -n langgraph\n- Масштабирование: kubectl scale deployment langgraph-agent --replicas=3 -n langgraph",
                    "tags": ["kubectl", "kubernetes", "команды"],
                    "source": "Документация проекта"
                }
            ],
            "faq": [
                {
                    "title": "Как добавить нового агента?",
                    "content": "1. Создать файл в src/agents/ (например, new_agent.py)\n2. Реализовать класс с методом process(message, context)\n3. Добавить импорт в orchestrator.py\n4. Добавить агент в словарь self.agents\n5. Обновить метод _detect_intent для маршрутизации",
                    "tags": ["faq", "агенты", "добавление", "как"],
                    "source": "Документация проекта"
                },
                {
                    "title": "Где посмотреть логи?",
                    "content": "Логи:\n- API: kubectl logs -f -l app=langgraph-agent -n langgraph\n- PostgreSQL: docker logs postgres\n- Elasticsearch: docker logs elasticsearch\n- Grafana: docker logs grafana",
                    "tags": ["faq", "логи", "отладка", "где"],
                    "source": "Документация проекта"
                }
            ],
            "project": [
                {
                    "title": "Технологический стек проекта",
                    "content": "Технологии: LangGraph, FastAPI, Streamlit, PostgreSQL, Elasticsearch, Kubernetes, Prometheus, Grafana, Docker",
                    "tags": ["технологии", "стек", "какие"],
                    "source": "Документация проекта"
                }
            ],
            "kubernetes": [
                {
                    "title": "Что такое Kubernetes?",
                    "content": "Kubernetes (K8s) - платформа для автоматизации развертывания, масштабирования и управления контейнерами.",
                    "tags": ["kubernetes", "k8s", "что", "такое"],
                    "source": "Документация"
                }
            ],
            "langgraph": [
                {
                    "title": "Что такое LangGraph?",
                    "content": "LangGraph - библиотека для создания графовых LLM приложений с управлением состоянием.",
                    "tags": ["langgraph", "что", "такое"],
                    "source": "Документация"
                }
            ]
        }
    
    def _count_documents(self) -> int:
        count = 0
        for category in self.knowledge_base.values():
            count += len(category)
        return count
    
    def _normalize_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = ' '.join(text.split())
        return text
    
    def _search_by_keywords(self, query: str) -> List[Dict[str, Any]]:
        """Расширенный поиск по ключевым словам"""
        normalized_query = self._normalize_text(query)
        query_words = set(normalized_query.split())
        
        results = []
        
        for category, documents in self.knowledge_base.items():
            for doc in documents:
                title_normalized = self._normalize_text(doc["title"])
                content_normalized = self._normalize_text(doc["content"])
                
                score = 0
                for word in query_words:
                    if word in title_normalized:
                        score += 5
                    if word in content_normalized:
                        score += 2
                    if any(word in tag for tag in doc.get("tags", [])):
                        score += 3
                
                # Специальные проверки для частых запросов
                if "запустить" in normalized_query and category == "how_to_run":
                    score += 10
                if "команды" in normalized_query and category == "commands":
                    score += 10
                if "логи" in normalized_query and category == "faq":
                    score += 10
                if "технологии" in normalized_query and category == "project":
                    score += 10
                
                if score > 0:
                    results.append({
                        "category": category,
                        "title": doc["title"],
                        "content": doc["content"],
                        "tags": doc.get("tags", []),
                        "source": doc.get("source", "Unknown"),
                        "score": score
                    })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5]
    
    def _generate_response(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Генерация ответа"""
        if not results:
            return f"""🔍 По запросу "{query}" ничего не найдено.

💡 Попробуйте спросить:
   - "Как запустить проект?"
   - "Какие технологии используются?"
   - "Где посмотреть логи?"
   - "Как добавить нового агента?"
   - "Что такое Kubernetes?" """
        
        response = f"📚 **{results[0]['title']}**\n\n"
        response += f"{results[0]['content']}\n\n"
        
        if len(results) > 1:
            response += f"📌 **Дополнительно:**\n"
            for r in results[1:3]:
                response += f"• {r['title']}\n"
        
        return response
    
    def process(self, message: str, context: Optional[Dict] = None) -> str:
        """Основной метод обработки запроса"""
        if context:
            self.context.update(context)
        
        results = self._search_by_keywords(message)
        response = self._generate_response(message, results)
        
        self.history.append({
            "query": message,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(self.history) > 100:
            self.history.pop(0)
        
        return response
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "total_queries": len(self.history),
            "total_documents": self._count_documents()
        }


if __name__ == "__main__":
    agent = RAGAgent()
    
    test_queries = [
        "Как запустить проект?",
        "Какие технологии используются?",
        "Где посмотреть логи?",
        "Как добавить нового агента?",
        "Что такое Kubernetes?"
    ]
    
    for query in test_queries:
        print(f"\n📝 Запрос: {query}")
        print(f"🤖 Ответ:\n{agent.process(query)}")