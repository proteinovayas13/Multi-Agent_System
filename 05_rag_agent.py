"""
RAG-агент с использованием LangGraph
Простой пример без сложных векторных хранилищ
"""
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Dict
import json

class RAGState(TypedDict):
    question: str
    documents: List[Dict]
    answer: str
    context: Dict

# База знаний (в реальном проекте здесь будет Elasticsearch)
KNOWLEDGE_BASE = {
    "анализ данных": [
        "Анализ данных включает 5 этапов: сбор, очистка, исследование, моделирование, интерпретация",
        "Для анализа данных используются библиотеки: pandas, numpy, scikit-learn, matplotlib",
        "EDA (Exploratory Data Analysis) - важный этап для понимания структуры данных"
    ],
    "архитектура": [
        "Архитектура системы: пользователь → оркестратор (LangGraph) → агенты → базы данных",
        "LangGraph обеспечивает управление состоянием и маршрутизацию между агентами",
        "Kubernetes используется для оркестрации контейнеров и масштабирования"
    ],
    "агент": [
        "Агенты - это автономные компоненты, выполняющие специализированные задачи",
        "В LangGraph агенты представлены как узлы графа с четко определенными функциями",
        "Агенты могут использовать различные инструменты: поиск, SQL, API, файловую систему"
    ],
    "langgraph": [
        "LangGraph - библиотека для создания графовых LLM приложений с управлением состоянием",
        "Основные концепции: State (состояние), Nodes (узлы), Edges (связи), Conditional Edges",
        "LangGraph поддерживает циклы, ветвления и человеко-машинное взаимодействие"
    ],
    "kubernetes": [
        "Kubernetes - платформа для оркестрации контейнеров",
        "Основные компоненты: Pods, Services, Deployments, Ingress",
        "Minikube используется для локального развертывания Kubernetes"
    ],
    "docker": [
        "Docker - платформа для контейнеризации приложений",
        "Dockerfile описывает инструкции для сборки образа",
        "Контейнеры обеспечивают изоляцию и воспроизводимость окружения"
    ]
}

def retrieve_documents(state: RAGState):
    """Поиск релевантных документов в базе знаний"""
    question = state["question"].lower()
    documents = []
    context = {}
    
    # Простой поиск по ключевым словам
    for topic, docs in KNOWLEDGE_BASE.items():
        if topic in question or any(word in question for word in topic.split()):
            for doc in docs:
                documents.append({
                    "topic": topic,
                    "content": doc,
                    "relevance": 1.0
                })
            context[topic] = len(docs)
    
    # Если ничего не найдено, добавляем общую информацию
    if not documents:
        documents.append({
            "topic": "general",
            "content": "Я могу ответить на вопросы по темам: " + ", ".join(KNOWLEDGE_BASE.keys()),
            "relevance": 0.5
        })
    
    print(f"🔍 Найдено документов: {len(documents)}")
    return {"documents": documents, "context": context}

def generate_answer(state: RAGState):
    """Генерация ответа на основе найденных документов"""
    if not state["documents"]:
        answer = "Извините, не нашел информации по вашему вопросу."
    else:
        answer = "📚 **Найденная информация:**\n\n"
        for i, doc in enumerate(state["documents"], 1):
            answer += f"{i}. **{doc['topic'].upper()}**: {doc['content']}\n\n"
        
        # Добавляем контекст
        if state.get("context"):
            answer += f"\n📊 **Статистика поиска:** Найдено в {len(state['context'])} категориях\n"
    
    return {"answer": answer}

# Строим граф
def create_rag_agent():
    """Создание RAG агента"""
    graph = StateGraph(RAGState)
    
    # Добавляем узлы
    graph.add_node("retrieve", retrieve_documents)
    graph.add_node("generate", generate_answer)
    
    # Добавляем связи
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    
    return graph.compile()

# Функция для интерактивного режима
def interactive_mode():
    """Интерактивный режим работы с агентом"""
    agent = create_rag_agent()
    print("="*60)
    print("🤖 RAG Agent - Интерактивный режим")
    print("="*60)
    print("Введите 'exit' или 'quit' для выхода")
    print("Введите 'help' для списка доступных тем")
    print("-"*60)
    
    while True:
        try:
            question = input("\n💬 Ваш вопрос: ").strip()
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("👋 До свидания!")
                break
            elif question.lower() == 'help':
                print("\n📚 Доступные темы:")
                for topic in KNOWLEDGE_BASE.keys():
                    print(f"  • {topic}")
                continue
            elif not question:
                continue
            
            print("\n🤔 Думаю...")
            result = agent.invoke({"question": question})
            print(f"\n✅ Ответ:\n{result['answer']}")
            
        except KeyboardInterrupt:
            print("\n\n👋 До свидания!")
            break
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

if __name__ == "__main__":
    import sys
    
    print("="*60)
    print("RAG Agent Demo")
    print("="*60)
    
    # Тестовые вопросы
    test_questions = [
        "Что такое анализ данных?",
        "Расскажи об архитектуре LangGraph",
        "Как работают агенты?",
        "Что такое Kubernetes?",
        "Расскажи про Docker"
    ]
    
    agent = create_rag_agent()
    
    print("\n📝 Тестовые запросы:\n")
    for i, q in enumerate(test_questions, 1):
        print(f"{i}. {q}")
        result = agent.invoke({"question": q})
        print(f"   {result['answer'].split(chr(10))[0]}...")
        print()
    
    print("-"*60)
    print("Запустить интерактивный режим? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice in ['y', 'yes', 'да', 'д']:
        interactive_mode()