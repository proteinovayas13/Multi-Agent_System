import requests
import sys

# Загружаем файл
url = "http://localhost:8000/upload"

try:
    with open("test_doc.txt", "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
        print("Status:", response.status_code)
        print("Response:", response.json())
except Exception as e:
    print(f"Error: {e}")
