$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
. (Join-Path $PSScriptRoot 'python_runtime.ps1')
$pythonPath = Get-UpgradePython
& $pythonPath (Join-Path $PSScriptRoot 'check_environment.py')
exit $LASTEXITCODE
