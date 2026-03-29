# stop-local.ps1
Write-Host " Stopping LangGraph Agent System..." -ForegroundColor Yellow

# Остановка контейнеров
docker stop elasticsearch kibana postgres 2>$null

# Остановка процессов
Get-Process | Where-Object { $_.ProcessName -eq "kubectl" -or $_.ProcessName -eq "streamlit" } | Stop-Process -Force 2>$null

Write-Host " System stopped!" -ForegroundColor Green