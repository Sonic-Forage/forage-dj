# =============================================================================
# STRICT PROJECT-ONLY CACHE CONFIG — /mnt/z/IMF2045/forage-dj/ ONLY (Windows)
# Dot-source this in PowerShell:  . .grok\hf-cache.ps1
# =============================================================================

$env:FORAGE_DJ_DATA_ROOT = "D:\forage-dj-data"   # <-- CHANGE THIS on your machine if needed
$env:HF_HOME = "$env:FORAGE_DJ_DATA_ROOT\.cache\huggingface"
$env:HUGGINGFACE_HUB_CACHE = "$env:HF_HOME\hub"
$env:TRANSFORMERS_CACHE = "$env:HF_HOME\transformers"

# Pin uv cache inside the data root
$env:UV_CACHE_DIR = "$env:FORAGE_DJ_DATA_ROOT\.cache\uv"

Write-Host "✅ forage-dj locked to large data drive only" -ForegroundColor Green
Write-Host "   HF cache : $env:HF_HOME"
Write-Host "   uv cache : $env:UV_CACHE_DIR"

# Optional: also create the dirs
New-Item -ItemType Directory -Force -Path $env:HF_HOME, $env:UV_CACHE_DIR | Out-Null