# start-local.ps1
Write-Host "🚀 Starting LangGraph Agent System..." -ForegroundColor Green

# Запуск Elasticsearch и Kibana
Write-Host "Starting Elasticsearch and Kibana..." -ForegroundColor Yellow
docker start elasticsearch kibana 2>$null

# Запуск PostgreSQL
Write-Host "Starting PostgreSQL..." -ForegroundColor Yellow
docker start postgres 2>$null

# Запуск port-forward
Write-Host "Starting port-forward..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit -Command kubectl port-forward service/langgraph-agent 8000:80 -n langgraph"

# Запуск Streamlit
Write-Host "Starting Streamlit..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit -Command cd C:\Users\user\Multi-Agent_System; streamlit run streamlit_app.py"

Write-Host "✅ System started!" -ForegroundColor Green
Write-Host "📡 API: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "🎨 UI: http://localhost:8501" -ForegroundColor Yellow
Write-Host "📊 Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor Yellow