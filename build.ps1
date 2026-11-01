<#
.SYNOPSIS
    Xperia Keyboard Universal Windows Build Script
.DESCRIPTION
    Runs the Python automated build pipeline to patch, align, sign, and verify the APK.
#>

param(
    [string]$InputApk,
    [string]$OutputApk = "release/Xperia-Keyboard-Universal-v8.0.A.0.110.apk"
)

$ErrorActionPreference = "Stop"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " Xperia Keyboard Universal Build Trigger" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python 3 is required but was not found on PATH."
    exit 1
}

$scriptPath = Join-Path $PSScriptRoot "build.py"
if ($InputApk) {
    python $scriptPath $InputApk $OutputApk
} else {
    python $scriptPath
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nBuild succeeded! APK available in release/ directory." -ForegroundColor Green
} else {
    Write-Host "`nBuild failed with exit code $LASTEXITCODE" -ForegroundColor Red
}
