param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('auto','local','resume','verify-version','verify-adb','smoke','smoke-plan','stress','login','plan','check','connect','cloud','prepare','upgrade','verify')]
    [string]$Action,
    [string]$Config = 'config.json',
    [ValidateSet('gas','no_gas')]
    [string]$Variant,
    [string]$ExpectedQnx,
    [switch]$SkipSmoke
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$pythonPath = $env:AUTOCAR_PYTHON
if (-not $pythonPath) { $pythonPath = 'C:/Users/TS/AppData/Roaming/iatset/venv/Scripts/python.exe' }
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'AutoCar Python not found. Set AUTOCAR_PYTHON.' }
if ($Action -in @('auto', 'cloud') -and -not $Variant) {
    Add-Type -AssemblyName System.Windows.Forms
    $form = New-Object System.Windows.Forms.Form
    $form.Text = 'Select upgrade package'
    $form.Width = 420
    $form.Height = 180
    $form.StartPosition = 'CenterScreen'
    $form.FormBorderStyle = 'FixedDialog'
    $form.MaximizeBox = $false
    $form.MinimizeBox = $false
    $label = New-Object System.Windows.Forms.Label
    $label.Text = 'Choose the package to download from cloud:'
    $label.SetBounds(20, 20, 370, 25)
    $form.Controls.Add($label)
    $gasButton = New-Object System.Windows.Forms.Button
    $gasButton.Text = 'GAS (full_userdebug)'
    $gasButton.SetBounds(20, 65, 180, 40)
    $gasButton.Add_Click({ $form.Tag = 'gas'; $form.DialogResult = 'OK' })
    $form.Controls.Add($gasButton)
    $noGasButton = New-Object System.Windows.Forms.Button
    $noGasButton.Text = 'no_gas (userdebug)'
    $noGasButton.SetBounds(210, 65, 180, 40)
    $noGasButton.Add_Click({ $form.Tag = 'no_gas'; $form.DialogResult = 'OK' })
    $form.Controls.Add($noGasButton)
    try {
        if ($form.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
            Write-Host 'Cancelled. No download or upgrade started.'
            exit 0
        }
        $Variant = [string]$form.Tag
    } finally {
        $form.Dispose()
    }
}
$scriptArguments = @($Action, '--config', $Config)
if ($Variant) { $scriptArguments += @('--variant', $Variant) }
if ($ExpectedQnx) { $scriptArguments += @('--expected-qnx', $ExpectedQnx) }
if ($SkipSmoke) { $scriptArguments += '--skip-smoke' }
& $pythonPath (Join-Path $PSScriptRoot 'usb_update.py') @scriptArguments
exit $LASTEXITCODE
