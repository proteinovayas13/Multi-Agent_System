FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем все файлы из src
COPY src/ ./src/
COPY *.py ./

# Создаем __init__.py файлы
RUN mkdir -p src/agents src/orchestrator && \
    touch src/__init__.py && \
    touch src/agents/__init__.py && \
    touch src/orchestrator/__init__.py

EXPOSE 8000

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]