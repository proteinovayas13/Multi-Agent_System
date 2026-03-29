"""
SQL Agent - работа с базами данных (поддерживает SELECT, INSERT, UPDATE, DELETE)
"""
import sqlite3
import re

class SQLAgent:
    def __init__(self):
        self.name = "SQL Agent"
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self._create_sample_tables()
        print(f"✅ {self.name} initialized")
    
    def _create_sample_tables(self):
        cursor = self.connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, age INTEGER, city TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, product TEXT, amount REAL, status TEXT)")
        
        cursor.executemany("INSERT OR IGNORE INTO users (name, email, age, city) VALUES (?, ?, ?, ?)", [
            ("Ivan Petrov", "ivan@example.com", 25, "Moscow"),
            ("Maria Sidorova", "maria@example.com", 30, "SPb"),
            ("Alexey Ivanov", "alexey@example.com", 28, "Moscow")
        ])
        
        cursor.executemany("INSERT OR IGNORE INTO orders (user_id, product, amount, status) VALUES (?, ?, ?, ?)", [
            (1, "Laptop", 75000, "completed"),
            (1, "Mouse", 1500, "completed"),
            (2, "Phone", 50000, "pending")
        ])
        self.connection.commit()
    
    def _execute_query(self, query: str):
        """Execute any SQL query"""
        cursor = self.connection.cursor()
        cursor.execute(query)
        
        # For SELECT queries, return results
        if query.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []
        else:
            # For INSERT, UPDATE, DELETE
            self.connection.commit()
            return {"affected_rows": cursor.rowcount}
    
    def process(self, message, context=None):
        """Process SQL query"""
        message_lower = message.lower()
        
        # Check if it's a SQL query
        sql_keywords = ["select", "insert", "update", "delete", "create", "alter", "drop"]
        is_sql = any(keyword in message_lower for keyword in sql_keywords)
        
        if is_sql:
            try:
                results = self._execute_query(message)
                
                if isinstance(results, list):
                    if results:
                        return f"✅ Found {len(results)} rows:\n" + "\n".join(str(r) for r in results[:10])
                    return "✅ Query executed. No results found."
                else:
                    return f"✅ Query executed. {results.get('affected_rows', 0)} rows affected."
                    
            except Exception as e:
                return f"❌ SQL Error: {e}"
        
        # Help message
        return """💡 **SQL Agent Help**

I can execute SQL queries on the database.

**Examples:**
- `SELECT * FROM users`
- `INSERT INTO users (name, email, age, city) VALUES ('Anna', 'anna@example.com', 28, 'Moscow')`
- `UPDATE users SET city = 'Moscow' WHERE name = 'Ivan'`
- `DELETE FROM users WHERE name = 'Anna'`

**Available tables:**
- `users` - id, name, email, age, city
- `orders` - id, user_id, product, amount, status

**Try these queries:**"""