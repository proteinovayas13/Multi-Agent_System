# LangGraph Multi-Agent System.

LangGraph — это "hard logic" (жесткая логика оркестрации). В отличие от сырой нейросети, моя система гарантирует структуру ответа и маршрутизации.

Я убираю 'галлюцинации' ИИ и даю контроль над расходами через оркестрацию."(в моем случае это 3 агента RAF, SQL, обычный чат бот.

Это не просто чат-бот, а фабрика агентов. Это приложение перевожу ваш бизнес-процесс (например, обработку заказа) на язык графов состояний, что исключает ошибки маршрутизации."


![LangGraph Agent](https://img.shields.io/badge/LangGraph-Agent-blue)
![Python](https://img.shields.io/badge/Python-3.12-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Minikube-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Grafana](https://img.shields.io/badge/Grafana-Monitoring-orange)
![License](https://youtube.com/shorts/wrsNgsw41LU?si=5tRZj8XAlcaQAcrI)

**Мультиагентная система на основе LangGraph с оркестрацией в Kubernetes**

[Документация](https://github.com/your-username/langgraph-agent) |  | [API Reference](http://localhost:8000/docs)]
ДОКУМЕНТАЦИЯ и НАСТРОЕННЫЕ ДАШБОРДЫ В GRAFANA на тестовых данных- можете спросить у моего RAG агента после локального запуска- 
DEMO (видео на Youtube) - https://youtube.com/shorts/wrsNgsw41LU?si=5tRZj8XAlcaQAcrI

</div>

---

## Описание проекта

Мультиагентная система, построенная на **LangGraph**, объединяющая трех специализированных агентов для решения различных задач. Система развернута в **Kubernetes** и предоставляет REST API, веб-интерфейс и полноценный мониторинг.

### Основные возможности

| Возможность | Описание |
|-------------|----------|
| **3 специализированных агента** | RAG, SQL и Chat агенты для разных задач |
| **RAG Agent** | Поиск информации по документам с Elasticsearch |
| **SQL Agent** | Выполнение SQL запросов к PostgreSQL |
| **Chat Agent** | Диалоговый ассистент |
| **Загрузка документов** | Поддержка TXT, PDF, DOCX |
| **REST API** | Автоматическая документация Swagger |
| **Веб-интерфейс** | Streamlit UI для удобного взаимодействия |
| **Мониторинг** | Prometheus + Grafana для отслеживания метрик |
| **Оркестрация** | Kubernetes для масштабирования |

---

## Архитектура системы
┌─────────────────────────────────────────────────────────────────┐
│ Streamlit UI (Port 8501) │
│ Веб-интерфейс для пользователей │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ FastAPI Server (Port 8000) │
│ REST API с Swagger документацией │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ LangGraph Orchestrator │
│ Маршрутизация запросов между агентами │
└─────────────────────────────────────────────────────────────────┘
│ │ │
▼ ▼ ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ RAG Agent │ │ SQL Agent │ │ Chat Agent │
│ Поиск инфо │ │ Работа с БД │ │ Диалоги │
└─────────────────┘ └─────────────────┘ └─────────────────┘
│ │ │
└────────────────────┴────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ Хранилища данных и мониторинг │
├─────────────────────────────────────────────────────────────────┤
│ PostgreSQL │ Elasticsearch │ Prometheus │ Grafana │ Kibana │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ Kubernetes (Minikube) │
│ Оркестрация контейнеров │
└─────────────────────────────────────────────────────────────────┘


---

## Технологический стек

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| Оркестратор | LangGraph | Управление агентами и состоянием |
| API | FastAPI | RESTful API сервер |
| UI | Streamlit | Веб-интерфейс |
| База данных | PostgreSQL | Хранение бизнес-данных |
| Поиск | Elasticsearch | Векторный поиск для RAG |
| Мониторинг | Prometheus + Grafana | Сбор метрик и визуализация |
| Логи | Kibana | Анализ логов |
| Контейнеризация | Docker | Упаковка приложения |
| Оркестрация | Kubernetes (Minikube) | Развертывание и масштабирование |

---

## Быстрый старт

### Предварительные требования

- Python 3.12+
- Docker Desktop
- Minikube
- kubectl

### 1. Клонирование и установка

```bash
git clone https://github.com/your-username/Multi-Agent_System.git
cd Multi-Agent_System

# Создание виртуального окружения
python -m venv langgraph-env

# Активация (Windows)
.\langgraph-env\Scripts\Activate.ps1

# Активация (Linux/Mac)
source langgraph-env/bin/activate

# Установка зависимостей
pip install -r requirements.txt
2. Запуск сервисов (Docker Compose)
bash
# Запуск всех сервисов (PostgreSQL, Elasticsearch, Prometheus, Grafana)
docker-compose up -d

# Проверка запуска
docker ps
3. Локальный запуск API
bash
# Запуск API сервера
python src/api.py

# В другом окне - запуск Streamlit UI
streamlit run streamlit_app.py
4. Запуск в Kubernetes
bash
# Запуск Minikube
minikube start --driver=hyperv

# Сборка Docker образа
docker build -t langgraph-agent:latest .

# Загрузка образа в Minikube
minikube image load langgraph-agent:latest

# Создание namespace и развертывание
kubectl create namespace langgraph
kubectl apply -f k8s/deployment.yaml -n langgraph
kubectl apply -f k8s/service.yaml -n langgraph

# Проброс порта для доступа к API
kubectl port-forward service/langgraph-agent 8000:80 -n langgraph
 
Агенты

1. RAG Agent (Retrieval-Augmented Generation)
Поиск информации в базе знаний с использованием Elasticsearch.

Примеры запросов:

Что такое Kubernetes?
Расскажи про LangGraph
Как работает Docker?
Что такое Elasticsearch?
2. SQL Agent
Выполнение SQL запросов к PostgreSQL базе данных.

Примеры запросов:

sql
SELECT * FROM users
SELECT * FROM users WHERE city = 'Москва'
SELECT city, COUNT(*) FROM users GROUP BY city
SELECT u.name, o.product FROM users u JOIN orders o ON u.id = o.user_id
3. Chat Agent
Диалоговый ассистент для общения.

Примеры запросов:


Привет, как дела?
Что ты умеешь?
Расскажи о себе
Спасибо за помощь!

API Endpoints

Метод	Endpoint	Описание
GET	/	Главная страница
GET	/health	Проверка здоровья сервиса
GET	/agents	Список доступных агентов
POST	/chat	Отправить сообщение агенту
POST	/upload	Загрузить документ
GET	/documents	Список документов
GET	/metrics	Метрики Prometheus
GET	/docs	Swagger документация
Примеры запросов
Health check:

bash
curl http://localhost:8000/health
Отправить сообщение:

bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is Kubernetes?","session_id":"test"}'

Загрузить документ:

bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.txt"


Мониторинг

Сервис	URL	Логин/Пароль
Grafana	http://localhost:3000	admin/admin
Prometheus	http://localhost:9090	-
Kibana	http://localhost:5601	-
Swagger UI	http://localhost:8000/docs	-
Streamlit UI	http://localhost:8501	-
Метрики в Grafana
Доступные дашборды:

PostgreSQL Analytics — бизнес-данные (пользователи, заказы)

API Metrics — технические метрики (запросы, время ответа)

 Docker команды

# Сборка образа
docker build -t langgraph-agent:latest .

# Запуск контейнера
docker run -p 8000:8000 langgraph-agent:latest

# Запуск всех сервисов
docker-compose up -d

# Остановка всех сервисов
docker-compose down -v

Kubernetes команды

# Просмотр подов
kubectl get pods -n langgraph

# Просмотр логов
kubectl logs -f -l app=langgraph-agent -n langgraph

# Перезапуск
kubectl rollout restart deployment langgraph-agent -n langgraph

# Масштабирование (3 экземпляра)
kubectl scale deployment langgraph-agent --replicas=3 -n langgraph

# Удаление

kubectl delete namespace langgraph


Структура проекта

Multi-Agent_System/
├── .github/
│ └── workflows/ # GitHub Actions CI/CD пайплайны
├── src/
│ ├── agents/ # Агенты LangGraph
│ │ ├── init.py
│ │ ├── rag_agent.py # RAG агент (Elasticsearch)
│ │ ├── sql_agent.py # SQL агент (PostgreSQL)
│ │ └── chat_agent.py # Chat агент (диалоговый)
│ ├── orchestrator/ # Оркестратор LangGraph
│ │ ├── init.py
│ │ └── orchestrator.py # Маршрутизация запросов
│ └── api.py # FastAPI сервер (Port 8000)
├── k8s/ # Kubernetes манифесты
│ ├── deployment.yaml
│ └── service.yaml
├── k8s-backup/ # Резервные копии манифестов
├── streamlit_app.py # Веб-интерфейс (Port 8501)
├── docker-compose.yml # Локальный запуск сервисов
├── Dockerfile # Сборка образа
├── requirements.txt # Python зависимости
└── README.md # Документация


Устранение неполадок

API не отвечает

# Проверьте port-forward
kubectl port-forward service/langgraph-agent 8000:80 -n langgraph

# Проверьте поды
kubectl get pods -n langgraph

# Проверьте логи

kubectl logs -l app=langgraph-agent -n langgraph

Elasticsearch не доступен

# Проверьте, что Elasticsearch запущен
docker ps | findstr elasticsearch

# Запустите Elasticsearch

docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.11.0

Ошибка загрузки документов

# Используйте правильную кодировку

with open('file.txt', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/upload', files=files)


# Упаковка https://railway.com/workspace/upgrade (30 дней бесплатного пользования, дальше 5 $.
-Веб-интерфейс на Streamlit

-Интеграция с PostgreSQL и Elasticsearch
