"""
Модели данных для работы с базой данных
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ChatHistory(Base):
    """Модель для хранения истории чатов"""
    __tablename__ = 'chat_history'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(50))
    user_id = Column(String(50))
    message = Column(Text)
    response = Column(Text)
    agent_used = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class AgentMetrics(Base):
    """Модель для хранения метрик агентов"""
    __tablename__ = 'agent_metrics'
    
    id = Column(Integer, primary_key=True)
    agent_name = Column(String(50))
    query = Column(Text)
    response_time = Column(Float)  # в секундах
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

# Для тестирования
if __name__ == "__main__":
    # Создаем SQLite базу данных
    engine = create_engine('sqlite:///langgraph.db')
    Base.metadata.create_all(engine)
    print("✅ База данных создана: langgraph.db")me, default=datetime.utcnow)