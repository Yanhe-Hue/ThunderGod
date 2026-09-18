param(
    [Parameter(Mandatory=$true)][string]$PythonPath,
    [string]$AtsProject,
    [switch]$InstallDependencies,
    [switch]$InstallAdb
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$resolvedPython = (Resolve-Path -LiteralPath $PythonPath).Path
& $resolvedPython -c 'import sys; assert sys.version_info >= (3,10); from autocar import AT; import tkinter; print(sys.executable)'
if ($LASTEXITCODE -ne 0) { throw 'Requires Python 3.10+, company AutoCar SDK and tkinter. Select your ATS Python.' }
Set-Content -LiteralPath (Join-Path $PSScriptRoot 'python.path.txt') -Value $resolvedPython -Encoding UTF8
if (-not $AtsProject) { $AtsProject = Split-Path -Parent $PSScriptRoot }
$resolvedProject = (Resolve-Path -LiteralPath $AtsProject).Path
foreach ($name in @('config','usb_stress_config')) {
    $targetConfig = Join-Path $PSScriptRoot ($name + '.json')
    if (-not (Test-Path -LiteralPath $targetConfig)) {
        $template = Get-Content -LiteralPath (Join-Path $PSScriptRoot ($name + '.example.json')) -Raw | ConvertFrom-Json
        $template.smoke.project_root = $resolvedProject.Replace('\','/')
        $template | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $targetConfig -Encoding UTF8
    }
}
if ($InstallDependencies) {
    & $resolvedPython -m pip install -r (Join-Path $PSScriptRoot 'requirements-support.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Support dependency installation failed.' }
}
if ($InstallAdb) { & (Join-Path $PSScriptRoot 'setup.ps1') -InstallAdb }
Write-Host 'Deployment initialized; existing config files preserved.'
Write-Host 'Edit both config files: adb, usb_serial, usb_root, power, usb_switch and smoke.project_root.'
Write-Host 'For bundled ADB set adb to tools/platform-tools/adb.exe. Run check_environment.ps1 next.'
