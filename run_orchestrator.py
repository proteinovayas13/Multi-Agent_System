#!/usr/bin/env python
"""
Запуск оркестратора из корневой директории
"""
import sys
import os

# Добавляем текущую директорию в путь
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("Запуск LangGraph Orchestrator")

try:
    from src.orchestrator.orchestrator import orchestrator
    
    # Тестовые сообщения
    test_messages = [
        "Найди информацию про Kubernetes",
        "Покажи пользователей из базы данных",
        "Привет, как дела?",
        "Что такое LangGraph?"
    ]
    
    for msg in test_messages:
        print(f"\nПользователь: {msg}")
        response = orchestrator.process(msg, session_id="test")
        print(f"Ассистент: {response}")
    
    print("\nСтатус агентов:")
    print(orchestrator.get_agents_status())
    
except Exception as e:
    print(f"\nОшибка: {e}")
    import traceback
    traceback.print_exc()