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
    Write-Error "[FAIL] $Msg" -ErrorAction Continue
}

function Get-PipxEnvironmentValue ($Name) {
    try {
        $Output = @(& pipx environment --value $Name 2>$null)
        $Status = $LASTEXITCODE
        if ($Status -eq 0) {
            $Value = $Output |
                ForEach-Object { $_.ToString().Trim() } |
                Where-Object { $_ } |
                Select-Object -Last 1
            if ($Value) {
                return $Value
            }
        }
    } catch {}

    return $null
}

function Resolve-PipxSdsCommand {
    $Candidates = @()

    $PipxVenvRoot = Get-PipxEnvironmentValue "PIPX_LOCAL_VENVS"
    if ($PipxVenvRoot) {
        $Candidates += Join-Path $PipxVenvRoot "sds-cli\Scripts\sds.exe"
        $Candidates += Join-Path $PipxVenvRoot "sds-cli\bin\sds"
    }

    $PipxBinDir = Get-PipxEnvironmentValue "PIPX_BIN_DIR"
    if ($PipxBinDir) {
        $Candidates += Join-Path $PipxBinDir "sds.exe"
        $Candidates += Join-Path $PipxBinDir "sds"
    }

    if ($HOME) {
        $Candidates += Join-Path $HOME ".local\bin\sds.exe"
        $Candidates += Join-Path $HOME ".local\bin\sds"
    }

    foreach ($Candidate in $Candidates) {
        if (Test-Path -LiteralPath $Candidate -PathType Leaf) {
            return (Resolve-Path -LiteralPath $Candidate).Path
        }
    }

    $Command = Get-Command sds -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($Command -and $Command.Path) {
        return (Resolve-Path -LiteralPath $Command.Path).Path
    }

    return $null
}

function Install-AgentIntegrations ($SdsCommand) {
    if (-not (Test-Path -LiteralPath $SdsCommand -PathType Leaf)) {
        Print-Error "The installed SDS executable could not be found at: $SdsCommand"
        return 1
    }

    Print-Info "Installing SDS integrations for supported agents and IDEs..."
    # Keep the CLI's output visible without allowing it to become part of this
    # function's numeric return value in PowerShell's success-output pipeline.
    & $SdsCommand install-agents --targets detected --command $SdsCommand | Out-Host
    $Status = $LASTEXITCODE
    if ($Status -ne 0) {
        Print-Error "SDS CLI was installed, but agent integration failed (exit code $Status)."
        Print-Error "Re-run: `"$SdsCommand`" install-agents --targets detected --command `"$SdsCommand`""
        return $Status
    }

    Print-Success "Agent and IDE integrations installed successfully."
    return 0
}

# --- Welcome Banner ---
Write-Host ""
Write-Host "==================================================" -ForegroundColor Blue
Write-Host "    🚀  SDS (Spec-Defined Software) Installer      " -ForegroundColor White
Write-Host "==================================================" -ForegroundColor Blue
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

# 1.5 Determine installation source (local vs remote). Only the repository that
# contains this installer is eligible for a local development install. This
# avoids installing an unrelated project merely because the current directory
# also contains a pyproject.toml.
$InstallSource = "git+https://github.com/flingfox63/spec-defined-software.git"
if ($PSScriptRoot) {
    $ProjectFile = Join-Path $PSScriptRoot "pyproject.toml"
    $CliFile = Join-Path $PSScriptRoot "skills\sds-core\src\sds\cli.py"
    if ((Test-Path -LiteralPath $ProjectFile -PathType Leaf) -and
        (Test-Path -LiteralPath $CliFile -PathType Leaf)) {
        $ProjectMetadata = Get-Content -LiteralPath $ProjectFile -Raw
        if ($ProjectMetadata -match '(?m)^[ \t]*name[ \t]*=[ \t]*["'']sds-cli["''][ \t]*(?:#.*)?$') {
            $InstallSource = (Resolve-Path -LiteralPath $PSScriptRoot).Path
            Print-Info "Detected the local SDS repository at $InstallSource."
        }
    }
}

if ($PipxInstalled) {
    Print-Info "Found pipx! Installing globally and isolating dependencies..."
    & pipx install $InstallSource --force
    $PipxInstallStatus = $LASTEXITCODE
    if ($PipxInstallStatus -eq 0) {
        $SdsCommand = Resolve-PipxSdsCommand
        if (-not $SdsCommand) {
            Print-Error "SDS was installed via pipx, but its executable path could not be resolved."
            exit 1
        }

        $AgentInstallStatus = Install-AgentIntegrations $SdsCommand
        if ($AgentInstallStatus -ne 0) {
            exit $AgentInstallStatus
        }

        Print-Success "SDS CLI successfully installed via pipx!"
        Write-Host ""
        Write-Host "Try running:"
        Write-Host "  $SdsCommand check" -ForegroundColor White
        Write-Host ""
        exit 0
    } else {
        Print-Warn "pipx installation failed (exit code $PipxInstallStatus). Falling back to isolated virtualenv..."
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
& python -m venv $VenvDir
if ($LASTEXITCODE -ne 0) {
    Print-Error "Could not create the isolated virtualenv at $VenvDir."
    exit 1
}
Print-Success "Isolated virtualenv created."

# Upgrade pip and install package
Print-Info "Installing sds-cli package..."
$PipCommand = Join-Path $VenvDir "Scripts\pip.exe"
if (-not (Test-Path -LiteralPath $PipCommand -PathType Leaf)) {
    Print-Error "The virtualenv was created, but pip is missing at $PipCommand."
    exit 1
}

& $PipCommand install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Print-Error "Could not upgrade pip in the isolated SDS environment."
    exit 1
}

& $PipCommand install $InstallSource
if ($LASTEXITCODE -ne 0) {
    Print-Error "Could not install sds-cli from $InstallSource."
    exit 1
}
Print-Success "Package installed successfully."

$SdsCommand = Join-Path $VenvDir "Scripts\sds.exe"
if (-not (Test-Path -LiteralPath $SdsCommand -PathType Leaf)) {
    Print-Error "Package installation completed, but the SDS executable is missing at $SdsCommand."
    exit 1
}

# 4. Expose CLI script
if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir | Out-Null
}

$SdsBatPath = Join-Path $BinDir "sds.bat"
"@echo off`n`"$SdsCommand`" %*" | Out-File -FilePath $SdsBatPath -Encoding ASCII
Print-Success "Command wrapper script created at: $SdsBatPath"

# 5. Install integrations only after the exact executable path is known. The
# same absolute path is persisted into generated MCP configurations.
$AgentInstallStatus = Install-AgentIntegrations $SdsCommand
if ($AgentInstallStatus -ne 0) {
    exit $AgentInstallStatus
}

# --- Output Path Verification ---
Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "    🎉  SDS Installation Completed Successfully!   " -ForegroundColor White
Write-Host "==================================================" -ForegroundColor Green
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
