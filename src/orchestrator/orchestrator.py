"""
Главный оркестратор на LangGraph
Управляет маршрутизацией между специализированными агентами
"""
from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.rag_agent import RAGAgent
from src.agents.sql_agent import SQLAgent
from src.agents.chat_agent import ChatAgent

class OrchestratorState(TypedDict):
    messages: Annotated[list, operator.add]
    current_agent: str
    context: dict
    user_id: str
    session_id: str
    intent: str
    confidence: float

class Orchestrator:
    def __init__(self):
        self.agents = {
            "rag": RAGAgent(),
            "sql": SQLAgent(),
            "chat": ChatAgent()
        }
        self.graph = self._build_graph()
        print("✅ Оркестратор инициализирован")
        print(f"📦 Доступные агенты: {', '.join(self.agents.keys())}")
    
    def _detect_intent(self, message: str):
        message_lower = message.lower()
        
        # === ЗАПРОСЫ ДЛЯ SQL AGENT (РАСШИРЕННЫЙ СПИСОК) ===
        sql_keywords = [
            # SQL команды
            "select", "insert", "update", "delete", "create", "drop", "alter",
            "from", "where", "join", "group by", "order by", "sql", "база",
            "данные", "таблица", "пользователь", "заказ", "users", "orders",
            "покажи", "выведи", "найди в бд", "запрос",
            # Русские фразы для SQL
            "сколько", "пользователей", "в москве", "в санкт-петербурге",
            "пользователи из", "список пользователей", "город", "города",
            "статистика", "количество", "подсчет", "посчитать",
            "топ", "лучшие", "самые", "максимальный", "минимальный",
            "средний", "сумма", "итого", "всего", "пользователь",
            "заказы", "заказ", "товар", "продукт", "продажи"
        ]
        
        # === ВОПРОСЫ ДЛЯ RAG AGENT ===
        rag_keywords = [
            "kubernetes", "docker", "langgraph", "python", "fastapi", "postgresql",
            "elasticsearch", "prometheus", "grafana", "kibana",
            "что такое", "расскажи", "найди", "поиск", "информация", "документация",
            "как запустить", "как работает", "как установить", "как настроить",
            "где посмотреть", "где найти", "где логи", "где документация",
            "как добавить", "как создать", "как удалить", "как обновить",
            "технологии", "стек", "архитектура", "команды", "настройка",
            "проект", "система", "приложение", "агенты", "оркестрация",
            "ошибка", "проблема", "не работает", "помощь", "вопрос", "ответ",
            "запустить", "старт", "run", "start", "деплой", "развернуть",
            "отчет", "report", "дашборд", "dashboard", "графана"
        ]
        
        # === ОБЫЧНЫЕ ДИАЛОГИ ДЛЯ CHAT AGENT ===
        chat_keywords = [
            "привет", "здравствуй", "добрый день", "hello", "hi",
            "как дела", "что нового", "пока", "до свидания", "bye",
            "спасибо", "thanks", "помощь", "help", "что ты умеешь"
        ]
        
        # Проверяем приоритетность: сначала SQL (бизнес-запросы), потом RAG, потом Chat
        if any(word in message_lower for word in sql_keywords):
            return ("sql", 0.95)
        elif any(word in message_lower for word in rag_keywords):
            return ("rag", 0.9)
        else:
            return ("chat", 0.5)
    
    def _route(self, state):
        last_message = state["messages"][-1] if state["messages"] else ""
        intent, confidence = self._detect_intent(last_message)
        print(f"🎯 Определено намерение: {intent} (уверенность: {confidence:.2f})")
        return intent
    
    def _call_agent(self, state):
        agent_name = state.get("current_agent", "")
        
        if not agent_name:
            last_message = state["messages"][-1] if state["messages"] else ""
            agent_name, _ = self._detect_intent(last_message)
        
        agent = self.agents.get(agent_name)
        
        if not agent:
            return {
                "messages": [f"❌ Агент {agent_name} не найден"],
                "context": state.get("context", {})
            }
        
        last_message = state["messages"][-1] if state["messages"] else ""
        
        try:
            response = agent.process(last_message, state.get("context", {}))
            context = state.get("context", {})
            context["last_agent"] = agent_name
            
            return {
                "messages": [response],
                "context": context,
                "current_agent": agent_name
            }
        except Exception as e:
            return {
                "messages": [f"⚠️ Ошибка в агенте {agent_name}: {str(e)}"],
                "context": state.get("context", {}),
                "current_agent": agent_name
            }
    
    def _build_graph(self):
        graph = StateGraph(OrchestratorState)
        
        graph.add_node("route", self._route_and_set_agent)
        graph.add_node("rag", self._call_agent)
        graph.add_node("sql", self._call_agent)
        graph.add_node("chat", self._call_agent)
        
        graph.add_edge(START, "route")
        
        graph.add_conditional_edges(
            "route",
            lambda x: x.get("intent", "chat"),
            {
                "rag": "rag",
                "sql": "sql",
                "chat": "chat"
            }
        )
        
        graph.add_edge("rag", END)
        graph.add_edge("sql", END)
        graph.add_edge("chat", END)
        
        memory = MemorySaver()
        return graph.compile(checkpointer=memory)
    
    def _route_and_set_agent(self, state):
        last_message = state["messages"][-1] if state["messages"] else ""
        intent, confidence = self._detect_intent(last_message)
        print(f"🎯 Определено намерение: {intent} (уверенность: {confidence:.2f})")
        
        return {
            "intent": intent,
            "confidence": confidence,
            "current_agent": intent
        }
    
    def process(self, message: str, session_id: str = "default", user_id: str = "anonymous"):
        config = {"configurable": {"thread_id": f"{user_id}_{session_id}"}}
        
        result = self.graph.invoke(
            {
                "messages": [message],
                "current_agent": "",
                "context": {},
                "user_id": user_id,
                "session_id": session_id,
                "intent": "",
                "confidence": 0.0
            },
            config=config
        )
        
        return result["messages"][-1] if result["messages"] else "Нет ответа"
    
    def get_agents_status(self):
        status = {}
        for name, agent in self.agents.items():
            status[name] = {
                "available": True,
                "type": agent.__class__.__name__
            }
        return status

orchestrator = Orchestrator()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 LangGraph Orchestrator - Тестирование")
    print("="*60)
    
    test_messages = [
        "Как запустить проект?",
        "Где посмотреть логи?",
        "Какие технологии используются?",
        "Как добавить нового агента?",
        "Что такое Kubernetes?",
        "SELECT * FROM users",
        "Пользователи из Санкт-Петербурга",
        "Сколько пользователей в Москве?",
        "Покажи все заказы",
        "Привет, как дела?"
    ]
    
    for msg in test_messages:
        print(f"\n💬 Пользователь: {msg}")
        response = orchestrator.process(msg, session_id="test")
        print(f"🤖 Ассистент: {response}")
        print("-" * 50)
    
    print("\n📊 Статус агентов:")
    print(orchestrator.get_agents_status())