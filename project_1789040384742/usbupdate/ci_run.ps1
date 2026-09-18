param([Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
. (Join-Path $PSScriptRoot 'python_runtime.ps1')
$pythonPath = Get-UpgradePython
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$taskStarted = Get-Date
$taskExit = 1
# Local CI mutex also protects against two runner processes on the same computer.
$taskMutex = New-Object System.Threading.Mutex($false, 'Local\USBUpgradeCIRenault')
$taskAcquired = $false
try {
    $taskAcquired = $taskMutex.WaitOne(0)
    if (-not $taskAcquired) { throw 'Another CI upgrade owns this device.' }
    Start-Transcript -Path (Join-Path $OutputDirectory 'console.txt') | Out-Null
    try {
        & $pythonPath -u (Join-Path $PSScriptRoot 'usb_update.py') ci-once --config (Join-Path $PSScriptRoot 'config.json')
        $taskExit = $LASTEXITCODE
    } finally {
        Stop-Transcript | Out-Null
    }
} finally {
    try {
        $logRoot = Join-Path $PSScriptRoot 'logs'
        if ($taskAcquired -and (Test-Path -LiteralPath $logRoot)) {
            Get-ChildItem -LiteralPath $logRoot -Directory |
                Where-Object { $_.CreationTime -ge $taskStarted } |
                ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $OutputDirectory -Recurse }
        }
        @{ exit_code=$taskExit; started=$taskStarted.ToString('o'); finished=(Get-Date).ToString('o') } |
            ConvertTo-Json | Set-Content -LiteralPath (Join-Path $OutputDirectory 'ci-result.json') -Encoding UTF8
    } finally {
        if ($taskAcquired) { $taskMutex.ReleaseMutex() }
        $taskMutex.Dispose()
    }
}
exit $taskExit
