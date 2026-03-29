from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
import random

# ШАГ 1: ОПРЕДЕЛЕНИЕ STATE (СОСТОЯНИЯ)

class MyState(TypedDict):
    """Состояние нашего графа."""
    user_name: str           # Имя пользователя
    mood: str                # Настроение (будет определяться)
    message: str             # Сообщение для вывода
    step_count: int          # Счетчик шагов

# ШАГ 2: ОПРЕДЕЛЕНИЕ NODES (УЗЛОВ)

def node_greet(state: MyState) -> dict:
    """Узел 1: Приветствие."""
    print("--- Node: GREET ---")
    name = state.get("user_name", "Гость")
    return {
        "message": f"Привет, {name}!",
        "step_count": state.get("step_count", 0) + 1
    }

def node_decide_mood(state: MyState) -> dict:
    """Узел 2: Определение настроения (имитация LLM)."""
    print("--- Node: DECIDE MOOD ---")
    # В реальном агенте здесь был бы вызов LLM
    moods = ["счастливый", "грустный", "задумчивый", "энергичный"]
    chosen_mood = random.choice(moods)
    return {
        "mood": chosen_mood,
        "message": f"Я чувствую себя {chosen_mood}",
        "step_count": state["step_count"] + 1
    }

def node_response_happy(state: MyState) -> dict:
    """Узел 3A: Реакция на счастливое настроение."""
    print("--- Node: HAPPY RESPONSE ---")
    return {
        "message": f"{state['message']} 🎉 Отлично! Давай творить!",
        "step_count": state["step_count"] + 1
    }

def node_response_sad(state: MyState) -> dict:
    """Узел 3B: Реакция на грустное настроение."""
    print("--- Node: SAD RESPONSE ---")
    return {
        "message": f"{state['message']} 🌧️ Не переживай, всё наладится!",
        "step_count": state["step_count"] + 1
    }

def node_response_default(state: MyState) -> dict:
    """Узел 3C: Реакция на остальные настроения."""
    print("--- Node: DEFAULT RESPONSE ---")
    return {
        "message": f"{state['message']} 🤔 Интересное настроение!",
        "step_count": state["step_count"] + 1
    }

# ШАГ 3: ОПРЕДЕЛЕНИЕ CONDITIONAL EDGE (УСЛОВНОГО РЕБРА)

def route_by_mood(state: MyState) -> Literal["node_happy", "node_sad", "node_default"]:
    """
    Определяет следующий узел на основе настроения.
    Возвращает строку — имя узла для перехода.
    """
    mood = state.get("mood", "default")
    
    if mood == "счастливый":
        return "node_happy"
    elif mood == "грустный":
        return "node_sad"
    else:
        return "node_default"

# ШАГ 4: ПОСТРОЕНИЕ ГРАФА

def build_graph():
    """Строит и компилирует граф."""
    
    # Создаем граф с нашим состоянием
    builder = StateGraph(MyState)
    
    # Добавляем узлы
    builder.add_node("node_greet", node_greet)
    builder.add_node("node_decide_mood", node_decide_mood)
    builder.add_node("node_happy", node_response_happy)
    builder.add_node("node_sad", node_response_sad)
    builder.add_node("node_default", node_response_default)
    
    # Добавляем ребра
    builder.add_edge(START, "node_greet")           # START → приветствие
    builder.add_edge("node_greet", "node_decide_mood")  # приветствие → решение
    
    # Условное ребро: от решения к одному из трех узлов
    builder.add_conditional_edges(
        "node_decide_mood",    # исходный узел
        route_by_mood,         # функция-маршрутизатор
        {
            "node_happy": "node_happy",
            "node_sad": "node_sad", 
            "node_default": "node_default"
        }
    )
    
    # Все конечные узлы ведут в END
    builder.add_edge("node_happy", END)
    builder.add_edge("node_sad", END)
    builder.add_edge("node_default", END)
    
    # Компилируем граф
    graph = builder.compile()
    return graph

# ЗАПУСК

if __name__ == "__main__":
    print("=" * 50)
    print("Первый LangGraph Agent")
    print("=" * 50)
    
    # Строим граф
    agent = build_graph()
    
    # Выводим информацию о графе
    print(f"Граф построен!")
    print(f"Доступные узлы: {[node for node in agent.get_graph().nodes]}")
    
    # Запускаем с разными входами
    test_inputs = [
        {"user_name": "Алексей"},
        {"user_name": "Мария"},
        {"user_name": "Дмитрий"}
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n{'=' * 40}")
        print(f"Запуск {i}")
        print(f"{'=' * 40}")
        result = agent.invoke(user_input)
        print(f"\nИтоговое сообщение: {result['message']}")
        print(f"Шагов выполнено: {result['step_count']}")
        print(f"Настроение: {result.get('mood', 'не определено')}")