"""
SQL Agent - работа с базами данных
"""
import sqlite3
import re
from typing import List, Dict, Any, Optional, Tuple

class SQLAgent:
    def __init__(self, db_path: str = ":memory:"):
        self.name = "SQL Agent"
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.query_history = []
        self.allowed_operations = ["SELECT", "SHOW", "DESCRIBE", "EXPLAIN"]
        self.max_rows = 100
        self._create_sample_tables()
        print(f"✅ {self.name} инициализирован")
    
    def _create_sample_tables(self):
        cursor = self.connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, age INTEGER, city TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user_id INTEGER, product TEXT, amount REAL, status TEXT)")
        
        cursor.executemany("INSERT OR IGNORE INTO users (name, email, age, city) VALUES (?, ?, ?, ?)", [
            ("Иван Петров", "ivan@example.com", 25, "Москва"),
            ("Мария Сидорова", "maria@example.com", 30, "Санкт-Петербург"),
            ("Алексей Иванов", "alexey@example.com", 28, "Москва")
        ])
        
        cursor.executemany("INSERT OR IGNORE INTO orders (user_id, product, amount, status) VALUES (?, ?, ?, ?)", [
            (1, "Ноутбук", 75000, "completed"),
            (1, "Мышь", 1500, "completed"),
            (2, "Телефон", 50000, "pending")
        ])
        self.connection.commit()
    
    def _validate_query(self, query: str) -> Tuple[bool, str]:
        query_upper = query.strip().upper()
        operation = query_upper.split()[0] if query_upper else ""
        if operation not in self.allowed_operations:
            return False, f"Операция '{operation}' запрещена"
        dangerous = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE"]
        for word in dangerous:
            if word in query_upper:
                return False, f"Команда {word} запрещена"
        return True, ""
    
    def _execute_query(self, query: str):
        cursor = self.connection.cursor()
        cursor.execute(query)
        if query.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        return []
    
    def _format_results(self, results: List[Dict], query: str) -> str:
        if not results:
            return "Запрос выполнен. Результатов не найдено."
        response = f"Результаты запроса:\n```sql\n{query}\n```\n\n"
        response += f"Найдено строк: {len(results)}\n\n"
        if results:
            headers = list(results[0].keys())
            response += "| " + " | ".join(headers) + " |\n"
            response += "|" + "|".join(["---" for _ in headers]) + "|\n"
            for row in results[:10]:
                values = [str(row.get(h, "")) for h in headers]
                response += "| " + " | ".join(values) + " |\n"
        return response
    
    def _get_schema(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        schema = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table[0]})")
            schema[table[0]] = [col[1] for col in cursor.fetchall()]
        return schema
    
    def _generate_query_help(self) -> str:
        schema = self._get_schema()
        help_text = "SQL Agent - помощь\n\nДоступные таблицы:\n"
        for table, columns in schema.items():
            help_text += f"  {table}: {', '.join(columns)}\n"
        help_text += "\nПримеры:\n  SELECT * FROM users\n  SELECT * FROM users WHERE city = 'Москва'\n  SELECT city, COUNT(*) FROM users GROUP BY city\n  SHOW TABLES"
        return help_text
    
    def process(self, message: str, context: Optional[Dict] = None) -> str:
        message_lower = message.lower()
        if any(w in message_lower for w in ["помощь", "help"]):
            return self._generate_query_help()
        if any(w in message_lower for w in ["таблицы", "tables"]):
            return "Таблицы: " + ", ".join(self._get_schema().keys())
        
        match = re.search(r"(SELECT|SHOW|DESCRIBE|EXPLAIN).+", message, re.IGNORECASE)
        if match:
            query = match.group(0).strip()
            is_valid, error = self._validate_query(query)
            if not is_valid:
                return f"Ошибка: {error}"
            try:
                results = self._execute_query(query)
                return self._format_results(results, query)
            except Exception as e:
                return f"Ошибка: {e}"
        return self._generate_query_help()