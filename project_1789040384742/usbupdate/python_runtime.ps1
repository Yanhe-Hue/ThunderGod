function Test-AutoCarPython([string]$Candidate) {
    if (-not $Candidate -or -not (Test-Path -LiteralPath $Candidate -PathType Leaf)) { return $false }
    # Windows Store aliases are launchers, not installed SDK environments.
    if ($Candidate -match '\\Microsoft\\WindowsApps\\') { return $false }
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo.FileName = $Candidate
    $process.StartInfo.Arguments = '-c "import sys; assert sys.version_info >= (3,10); from autocar import AT; import tkinter; print(''AUTOCAR_ENV_OK'')"'
    $process.StartInfo.UseShellExecute = $false
    $process.StartInfo.CreateNoWindow = $true
    $process.StartInfo.RedirectStandardOutput = $true
    $process.StartInfo.RedirectStandardError = $true
    try {
        if (-not $process.Start()) { return $false }
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit(20000)) {
            $process.Kill()
            $process.WaitForExit()
            return $false
        }
        $valid = $process.ExitCode -eq 0 -and $stdout.Result.Contains('AUTOCAR_ENV_OK')
        if (-not $valid) {
            Write-Host "PYTHON_PROBE_FAILED: $Candidate (exit $($process.ExitCode))"
            Write-Host $stderr.Result
        }
        return $valid
    } catch { return $false }
    finally { $process.Dispose() }
}

function Find-AutoCarPython([string]$ProjectPath) {
    $candidates = New-Object System.Collections.Generic.List[string]
    if ($env:AUTOCAR_PYTHON) { $candidates.Add($env:AUTOCAR_PYTHON) }
    $savedPath = Join-Path $PSScriptRoot 'python.path.txt'
    if (Test-Path -LiteralPath $savedPath) { $candidates.Add((Get-Content -LiteralPath $savedPath -Raw).Trim()) }
    if ($env:APPDATA) { $candidates.Add((Join-Path $env:APPDATA 'iatset\venv\Scripts\python.exe')) }
    if ($env:VIRTUAL_ENV) { $candidates.Add((Join-Path $env:VIRTUAL_ENV 'Scripts\python.exe')) }
    foreach ($base in @($ProjectPath, $PSScriptRoot, (Split-Path -Parent $PSScriptRoot))) {
        if ($base) {
            foreach ($venv in @('.venv', 'venv')) { $candidates.Add((Join-Path $base "$venv\Scripts\python.exe")) }
        }
    }
    foreach ($command in @(Get-Command python.exe -All -ErrorAction SilentlyContinue)) {
        if ($command.Source) { $candidates.Add($command.Source) }
    }
    $seen = @{}
    foreach ($candidate in $candidates) {
        if (-not $candidate) { continue }
        $candidate = [Environment]::ExpandEnvironmentVariables($candidate.Trim().Trim('"'))
        if ($seen.ContainsKey($candidate)) { continue }
        $seen[$candidate] = $true
        Write-Host "Checking AutoCar Python: $candidate"
        if (Test-AutoCarPython $candidate) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }
    return $null
}

function Get-UpgradePython {
    if ($env:AUTOCAR_PYTHON) {
        if (-not (Test-Path -LiteralPath $env:AUTOCAR_PYTHON -PathType Leaf)) { throw 'AUTOCAR_PYTHON does not exist.' }
        return $env:AUTOCAR_PYTHON
    }
    $savedPath = Join-Path $PSScriptRoot 'python.path.txt'
    if (Test-Path -LiteralPath $savedPath) {
        $savedPython = (Get-Content -LiteralPath $savedPath -Raw).Trim()
        if (-not (Test-Path -LiteralPath $savedPython -PathType Leaf)) { throw 'Saved Python path does not exist. Run deploy.ps1 again.' }
        return $savedPython
    }
    $atsPython = Join-Path $env:APPDATA 'iatset\venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $atsPython) { return $atsPython }
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) { return $pythonCommand.Source }
    throw 'AutoCar Python unavailable. Run deploy.ps1 -PythonPath <python.exe>.'
}
