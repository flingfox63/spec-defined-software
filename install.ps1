# SDS (Spec-Defined Software) Windows PowerShell One-Click Installer

$ErrorActionPreference = 'Stop'

# --- Styles ---
function Print-Info ($Msg) {
    Write-Host "[INFO] $Msg" -ForegroundColor Blue
}

function Print-Success ($Msg) {
    Write-Host "[PASS] $Msg" -ForegroundColor Green
}

function Print-Warn ($Msg) {
    Write-Host "[WARN] $Msg" -ForegroundColor Yellow
}

function Print-Error ($Msg) {
    Write-Error "[FAIL] $Msg"
}

# --- Welcome Banner ---
Write-Host ""
Write-Host "==================================================" -ForegroundColor Blue -FontBold
Write-Host "    🚀  SDS (Spec-Defined Software) Installer      " -ForegroundColor White -FontBold
Write-Host "==================================================" -ForegroundColor Blue -FontBold
Write-Host ""

# 1. Check Python
$PythonInstalled = $false
try {
    $PythonCheck = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $PythonInstalled = $true
        Print-Success "Found Python: $PythonCheck"
    }
} catch {}

if (-not $PythonInstalled) {
    Print-Error "Python 3 is required but could not be detected in your PATH."
    Print-Error "Please install Python from https://python.org and try again."
    exit 1
}

# 2. Check Pipx
$PipxInstalled = $false
try {
    $PipxCheck = pipx --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $PipxInstalled = $true
    }
} catch {}

# 1.5 Determine installation source (local vs remote)
$InstallSource = "git+https://github.com/flingfox63/spec-defined-software.git"
if (Test-Path "pyproject.toml") {
    Print-Info "Detected local 'pyproject.toml'! Running in local development installation mode..."
    $InstallSource = "."
}

if ($PipxInstalled) {
    Print-Info "Found pipx! Installing globally and isolating dependencies..."
    try {
        pipx install $InstallSource --force | Out-Null
        Print-Success "SDS CLI successfully installed via pipx!"
        Write-Host ""
        Write-Host "Try running:"
        Write-Host "  sds check" -ForegroundColor White -FontBold
        Write-Host ""
        exit 0
    } catch {
        Print-Warn "pipx installation failed. Falling back to isolated virtualenv..."
    }
}

# 3. Fallback: Create isolated venv in $HOME\.sds\venv
$InstallDir = Join-Path $HOME ".sds"
$VenvDir = Join-Path $InstallDir "venv"
$BinDir = Join-Path $InstallDir "bin"

Print-Info "Setting up isolated sandbox environment in $VenvDir..."
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir | Out-Null
}

# Create venv
python -m venv $VenvDir
Print-Success "Isolated virtualenv created."

# Upgrade pip and install package
Print-Info "Installing sds-cli package..."
& (Join-Path $VenvDir "Scripts\pip.exe") install --upgrade pip --quiet
& (Join-Path $VenvDir "Scripts\pip.exe") install $InstallSource --quiet
Print-Success "Package installed successfully."

# 4. Expose CLI script
if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir | Out-Null
}

$SdsBatPath = Join-Path $BinDir "sds.bat"
"@echo off`n`"" + (Join-Path $VenvDir "Scripts\sds.exe") + "`" %*" | Out-File -FilePath $SdsBatPath -Encoding ASCII
Print-Success "Command wrapper script created at: $SdsBatPath"

# --- Output Path Verification ---
Write-Host ""
Write-Host "==================================================" -ForegroundColor Green -FontBold
Write-Host "    🎉  SDS Installation Completed Successfully!   " -ForegroundColor White -FontBold
Write-Host "==================================================" -ForegroundColor Green -FontBold
Write-Host ""

# Check if $BinDir is in PATH
$PathEnv = [Environment]::GetEnvironmentVariable("Path", "User")
if ($PathEnv -like "*$BinDir*") {
    Print-Success "SDS is ready! Restart your terminal or runs: sds check"
} else {
    Print-Warn "The directory $BinDir is not in your environment PATH."
    Print-Info "Adding $BinDir to your User PATH variable..."
    $NewPath = $PathEnv + ";" + $BinDir
    [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
    Print-Success "PATH updated! Please RESTART your terminal/IDE and run: sds check"
}
Write-Host ""
