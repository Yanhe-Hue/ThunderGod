$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
. (Join-Path $PSScriptRoot 'python_runtime.ps1')
$pythonPath = Get-UpgradePython
& $pythonPath (Join-Path $PSScriptRoot 'configure_stress.py')
exit $LASTEXITCODE
