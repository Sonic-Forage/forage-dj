# forage-dj Windows Easy Installer (PowerShell)
#
# Usage (from the forage-dj root folder):
#   powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
#   powershell -ExecutionPolicy Bypass -File scripts/setup.ps1 -Full
#
# This is the direct Windows equivalent of scripts/setup.sh

param(
    [switch]$Full,
    [switch]$NoDoctor
)

$ErrorActionPreference = "Stop"

Write-Host "🎧 forage-dj Windows Setup" -ForegroundColor Cyan
Write-Host "   Sonic Forage Music Diffusion OS - Cross-platform edition`n"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
Set-Location $repoRoot

# 1. Ensure uv
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "→ Installing uv (Astral) for Windows..." -ForegroundColor Yellow
    irm https://astral.sh/uv/install.ps1 | iex
    # Refresh PATH for current session
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine")
}

Write-Host "→ uv version: $(uv --version)"

# 2. Delegate to the universal Python installer (best cross-platform logic)
$mode = if ($Full) { "--full" } else { "" }
$doctorFlag = if ($NoDoctor) { "--no-doctor" } else { "" }

Write-Host "`n→ Launching universal cross-platform installer...`n" -ForegroundColor Green

python scripts/install.py $mode $doctorFlag

Write-Host "`n✅ Windows setup finished. Use the printed instructions above." -ForegroundColor Green
Write-Host "   Next time: . .grok\hf-cache.ps1 ; .venv\Scripts\Activate.ps1" -ForegroundColor DarkGray
