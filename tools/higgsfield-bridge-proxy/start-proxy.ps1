# Idempotent start for the Higgsfield bridge proxy. Safe to run at login.
param(
  [int]$Port = 18777,
  [string]$LogPath = "C:\OpenMontage\tmp\higgsfield-bridge-proxy.log"
)

$script = Join-Path $PSScriptRoot "proxy.mjs"

# Match node only, so the PowerShell process running this script isn't counted.
$existing = Get-CimInstance Win32_Process |
  Where-Object { $_.Name -eq 'node.exe' -and $_.CommandLine -match 'higgsfield-bridge-proxy' }

if ($existing) {
  Write-Host "Already running (PID $($existing.ProcessId -join ', '))."
  exit 0
}

New-Item -ItemType Directory -Force -Path (Split-Path $LogPath) | Out-Null

$proc = Start-Process -FilePath "node" `
  -ArgumentList $script, "--port", $Port, "--log", $LogPath `
  -WindowStyle Hidden -PassThru

Write-Host "Started proxy PID $($proc.Id) on http://127.0.0.1:$Port -> https://bridge.higgsfield.ai"
Write-Host "Log: $LogPath"
