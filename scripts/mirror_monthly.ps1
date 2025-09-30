param(
  [string]$ConfigPath = "$PSScriptRoot\config.json"
)

$cfg    = Get-Content $ConfigPath | ConvertFrom-Json
$Source = $cfg.source
$Dest   = $cfg.dest
$LogDir = $cfg.log_dir
New-Item -ItemType Directory -Force -Path $Dest, $LogDir | Out-Null

$stamp   = (Get-Date).ToString("yyyy-MM-dd_HH-mm-ss")
$robolog = Join-Path $LogDir "mirror_$stamp.log"

# Build /XD and /XF
$XD = @()
foreach($d in $cfg.excludes){ $XD += @(" /XD `"$d`"") }
$XF = @()
foreach($x in $cfg.exclude_ext){ $XF += @(" /XF `*$x`") }
$xdxf = ($XD -join "") + ($XF -join "")

# robocopy /MIR (sync deletions/changes)
$cmd = "robocopy `"$Source`" `"$Dest`" /MIR /Z /R:2 /W:3 /NP /NFL /NDL /MT:16 /TEE /LOG:`"$robolog`"$xdxf"
Write-Host $cmd
cmd /c $cmd
$rc = $LASTEXITCODE

"[$(Get-Date)] Robocopy exit code: $rc" | Add-Content -Path (Join-Path $LogDir "mirror_summary_$stamp.log")
exit $rc
