# Allow script execution (once)
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope LocalMachine -Force

$root   = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = "C:\Windows\py.exe"  # Use py launcher; change if needed
$inc    = Join-Path $root "backup_incremental.py"
$mir    = Join-Path $root "mirror_monthly.ps1"

# Daily incremental at 01:30
schtasks /Create /TN "MyBackupStyle_DailyIncremental" /SC DAILY /ST 01:30 /RU SYSTEM /TR "`"$python`" `"$inc`""

# Monthly mirror on day 1 at 02:30
schtasks /Create /TN "MyBackupStyle_MonthlyMirror" /SC MONTHLY /D 1 /ST 02:30 /RU SYSTEM /TR "powershell.exe -ExecutionPolicy Bypass -File `"$mir`""

Write-Host "Scheduled tasks created."
