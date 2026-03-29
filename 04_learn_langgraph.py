"""
Учимся работать с LangGraph
Концепции: граф, состояния, узлы, conditional edges, циклы
"""
from typing import TypedDict, Annotated, Literal
import operator
from langgraph.graph import StateGraph, START, END
# Исправленный импорт - в новых версиях MemorySaver в другом месте
from langgraph.checkpoint.memory import MemorySaver
import random

# 1. Определяем состояние (state) - память агента
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]  # история сообщений
    step: str  # текущий шаг
    user_goal: str  # цель пользователя
    attempts: int  # количество попыток
    success: bool  # успешно ли выполнено

# 2. Создаем узлы (nodes) - функции, которые обрабатывают состояние
def understand_goal(state: AgentState):
    """Понять цель пользователя"""
    user_input = state["messages"][-1] if state["messages"] else ""
    
    # Простая логика определения цели
    if "анализ" in user_input.lower():
        goal = "analysis"
    elif "данные" in user_input.lower():
        goal = "data_query"
    elif "отчет" in user_input.lower():
        goal = "report"
    else:
        goal = "general"
    
    print(f"[1] Понимаю цель: {goal}")
    return {
        "user_goal": goal,
        "step": "understanding_done",
        "attempts": state.get("attempts", 0) + 1
    }

def analyze(state: AgentState):
    """Аналитический агент"""
    print(f"[2] Выполняю анализ данных...")
    return {
        "messages": ["Анализ завершен: найдено 42 инсайта"],
        "step": "analysis_done"
    }

def query_data(state: AgentState):
    """Агент запроса данных"""
    print(f"[3] Запрашиваю данные из SQL...")
    return {
        "messages": ["Данные получены: 1,234 записи"],
        "step": "query_done"
    }

def generate_report(state: AgentState):
    """Агент генерации отчетов"""
    print(f"[4] Генерирую отчет...")
    return {
        "messages": ["Отчет сгенерирован в формате PDF"],
        "step": "report_done"
    }

def general_chat(state: AgentState):
    """Обычный чат"""
    print(f"[5] Отвечаю как обычный ассистент...")
    return {
        "messages": ["Я могу помочь с анализом данных, запросами или отчетами"],
        "step": "general_done"
    }

def validate_result(state: AgentState):
    """Проверить результат"""
    print(f"[6] Проверяю результат...")
    if state.get("attempts", 0) < 3:
        return {"success": True, "step": "validated"}
    else:
        return {"success": False, "step": "failed"}

# 3. Определяем conditional edges - маршрутизация на основе состояния
def route_based_on_goal(state: AgentState) -> Literal["analyze", "query_data", "generate_report", "general_chat"]:
    """Маршрутизация на основе цели пользователя"""
    goal = state.get("user_goal", "general")
    
    routing = {
        "analysis": "analyze",
        "data_query": "query_data", 
        "report": "generate_report",
        "general": "general_chat"
    }
    return routing.get(goal, "general_chat")

def should_retry(state: AgentState) -> Literal["understand_goal", "validate_result"]:
    """Нужно ли повторить попытку?"""
    if not state.get("success", False) and state.get("attempts", 0) < 3:
        print(f"⚠️ Попытка {state['attempts']}/3 не удалась, повторяем...")
        return "understand_goal"
    return "validate_result"

# 4. Строим граф
def build_agent_graph():
    # Создаем граф с состоянием
    graph = StateGraph(AgentState)
    
    # Добавляем узлы
    graph.add_node("understand_goal", understand_goal)
    graph.add_node("analyze", analyze)
    graph.add_node("query_data", query_data)
    graph.add_node("generate_report", generate_report)
    graph.add_node("general_chat", general_chat)
    graph.add_node("validate_result", validate_result)
    
    # Добавляем связи
    graph.add_edge(START, "understand_goal")
    
    # Conditional edge: после понимания цели выбираем агента
    graph.add_conditional_edges(
        "understand_goal",
        route_based_on_goal,
        {
            "analyze": "analyze",
            "query_data": "query_data", 
            "generate_report": "generate_report",
            "general_chat": "general_chat"
        }
    )
    
    # После работы агента проверяем результат
    graph.add_edge("analyze", "validate_result")
    graph.add_edge("query_data", "validate_result")
    graph.add_edge("generate_report", "validate_result")
    graph.add_edge("general_chat", "validate_result")
    
    # Если не успешно - повторяем
    graph.add_conditional_edges(
        "validate_result",
        should_retry,
        {
            "understand_goal": "understand_goal",
            "validate_result": END
        }
    )
    
    # Компилируем с памятью (checkpointer)
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)

# 5. Тестируем
if __name__ == "__main__":
    print("="*50)
    print("LangGraph Demo - Маршрутизация агентов")
    print("="*50)
    
    agent = build_agent_graph()
    
    # Тестовые запросы
    test_queries = [
        "Сделай анализ продаж",  # analysis
        "Дай данные по клиентам",  # data_query
        "Сформируй отчет",  # report
        "Как дела?"  # general
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Запрос {i}: '{query}' ---")
        
        # Важно: каждый запрос в отдельном потоке (разные thread_id)
        config = {"configurable": {"thread_id": f"session_{i}"}}
        
        result = agent.invoke(
            {"messages": [query]},
            config=config
        )
        
        print(f"✅ Успешно: {result['success']}")
        print(f"📝 Ответ: {result['messages'][-1] if result['messages'] else 'Нет ответа'}")
        print(f"🔄 Попыток: {result['attempts']}")