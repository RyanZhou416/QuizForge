# QuizForge Windows Build Script
# Builds Tauri desktop application for Windows
# Usage: powershell -ExecutionPolicy Bypass -File scripts/build-win.ps1

Set-StrictMode -Version Latest

function Abort($msg) {
    Write-Host "`nERROR: $msg" -ForegroundColor Red
    Write-Host "`nPress any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "=== QuizForge Windows Build ===" -ForegroundColor Cyan

# Check Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Abort "Node.js is not installed. Install from https://nodejs.org/"
}
Write-Host "Node.js: $(node --version)" -ForegroundColor Green

# Check Rust
if (-not (Get-Command rustc -ErrorAction SilentlyContinue)) {
    Abort "Rust is not installed. Install from https://rustup.rs/"
}
Write-Host "Rust: $(rustc --version)" -ForegroundColor Green

# Check cargo
if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    Abort "Cargo is not found. Reinstall Rust from https://rustup.rs/"
}

# Navigate to project root
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $projectRoot
Write-Host "Project root: $projectRoot" -ForegroundColor Gray

Write-Host "`nInstalling npm dependencies..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -ne 0) { Abort "npm install failed (exit code $LASTEXITCODE)" }

Write-Host "`nBuilding Tauri application..." -ForegroundColor Yellow
npm run tauri build
if ($LASTEXITCODE -ne 0) { Abort "Tauri build failed (exit code $LASTEXITCODE)" }

Write-Host "`n=== Build Complete ===" -ForegroundColor Cyan
Write-Host "Installers are located in:" -ForegroundColor Green
Write-Host "  src-tauri\target\release\bundle\msi\" -ForegroundColor White
Write-Host "  src-tauri\target\release\bundle\nsis\" -ForegroundColor White
Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
