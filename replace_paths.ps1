# replace_paths.ps1
Write-Host "Auto replacing paths..." -ForegroundColor Green

$oldName = "Multi-Agent_System"
$newName = "Multi-Agent_System"

$extensions = @("*.md", "*.ps1", "*.yml", "*.yaml", "*.json", "*.txt", "*.sh", "*.bat", "*.cfg", "*.conf")
$excludeFolders = @("langgraph-env", "__pycache__", ".git", "uploads", "logs", "node_modules")

Write-Host "Searching files..." -ForegroundColor Yellow

$files = Get-ChildItem -Recurse -File | Where-Object {
    $extension = $_.Extension
    $shouldInclude = $extensions | Where-Object { $_ -eq "*$extension" -or $_ -eq $_.Name }
    $shouldExclude = $excludeFolders | Where-Object { $_.FullName -like "*$_*" }
    
    return ($shouldInclude -and -not $shouldExclude)
}

$count = 0
foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
    if ($content -and $content -match $oldName) {
        $newContent = $content -replace $oldName, $newName
        Set-Content $file.FullName -Value $newContent -NoNewline
        Write-Host "  Updated: $($file.FullName)" -ForegroundColor Cyan
        $count++
    }
}

Write-Host ""
Write-Host "Done! Updated files: $count" -ForegroundColor Green
Write-Host "Old name: $oldName" -ForegroundColor Yellow
Write-Host "New name: $newName" -ForegroundColor Yellow