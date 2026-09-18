param([switch]$Configure)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
. (Join-Path $PSScriptRoot 'python_runtime.ps1')
$pythonPath = Get-UpgradePython
if ($Configure -or -not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'usb_stress_config.json'))) {
    & $pythonPath (Join-Path $PSScriptRoot 'configure_stress.py')
    exit $LASTEXITCODE
}
& $pythonPath (Join-Path $PSScriptRoot 'usb_stress.py') --config (Join-Path $PSScriptRoot 'usb_stress_config.json')
exit $LASTEXITCODE
