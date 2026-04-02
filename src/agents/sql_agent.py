"""
SQL Agent - работа с базами данных (поддерживает SELECT, INSERT, UPDATE, DELETE)
"""
import sqlite3
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

class SQLAgent:
    def __init__(self, db_path: str = ":memory:"):
        self.name = "SQL Agent"
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.query_history = []
        self.allowed_operations = ["SELECT", "INSERT", "UPDATE", "DELETE", "SHOW", "DESCRIBE", "EXPLAIN"]
        self.max_rows = 100
        self._create_sample_tables()
        print(f"✅ {self.name} инициализирован")
    
    def _create_sample_tables(self):
        """Создание тестовых таблиц с данными"""
        cursor = self.connection.cursor()
        
        # Таблица пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                age INTEGER,
                city TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица заказов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product TEXT NOT NULL,
                amount REAL,
                quantity INTEGER DEFAULT 1,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Добавляем тестовые данные
        sample_users = [
            ("Иван Петров", "ivan@example.com", 25, "Москва"),
            ("Мария Сидорова", "maria@example.com", 30, "Санкт-Петербург"),
            ("Алексей Иванов", "alexey@example.com", 28, "Москва"),
            ("Елена Смирнова", "elena@example.com", 35, "Казань"),
            ("Дмитрий Козлов", "dmitry@example.com", 32, "Новосибирск"),
            ("Анна Морозова", "anna@example.com", 27, "Екатеринбург"),
            ("Сергей Волков", "sergey@example.com", 40, "Москва"),
            ("Ольга Соколова", "olga@example.com", 29, "Санкт-Петербург")
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO users (name, email, age, city) VALUES (?, ?, ?, ?)",
            sample_users
        )
        
        sample_orders = [
            (1, "Ноутбук", 75000, 1, "completed"),
            (1, "Мышь", 1500, 2, "completed"),
            (2, "Телефон", 50000, 1, "pending"),
            (3, "Клавиатура", 3000, 1, "completed"),
            (4, "Монитор", 25000, 1, "shipped"),
            (5, "Наушники", 5000, 1, "pending"),
            (2, "Чехол", 1000, 3, "completed"),
            (1, "Планшет", 35000, 1, "shipped"),
            (3, "Мышь", 1500, 2, "completed"),
            (6, "Телефон", 50000, 1, "pending")
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO orders (user_id, product, amount, quantity, status) VALUES (?, ?, ?, ?, ?)",
            sample_orders
        )
        
        self.connection.commit()
        
        print("   📊 Созданы тестовые таблицы: users, orders")
    
    def _validate_query(self, query: str) -> Tuple[bool, str]:
        """Валидация SQL запроса"""
        query_upper = query.strip().upper()
        
        operation = query_upper.split()[0] if query_upper else ""
        if operation not in self.allowed_operations:
            return False, f"Операция '{operation}' запрещена. Разрешены: SELECT, INSERT, UPDATE, DELETE"
        
        dangerous_patterns = [
            (r'DROP\s+TABLE', "DROP TABLE запрещен"),
            (r'ALTER\s+TABLE', "ALTER TABLE запрещен"),
            (r'CREATE\s+TABLE', "CREATE TABLE запрещен (используйте только существующие таблицы)"),
        ]
        
        for pattern, message in dangerous_patterns:
            if re.search(pattern, query_upper):
                return False, message
        
        return True, ""
    
    def _execute_query(self, query: str):
        """Выполнение SQL запроса"""
        cursor = self.connection.cursor()
        cursor.execute(query)
        
        if query.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description] if cursor.description else []
            return [dict(zip(columns, row)) for row in rows]
        else:
            self.connection.commit()
            return {"affected_rows": cursor.rowcount}
    
    def _format_results(self, results, query: str) -> str:
        """Форматирование результатов для вывода"""
        if isinstance(results, dict):
            return f"✅ Запрос выполнен. Затронуто строк: {results.get('affected_rows', 0)}"
        
        if not results:
            return "✅ Запрос выполнен. Результатов не найдено."
        
        if len(results) > self.max_rows:
            results = results[:self.max_rows]
            truncated = True
        else:
            truncated = False
        
        response = f"📊 **Результаты запроса:**\n```sql\n{query}\n```\n\n"
        response += f"📈 **Найдено строк:** {len(results)}\n\n"
        
        if truncated:
            response += f"⚠️ Показаны первые {self.max_rows} строк\n\n"
        
        if results:
            headers = list(results[0].keys())
            response += "| " + " | ".join(headers) + " |\n"
            response += "|" + "|".join(["---" for _ in headers]) + "|\n"
            
            for row in results:
                values = [str(row.get(h, ""))[:50] for h in headers]
                response += "| " + " | ".join(values) + " |\n"
        
        return response
    
    def _get_schema(self):
        """Получение схемы базы данных"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        schema = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            schema[table_name] = [col[1] for col in columns]
        return schema
    
    def get_grafana_summary(self):
        """Получение сводки данных, которые отображаются в Grafana"""
        cursor = self.connection.cursor()
        
        cursor.execute("SELECT city, COUNT(*) as count FROM users GROUP BY city ORDER BY count DESC")
        users_by_city = cursor.fetchall()
        
        cursor.execute("SELECT status, COUNT(*) as count, SUM(amount) as total FROM orders GROUP BY status")
        orders_stats = cursor.fetchall()
        
        cursor.execute("""
            SELECT u.name, COUNT(o.id) as orders, SUM(o.amount) as total 
            FROM users u 
            LEFT JOIN orders o ON u.id = o.user_id 
            GROUP BY u.name 
            ORDER BY total DESC 
            LIMIT 5
        """)
        top_users = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as total_users FROM users")
        total_users = cursor.fetchone()['total_users']
        
        cursor.execute("SELECT COUNT(*) as total_orders, SUM(amount) as total_amount FROM orders")
        total_stats = cursor.fetchone()
        
        response = "📊 **Данные из Grafana дашбордов:**\n\n"
        
        response += f"📈 **Общая статистика:**\n"
        response += f"• Всего пользователей: {total_users}\n"
        response += f"• Всего заказов: {total_stats['total_orders']}\n"
        response += f"• Общая выручка: {total_stats['total_amount']:.0f} руб.\n\n"
        
        response += "👥 **Пользователи по городам:**\n"
        for row in users_by_city:
            response += f"• {row['city']}: {row['count']} чел.\n"
        
        response += "\n📦 **Заказы по статусам:**\n"
        for row in orders_stats:
            response += f"• {row['status']}: {row['count']} заказов, {row['total']:.0f} руб.\n"
        
        response += "\n🏆 **Топ пользователей по сумме заказов:**\n"
        for row in top_users:
            orders_count = row['orders'] if row['orders'] else 0
            total = row['total'] if row['total'] else 0
            response += f"• {row['name']}: {orders_count} заказов, {total:.0f} руб.\n"
        
        response += "\n💡 **Для просмотра графиков откройте:** http://localhost:3000\n"
        response += "🔑 Логин: admin, Пароль: admin\n"
        response += "\n📊 **Доступные дашборды:**\n"
        response += "• PostgreSQL Analytics - бизнес-данные\n"
        response += "• API Metrics - технические метрики"
        
        return response
    
    def _show_grafana_help(self) -> str:
        """Помощь по просмотру отчетов в Grafana"""
        return """📊 **Просмотр отчетов в Grafana**

