# Lệnh tắt:  .\run.ps1 sync | lessons | money | auth | edit <VIDEO_ID> [tùy chọn]
param([Parameter(Position = 0)][string]$Cmd = 'help', [Parameter(ValueFromRemainingArguments = $true)]$Rest)
$py = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
Set-Location $PSScriptRoot
switch ($Cmd) {
    'sync'  { & $py scripts/sync_videos.py; & $py scripts/blogger_inventory.py; & $py scripts/analyze.py; & $py scripts/marketing.py }
    'lessons' { & $py scripts/blogger_inventory.py }
    'money' { & $py scripts/monetization.py }
    'auth'  { & $py scripts/auth_first_time.py }
    'edit'  { & $py scripts/update_video.py @Rest }
        'push'  {
        $msg = if ($Rest) { $Rest -join ' ' } else { 'cap nhat tu may' }
        git add -A
        $bad = git diff --cached --name-only | Select-String -Pattern 'secrets/|private/|token|client_secret|\.env'
        if ($bad) {
            git reset -q
            Write-Host 'DUNG LAI: co file nhay cam trong danh sach chuan bi day len:' -ForegroundColor Red
            $bad
            return
        }
        git diff --cached --quiet
        if ($LASTEXITCODE -ne 0) { git commit -m $msg }
        git pull --rebase
        if ($LASTEXITCODE -ne 0) { Write-Host 'Pull bi loi hoac xung dot. DUNG LAI va gui thong bao cho tro ly.' -ForegroundColor Red; return }
        git push
        if ($LASTEXITCODE -ne 0) { Write-Host 'Push bi loi.' -ForegroundColor Red } else { Write-Host 'Da day len GitHub.' -ForegroundColor Green }
    }
    default { Get-Content README.md }
}