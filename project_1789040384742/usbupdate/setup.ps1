param([switch]$InstallAdb, [switch]$InstallCloud)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$pythonPath = $env:AUTOCAR_PYTHON
if (-not $pythonPath -and (Test-Path -LiteralPath 'C:/Users/TS/AppData/Roaming/iatset/venv/Scripts/python.exe')) {
    $pythonPath = 'C:/Users/TS/AppData/Roaming/iatset/venv/Scripts/python.exe'
}
if (-not $pythonPath) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) { $pythonCommand = Get-Command py -ErrorAction SilentlyContinue }
    if ($pythonCommand) { $pythonPath = $pythonCommand.Source }
}
if ($pythonPath) {
    & $pythonPath --version
    if ($LASTEXITCODE -ne 0) { throw 'Python unavailable. Install Python 3.10+ and enable PATH.' }
    & $pythonPath -c 'import importlib.util; raise SystemExit(0 if importlib.util.find_spec("autocar") else 1)'
    if ($LASTEXITCODE -ne 0) { Write-Warning 'AutoCar missing. Set AUTOCAR_PYTHON to the Python executable in your existing AutoCar environment.' }
} else {
    Write-Warning 'Python not found. Set AUTOCAR_PYTHON to your AutoCar environment. Do not install an unrelated package with a similar name.'
}
if ($InstallAdb) {
    $toolsDirectory = Join-Path $PSScriptRoot 'tools'
    New-Item -ItemType Directory -Path $toolsDirectory -Force | Out-Null
    $zipPath = Join-Path $toolsDirectory 'platform-tools.zip'
    if (Test-Path -LiteralPath (Join-Path $toolsDirectory 'platform-tools')) {
        throw 'tools/platform-tools already exists. Check it before installing again.'
    }
    Invoke-WebRequest -Uri 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip' -OutFile $zipPath
    Expand-Archive -LiteralPath $zipPath -DestinationPath $toolsDirectory
    Write-Host 'Set config.json adb to tools/platform-tools/adb.exe.'
}
if ($InstallCloud) {
    if (-not $pythonPath) { throw 'Set AUTOCAR_PYTHON before installing cloud dependencies.' }
    & $pythonPath -m pip install playwright
    if ($LASTEXITCODE -ne 0) { throw 'Playwright installation failed.' }
    Write-Host 'Cloud automation uses installed Microsoft Edge (msedge).'
}
$adbCommand = Get-Command adb -ErrorAction SilentlyContinue
if ($adbCommand) { & $adbCommand.Source version }
elseif (Test-Path -LiteralPath 'tools/platform-tools/adb.exe') { & './tools/platform-tools/adb.exe' version }
else { Write-Warning 'ADB missing. Run ./setup.ps1 -InstallAdb to download official Android Platform Tools.' }
if (-not (Test-Path -LiteralPath 'config.json')) { Copy-Item -LiteralPath 'config.example.json' -Destination 'config.json' }
if (-not (Test-Path -LiteralPath 'packages.json')) { Set-Content -LiteralPath 'packages.json' -Value '[]' -Encoding UTF8 }
Write-Host 'Review config.json and packages.json before running. Existing configuration is preserved.'