Для просмотра дашбордов и отчетов перейдите по ссылке:

🌐 **Grafana Dashboard:** http://localhost:3000

🔑 **Логин:** admin
🔑 **Пароль:** admin

📊 **Доступные дашборды:**

📈 **PostgreSQL Analytics** - бизнес-данные:
   - Пользователи по городам
   - Распределение по возрастам
   - Заказы по статусам
   - Топ пользователей

📊 **API Metrics** - технические метрики:
   - Количество запросов в секунду
   - Время ответа API
   - Распределение по агентам
   - Процент ошибок

💡 **Как пользоваться:**
1. Откройте браузер и перейдите по ссылке выше
2. Войдите с учетными данными
3. Выберите нужный дашборд
4. Используйте фильтры для детализации

💡 **Совет:** Дашборды автоматически обновляются каждые 30 секунд

📋 **Быстрые команды:**
- "Покажи сводку данных" - получить текстовую сводку
- "SELECT * FROM users" - показать всех пользователей
- "Статистика заказов" - показать статистику по заказам"""
    
    def _generate_query_help(self) -> str:
        """Генерация справки по запросам"""
        schema = self._get_schema()
        
        help_text = "💡 **SQL Agent - помощь**\n\n"
        help_text += "**Доступные таблицы:**\n\n"
        
        for table, columns in schema.items():
            help_text += f"📋 **{table}**\n"
            help_text += f"Поля: {', '.join(columns)}\n\n"
        
        help_text += "**Примеры запросов:**\n\n"
        help_text += "**SELECT (чтение):**\n"
        help_text += "```sql\n"
        help_text += "-- Все пользователи\n"
        help_text += "SELECT * FROM users;\n\n"
        help_text += "-- Пользователи из Москвы\n"
        help_text += "SELECT * FROM users WHERE city = 'Москва';\n\n"
        help_text += "-- Статистика по городам\n"
        help_text += "SELECT city, COUNT(*) as count, AVG(age) as avg_age\n"
        help_text += "FROM users GROUP BY city;\n"
        help_text += "```\n\n"
        
        help_text += "**INSERT (добавление):**\n"
        help_text += "```sql\n"
        help_text += "INSERT INTO users (name, email, age, city) \n"
        help_text += "VALUES ('Анна', 'anna@example.com', 28, 'Москва');\n"
        help_text += "```\n\n"
        
        help_text += "**UPDATE (обновление):**\n"
        help_text += "```sql\n"
        help_text += "UPDATE users SET city = 'Санкт-Петербург' \n"
        help_text += "WHERE name = 'Иван Петров';\n"
        help_text += "```\n\n"
        
        help_text += "**DELETE (удаление):**\n"
        help_text += "```sql\n"
        help_text += "DELETE FROM users WHERE name = 'Анна';\n"
        help_text += "```\n\n"
        
        help_text += "**Аналитика:**\n"
        help_text += "```sql\n"
        help_text += "-- Заказы с именами пользователей\n"
        help_text += "SELECT u.name, o.product, o.amount, o.status\n"
        help_text += "FROM users u JOIN orders o ON u.id = o.user_id;\n\n"
        help_text += "-- Топ продуктов по продажам\n"
        help_text += "SELECT product, SUM(amount) as total_sales\n"
        help_text += "FROM orders GROUP BY product ORDER BY total_sales DESC;\n"
        help_text += "```\n\n"
        
        help_text += "**Команды:**\n"
        help_text += "- `SHOW TABLES` - список таблиц\n"
        help_text += "- `DESCRIBE table_name` - структура таблицы\n"
        help_text += "- `Покажи сводку данных` - получить данные из Grafana\n"
        help_text += "- `Покажи отчеты в Grafana` - открыть дашборды\n"
        
        return help_text
    
    def process(self, message: str, context: Optional[Dict] = None) -> str:
        """Обработка SQL запроса или запроса отчетов"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["сводка", "summary", "дашборд", "dashboard", "графана данные", "покажи данные", "статистика", "общая статистика"]):
            return self.get_grafana_summary()
        
        if any(word in message_lower for word in ["отчет", "report", "grafana", "дашборд", "dashboard", "графана", "покажи отчет", "посмотреть отчет"]):
            return self._show_grafana_help()
        
        if any(word in message_lower for word in ["помощь", "help", "что умеешь", "как работать"]):
            return self._generate_query_help()
        
        if any(word in message_lower for word in ["таблицы", "tables", "список таблиц"]):
            schema = self._get_schema()
            if schema:
                response = "📋 **Список таблиц в базе данных:**\n\n"
                for table in schema.keys():
                    response += f"• {table}\n"
                return response
            return "Не удалось получить список таблиц"
        
        if any(word in message_lower for word in ["структура", "describe", "описание"]):
            for table in self._get_schema().keys():
                if table in message_lower:
                    schema = self._get_schema()
                    if table in schema:
                        response = f"📋 **Структура таблицы {table}:**\n\n"
                        for col in schema[table]:
                            response += f"• {col}\n"
                        return response
            return "Укажите название таблицы. Например: 'структура users'"
        
        sql_pattern = r"(SELECT|INSERT|UPDATE|DELETE|SHOW|DESCRIBE|EXPLAIN).+?(;|$)"
        match = re.search(sql_pattern, message, re.IGNORECASE | re.DOTALL)
        
        if match:
            query = match.group(0).strip()
            
            is_valid, error = self._validate_query(query)
            if not is_valid:
                return f"❌ **Ошибка валидации:** {error}\n\n" + self._generate_query_help()
            
            try:
                results = self._execute_query(query)
                
                self.query_history.append({
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "results_count": len(results) if isinstance(results, list) else 1
                })
                
                return self._format_results(results, query)
                
            except Exception as e:
                return f"❌ **Ошибка выполнения запроса:**\n```\n{str(e)}\n```\n\n" + self._generate_query_help()
        
        return self._generate_query_help()
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики работы агента"""
        return {
            "name": self.name,
            "total_queries": len(self.query_history),
            "tables_count": len(self._get_schema()),
            "tables": list(self._get_schema().keys()),
            "last_query": self.query_history[-1]["query"] if self.query_history else None
        }
    
    def close(self):
        """Закрытие соединения с БД"""
        if self.connection:
            self.connection.close()
            print(f"🔒 Соединение с БД закрыто")


if __name__ == "__main__":
    print("Тестирование SQL Agent")
    
    agent = SQLAgent()
    
    test_queries = [
        "Покажи сводку данных",
        "SELECT * FROM users LIMIT 3",
        "Покажи отчеты в Grafana"
    ]
    
    for query in test_queries:
        print(f"\n📝 Запрос: {query}")
        response = agent.process(query)
        print(f"🤖 Ответ:\n{response}")
    
    agent.close()