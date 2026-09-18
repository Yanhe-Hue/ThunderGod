param([string]$PythonPath, [string]$AtsProject)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

function Ask-Value([string]$Label, [string]$Default) {
    $answer = Read-Host "$Label [$Default]"
    if ([string]::IsNullOrWhiteSpace($answer)) { return $Default }
    return $answer.Trim().Trim('"')
}
function Assert-Exit([string]$Label) {
    if ($LASTEXITCODE -ne 0) { throw "$Label failed (exit $LASTEXITCODE). See deployment log." }
}
function Find-Code {
    $command = Get-Command code.cmd -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    foreach ($candidate in @(
        (Join-Path $env:LOCALAPPDATA 'Programs\Microsoft VS Code\bin\code.cmd'),
        (Join-Path $env:ProgramFiles 'Microsoft VS Code\bin\code.cmd'))) {
        if (Test-Path -LiteralPath $candidate) { return $candidate }
    }
    return $null
}
function Find-Edge {
    foreach ($base in @(${env:ProgramFiles(x86)}, $env:ProgramFiles, $env:LOCALAPPDATA)) {
        if ($base -and (Test-Path -LiteralPath (Join-Path $base 'Microsoft\Edge\Application\msedge.exe'))) { return $true }
    }
    return $false
}
function Install-WindowsApp([string]$Id) {
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) { throw "Install $Id manually; Windows winget is unavailable. Then rerun this file." }
    & $winget.Source install --id $Id --exact --source winget --silent --accept-package-agreements --accept-source-agreements
    Assert-Exit "Install $Id"
}

