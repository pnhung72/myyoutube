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
    default { Get-Content README.md }
}