import pytest
from src.agents.rag_agent import RAGAgent
from src.agents.sql_agent import SQLAgent
from src.agents.chat_agent import ChatAgent

def test_rag_agent():
    agent = RAGAgent()
    response = agent.process("What is Kubernetes?")
    assert "Kubernetes" in response

def test_sql_agent():
    agent = SQLAgent()
    response = agent.process("SELECT * FROM users")
    assert "users" in response.lower()

def test_chat_agent():
    agent = ChatAgent()
    response = agent.process("Hello")
    assert response is not None