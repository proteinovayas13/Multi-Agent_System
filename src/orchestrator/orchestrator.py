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
        print("Оркестратор инициализирован")
        print(f"Доступные агенты: {', '.join(self.agents.keys())}")
    
    def _detect_intent(self, message: str):
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["kubernetes", "docker", "langgraph", "python", "что такое", "расскажи", "найди"]):
            return ("rag", 0.9)
        elif any(word in message_lower for word in ["select", "users", "orders", "таблица", "данные", "sql"]):
            return ("sql", 0.9)
        else:
            return ("chat", 0.5)
    
    def _route(self, state):
        last_message = state["messages"][-1] if state["messages"] else ""
        intent, confidence = self._detect_intent(last_message)
        print(f"Определено намерение: {intent} (уверенность: {confidence:.2f})")
        return intent
    
    def _call_agent(self, state):
        agent_name = state.get("current_agent", "")
        
        if not agent_name:
            last_message = state["messages"][-1] if state["messages"] else ""
            agent_name, _ = self._detect_intent(last_message)
        
        agent = self.agents.get(agent_name)
        
        if not agent:
            return {
                "messages": [f"Агент {agent_name} не найден"],
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
                "messages": [f"Ошибка в агенте {agent_name}: {str(e)}"],
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
        print(f"Определено намерение: {intent} (уверенность: {confidence:.2f})")
        
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
    print("LangGraph Orchestrator - Тестирование")

    test_messages = [
        "Найди информацию про Kubernetes",
        "SELECT * FROM users",
        "Привет, как дела?"
    ]
    
    for msg in test_messages:
        print(f"\nПользователь: {msg}")
        response = orchestrator.process(msg, session_id="test")
        print(f"Ассистент: {response}")
    
    print("\nСтатус агентов:")
    print(orchestrator.get_agents_status())