$logDirectory = Join-Path $PSScriptRoot 'deployment_logs'
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
$logPath = Join-Path $logDirectory ((Get-Date -Format 'yyyyMMdd_HHmmss_fff') + '.txt')
Start-Transcript -Path $logPath | Out-Null
$deploymentExit = 1
try {
    Write-Host '=== One-entry USB upgrade / stress environment deployment ==='
    Write-Host 'No USB formatting, power switching or test execution will be performed.'
    $cloudMode = (Ask-Value 'Include cloud browser and login? y/n (n = local stress)' 'n') -eq 'y'

    # Select the company SDK environment before attempting public pip packages.
    . (Join-Path $PSScriptRoot 'python_runtime.ps1')
    if (-not $PythonPath) {
        $PythonPath = Find-AutoCarPython -ProjectPath $AtsProject
        if ($PythonPath) {
            Write-Host "AutoCar Python detected automatically: $PythonPath"
        } else {
            Write-Host 'No usable AutoCar Python found. Install the company ATS/AutoCar SDK or select its existing interpreter.'
            $PythonPath = Ask-Value 'AutoCar/ATS python.exe full path' ''
        }
    }
    $PythonPath = (Resolve-Path -LiteralPath $PythonPath).Path
    # Use the same bounded process probe; PS 5.1 strips nested quotes in native -c arguments.
    if (-not (Test-AutoCarPython $PythonPath)) {
        throw 'Company AutoCar SDK/tkinter validation failed. See PYTHON_PROBE_FAILED above.'
    }
    Write-Host "Company SDK/Python OK: $PythonPath"
    $env:AUTOCAR_PYTHON = $PythonPath
    Set-Content -LiteralPath (Join-Path $PSScriptRoot 'python.path.txt') -Value $PythonPath -Encoding UTF8

    if (-not $AtsProject) {
        $suggestedProject = Split-Path -Parent $PSScriptRoot
        $existingConfig = Join-Path $PSScriptRoot 'usb_stress_config.json'
        if (Test-Path -LiteralPath $existingConfig) {
            $old = Get-Content -LiteralPath $existingConfig -Raw | ConvertFrom-Json
            if ($old.smoke.project_root) { $suggestedProject = $old.smoke.project_root }
        }
        $AtsProject = Ask-Value 'ATS project root (containing tests_scripts)' $suggestedProject
    }
    $AtsProject = (Resolve-Path -LiteralPath $AtsProject).Path
    if (-not (Test-Path -LiteralPath (Join-Path $AtsProject 'tests_scripts') -PathType Container)) {
        throw 'ATS project has no tests_scripts. Migrate the complete real test project first.'
    }
    # Bridge requires requests under the ATS project's usbupdate/logs.
    New-Item -ItemType Directory -Path (Join-Path $AtsProject 'usbupdate\logs') -Force | Out-Null

    Write-Host '[1/6] Install Python support dependencies and initialize missing configs'
    & (Join-Path $PSScriptRoot 'deploy.ps1') -PythonPath $PythonPath -AtsProject $AtsProject -InstallDependencies
    if (-not $?) { throw 'Base deployment failed.' }

    Write-Host '[2/6] Resolve ADB (download only if missing)'
    $adbPath = Join-Path $PSScriptRoot 'tools\platform-tools\adb.exe'
    if (-not (Test-Path -LiteralPath $adbPath)) {
        $adbCommand = Get-Command adb -ErrorAction SilentlyContinue
        if ($adbCommand) { $adbPath = $adbCommand.Source }
        else {
            & (Join-Path $PSScriptRoot 'setup.ps1') -InstallAdb
            if (-not $?) { throw 'ADB installation failed.' }
        }
    }
    & $adbPath version
    Assert-Exit 'ADB check'
    & $adbPath devices -l
    Assert-Exit 'ADB device listing'

    Write-Host '[3/6] Confirm hardware configuration (existing files are backed up)'
    $stressPath = Join-Path $PSScriptRoot 'usb_stress_config.json'
    $stress = Get-Content -LiteralPath $stressPath -Raw | ConvertFrom-Json
    $serial = Ask-Value 'Wired ADB serial from the list above' $stress.usb_serial
    if (-not $serial -or $serial.StartsWith('REPLACE') -or $serial.Contains(':')) { throw 'A real wired ADB serial is required.' }
    $usbRoot = Ask-Value 'USB root drive (for example F:/)' $stress.usb_root
    if ($usbRoot -notmatch '^[D-Zd-z]:[/\\]$') { throw 'USB root must be a drive root D:/ through Z:/.' }
    $switchPort = Ask-Value 'USB switch control COM port' $stress.usb_switch.port
    if ($switchPort -notmatch '^COM[1-9][0-9]*$') { throw 'Invalid switch COM port.' }
    $power = Ask-Value 'Power resource name' $stress.power.resource
    if (-not $power) { throw 'Power resource is required.' }
    $pcPort = [int](Ask-Value 'USB channel connected to PC' $stress.usb_switch.pc_usb_port)
    $carPort = [int](Ask-Value 'USB channel connected to car' $stress.usb_switch.car_usb_port)
    if ($pcPort -notin 1..4 -or $carPort -notin 1..4 -or $pcPort -eq $carPort) { throw 'USB channels must be different numbers from 1 to 4.' }
    $variant = Ask-Value 'Cloud variant: gas / no_gas' $stress.variant
    if ($variant -notin @('gas','no_gas')) { throw 'Variant must be gas or no_gas.' }
    $backupDirectory = Join-Path $logDirectory ('config_backup_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff'))
    New-Item -ItemType Directory -Path $backupDirectory | Out-Null
    foreach ($name in @('config.json','usb_stress_config.json')) {
        $file = Join-Path $PSScriptRoot $name
        Copy-Item -LiteralPath $file -Destination (Join-Path $backupDirectory $name)
        $cfg = Get-Content -LiteralPath $file -Raw | ConvertFrom-Json
        $cfg.adb = $adbPath.Replace('\','/')
        $cfg.usb_serial = $serial
        $cfg.usb_root = $usbRoot.Replace('\','/')
        $cfg.wired_adb_independent = $true
        $cfg.variant = $variant
        $cfg.power.resource = $power
        $cfg.usb_switch.port = $switchPort
        $cfg.usb_switch.pc_usb_port = $pcPort
        $cfg.usb_switch.car_usb_port = $carPort
        $cfg.smoke | Add-Member -NotePropertyName project_root -NotePropertyValue $AtsProject.Replace('\','/') -Force
        if ($name -eq 'usb_stress_config.json') {
            $cfg.smoke | Add-Member -NotePropertyName case_directory -NotePropertyValue 'tests_scripts' -Force
            $cfg.smoke | Add-Member -NotePropertyName select_before_stress -NotePropertyValue $true -Force
            # Old project-specific selections are not portable. Keep the real test files in place.
            $cfg.smoke.PSObject.Properties.Remove('case_files')
        }
        $cfg | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $file -Encoding UTF8
    }

    Write-Host '[4/6] Install/verify VS Code and ATS bridge'
    $codePath = Find-Code
    if (-not $codePath) { Install-WindowsApp 'Microsoft.VisualStudioCode'; $codePath = Find-Code }
    if (-not $codePath) { throw 'VS Code CLI not found after installation.' }
    $extensions = & $codePath --list-extensions
    Assert-Exit 'VS Code extension list'
    if (-not ($extensions | Where-Object { $_ -ieq 'ThunderSoft.AITestStudio' })) {
        throw 'Install the company AI Test Studio extension and its environment, then rerun deploy_all.ps1.'
    }
    & $codePath --install-extension (Join-Path $PSScriptRoot 'ats_bridge\usbupdate-ats-bridge-1.0.2.vsix') --force
    Assert-Exit 'ATS bridge install'
    if ($cloudMode -and -not (Find-Edge)) { Install-WindowsApp 'Microsoft.Edge' }

    Write-Host '[5/6] Validate installed environment and original ATS case discovery'
    & $PythonPath (Join-Path $PSScriptRoot 'check_environment.py')
    Assert-Exit 'Environment validation'
    & $adbPath -s $serial get-state
    Assert-Exit 'Wired ADB connection'

    Write-Host '[6/6] Optional cloud initialization'
    if ($cloudMode) {
        & $PythonPath (Join-Path $PSScriptRoot 'usb_update.py') check --config (Join-Path $PSScriptRoot 'config.json') --variant $variant
        Assert-Exit 'Cloud check/login'
    }
    $deploymentExit = 0
    Write-Host 'DEPLOYMENT COMPLETE. No upgrade has been started.'
    Write-Host 'Open the original ATS project; run Developer: Reload Window and trust the workspace.'
    Write-Host 'Review A/B package paths and dates in usb_stress_config.json, then run .\run_stress.ps1.'
    Write-Host 'Power/USB drivers and electrical wiring were not exercised by this deployment.'
} catch {
    Write-Host ('DEPLOYMENT STOPPED: ' + $_.Exception.Message) -ForegroundColor Red
    Write-Host 'Fix the reported prerequisite and rerun this same file. Do not start stress until deployment succeeds.'
} finally {
    Write-Host "Deployment log: $logPath"
    Stop-Transcript | Out-Null
}
exit $deploymentExit
