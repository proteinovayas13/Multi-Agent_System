"""
Streamlit UI для LangGraph Agent
"""
import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# Настройка страницы
st.set_page_config(
    page_title="LangGraph Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API URL
API_URL = "http://localhost:8000"

# Стили
st.markdown("""
<style>
    .stChatMessage {
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
    }
    .user-message {
        background-color: #007bff;
        color: white;
    }
    .assistant-message {
        background-color: #28a745;
        color: white;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .agent-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        margin: 2px;
    }
    .agent-rag { background-color: #e3f2fd; color: #1976d2; }
    .agent-sql { background-color: #e8f5e9; color: #388e3c; }
    .agent-chat { background-color: #fff3e0; color: #f57c00; }
    .status-badge {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-active { background-color: #4caf50; box-shadow: 0 0 5px #4caf50; }
    .status-inactive { background-color: #9e9e9e; }
    .agent-item {
        padding: 5px 0;
        border-bottom: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Заголовок
st.title("🤖 LangGraph Agent Assistant")
st.markdown("---")

# Боковая панель
with st.sidebar:
    st.header("📊 Статус системы")
    
    # Проверка API
    api_connected = False
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            st.success("✅ API подключен")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Статус", health.get("status", "unknown"))
            with col2:
                st.metric("Агентов", health.get("agents", 0))
            api_connected = True
        else:
            st.error("❌ API не отвечает")
    except Exception as e:
        st.error(f"❌ Ошибка подключения: {e}")
        st.info("Убедитесь, что API запущен: kubectl port-forward service/langgraph-agent 8000:80 -n langgraph")
    
    st.markdown("---")
    
    # Список агентов
    st.header("🤖 Доступные агенты")
    
    # Список 3 агентов
    all_agents = {
        "rag": {"name": "RAG Agent", "desc": "📚 Поиск информации", "color": "agent-rag"},
        "sql": {"name": "SQL Agent", "desc": "🗄️ Работа с базой данных", "color": "agent-sql"},
        "chat": {"name": "Chat Agent", "desc": "💬 Диалоговый ассистент", "color": "agent-chat"}
    }
    
    # Получаем статус агентов из API
    agent_status = {}
    if api_connected:
        try:
            response = requests.get(f"{API_URL}/agents", timeout=5)
            if response.status_code == 200:
                api_agents = response.json()
                if isinstance(api_agents, dict):
                    for agent_name in api_agents.keys():
                        agent_status[agent_name.lower()] = "active"
        except Exception as e:
            pass
    
    # Отображаем агентов
    for agent_key, agent_info in all_agents.items():
        col1, col2 = st.columns([1, 20])
        with col1:
            st.markdown(f"<span class='status-badge status-{'active' if agent_key in agent_status else 'inactive'}'></span>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**{agent_info['name']}**")
        
        st.markdown(f"{agent_info['desc']}")
        st.markdown("---")
    
    st.markdown("---")
    
    # Статистика документов
    st.header("📚 База знаний")
    if api_connected:
        try:
            docs = requests.get(f"{API_URL}/documents", timeout=5).json()
            if isinstance(docs, dict) and "documents" in docs:
                doc_count = docs.get("count", 0)
            elif isinstance(docs, list):
                doc_count = len(docs)
            else:
                doc_count = 0
            st.metric("Всего документов", doc_count)
        except:
            st.metric("Всего документов", "?")
    else:
        st.metric("Всего документов", "?")
    
    st.markdown("---")
    
    # Примеры запросов
    st.header("💡 Примеры запросов")
    
    with st.expander("📚 RAG Agent"):
        st.markdown("- What is Kubernetes?")
        st.markdown("- Tell me about LangGraph")
        st.markdown("- What is Docker?")
        st.markdown("- Explain Python")
    
    with st.expander("🗄️ SQL Agent"):
        st.markdown("- SELECT * FROM users")
        st.markdown("- Show me all orders")
        st.markdown("- SELECT city, COUNT(*) FROM users GROUP BY city")
        st.markdown("- Show users from Moscow")
    
    with st.expander("💬 Chat Agent"):
        st.markdown("- Hello, how are you?")
        st.markdown("- What can you do?")
        st.markdown("- Help me")
        st.markdown("- Thank you")
    
    st.markdown("---")
    
    # Загрузка документов
    st.header("📤 Загрузить документ")
    uploaded_file = st.file_uploader("Выберите файл", type=['txt', 'pdf', 'docx'])
    if uploaded_file is not None:
        if st.button("Загрузить", use_container_width=True):
            with st.spinner("Загрузка..."):
                files = {"file": uploaded_file}
                try:
                    response = requests.post(f"{API_URL}/upload", files=files, timeout=30)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Файл загружен: {result.get('filename')}")
                        st.info(f"Размер: {result.get('size')} байт, Текст: {result.get('text_length')} символов")
                    else:
                        st.error(f"❌ Ошибка: {response.text}")
                except Exception as e:
                    st.error(f"❌ Ошибка загрузки: {e}")

# Основная область - чат
st.header("💬 Чат с ассистентом")

# Инициализация истории сообщений
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm LangGraph Assistant. I have 3 specialized agents:\n\n📚 **RAG Agent** - search for information\n🗄️ **SQL Agent** - work with databases\n💬 **Chat Agent** - conversation\n\nHow can I help you today?"}
    ]
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

# Отображение истории
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Обработка ввода
if prompt := st.chat_input("Enter your message..."):
    # Добавляем сообщение пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Отправляем запрос к API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "message": prompt,
                        "session_id": st.session_state.session_id
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    answer = response.json().get("response", "No response")
                else:
                    answer = f"Error: {response.status_code}"
            except Exception as e:
                answer = f"Error: {e}"
            
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
    
    # Ограничиваем историю
    if len(st.session_state.messages) > 50:
        st.session_state.messages = st.session_state.messages[-50:]

# Footer
st.markdown("---")
st.markdown("🚀 LangGraph Agent | Powered by LangGraph + Elasticsearch + Kubernetes | 3 Agents: RAG, SQL, Chat")