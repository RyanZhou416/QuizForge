# QuizForge Portable Build Script
# Builds a portable (no-install) zip package for Windows
# Usage: powershell -ExecutionPolicy Bypass -File scripts/build-portable.ps1

Set-StrictMode -Version Latest

function Abort($msg) {
    Write-Host "`nERROR: $msg" -ForegroundColor Red
    Write-Host "`nPress any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "=== QuizForge Portable Build ===" -ForegroundColor Cyan

if (-not (Get-Command node -ErrorAction SilentlyContinue)) { Abort "Node.js is not installed." }
Write-Host "Node.js: $(node --version)" -ForegroundColor Green

if (-not (Get-Command rustc -ErrorAction SilentlyContinue)) { Abort "Rust is not installed." }
Write-Host "Rust: $(rustc --version)" -ForegroundColor Green

if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) { Abort "Cargo is not found." }

$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $projectRoot
Write-Host "Project root: $projectRoot" -ForegroundColor Gray

$version = (Get-Content src-tauri\tauri.conf.json | ConvertFrom-Json).version
Write-Host "Version: $version" -ForegroundColor Green

Write-Host "`nInstalling npm dependencies..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -ne 0) { Abort "npm install failed" }

Write-Host "`nBuilding Tauri application..." -ForegroundColor Yellow
npm run tauri build
if ($LASTEXITCODE -ne 0) { Abort "Tauri build failed" }

$exe = "src-tauri\target\release\quizforge.exe"
if (-not (Test-Path $exe)) { Abort "Built executable not found at $exe" }

$portableDir = "src-tauri\target\release\portable"
$zipName = "QuizForge_${version}_x64_portable.zip"
$zipPath = "src-tauri\target\release\bundle\$zipName"

Write-Host "`nPackaging portable version..." -ForegroundColor Yellow

if (Test-Path $portableDir) { Remove-Item -Recurse -Force $portableDir }
New-Item -ItemType Directory -Path $portableDir | Out-Null

Copy-Item $exe "$portableDir\QuizForge.exe"

@"
QuizForge $version - Portable Edition

Usage:
  Double-click QuizForge.exe to run.
  No installation required.

Note:
  Windows WebView2 runtime is required (pre-installed on Windows 10/11).
  User data is stored in: %APPDATA%\com.quizforge.app
"@ | Out-File -Encoding utf8 "$portableDir\README.txt"

if (Test-Path $zipPath) { Remove-Item -Force $zipPath }
Compress-Archive -Path "$portableDir\*" -DestinationPath $zipPath

Remove-Item -Recurse -Force $portableDir

$size = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)

Write-Host "`n=== Build Complete ===" -ForegroundColor Cyan
Write-Host "Portable zip: $zipPath ($size MB)" -ForegroundColor Green
Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
