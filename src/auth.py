"""
Simple authentication - no JWT
"""
class SimpleUser:
    def __init__(self, username: str, role: str = "user"):
        self.username = username
        self.role = role

async def get_current_active_user():
    return SimpleUser("user", "user")

async def get_current_user():
    return SimpleUser("user", "user")

def create_access_token(data: dict):
    return "dummy_token"

def authenticate_user(username: str, password: str):
    if username == "admin" and password == "admin123":
        return SimpleUser("admin", "admin")
    if username == "user" and password == "user123":
        return SimpleUser("user", "user")
    return None